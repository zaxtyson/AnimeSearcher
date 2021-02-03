import re
from time import time
from typing import AsyncIterator, Tuple

from aiohttp import ClientResponse
from quart import Response
from quart.wrappers.response import IterableBody
from yarl import URL

from api.core.helper import HtmlParseHelper
from api.core.models import AnimeMeta, AnimeDetail, Video
from api.utils.logger import logger

__all__ = ["AnimeSearcher", "AnimeDetailParser", "AnimeHandler"]

from api.utils.useragent import get_random_ua


class AnimeSearcher(HtmlParseHelper):
    """
    番剧搜索引擎
    """

    async def search(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        """
        搜索番剧, 提取关键词对应的全部番剧摘要信息
        :param keyword: 搜索关键词
        :return: 元素为番剧摘要信息类 AnimeMeta 的异步生成器
        """
        yield

    async def _search(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        """本方法由引擎管理器负责调用, 创建 session, 捕获异常并记录"""
        try:
            await self.init_session()
            async for item in self.search(keyword):
                yield item
        except Exception as e:
            logger.exception(e)
            return
        finally:
            await self.close_session()


class AnimeDetailParser(HtmlParseHelper):
    """
    番剧详情页面解析器
    """

    async def parse(self, detail_url: str) -> AnimeDetail:
        """
        解析番剧的详情页面, 提取视频播放列表和其它信息
        :param detail_url: 详情页面的 URL(可能并不完整)
        :return: 番剧详情信息类 AnimeDetail
        """
        pass

    async def _parse(self, detail_url: str) -> AnimeDetail:
        """本方法由引擎管理器负责调用, 创建 session, 捕获异常并记录"""
        try:
            await self.init_session()
            return await self.parse(detail_url)
        except Exception as e:
            logger.exception(e)
            return AnimeDetail()
        finally:
            await self.close_session()


class AnimeUrlParser(HtmlParseHelper):
    """
    视频直链解析器
    """

    def __init__(self, video: Video):
        super().__init__()
        self._raw_url = video.raw_url  # 视频的原始链接, 可能只是些参数信息, 需要进一步处理
        self._real_url = ""  # 解析出来的视频直链
        self._parse_time = 0  # 解析出直链的时刻
        self._lifetime = 3600 * 24  # 直链剩余寿命, 单位秒

    async def parse(self, raw_url: str) -> str:
        """
        重写此方法以完成直链的解析工作
        :param raw_url: 原始链接
        :return: 视频直链
        """
        return self._raw_url

    def set_lifetime(self, real_url: str) -> int:
        """
        重写此方法以设置直链寿命, 单位秒, 未设置则使用默认值
        :param real_url: 视频直链
        :return: 有效时间
        """
        pass

    @property
    def _left_lifetime(self) -> int:
        """直链剩余寿命"""
        seconds = int(self._parse_time + self._lifetime - time())
        return seconds if seconds > 0 else 0

    def _has_expired(self) -> bool:
        """视频直链是否过期"""
        return self._left_lifetime == 0

    def _extract_lifetime_from_url(self, real_url: str) -> int:
        """尝试从直链中找到资源失效时间戳, 计算直链寿命"""
        ts_start = int(time() / 1e5)  # 当前时间戳的前5位
        stamps = re.findall(rf"{ts_start}\d{{5}}", real_url)
        for stamp in stamps:
            lifetime = int(stamp) - int(time())
            if lifetime > 60:  # 有效期大于 1 分钟的算有效
                logger.info(f"Found timestamp in real url, resource left lifetime: {lifetime}s")
                return int(lifetime)
        return self._lifetime

    async def _parse_all(self, raw_url: str) -> Tuple[str, int]:
        """解析直链, 获取直链有效时间, 捕获引擎模块未处理的异常"""
        try:
            await self.init_session()
            real_url = await self.parse(raw_url)
            real_url = URL(real_url).human_repr()
            lifetime = self.set_lifetime(real_url) or self._extract_lifetime_from_url(real_url)
            if not real_url or not real_url.startswith("http"):
                return "", 0
            self._parse_time = time()
            self._lifetime = lifetime
            self._real_url = real_url
            return real_url, lifetime
        except Exception as e:
            logger.exception(e)
            return "", 0
        # finally:
        #     await self.close_session()

    async def get_real_url(self) -> str:
        """获取视频直链, 如果有缓存且缓存未过期, 则使用缓存的值"""
        if self._real_url.startswith("http"):  # 存在缓存
            if not self._has_expired():  # 未过期
                logger.info(f"Use cached real url: {self._real_url}, Lifetime: {self._left_lifetime}s")
                return self._real_url
            logger.info(f"Cached real url has expired")

        # 视频直链尚未解析或直链已经过期
        for _ in range(3):  # 解析时给 3 次机会, 防止网络异常导致解析失败
            real_url, lifetime = await self._parse_all(self._raw_url)
            if real_url:  # 解析成功
                logger.info(f"Real url: {real_url}, Lifetime: {lifetime}s")
                return real_url
            logger.warning("Parsing real url failed, retry...")

        # 这还解析失败的话, 这个资源多半失效了
        logger.error(f"Parsing failed, the resource may be invalid.")
        return ""


class AnimeProxy(AnimeUrlParser):
    """
    代理访问视频数据流, 以绕过资源服务器的防盗链和本地浏览器跨域策略
    """

    def __init__(self, video: Video):
        super().__init__(video)
        self._video_format = ""  # 视频格式

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

    async def _detect_video_format(self) -> str:
        """判断视频的格式"""
        # 尝试从 url 提取视频后缀
        real_url = await self.get_real_url()
        try:
            ext = real_url.split("?")[0].split(".")[-1].lower()
            if ext in ["mp4", "flv"]:
                logger.info(f"Detected format from url: [{ext}]")
                return ext
            if ext in ["m3u", "m3u8"]:
                logger.info(f"Detected format from url: [{ext}]")
                return "hls"
        except (IndexError, AttributeError):
            pass

        # 通过 magic number 识别数据格式
        format_hex = {
            "mp4": ["69736F6D", "70617663", "18667479706D703432", "4D50454734", "4C617666"],
            "flv": ["464C56"],
            "hls": ["4558544D3355"]
        }

        headers = self._get_proxy_headers(real_url)
        resp = await self.get(real_url, headers=headers, allow_redirects=True)
        if not resp or resp.status != 200:
            return ""

        data = await resp.content.read(512)
        resp.close()
        logger.debug("Detecting video format from binary stream")
        video_meta = data.hex().upper()
        for fmt, hex_list in format_hex.items():
            for magic in hex_list:
                if magic in video_meta:
                    logger.debug(f"Video format: [{fmt}]")
                    return fmt

        logger.error("Can't detect video format from binary stream")
        logger.debug(f"Raw binary stream (512byte): {video_meta}")
        return ""

    async def get_video_format(self) -> str:
        """获取视频格式"""
        if not self._video_format:
            self._video_format = await self._detect_video_format()
        return self._video_format

    @staticmethod
    def _build_response(resp: ClientResponse) -> IterableBody:
        async def stream():
            async with resp:
                while True:
                    chunk = await resp.content.readany()
                    if not chunk:
                        break
                    yield chunk

        return IterableBody(stream())

    async def make_response(self, req_headers: dict) -> Response:
        """
        读取远程的视频流，并伪装成本地的响应返回给客户端
        """
        fmt = await self.get_video_format()
        real_url = await self.get_real_url()
        proxy_headers = self._get_proxy_headers(real_url)
        range_field = req_headers.get("range")

        if range_field:
            proxy_headers["range"] = range_field

        if fmt in ["mp4", "flv"]:
            resp = await self.get(real_url, headers=proxy_headers)
            body = self._build_response(resp)
            return Response(body, headers=dict(resp.headers), status=resp.status)

        # TODO: implement m3u8 video stream proxy
        if fmt == "hls":  # m3u8 代理暂未实现, 重定向回去
            logger.info(f"Can't proxy video with format: [m3u8]")
            return Response("", status=302, headers={"Location": real_url})

        return Response("Can't proxy this video stream", status=500)


class AnimeHandler(AnimeProxy):
    """
    视频处理器, 实现直链解析, 代理访问等功能
    """
    pass
