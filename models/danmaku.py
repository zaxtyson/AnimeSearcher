from typing import List

from models.base import DataClass

__all__ = ["Danmaku", "DanmakuMeta", "DanmakuDetail", "DanmakuData", "Bullet"]


class Danmaku(DataClass):
    HIDE_FILED = ["parse_args"]

    def __init__(self):
        self.name = ""
        self.parse_args = {}

        self.data_url = ""


class DanmakuMeta(DataClass):
    HIDE_FILED = ["parse_args"]

    def __init__(self):
        self.title = ""
        self.num = 0
        self.parse_args = {}

        self.detail_url = ""
        self.module = ""
        self.engine_name = ""


class DanmakuDetail(DataClass):

    def __init__(self):
        self.title = ""

        self.num = 0
        self.module = ""
        self.engine_name = ""
        self.playlist: List[Danmaku] = []

    def append_danmaku(self, danmaku: Danmaku):
        self.num += 1
        self.playlist.append(danmaku)

    def get_danmaku(self, idx: int) -> Danmaku:
        return self.playlist[idx - 1]


class Bullet:
    RTL = 0
    TOP = 1
    BOTTOM = 2

    def __init__(self):
        self.time: float = 0
        self.pos = Bullet.RTL
        self.color = 0
        self.sender = ""
        self.msg = ""

    def to_array(self):
        return [self.time, self.pos, self.color, self.sender, self.msg]


class DanmakuData:

    def __init__(self):
        self._bullets = []

    def size(self) -> int:
        return len(self._bullets)

    def append_bullet(self, bullet: Bullet):
        self._bullets.append(bullet.to_array())

    def data(self):
        return self._bullets
