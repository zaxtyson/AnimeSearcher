from json import JSONDecodeError

from api.core.anime import *
from api.core.proxy import AnimeProxy
from api.utils.tool import extract_domain


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
        data = []
        try:
            data = await resp.json(content_type=None)
            data = list(filter(lambda x: x["type"] == "vod", data["data"]))[0]
            data = data["videos"]
        except JSONDecodeError:  # 没结果的时候, 返回的json格式错误
            pass
        for item in data:
            meta = AnimeMeta()
            meta.title = item["vod_name"]
            meta.category = item["vod_type"]
            meta.cover_url = item["vod_pic"]
            meta.desc = item["vod_keywords"]
            meta.detail_url = str(item["vod_id"])  # 详情页id参数
            yield meta


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
            if pl.name in ["畅播", "酷播"]:
                continue  # 垃圾资源
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


class MeijuxiaProxy(AnimeProxy):

    async def get_m3u8_text(self, index_url: str) -> str:
        if "dious.cc" in index_url:  # 需要再跳转一次
            text = await self.read_text(index_url)
            index_url = extract_domain(index_url) + text.split()[-1]

        return await self.read_text(index_url)
