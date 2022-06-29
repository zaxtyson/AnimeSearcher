import re
from typing import Optional

from sanic.request import Request as SanicRequest, Header

from core.cache import cache
from core.http_client import client
from models.anime import VideoInfo
from utils.log import logger
from utils.misc import get_path, get_host, get_name
from utils.useragent import get_random_ua

__all__ = ["VideoProxy", "clean_resp_headers"]


def clean_resp_headers(resp_headers: Header) -> Header:
    allow_filed = ["connection", "server", "date", "accept-ranges", "access-control-allow-origin",
                   "access-control-allow-origin", "content-length", "content-type", "content-range"]
    headers = Header()
    for k, v in resp_headers.items():
        if k in allow_filed:
            headers[k] = v
    return headers


class BaseProxy:

    def __init__(self, info: VideoInfo):
        self._info = info

    def set_proxy_headers(self, request_url: str) -> Optional[Header]:
        """
        重写此方法, 可为不同的 url 设置不同的 headers
        若返回 None, 则使用默认 headers(随机 user-agent, referer 指向请求站点)

        :param request_url: 待请求资源的 url
        :return: 指定的 headers
        """
        return None

    def _get_proxy_headers(self, url: str) -> Header:
        headers = self.set_proxy_headers(url) or Header()
        headers.setdefault("Referer", get_host(url))
        headers.setdefault("User-Agent", get_random_ua())
        return headers


class StreamProxy(BaseProxy):

    async def make_response_for_stream(self, request: SanicRequest):
        url = self._info.raw_url
        headers = self._get_proxy_headers(url)
        if range_header := request.headers.get("range"):
            headers["Range"] = range_header

        async with client.do(request.method, url, headers=headers) as r:
            r_headers = clean_resp_headers(r.headers)
            r_headers["Server"] = self.__class__.__name__
            r_headers["Content-Disposition"] = f'attachment; filename="{get_name(request.url)}.{self._info.format}"'
            resp = await request.respond(status=r.status, headers=r_headers)
            while chunk := await r.content.read(4096):
                # logger.debug(f"Read {len(chunk)} bytes")
                await resp.send(chunk)


class M3U8Proxy(BaseProxy):

    def __init__(self, info: VideoInfo):
        super().__init__(info)
        self._proxy_router_prefix = ""

    def set_chunk_proxy_prefix(self, url_prefix: str):
        self._proxy_router_prefix = url_prefix

    async def read_data(self, url: str) -> bytes:
        headers = self._get_proxy_headers(url)
        async with client.get(url, headers=headers) as r:
            return await r.content.read()

    async def read_text(self, url: str) -> str:
        data = await self.read_data(url)
        return data.decode()

    async def get_m3u8_text(self, index_url: str) -> str:
        """
        获取 index.m3u8 文件的内容, 如果该文件需要进一步处理, 比如需要跳转一次
        才能得到 m3u8 的内容, 或者接口返回的数据经过加密、压缩时, 请重写本方法以
        获取 m3u8 文件的真实内容

        :param index_url: index.m3u8 文件的链接
        :return: index.m3u8 的内容
        """
        text = await self.read_text(index_url)
        chunk_urls = []
        for line in text.splitlines():
            if not line.startswith("#"):
                chunk_urls.append(line)
        if len(chunk_urls) > 1:
            return text  # m3u8 文件完整

        # 只有一行, 说明还需继续跟进
        next_url = chunk_urls[0]
        if not next_url.startswith("http"):
            if next_url.startswith("/"):
                next_url = get_host(index_url) + next_url
            else:
                next_url = get_path(index_url) + "/" + next_url

        return await self.read_text(next_url)

    def fix_m3u8_key_url(self, index_url: str, key_url: str) -> str:
        """
        修复 m3u8 密钥的链接(通常使用 AES-128 加密数据流), 默认以 index.m3u8
        同级路径补全 key 的链接, 其它情况请重写本方法

        :param index_url: index.m3u8 的链接
        :param key_url: 密钥的链接(可能不完整)
        :return: 密钥的完整链接
        """
        if key_url.startswith("http"):
            return key_url

        if key_url.startswith("/"):
            return get_host(index_url) + key_url

        return get_path(index_url) + '/' + key_url

    def fix_m3u8_chunk_url(self, index_url: str, chunk_url: str) -> str:
        """
        修复 m3u8 文件中数据块的链接, 通常需要补全域名. 默认使用 index.m3u8
        的域名补全数据块的域名部分, 其它情况请重新此方法

        :param index_url: index.m3u8 的链接
        :param chunk_url: 数据块的链接(通常不完整)
        :return: 数据块的完整链接
        """
        if chunk_url.startswith("http"):
            return chunk_url

        if chunk_url.startswith("/"):
            return get_host(index_url) + chunk_url

        return get_path(index_url) + "/" + chunk_url

    def fix_chunk_data(self, chunk_url: str, chunk: bytes) -> bytes:
        """
        修复数 m3u8 数据据块, 用于解除数据混淆
        比如常见的图片隐写, 每一段视频数据存放于一张图片中, 需要剔除图片的数据
        可使用 binwalk 等工具对二进制数据进行分析, 以确定图像与视频流的边界位置

        :param chunk_url: 数据块的链接
        :param chunk: 数据块的二进制数据
        :return: 修复完成的二进制数据
        """
        return chunk

    async def _fix_m3u8_text(self, text: str) -> str:
        if not text.startswith("#EXTM3U"):
            logger.error(f"Format error, not a M3U8 file: {text[:512]}")
            return ""

        fixed_m3u8_text = []
        for line in text.splitlines():
            if line.startswith("#EXT-X-KEY"):  # fix url of key
                key_url = re.search(r'URI="(.+?)"', line).group(1)
                fixed_key_url = self._proxy_router_prefix + self.fix_m3u8_key_url(self._info.raw_url, key_url)
                line = line.replace(key_url, fixed_key_url)
            if not line.startswith("#"):  # fix chunk data
                line = self._proxy_router_prefix + self.fix_m3u8_chunk_url(self._info.raw_url, line)
            fixed_m3u8_text.append(line)
        return '\n'.join(fixed_m3u8_text)

    async def make_response_for_m3u8(self, request: SanicRequest):
        direct_link = self._info.raw_url
        cached_text = cache.get(direct_link)
        if cached_text:
            logger.info(f"Use cached M3U8 file for {direct_link}")
            resp = await request.respond(
                content_type="application/vnd.apple.mpegurl",
                headers={
                    "Server": self.__class__.__name__,
                    "Content-Disposition": f'attachment; filename="{get_name(request.url)}.m3u8"'
                }
            )
            await resp.send(cached_text)
        else:
            text = await self.get_m3u8_text(direct_link)
            text = await self._fix_m3u8_text(text)
            logger.info(f"Read M3U8 file: {len(text) / 1024}kb")
            if text:
                cache.set(direct_link, text, self._info.lifetime)
                resp = await request.respond(
                    content_type="application/vnd.apple.mpegurl",
                    headers={
                        "Server": self.__class__.__name__,
                        "Content-Disposition": f'attachment; filename="{get_name(request.url)}.m3u8"'
                    }
                )
                await resp.send(text)
            else:
                logger.error(f"Parse M3U8 file failed: {direct_link}")
                resp = await request.respond(
                    status=500,
                    content_type="text/plain",
                    headers={"Server": self.__class__.__name__}
                )
                await resp.send("Parse m3u8 file failed")

    async def make_response_for_chunk(self, request: SanicRequest, chunk_url: str):
        headers = self._get_proxy_headers(chunk_url)
        async with client.get(chunk_url, headers=headers) as r:
            r_headers = clean_resp_headers(r.headers)
            r_headers["Server"] = self.__class__.__name__
            resp = await request.respond(status=r.status, headers=r_headers)
            chunk = await r.read()
            chunk = self.fix_chunk_data(chunk_url, chunk)
            await resp.send(chunk)


class VideoProxy(StreamProxy, M3U8Proxy):
    module = ""

    def __init__(self, info: VideoInfo):
        super().__init__(info)

    async def make_response(self, request: SanicRequest):
        if self._info.format.lower() == "hls":
            await self.make_response_for_m3u8(request)
        else:
            await self.make_response_for_stream(request)
