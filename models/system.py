from typing import List

from models.base import DataClass


class ReleaseAsset(DataClass):

    def __init__(self):
        self.name = ""  # resource name
        self.url = ""  # download url


class ReleaseInfo(DataClass):

    def __init__(self):
        self.version = "1.0.0"
        self.release_time = "2022-06-23 12:00"
        self.release_log = ""
        self.repos = {
            "github": "",
            "gitee": ""
        }
        self.assets: List[ReleaseAsset] = []


class SystemVersion(DataClass):

    def __init__(self):
        self.update = False  # need update?
        self.current = ReleaseInfo()
        self.latest = ReleaseInfo()


class EngineUpdateInfo(DataClass):

    def __init__(self):
        self.module = ""
        self.engine_name = ""
        self.action = "update"  # or "deprecate"


class ProxyPolicy(DataClass):

    def __init__(self):
        self.enforce_images = False
        self.enforce_videos = False


class CachePolicy(DataClass):

    def __init__(self):
        self.anime_detail = 1800
        self.anime_bangumi = 3600
        self.danmaku_meta = 7200
        self.danmaku_detail = 7200
        self.danmaku_data = 7200
