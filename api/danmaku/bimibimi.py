import re

from api.core.danmaku import *


class Bimibimi(DanmakuSearcher):

    async def search(self, keyword: str):
        api = "https://proxy.app.maoyuncloud.com/app/video/search"
        params = {"limit": "100", "key": keyword, "page": "1"}
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        resp = await self.get(api, params=params, headers=headers)
        if not resp or resp.status != 200:
            return

        data = await resp.json(content_type=None)
        if data["data"]["total"] == 0:
            return

        data = data["data"]["items"]
        for anime in data:
            meta = DanmakuMeta()
            meta.title = anime["name"]
            meta.play_url = str(anime["id"])
            meta.num = anime["total"] or -1  # 集数未知的为 0, 我们统一用 -1 表示
            yield meta


class BimiDanmakuDetailParser(DanmakuDetailParser):

    async def parse(self, play_url: str):
        detail = DanmakuDetail()
        api = "https://proxy.app.maoyuncloud.com/app/video/detail"
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        resp = await self.get(api, params={"id": play_url}, headers=headers)
        if not resp or resp.status != 200:
            return detail

        data = await resp.json(content_type=None)
        data = data["data"]  # 视频详情信息
        ep_fid = data["fid"]  # 本番的弹幕池 id 2818
        ep_videos = data["parts"][0]["part"]  # 各集视频的名字, 如第 x 话
        for i, name in enumerate(ep_videos, 1):
            danmaku = Danmaku()
            danmaku.name = name
            danmaku.cid = f"{ep_fid}/{ep_fid}-{i}"  # 2818/2818-1  弹幕id/弹幕id-集数
            detail.append(danmaku)
        return detail


class BimiDanmakuDataParser(DanmakuDataParser):

    async def parse(self, cid: str):
        result = DanmakuData()
        api = f"http://49.234.56.246/danmu/dm/{cid}.php"
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return result
        text = await resp.text()
        bullets = re.findall(r"p='(\d+\.?\d*?),\d,\d\d,(\d+?),\d+,(\d),.+?>(.+?)</d>", text)
        for bullet in bullets:
            result.append_bullet(
                time=float(bullet[0]),
                pos=int(bullet[2]),
                color=int(bullet[1]),
                message=bullet[3]
            )
        return result
