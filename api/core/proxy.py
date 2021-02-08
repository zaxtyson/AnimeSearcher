from quart import Response, stream_with_context

from api.core.anime import DirectUrl
from api.core.helper import HtmlParseHelper

__all__ = ["RequestProxy", "StreamProxy"]

from api.utils.logger import logger
from api.utils.useragent import get_random_ua


class RequestProxy(HtmlParseHelper):

    async def make_response(self, url: str) -> Response:
        """代理访问远程请求"""
        await self.init_session()
        resp = await self.get(url, allow_redirects=True)
        if not resp or resp.status != 200:
            return Response("resource maybe not available", status=404)
        data = await resp.read()
        resp_headers = {
            "Content-Type": resp.content_type
        }
        return Response(data, headers=resp_headers, status=200)

    async def close(self):
        await self.close_session()


class StreamProxy(HtmlParseHelper):
    """
    代理访问视频数据流, 以绕过资源服务器的防盗链和本地浏览器跨域策略
    """

    def __init__(self, url: DirectUrl):
        super().__init__()
        self._url = url.real_url  # 直链应该有效

    def set_proxy_headers(self, real_url: str) -> dict:
        """
        为特定的直链设置代理 Headers, 如果服务器存在防盗链, 可以尝试重写本方法
        若本方法返回空则使用默认 Headers
        若设置的 Headers 不包含 User-Agent 则随机生成一个
        """
        return {}

    def _get_proxy_headers(self, real_url: str) -> dict:
        """获取代理访问使用的 Headers"""
        headers = self.set_proxy_headers(real_url)
        if not headers:
            return {"User-Agent": get_random_ua()}
        if "user-agent" not in (key.lower() for key in headers.keys()):
            headers["User-Agent"] = get_random_ua()
        return headers

    # async def get_m3u8_response(self) -> Response:
    #     hls_type = "application/vnd.apple.mpegURL"
    #     headers = {"Location": self._url}
    #     return Response(headers=headers, content_type=hls_type)

    async def get_stream_response(self, range_field: str = None):
        """
        读取远程的视频流，并伪装成本地的响应返回给客户端
        206 连续请求会导致连接中断, asyncio 库在 Windows 平台触发 ConnectionAbortedError
        偶尔出现 LocalProtocolError, 是 RFC2616 与 RFC7231 HEAD 请求冲突导致
        See:
            https://bugs.python.org/issue26509
            https://gitlab.com/pgjones/quart/-/issues/45
        """
        await self.init_session()
        proxy_headers = self._get_proxy_headers(self._url)
        if range_field is not None:
            proxy_headers["range"] = range_field
            logger.debug(f"Client request stream range: {range_field}")

        resp = await self.get(self._url, headers=proxy_headers)
        if not resp:
            return Response(b"", status=404)

        @stream_with_context
        async def stream_iter():
            while chunk := await resp.content.readany():
                yield chunk

        status = 200
        if resp.content_type in ["video/mp4", "application/octet-stream"]:
            status = 206  # 否则无法拖到进度条

        resp_headers = {
            "Content-Type": resp.content_type,
            "Content-Range": resp.headers.get("Content-Range")
        }
        return Response(stream_iter(), headers=resp_headers, status=status)

    # async def make_response(self, range_field: str = None):
    #     await self.init_session()
    #     if self._url.endswith("m3u8"):
    #         return await self.get_m3u8_response()
    #     return await self.get_stream_response(range_field)
