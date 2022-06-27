from typing import List

from models.base import DataClass

__all__ = ["Video", "VideoInfo", "AnimeMeta", "AnimeDetail", "PlayRoute"]


class Video(DataClass):
    HIDE_FILED = ["parse_args"]

    def __init__(self, name: str = ""):
        self.name = name
        self.parse_args = {}

        # 以下字段由框架注入, 无需手动填写
        self.info_url = ""
        self.player_url = ""


class PlayRoute(DataClass):

    def __init__(self):
        self.name = ""
        # self.quality = 1

        self.num = 0
        self.videos: List[Video] = []

    def append_video(self, video: Video):
        self.num += 1
        self.videos.append(video)


class AnimeMeta(DataClass):
    HIDE_FILED = ["parse_args"]

    def __init__(self):
        self.title = ""
        self.cover_url = ""
        self.categories = []
        self.description = ""
        self.parse_args = {}

        self.detail_url = ""
        self.module = ""
        self.engine_name = ""


class AnimeDetail(DataClass):

    def __init__(self):
        self.title = ""
        self.cover_url = ""
        self.categories = []
        self.description = ""

        self.module = ""
        self.engine_name = ""
        self.routes: List[PlayRoute] = []

    def append_route(self, route: PlayRoute):
        self.routes.append(route)

    def get_video(self, route_idx: int, ep_idx: int) -> Video:
        return self.routes[route_idx - 1].videos[ep_idx - 1]


class VideoInfo(DataClass):

    def __init__(self, fmt: str, lifetime: int):
        self.format = fmt  # mp4,flv,hls
        self.lifetime = lifetime  # seconds

        self.raw_url = ""
        self.proxy_url = ""
