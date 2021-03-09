import re
from base64 import b16encode, b16decode
from inspect import currentframe
from time import time
from typing import AsyncIterator, List, Optional, Union
from urllib.parse import unquote

from api.core.abc import Tokenizable
from api.core.helper import HtmlParseHelper
from api.utils.logger import logger

__all__ = ["Anime", "AnimeMeta", "AnimeDetail", "AnimePlayList", "AnimeInfo",
           "AnimeSearcher", "AnimeDetailParser", "AnimeUrlParser"]


class Anime(object):
    """单集视频对象"""

    def __init__(self, name: str = "", raw_url: str = ""):
        #: 视频名, 比如 "第1集"
        self.name = name
        #: 视频原始 url, 可能需要进一步处理
        self.raw_url = raw_url
        self.module = ""

    def __repr__(self):
        return f"<Anime {self.name}>"


class AnimePlayList(object):
    """播放列表"""

    def __init__(self):
        #: 播放列表名, 比如 "播放线路1"
        self.name = ""
        #: 视频集数, 不确定时为  -1
        self.num = 0
        self.module = ""
        self._anime_list: List[Anime] = []

    def append(self, anime: Anime):
        """添加一集视频"""
        self._anime_list.append(anime)
        self.num += 1

    def is_empty(self):
        """播放列表判空"""
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
        #: 番剧标题
        self.title = ""
        #: 封面图片链接
        self.cover_url = ""
        #: 番剧的分类
        self.category = ""
        #: 简介信息
        self.desc = ""
        #: 详情页面的链接或者相关参数
        self.detail_url = ""
        #: 当前模块名(调度器使用)
        self.module = currentframe().f_back.f_globals["__name__"]

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
        #: 番剧标题
        self.title = ""
        #: 封面图片链接
        self.cover_url = ""
        #: 番剧的分类
        self.category = ""
        #: 番剧的简介信息
        self.desc = ""
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


class AnimeInfo(HtmlParseHelper):
    """
    解析之后的视频, 保存了链接和有效时间等信息
    """

    def __init__(self, url: str = "", lifetime: int = 0):
        super().__init__()
        self._url = unquote(url)  # 直链
        self._parse_time = time()  # 解析出直链的时刻
        self._format = "unknown"  # 视频格式
        self._lifetime = lifetime
        self._size = 0
        self._resolution = "0x0"

    @property
    def real_url(self) -> str:
        return self._url

    @property
    def left_lifetime(self) -> int:
        """直链剩余寿命"""
        seconds = int(self._parse_time + self._lifetime - time())
        return seconds if seconds > 0 else 0

    @property
    def format(self) -> str:
        """获取视频格式"""
        return self._format

    @property
    def size(self) -> float:
        return self._size

    @property
    def resolution(self) -> str:
        return self._resolution

    def is_available(self) -> bool:
        """视频直链是有效"""
        return self._url.startswith("http") and self.left_lifetime > 0

    async def detect_more_info(self):
        await self.init_session()
        logger.info("Detect information of video...")
        resp = await self.get(self._url, allow_redirects=True)
        if resp and resp.status == 200:
            self._lifetime = await self._detect_lifetime()
            self._format = self._detect_format(resp.content_type)
            self._size = resp.content_length or 0
            chunk = await resp.content.read(512)
            self._resolution = self._detect_resolution(chunk)
        else:
            self._lifetime = 0  # 多半是资源失效了
        await self.close_session()

    async def _detect_lifetime(self):
        """尝试从直链中找到资源失效时间戳, 计算直链寿命"""
        ts_start = int(time() / 1e5)  # 当前时间戳的前5位
        stamps = re.findall(rf"{ts_start}\d{{5}}", self._url)
        for stamp in stamps:
            lifetime = int(stamp) - int(time())
            if lifetime > 60:  # 有效期大于 1 分钟的算有效
                logger.info(f"Found timestamp in real url, resource left lifetime: {lifetime}s")
                return lifetime
        return 86400  # 默认资源有效期为一天

    def _detect_format(self, c_type: str):
        fmt_table = {".m3u8": "hls", ".flv": "flv", ".mpd": "dash", ".mp4": "mp4"}
        for k, v in fmt_table.items():
            if k in self._url:
                return v

        if c_type in ["application/vnd.apple.mpegurl", "application/x-mpegurl"]:
            return "hls"
        if c_type in ["video/mp4", "application/octet-stream"]:
            return "mp4"
        return "unknown"

    def _detect_resolution(self, data: bytes) -> str:
        # TODO: detect video resolution from meta block, MPEG-TS/MPEG-4
        if self._format == "hls":
            text = data.decode("utf-8")
            if ret := re.search(r"RESOLUTION=(\d+x\d+)", text):
                self._resolution = ret.group(1)
        elif self._format == "mp4":
            tkhd_box_pos = data.find(b"\x74\x6B\x68\x64")
            if tkhd_box_pos != -1:
                start = tkhd_box_pos + 0x4E
                width = int(data[start:start + 4].hex(), 16)
                height = int(data[start + 4:start + 8].hex(), 16)
                self._resolution = f"{width}x{height}"
                logger.debug(f"Find video resolution in tkhd box(MPEG-4): {self._resolution}")
        return self._resolution

    def __repr__(self):
        return f"<AnimeInfo ({self._format}|{self._size}|{self.left_lifetime}s) {self._url[:40]}...>"


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

    async def parse(self, raw_url: str) -> Union[AnimeInfo, str]:
        """
        重写此方法以实现直链的解析和有效期提取工作

        :param raw_url: 原始链接
        :return: 视频直链对象(含直链和有效期)
        """
        return AnimeInfo(raw_url)

    async def _parse(self, raw_url: str) -> AnimeInfo:
        """解析直链, 捕获引擎模块未处理的异常"""
        try:
            await self.init_session()
            info = await self.parse(raw_url)
            if not isinstance(info, AnimeInfo):
                info = AnimeInfo(info)  # 方便 parse 直接返回字符串链接
            await info.detect_more_info()
            if info.is_available():  # 解析成功
                logger.info(f"Parse success: {info}")
                logger.info(f"Real url: {info.real_url}")
                return info
            logger.error(f"Parse failed: {info}")
            return AnimeInfo()
        except Exception as e:
            logger.exception(e)
            return AnimeInfo()
        finally:
            await self.close_session()
