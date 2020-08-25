from inspect import currentframe

__all__ = ["Video", "VideoCollection", "AnimeMetaInfo", "AnimeDetailInfo"]


class Video(object):
    """单集视频对象"""

    def __init__(self, name="", raw_url="", handler="VideoHandler"):
        self.name = name  # 视频名, 比如 "第1集"
        self.raw_url = raw_url  # 视频原始 url, 可能需要进一步处理
        self.handler = handler  # 视频绑定的处理器类名, 默认绑定 VideoHandler
        self.real_url = ""  # 解析出来的真实链接


class VideoCollection(object):
    """番剧的视频集合, 包含许多 Video"""

    def __init__(self):
        self.name = ""  # 集合名, 比如 "播放线路1"
        self.num = 0  # 视频集数
        self.video_list = []

    def append(self, video: Video):
        self.video_list.append(video)
        self.num += 1


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


class AnimeDetailInfo(object):
    """番剧详细信息, 包括视频播放列表"""

    def __init__(self):
        self.title = ""  # 番剧标题
        self.cover_url = ""  # 封面图片链接
        self.category = ""  # 番剧的分类
        self.desc = ""  # 番剧的简介信息
        self.play_lists = []  # 播放列表, 一部番剧可能有多条播放路线, 一条线路对应一个 VideoCollection

    def append(self, video_collection: VideoCollection):
        self.play_lists.append(video_collection)
