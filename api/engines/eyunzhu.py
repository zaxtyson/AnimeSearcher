from api.base import BaseEngine
from api.logger import logger
from api.models import AnimeMetaInfo, AnimeDetailInfo, Video, VideoCollection


class EYunZun(BaseEngine):
    def __init__(self):
        self._base_url = "https://api.eyunzhu.com/api/vatfs/resource_site_collect"
        self._search_api = self._base_url + "/search"
        self._detail_api = self._base_url + "/getVDetail"

    def search(self, keyword: str):
        logger.info(f"Searching for: {keyword}")
        resp = self.get(self._search_api, params={"kw": keyword, "per_page": 50, "page": 1})
        if resp.status_code != 200 or resp.json()["code"] != 1:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return []

        anime_meta_list = resp.json().get("data").get("data")
        ret = []
        for meta in anime_meta_list:
            anime = AnimeMetaInfo()
            anime.title = meta["name"]
            anime.cover_url = meta["pic"]
            anime.category = meta["type"]
            anime.detail_page_url = str(meta["vid"])
            anime.desc = meta["label"]
            ret.append(anime)
        return ret

    def get_detail(self, detail_page_url: str):
        resp = self.get(self._detail_api, params={"vid": detail_page_url})
        if resp.status_code != 200 or resp.json()["code"] != 1:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return AnimeDetailInfo()

        detail = resp.json().get("data")  # 视频详情信息
        anime_detail = AnimeDetailInfo()
        anime_detail.title = detail["name"]
        anime_detail.cover_url = detail["pic"]
        anime_detail.desc = detail["label"]
        anime_detail.category = detail["type"]

        vc = VideoCollection()
        vc.name = "视频列表"
        video_set = dict(detail["playUrl"])
        for name, url in video_set.items():
            vc.append(Video(name, url))
        anime_detail.append(vc)
        return anime_detail
