from base64 import b16encode, b16decode
from inspect import currentframe
from typing import List, Optional


class Video(object):
    """单集视频对象"""

    def __init__(self, name: str = "", raw_url: str = "", handler: str = "AnimeHandler"):
        self.name = name  # 视频名, 比如 "第1集"
        self.raw_url = raw_url  # 视频原始 url, 可能需要进一步处理
        self.handler = handler  # 视频绑定的处理器类名

    def __repr__(self):
        return f"<Video {self.name}>"


class PlayList(object):
    """播放列表"""

    def __init__(self):
        self.name = ""  # 播放列表名, 比如 "播放线路1"
        self.num = 0  # 视频集数
        self._video_list: List[Video] = []

    def append(self, video: Video):
        self._video_list.append(video)
        self.num += 1

    def is_empty(self):
        return not self._video_list

    def __iter__(self):
        return iter(self._video_list)

    def __getitem__(self, idx: int) -> Video:
        return self._video_list[idx]

    def __repr__(self):
        return f"<PlayList {self.name} [{self.num}]>"


class AnimeMeta(object):
    """
    番剧的摘要信息, 不包括视频播放列表, 只用于表示搜索结果
    """

    def __init__(self, token: str = ""):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 番剧的简介信息
        self.detail_url = ""  # 番剧详情页面的链接, 用于进一步提取视频列表
        if token:
            self._build_from(token)
        else:
            # 自动设置解析该番剧的引擎模块名, 如 "api.anime.name"
            self.module = currentframe().f_back.f_globals["__name__"]

    def __repr__(self):
        return f"<AnimeMeta {self.title}>"

    @property
    def token(self) -> str:
        """通过引擎名和详情页信息生成, 可唯一表示本资源位置"""
        name = self.module.split('.')[-1]  # 缩短 token 长度, 只保留引擎名
        sign = f"{name}|{self.detail_url}".encode("utf-8")
        return b16encode(sign).decode("utf-8").lower()

    def _build_from(self, token: str):
        """提取 token 中的信息, 构建一个不完整但可以被解析的 AnimeMeta"""
        name, detail_url = b16decode(token.upper()).decode("utf-8").split("|")
        self.module = "api.anime." + name
        self.detail_url = detail_url


class AnimeDetail(object):
    """
    番剧详细页的信息, 包括多个视频播放列表, 番剧的描述、分类等信息
    """

    def __init__(self):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 番剧的简介信息
        self.filtered = False  # 播放列表是否经过过滤
        self.playlists: List[PlayList] = []  # 一部番剧可能有多条播放列表
        self.module = currentframe().f_back.f_globals["__name__"]

    def get_video(self, playlist: int, episode: int) -> Optional[Video]:
        """获取某一个播放列表的某个视频对象"""
        try:
            return self[playlist][episode]
        except IndexError:
            return None

    def append(self, playlist: PlayList):
        self.playlists.append(playlist)

    def is_empty(self):
        return not self.playlists

    def __getitem__(self, idx: int) -> PlayList:
        return self.playlists[idx]

    def __iter__(self):
        return iter(self.playlists)

    def __repr__(self):
        return f"<AnimeDetail {self.title} [{len(self.playlists)}]>"


class Danmaku(object):
    """视频的弹幕库, 包含弹幕的 id 信息, 用于进一步解析出弹幕数据"""

    def __init__(self):
        self.name = ""  # 视频名
        self.cid = ""  # 弹幕 id, 用于解析出弹幕

        # 自动设置引擎的名字, 管理器进一步解析需要知道它
        frame = currentframe().f_back
        self.dm_engine = frame.f_globals["__name__"]
        del frame

    def __repr__(self):
        return f"<Danmaku {self.name}>"


class DanmakuMeta(object):
    """番剧弹幕的元信息, 包含指向播放页的链接, 用于进一步处理"""

    def __init__(self):
        self.title = ""  # 弹幕库名字(番剧名)
        self.num = 0  # 视频数量
        self.play_page_url = ""  # 番剧播放页的链接

        # 自动设置引擎的名字, 管理器进一步解析需要知道它
        frame = currentframe().f_back
        self.dm_engine = frame.f_globals["__name__"]
        del frame

    def __repr__(self):
        return f"<DanmakuMeta {self.title}[{self.num}]>"


class DanmakuCollection(object):
    """一部番剧所有视频的 Danmaku 集合"""

    def __init__(self):
        self.title = ""  # 弹幕库名字(番剧名)
        self.num = 0  # 视频数量
        self.dm_list: List[Danmaku] = []  # 弹幕对象列表

    def append(self, dmk: Danmaku):
        self.dm_list.append(dmk)
        self.num += 1

    def __iter__(self):
        return iter(self.dm_list)

    def __repr__(self):
        return f"<DanmakuDetailInfo {self.title}[{self.num}]>"


class TimelineAnimeInfo(object):
    """更新的番剧信息"""

    def __init__(self):
        self.title = ""  # 番剧名
        self.cover = ""  # 番剧封面
        self.update_time = ""  # 更新时间 %Y-%m-%d %H:%M:%S
        self.update_to = ""  # 更新到第几集

    def to_dict(self):
        return self.__dict__


class TimelineOneDay(object):
    """时间线中一天更新的番剧信息"""

    def __init__(self):
        self.date = ""  # 这一天的日期 %Y-%m-%d
        self.day_of_week = ""  # 这一天是星期几
        self.is_today = False  # 是今天吗
        self.updates: List[TimelineAnimeInfo] = []  # 这一天更新的番剧列表

    def append(self, anime: TimelineAnimeInfo):
        self.updates.append(anime)

    def __iter__(self):
        return iter(self.updates)

    def to_dict(self):
        json = self.__dict__.copy()
        json["updates"] = [i.to_dict() for i in self]
        return json
