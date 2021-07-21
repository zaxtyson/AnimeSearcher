# 本模块已弃用
from api.core.anime import *


class EYunZun(AnimeSearcher):

    async def search(self, keyword: str):
        params = {"kw": keyword, "per_page": 100, "page": 1}
        api = "https://api.eyunzhu.com/api/vatfs/resource_site_collect/search"
        resp = await self.get(api, params=params)  # 取前 100 条结果
        if not resp or resp.status != 200:
            return
        data = await resp.json(content_type=None)
        if data["code"] != 1:
            return

        for meta in data["data"]["data"]:
            anime = AnimeMeta()
            anime.title = meta["name"]
            anime.cover_url = meta["pic"]
            anime.category = meta["type"]
            anime.detail_url = str(meta["vid"])
            anime.desc = meta["label"]
            yield anime


class EYunZunDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = "https://api.eyunzhu.com/api/vatfs/resource_site_collect/getVDetail"
        resp = await self.get(api, params={"vid": detail_url})
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        if data["code"] != 1:
            return detail

        data = data["data"]  # 视频详情信息
        detail = AnimeDetail()
        detail.title = data["name"]
        detail.cover_url = data["pic"]
        detail.desc = data["label"]
        detail.category = data["type"]

        playlist = AnimePlayList()
        playlist.name = "视频列表"
        video_set = dict(data["playUrl"])
        for name, url in video_set.items():
            playlist.append(Anime(name, url))
        detail.append_playlist(playlist)
        return detail
