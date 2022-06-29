from random import randint, choice
from typing import AsyncIterator

from core.engine import DanmakuEngine
from models.danmaku import *


class DemoEngine(DanmakuEngine):
    name = "Demo"
    quality = 5
    version = "2022-06-28"
    notes = "Demo danmaku engine"
    deprecated = True

    async def search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        for i in range(3):
            meta = DanmakuMeta()
            meta.title = f"{keyword} 第{i}季"
            meta.parse_args["aid"] = f"abc-{i}"
            yield meta

    async def parse_detail(self, **parse_args) -> DanmakuDetail:
        aid = parse_args.get("aid")
        detail = DanmakuDetail()
        detail.title = "剧集标题"
        for idx in range(1, 3):
            dmk = Danmaku()
            dmk.name = f"第{idx}集"
            dmk.parse_args["cid"] = f"cid-{idx}"
            detail.append_danmaku(dmk)
        return detail

    async def parse_data(self, **parse_args) -> DanmakuData:
        cid = parse_args.get("cid")
        data = DanmakuData()
        for _ in range(500):
            bullet = Bullet()
            bullet.time = randint(0, 60 * 24)  # 0~24min
            bullet.pos = choice([Bullet.RTL, Bullet.TOP, Bullet.BOTTOM])
            bullet.color = choice([0xffffff, 0xff0000, 0x00ff00, 0x0000ff])
            bullet.msg = "这是一条弹幕~"
            data.append_bullet(bullet)
        return data
