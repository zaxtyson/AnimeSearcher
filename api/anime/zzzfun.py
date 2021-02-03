import time
from hashlib import md5

from api.core.anime import *
from api.core.models import AnimeMeta, AnimeDetail, Video, PlayList


class ZZZFun(AnimeSearcher):

    async def search(self, keyword: str):
        api = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android/search"
        resp = await self.post(api, data={"userid": "", "key": keyword})
        if not resp or resp.status != 200:
            return
        data = await resp.json(content_type=None)
        for meta in data["data"]:
            anime = AnimeMeta()
            anime.title = meta["videoName"]
            anime.cover_url = meta["videoImg"]
            anime.category = meta["videoClass"]
            anime.detail_url = meta["videoId"]
            yield anime


class ZZZFunDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android/video/list_ios"
        resp = await self.get(api, params={"userid": "", "videoId": detail_url})
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        data = data["data"]  # 视频详情信息
        detail.title = data["videoName"]
        detail.cover_url = data["videoImg"]
        detail.desc = data["videoDoc"].replace("\r\n", "")  # 完整的简介
        detail.category = data["videoClass"]
        for playlist in data["videoSets"]:
            pl = PlayList()  # 番剧的视频列表
            pl.name = playlist["load"]  # 列表名, 线路 I, 线路 II
            for video in playlist["list"]:
                pl.append(Video(video["ji"], video["playid"], "ZZZFunHandler"))
            detail.append(pl)
        return detail


class ZZZFunHandler(AnimeHandler):

    async def parse(self, raw_url: str):
        play_api = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android/video/107play"
        secret_key = "zandroidzz"
        now = int(time.time() * 1000)  # 13 位时间戳
        sing = secret_key + str(now)
        sing = md5(sing.encode("utf-8")).hexdigest()
        payload = {"playid": raw_url, "userid": "", "apptoken": "", "sing": sing, "map": now}
        resp = await self.post(play_api, data=payload)
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        real_url = data["data"]["videoplayurl"]
        return real_url

    def set_proxy_headers(self, real_url: str):
        # 有些视频是超星学习通网盘里面的, 需要设置为客户端的 UA, 直接访问会 403
        # TODO : find out which video should use proxy
        if "chaoxing.com" in real_url:
            return {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 8.1.0; 16th Build/OPM1.171019.026)"}
        if "zzzfun123pch" in real_url:
            return {"User-Agent": "ExoSourceManager/1.1.2 (Linux;Android 8.1.0) ExoPlayerLib/2.11.3"}
