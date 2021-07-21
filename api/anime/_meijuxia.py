"""
美剧侠的质量越来越差了, 返回点结果没几个能正常解析的, 弃用
"""

from json import JSONDecodeError

from api.core.anime import *
from api.core.proxy import AnimeProxy
from api.utils.tool import extract_domain


class Meijuxia(AnimeSearcher):

    async def search(self, keyword: str):
        payload = {
            "service": "App.Vod.Search",
            "search": keyword,
            "page": 1,
            "perpage": 24,
            "versionCode": 1000,
            "time": "1626701869178",  # 搜索和详情使用的时间不能相同
            "md5": "6fb6c8296bb2bacbc7b385f343adf3c6",
            "sign": "fff4d7b9366d25c42aa8f49dd3433211"
        }
        api = "http://27.124.4.42/"
        headers = {
            "Host": "27.124.4.42:8808",
            "User-Agent": "okhttp/3.12.1"  # 为了伪装的更像
        }
        resp = await self.post(api, data=payload, headers=headers)
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
            "versionCode": 1000,
            "time": "1626701872503",
            "md5": "3ef146bf72e916b3490dc503b4655bd3",
            "sign": "5e84d109f2df774b04d85ff08d053e70"
        }
        api = "http://27.124.4.42/"
        headers = {
            "Host": "27.124.4.42:8808",
            "User-Agent": "okhttp/3.12.1"
        }
        resp = await self.post(api, data=payload, headers=headers)
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
