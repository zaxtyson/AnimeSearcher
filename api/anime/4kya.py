"""
4K鸭奈飞: https://app.4kya.com/
"""

from api.core.anime import *


class YaNetflix(AnimeSearcher):
    async def search(self, keyword: str):
        api = "http://4kya.net:6969/api.php/v2/videos"
        payload = {
            "start": 0,
            "num": 10,
            "key": keyword,
            "paging": True
        }
        resp = await self.post(api, json=payload, headers={"User-Agent": "okhttp/3.11.0"})
        if not resp or resp.status != 200:
            return
        data = await resp.json(content_type=None)
        data = data["result"]["rows"]
        for item in data:
            meta = AnimeMeta()
            meta.cover_url = item["pic"].replace("mac://", "http://")
            meta.title = item["title"]
            meta.detail_url = item["id"]
            meta.desc = item["blurb"]
            meta.category = " ".join(item["ext_types"])
            yield meta


class YaNetflixDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = "http://4kya.net:6969/api.php/v2/video"
        payload = {"video_id": detail_url}
        resp = await self.post(api, json=payload, headers={"User-Agent": "okhttp/3.11.0"})
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        data = data["result"]
        detail.cover_url = data["pic"].replace("mac://", "http://")
        detail.title = data["title"]
        detail.desc = data["blurb"]
        detail.category = " ".join(data["ext_types"])

        for source in data["players"]:
            playlist = AnimePlayList()
            playlist.name = source["name"]
            for video in source["datas"]:
                if isinstance(video, bool):
                    continue  # 有时候列表里会带有布尔值
                anime = Anime()
                anime.name = video["text"]
                anime.raw_url = video["play_url"]
                playlist.append(anime)
            if not playlist.is_empty():
                detail.append_playlist(playlist)
        return detail
