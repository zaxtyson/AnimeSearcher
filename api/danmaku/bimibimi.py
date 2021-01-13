import re

from api.core.base import DanmakuEngine
from api.core.models import Danmaku, DanmakuMetaInfo, DanmakuCollection
from api.utils.logger import logger


class DanmukaBimibimi(DanmakuEngine):

    def __init__(self):
        self._base_url = "https://proxy.app.maoyuncloud.com"
        self._search_api = self._base_url + "/app/video/search"
        self._detail_api = self._base_url + "/app/video/detail"
        self._headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}

    def search(self, keyword: str):
        logger.info(f"Searching for danmaku: {keyword}")
        resp = self.get(self._search_api, params={"limit": "100", "key": keyword, "page": "1"}, headers=self._headers)
        if resp.status_code != 200 or resp.json()["data"]["total"] == 0:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return
        anime_meta_list = resp.json().get("data").get("items")
        for anime in anime_meta_list:
            meta = DanmakuMetaInfo()
            meta.title = anime["name"]
            meta.play_page_url = str(anime["id"])
            meta.num = anime["total"]
            yield meta

    def get_detail(self, play_page_url: str):
        collection = DanmakuCollection()
        resp = self.get(self._detail_api, params={"id": play_page_url}, headers=self._headers)
        if resp.status_code != 200:
            return collection
        detail = resp.json().get("data")  # 视频详情信息
        ep_fid = detail.get("fid")  # 本番的弹幕池 id 2818
        ep_videos = detail["parts"][0]["part"]  # 各集视频的名字, 如第 x 话
        for i, name in enumerate(ep_videos, 1):
            dmk = Danmaku()
            dmk.name = name
            dmk.cid = f"{ep_fid}/{ep_fid}-{i}"  # 2818/2818-1  弹幕id/弹幕id-集数
            collection.append(dmk)
        return collection

    def get_danmaku(self, cid: str):
        ret = []
        url = f"http://49.234.56.246/danmu/dm/{cid}.php"
        resp = self.get(url, timeout=10)
        if resp.status_code != 200:
            return ret
        dm_list = re.findall(r"p='(\d+\.?\d*?),\d,\d\d,(\d+?),\d+,(\d),.+?>(.+?)</d>", resp.text)
        ret = [[float(dm[0]), int(dm[2]), int(dm[1]), "", dm[3]] for dm in dm_list]
        return ret
