from api.base import BaseEngine
from api.models import AnimeMetaInfo, AnimeDetailInfo
from api.models import Video, VideoCollection


class Meijuxia(BaseEngine):
    """美剧侠"""

    def __init__(self):
        self._api = "http://api.meijuxia.com/"

    def search(self, keyword: str):
        payload = {
            "service": "App.Vod.Search",
            "search": keyword,
            "page": 1,
            "perpage": 50,
            "versionCode": 60,
        }
        payload.update(self.encrypt())
        resp = self.post(self._api, data=payload)
        if resp.status_code != 200:
            return
        data = resp.json()
        data = list(filter(lambda x: x["type"] == "vod", data["data"]))[0]
        for item in data["videos"]:
            anime = AnimeMetaInfo()
            anime.title = item["vod_name"]
            anime.category = item["vod_type"]
            anime.cover_url = item["vod_pic"]
            anime.desc = item["vod_keywords"] + " 豆瓣评分:" + item["vod_douban_score"]
            anime.detail_page_url = str(item["vod_id"])  # 详情页id参数
            yield anime

    def get_detail(self, detail_id: str) -> AnimeDetailInfo:
        detail = AnimeDetailInfo()
        payload = {
            "service": "App.Vod.Video",
            "id": detail_id,
            "versionCode": 60
        }
        payload.update(self.encrypt())
        resp = self.post(self._api, data=payload)
        if resp.status_code != 200:
            return detail
        data = resp.json()
        data = list(filter(lambda x: x["type"] == "player", data["data"]))
        info = data[0]["player_vod"]
        detail.title = info["vod_name"]
        detail.desc = self.desc_format(info["vod_content"])
        detail.cover_url = info["vod_pic"]
        for playlist in info["vod_play"]:
            vc = VideoCollection()
            vc.name = playlist["player_name_zh"] + playlist["title"]
            for video in playlist["players"]:
                url = video["url"].split("=")[-1]
                vc.append(Video(
                    name=video["title"],
                    raw_url=url
                ))
            detail.append(vc)
        return detail

    def desc_format(self, text: str):
        """去除简介中的HTML符号"""
        return text.replace("<p>", "").replace("</p>", ""). \
            replace("&middot;", "·").replace("&ldquo;", "")

    def encrypt(self):
        """加密算法"""
        # TODO: APP 待脱壳解密(爱加密V2)
        data = {
            "time": "1602494010458",
            "md5": "586f76b4f969eb715e2949ecd7d7fefa",
            "sign": "d8a1999ecd07d17c78f4e8c0f57b9f02"
        }
        return data
