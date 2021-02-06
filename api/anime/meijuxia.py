from api.core.anime import *


def encrypt():
    """加密算法, 以前的时间也可以， 能用就行"""
    # TODO: APP 待脱壳解密(爱加密V2)
    data = {
        "time": "1602494010458",
        "md5": "586f76b4f969eb715e2949ecd7d7fefa",
        "sign": "d8a1999ecd07d17c78f4e8c0f57b9f02"
    }
    return data


class Meijuxia(AnimeSearcher):

    async def search(self, keyword: str):
        payload = {
            "service": "App.Vod.Search",
            "search": keyword,
            "page": 1,
            "perpage": 50,
            "versionCode": 60,
        }
        payload.update(encrypt())
        api = "http://api.meijuxia.com/"
        resp = await self.post(api, data=payload)
        if not resp or resp.status != 200:
            return
        data = await resp.json(content_type=None)
        data = list(filter(lambda x: x["type"] == "vod", data["data"]))[0]
        for item in data["videos"]:
            anime = AnimeMeta()
            anime.title = item["vod_name"]
            anime.category = item["vod_type"]
            anime.cover_url = item["vod_pic"]
            anime.desc = item["vod_keywords"]
            anime.detail_url = str(item["vod_id"])  # 详情页id参数
            yield anime


class MeijuxiaDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        payload = {
            "service": "App.Vod.Video",
            "id": detail_url,
            "versionCode": 60
        }
        payload.update(encrypt())
        api = "http://api.meijuxia.com/"
        resp = await self.post(api, data=payload)
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        data = list(filter(lambda x: x["type"] == "player", data["data"]))
        info = data[0]["player_vod"]
        detail.title = info["vod_name"]
        detail.desc = self.desc_format(info["vod_content"])
        detail.cover_url = info["vod_pic"]
        for playlist in info["vod_play"]:
            pl = AnimePlayList()
            pl.name = playlist["player_name_zh"] + playlist["title"]
            for video in playlist["players"]:
                url = video["url"].split("=")[-1]
                pl.append(Anime(video["title"], url))
            detail.append_playlist(pl)
        return detail

    @staticmethod
    def desc_format(text: str):
        """去除简介中的HTML符号"""
        return text.replace("<p>", "").replace("</p>", ""). \
            replace("&middot;", "·").replace("&ldquo;", "")
