from typing import List

from models.base import DataClass


class ReleaseAsset(DataClass):

    def __init__(self):
        self.name = ""  # resource name
        self.url = ""  # download url
        self.size = 0  # bytes size


class ReleaseInfo(DataClass):

    def __init__(self):
        self.version = "1.0.0"
        self.release_time = "2022-06-23 12:00"
        self.release_log = ""
        self.release_url = ""
        self.assets: List[ReleaseAsset] = []


class SystemVersion(DataClass):

    def __init__(self):
        self.need_update = False
        self.current = ReleaseInfo()
        self.latest = ReleaseInfo()


# class EngineUpdateInfo(DataClass):
#
#     def __init__(self):
#         self.module = ""
#         self.engine_name = ""
#         self.action = "update"  # or "deprecate"
