import re

from quart import Response, stream_with_context

from api.core.anime import AnimeInfo
from api.core.helper import HtmlParseHelper
from api.utils.logger import logger
from api.utils.tool import extract_domain
from api.utils.useragent import get_random_ua

__all__ = ["RequestProxy", "AnimeProxy"]


class HttpProxy(HtmlParseHelper):

    def __init__(self):
        super().__init__()

    def set_proxy_headers(self, url: str) -> dict:
        """
        为特定的直链设置代理 Headers, 如果服务器存在防盗链, 可以尝试重写本方法,
        若本方法返回空则使用默认 Headers,
        若设置的 Headers 不包含 User-Agent 则随机生成一个
        """
        return {}

    def _get_proxy_headers(self, url: str) -> dict:
        """获取代理访问使用的 Headers"""
        headers = self.set_proxy_headers(url)
        if not headers:
            return {"User-Agent": get_random_ua()}
        if "user-agent" not in (key.lower() for key in headers.keys()):
            headers["User-Agent"] = get_random_ua()
        return headers


class RequestProxy(HttpProxy):

    async def make_response(self, url: str) -> Response:
        """代理访问远程请求"""
        await self.init_session()
        resp = await self.get(url, allow_redirects=True)
        if not resp or resp.status != 200:
            return Response("resource maybe not available", status=404)
        data = await resp.read()
        resp_headers = {
            "Content-Type": resp.content_type,
            "Content-Length": resp.content_length
        }
        return Response(data, headers=resp_headers, status=200)

    async def close(self):
        await self.close_session()


class BaseAnimeProxy(HttpProxy):

    def __init__(self, info: AnimeInfo):
        super().__init__()
        self._info = info

    def is_available(self) -> bool:
        return self._info.is_available()

    def get_stream_format(self) -> str:
        return self._info.format


class StreamProxy(BaseAnimeProxy):
    """
    支持 MP4, FLV 之类的数据流代理播放
    """

    async def make_response_with_range(self, range_field: str = None) -> Response:
        """
        读取远程的视频流，并伪装成本地的响应返回给客户端,
        206 连续请求会导致连接中断, asyncio 库在 Windows 平台触发 ConnectionAbortedError,
        偶尔出现 LocalProtocolError, 是 RFC2616 与 RFC7231 HEAD 请求冲突导致,
        See:

            https://bugs.python.org/issue26509
            https://gitlab.com/pgjones/quart/-/issues/45
        """
        url = self._info.real_url
        proxy_headers = self._get_proxy_headers(url)
        if range_field is not None:
            proxy_headers["range"] = range_field
            logger.debug(f"Client request stream range: {range_field}")

        await self.init_session()
        resp = await self.get(url, headers=proxy_headers)
        if not resp:
            return Response(b"", status=404)

        @stream_with_context
        async def stream_iter():
            while chunk := await resp.content.read(4096):
                yield chunk

        status = 206 if self._info.format == "mp4" else 200  # 否则无法拖到进度条
        return Response(stream_iter(), headers=dict(resp.headers), status=status)


class M3U8Proxy(BaseAnimeProxy):
    """
    支持 M3u8 视频代理播放
    """

    def __init__(self, info: AnimeInfo):
        super().__init__(info)
        self._chunk_proxy_router = ""
        self._cache_m3u8_text = ""

    def set_chunk_proxy_router(self, domain: str):
        """设置 m3u8 数据块代理路由地址"""
        self._chunk_proxy_router = domain

    async def read_data(self, url: str) -> bytes:
        """使用设置的 Header 读取 URL 对应的资源, 返回原始二进制数据"""
        await self.init_session()
        proxy_headers = self._get_proxy_headers(url)
        resp = await self.get(url, headers=proxy_headers, allow_redirects=True)
        if not resp or resp.status != 200:
            return b""
        return await resp.read()

    async def read_text(self, url: str, encoding="utf-8") -> str:
        """使用设置的 Header 读取 URL 对应的资源, 返回编码后的文本"""
        return (await self.read_data(url)).decode(encoding)

    async def get_m3u8_text(self, index_url: str) -> str:
        """
        获取 index.m3u8 文件的内容, 如果该文件需要进一步处理,
        比如需要跳转或者存在数据隐写, 请重写本方法

        :param index_url: index.m3u8 文件的链接
        :return: index.m3u8 的内容
        """
        return await self.read_text(index_url)

    def fix_m3u8_key_url(self, index_url: str, key_url: str) -> str:
        """
        修复 m3u8 密钥的链接(通常使用 AES-128 加密数据流),
        默认以 index.m3u8 同级路径补全 key 的链接,
        其它情况请重写本方法

        :param index_url: index.m3u8 的链接
        :param key_url: 密钥的链接(可能不完整)
        :return: 密钥的完整链接
        """
        if key_url.startswith("http"):
            return key_url

        path = '/'.join(index_url.split('/')[:-1])
        return path + '/' + key_url

    def fix_m3u8_chunk_url(self, index_url: str, chunk_url: str) -> str:
        """
        替换 m3u8 文件中数据块的链接, 通常需要补全域名,
        默认情况使用 index.m3u8 的域名补全数据块域名部分,
        其它情况请重新此方法

        :param index_url: index.m3u8 的链接
        :param chunk_url: m3u8 文件中数据块的链接(通常不完整)
        :return: 修复完成的 m3u8 文件
        """
        if chunk_url.startswith("http"):  # url 无需补全
            return chunk_url
        elif chunk_url.startswith('/'):
            return extract_domain(index_url) + chunk_url
        else:
            return extract_domain(index_url) + '/' + chunk_url

    def fix_chunk_data(self, url: str, chunk: bytes) -> bytes:
        """
        修复数 m3u8 数据据块, 用于解除数据混淆(比如常见的图片隐写)

        :param url: 数据块的链接
        :param chunk: 数据块的二进制数据
        :return: 修复完成的二进制数据
        """
        return chunk

    async def _fix_m3u8_text(self, text: str) -> str:
        fixed_m3u8_text = []
        for line in text.splitlines():
            if line.startswith("#EXT-X-KEY"):  # 修复密钥链接
                key_url = re.search(r'URI="(.+?)"', line).group(1)
                fixed_key_url = self._chunk_proxy_router + '/' + self.fix_m3u8_key_url(self._info.real_url, key_url)
                line = line.replace(key_url, fixed_key_url)
            if not line.startswith("#"):  # 修复数据块链接
                line = self._chunk_proxy_router + '/' + self.fix_m3u8_chunk_url(self._info.real_url, line)
            fixed_m3u8_text.append(line)
        return '\n'.join(fixed_m3u8_text)

    async def _get_fixed_m3u8_text(self) -> str:
        text = await self.get_m3u8_text(self._info.real_url)
        return await self._fix_m3u8_text(text)

    async def make_response_for_m3u8(self) -> Response:
        if not self._cache_m3u8_text:
            self._cache_m3u8_text = await self._get_fixed_m3u8_text()
            logger.debug(f"Cache m3u8 text, size: {len(self._cache_m3u8_text) // 1024}kb")
        return Response(self._cache_m3u8_text, mimetype="application/vnd.apple.mpegurl")

    async def make_response_for_chunk(self, url: str) -> Response:
        proxy_headers = self._get_proxy_headers(url)
        resp = await self.get(url, headers=proxy_headers)
        if not resp:
            return Response(b"", status=404)
        chunk = self.fix_chunk_data(url, await resp.read())
        return Response(chunk, headers=dict(resp.headers), status=200)


class AnimeProxy(StreamProxy, M3U8Proxy):
    """
    代理访问视频数据流, 以绕过资源服务器的防盗链和本地浏览器跨域策略
    """

    def __init__(self, info: AnimeInfo):
        super(AnimeProxy, self).__init__(info)
