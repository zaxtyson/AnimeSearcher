from api.base import AnimeEngine, VideoHandler, HtmlParseHelper
from api.logger import logger
from api.models import AnimeMetaInfo, AnimeDetailInfo, Video, VideoCollection


class Bimibimi(AnimeEngine):

    def __init__(self):
        self._base_url = "https://proxy.app.maoyuncloud.com"
        self._search_api = self._base_url + "/app/video/search"
        self._detail_api = self._base_url + "/app/video/detail"
        self._headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}

    def search(self, keyword: str):
        ret = []
        logger.info(f"Searching for: {keyword}")
        resp = self.get(self._search_api, params={"limit": "100", "key": keyword, "page": "1"}, headers=self._headers)
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return ret
        if resp.json().get("data").get("total") == 0:
            return ret
        anime_meta_list = resp.json().get("data").get("items")
        for meta in anime_meta_list:
            anime = AnimeMetaInfo()
            anime.title = meta["name"]
            anime.cover_url = meta["pic"]
            anime.category = meta["type"]
            anime.detail_page_url = meta["id"]
            ret.append(anime)
        return ret

    def get_detail(self, anime_id: str):
        resp = self.get(self._detail_api, params={"id": anime_id}, headers=self._headers)
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return AnimeDetailInfo()
        detail = resp.json().get("data")  # 视频详情信息
        anime_detail = AnimeDetailInfo()
        anime_detail.title = detail["name"]
        anime_detail.cover_url = detail["pic"]
        anime_detail.desc = detail["content"]  # 完整的简介
        anime_detail.category = detail["type"]
        for play_list in detail["parts"]:
            vc = VideoCollection()  # 番剧的视频列表
            vc.name = play_list["play_zh"]  # 列表名, 线路 I, 线路 II
            for name in play_list["part"]:
                video_params = f"?id={anime_id}&play={play_list['play']}&part={name}"
                vc.append(Video(name, video_params, "BimibimiVideoHandler"))
            anime_detail.append(vc)
        return anime_detail


class BimibimiVideoHandler(VideoHandler, HtmlParseHelper):
    def get_real_url(self):
        """通过视频的 play_id 获取视频链接"""
        play_url = "https://proxy.app.maoyuncloud.com/app/video/play" + self.get_raw_url()
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        logger.info(f"Parsing real url for {play_url}")
        resp = self.get(play_url, headers=headers)
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {play_url}")
            return "error"
        data = resp.json()["data"][0]
        real_url = data["url"]
        if data.get("parse"):  # 需要进一步处理
            url = "http://49.234.56.246/danmu/json.php?url=" + real_url
            resp = self.get(url)
            real_url = resp.json().get("url") or "error"
        elif "qq.com" in real_url:
            resp = self.head(real_url, allow_redirects=False)
            real_url = resp.headers.get("Location")  # 重定向之后才是直链
        logger.info(f"Video real url: {real_url}")
        return real_url
