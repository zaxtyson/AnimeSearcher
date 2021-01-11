from base64 import b16encode
from inspect import currentframe
from typing import List


class Video(object):
    """单集视频对象"""

    def __init__(self, name="", raw_url="", handler="VideoHandler"):
        self.name = name  # 视频名, 比如 "第1集"
        self.raw_url = raw_url  # 视频原始 url, 可能需要进一步处理
        self.handler = handler  # 视频绑定的处理器类名, 默认绑定 VideoHandler
        self.real_url = ""  # 解析出来的真实链接

    def __repr__(self):
        return f"<Video {self.name}>"


class VideoCollection(object):
    """番剧的视频集合, 包含许多 Video"""

    def __init__(self):
        self.name = ""  # 集合名, 比如 "播放线路1"
        self.num = 0  # 视频集数
        self.video_list: List[Video] = []

    def append(self, video: Video):
        self.video_list.append(video)
        self.num += 1

    def __iter__(self):
        return iter(self.video_list)

    def __repr__(self):
        return f"<VideoCollection {self.name} [{self.num}]>"


class AnimeMetaInfo(object):
    """番剧的摘要信息, 不包括视频播放列表, 用于表示搜索结果"""

    def __init__(self):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 番剧的简介信息
        self.detail_page_url = ""  # 番剧详情页面的链接, 用于进一步提取视频列表

        # 解析该番剧的引擎名, "api.engine.name"
        # 后续提取番剧详情页需要知道它, 为了编写引擎方便, 这里自动设置类名
        frame = currentframe().f_back
        self.engine = frame.f_globals["__name__"]
        del frame

    def __repr__(self):
        return f"<AnimeMetaInfo {self.title}>"

    @property
    def hash(self):
        """可以通过此信息构造一个对象, 包含引擎和详情页信息"""
        sign = f"{self.engine}|{self.detail_page_url}".encode("utf-8")
        return b16encode(sign).decode("utf-8").lower()


class AnimeDetailInfo(object):
    """番剧详细信息, 包括视频播放列表"""

    def __init__(self):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 番剧的简介信息
        self.play_lists: List[VideoCollection] = []  # 播放列表, 一部番剧可能有多条播放路线, 一条线路对应一个 VideoCollection

    def append(self, video_collection: VideoCollection):
        self.play_lists.append(video_collection)

    def __iter__(self):
        return iter(self.play_lists)

    def __repr__(self):
        return f"<AnimeDetailInfo {self.title}>"


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


class DanmakuMetaInfo(object):
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
        return f"<DanmakuMetaInfo {self.title}[{self.num}]>"


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
