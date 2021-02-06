import re
from base64 import b16encode, b16decode
from inspect import currentframe
from time import time
from typing import AsyncIterator, List, Optional, Union
from urllib.parse import unquote

from quart import Response, stream_with_context

from api.core.abc import Tokenizable
from api.core.helper import HtmlParseHelper
from api.utils.logger import logger
from api.utils.useragent import get_random_ua

__all__ = ["Anime", "AnimeMeta", "AnimeDetail", "AnimePlayList", "DirectUrl",
           "AnimeSearcher", "AnimeDetailParser", "AnimeUrlParser", "AnimeStreamProxy"]


class Anime(object):
    """单集视频对象"""

    def __init__(self, name: str = "", raw_url: str = ""):
        self.name = name  # 视频名, 比如 "第1集"
        self.raw_url = raw_url  # 视频原始 url, 可能需要进一步处理
        self.module = ""  # 用于解析的模块名

    def __repr__(self):
        return f"<Anime {self.name}>"


class AnimePlayList(object):
    """播放列表"""

    def __init__(self):
        self.name = ""  # 播放列表名, 比如 "播放线路1"
        self.num = 0  # 视频集数
        self.module = ""
        self._anime_list: List[Anime] = []

    def append(self, anime: Anime):
        self._anime_list.append(anime)
        self.num += 1

    def is_empty(self):
        return not self._anime_list

    def __iter__(self):
        return iter(self._anime_list)

    def __getitem__(self, idx: int) -> Anime:
        return self._anime_list[idx]

    def __repr__(self):
        return f"<AnimePlayList {self.name} [{self.num}]>"


class AnimeMeta(Tokenizable):
    """
    番剧的摘要信息, 不包括视频播放列表, 只用于表示搜索结果
    """

    def __init__(self, ):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 简介信息
        self.detail_url = ""  # 详情页面的链接或者参数
        self.module = currentframe().f_back.f_globals["__name__"]  # 当前模块名(调度器使用)

    @property
    def token(self) -> str:
        """通过引擎名和详情页信息生成, 可唯一表示本资源位置"""
        name = self.module.split('.')[-1]  # 缩短 token 长度, 只保留引擎名
        sign = f"{name}|{self.detail_url}".encode("utf-8")
        return b16encode(sign).decode("utf-8").lower()

    @classmethod
    def build_from(cls, token: str) -> "AnimeMeta":
        """使用 token 构建一个不完整但可以被解析的 AnimeMeta 对象"""
        name, detail_url = b16decode(token.upper()).decode("utf-8").split("|")
        meta = AnimeMeta()
        meta.module = "api.anime." + name
        meta.detail_url = detail_url
        return meta

    def __repr__(self):
        return f"<AnimeMeta {self.title}>"


class AnimeDetail(object):
    """
    番剧详细页的信息, 包括多个视频播放列表, 番剧的描述、分类等信息
    """

    def __init__(self):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 番剧的简介信息
        # self.filtered = False  # 播放列表是否经过过滤
        self.module = currentframe().f_back.f_globals["__name__"]  # 自动设置当前模块名
        self._playlists: List[AnimePlayList] = []  # 一部番剧可能有多条播放列表

    def get_anime(self, p_index: int, ep_index: int) -> Optional[Anime]:
        """获取某一个播放列表的某个视频对象"""
        try:
            return self[p_index][ep_index]
        except IndexError:
            logger.error(f"IndexError, anime index: {p_index} {ep_index}")
            return None

    def append_playlist(self, playlist: AnimePlayList):
        """添加一个播放列表"""
        playlist.module = self.module
        for anime in playlist:
            anime.module = self.module
        self._playlists.append(playlist)

    def is_empty(self):
        return not self._playlists

    def __getitem__(self, p_index: int) -> AnimePlayList:
        return self._playlists[p_index]

    def __iter__(self):
        return iter(self._playlists)

    def __repr__(self):
        return f"<AnimeDetail {self.title} [{len(self._playlists)}]>"


class DirectUrl(object):
    """
    直链对象, 保存了链接和有效时间
    """

    def __init__(self, url: str = "", lifetime: int = 86400):
        self._url = unquote(url)  # 直链
        self._parse_time = time()  # 解析出直链的时刻
        self._lifetime = lifetime  # 直链剩余寿命, 单位秒
        self._extract_lifetime_from_url()

    @property
    def real_url(self):
        return self._url

    @property
    def left_lifetime(self) -> int:
        """直链剩余寿命"""
        seconds = int(self._parse_time + self._lifetime - time())
        return seconds if seconds > 0 else 0

    def is_available(self) -> bool:
        """视频直链是有效"""
        return self._url.startswith("http") and self.left_lifetime > 0

    def _extract_lifetime_from_url(self):
        """尝试从直链中找到资源失效时间戳, 计算直链寿命"""
        ts_start = int(time() / 1e5)  # 当前时间戳的前5位
        stamps = re.findall(rf"{ts_start}\d{{5}}", self._url)
        for stamp in stamps:
            lifetime = int(stamp) - int(time())
            if lifetime > 60:  # 有效期大于 1 分钟的算有效
                logger.info(f"Found timestamp in real url, resource left lifetime: {lifetime}s")
                self._lifetime = lifetime

    def __repr__(self):
        return f"<DirectUrl ({self.left_lifetime}s) {self._url}>"


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

    async def parse(self, raw_url: str) -> Union[DirectUrl, str]:
        """
        重写此方法以实现直链的解析和有效期提取工作
        :param raw_url: 原始链接
        :return: 视频直链对象(含直链和有效期)
        """
        return DirectUrl(raw_url)

    async def _parse(self, raw_url: str) -> DirectUrl:
        """解析直链, 捕获引擎模块未处理的异常"""
        try:
            await self.init_session()
            url = await self.parse(raw_url)
            if not isinstance(url, DirectUrl):
                url = DirectUrl(url)  # 方便 parse 直接返回字符串链接
            if url.is_available():  # 解析成功
                logger.info(f"Parse success: {url}")
                return url
            return DirectUrl()
        except Exception as e:
            logger.exception(e)
            return DirectUrl()
        finally:
            await self.close_session()


class AnimeStreamProxy(HtmlParseHelper):
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

    async def make_response(self, range_field: str = None):
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
            return Response(b"")

        @stream_with_context
        async def stream_iter():
            while chunk := await resp.content.readany():
                yield chunk

        status = 200
        if resp.headers.get("Content-Type") == "video/mp4":
            status = 206  # 否则无法拖到进度条
        return Response(stream_iter(), headers=dict(resp.headers), status=status)
