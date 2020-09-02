import time
from hashlib import md5

from api.base import AnimeEngine, VideoHandler, HtmlParseHelper
from api.logger import logger
from api.models import AnimeMetaInfo, AnimeDetailInfo, Video, VideoCollection


class ZZFun(AnimeEngine):

    def __init__(self):
        self._base_url = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android"
        self._search_api = self._base_url + "/search"
        self._detail_api = self._base_url + "/video/list_ios"

    def search(self, keyword: str):
        logger.info(f"Searching for: {keyword}")
        resp = self.post(self._search_api, data={"userid": "", "key": keyword})
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return []

        anime_meta_list = resp.json().get("data")
        ret = []
        for meta in anime_meta_list:
            anime = AnimeMetaInfo()
            anime.title = meta["videoName"]
            anime.cover_url = meta["videoImg"]
            anime.category = meta["videoClass"]
            anime.detail_page_url = meta["videoId"]
            ret.append(anime)
        return ret

    def get_detail(self, detail_page_url: str):
        resp = self.get(self._detail_api, params={"userid": "", "videoId": detail_page_url})
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return AnimeDetailInfo()
        detail = resp.json().get("data")  # 视频详情信息
        anime_detail = AnimeDetailInfo()
        anime_detail.title = detail["videoName"]
        anime_detail.cover_url = detail["videoImg"]
        anime_detail.desc = detail["videoDoc"].replace("\r\n", "")  # 完整的简介
        anime_detail.category = detail["videoClass"]
        for play_list in detail["videoSets"]:
            vc = VideoCollection()  # 番剧的视频列表
            vc.name = play_list["load"]  # 列表名, 线路 I, 线路 II
            for video in play_list["list"]:
                vc.append(Video(video["ji"], video["playid"], "ZZFunVideoHandler"))
            anime_detail.append(vc)
        return anime_detail


class ZZFunVideoHandler(VideoHandler, HtmlParseHelper):
    def get_real_url(self):
        """通过视频的 play_id 获取视频链接"""
        play_api = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android/video/newplay"
        play_id = self.get_raw_url()
        secret_key = "zandroidzz"
        now = int(time.time() * 1000)  # 13 位时间戳
        sing = secret_key + str(now)
        sing = md5(sing.encode("utf-8")).hexdigest()
        logger.info(f"Parsing real url for {play_id}")
        payload = {"playid": play_id, "userid": "", "apptoken": "", "sing": sing, "map": now}
        resp = self.post(play_api, data=payload)
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {play_api}")
            logger.debug(f"POST params: {payload}")
            return "error"
        real_url = resp.json()["data"]["videoplayurl"]
        logger.info(f"Video real url: {real_url}")
        return real_url

    def set_proxy_headers(self):
        # 有些视频是超星学习通网盘里面的, 需要设置为客户端的 UA, 直接访问会 403
        real_url = self._get_real_url()
        if "chaoxing.com" in real_url:
            logger.info(f"Set proxy headers for {real_url}")
            return {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.0; 16th Build/OPM1.171019.026)"
            }
