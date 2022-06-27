from models.base import DataClass
from models.danmaku import DanmakuData
from typing import Any


class GenericResp(DataClass):

    def __init__(self, code: int = 0, msg: str = "ok", data: Any = None):
        self.code = code
        self.msg = msg
        self.data = data


class DplayerResp(DataClass):

    def __init__(self, code: int = 0, msg: str = "ok", data: DanmakuData = None):
        self.code = code
        self.msg = msg
        self.num = data.size()
        self.data = data.data()
