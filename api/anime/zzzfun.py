import time

from api.core.anime import *
from api.core.proxy import AnimeProxy
from api.utils.tool import md5


class ZZZFun(AnimeSearcher):

    async def search(self, keyword: str):
        api = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android/search"
        resp = await self.post(api, data={"userid": "", "key": keyword}, headers={"User-Agent": "okhttp/3.12.0"})
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
        resp = await self.get(api, params={"userid": "", "videoId": detail_url},
                              headers={"User-Agent": "okhttp/3.12.0"})
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        data = data["data"]  # 视频详情信息
        detail.title = data["videoName"]
        detail.cover_url = data["videoImg"]
        detail.desc = data["videoDoc"].replace("\r\n", "")  # 完整的简介
        detail.category = data["videoClass"]
        for video_set in data["videoSets"]:
            playlist = AnimePlayList()  # 番剧的视频列表
            playlist.name = video_set["load"]  # 列表名, 线路 I, 线路 II
            for video in video_set["list"]:
                playlist.append(Anime(video["ji"], video["playid"]))
            detail.append_playlist(playlist)
        return detail


class ZZZFunUrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        # 加密算法 Smali 位置
        # .class final Lorg/daimhim/zzzfun/data/remote/HttpRequestManager$getVideoPlayInfo$2;
        # .source "HttpRequestManager.kt"
        # .method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
        # .line 460 ~ .line 463
        secret_key = "zan109drdddzz"
        now = int(time.time() * 1000)  # 13 位时间戳
        sing = md5(secret_key + str(now))

        # 接口随 App 更新变化
        play_api = "http://service-agbhuggw-1259251677.gz.apigw.tencentcs.com/android/video/112play"
        payload = {"playid": raw_url, "userid": "", "apptoken": "", "sing": sing, "map": now}
        resp = await self.post(play_api, data=payload, headers={"User-Agent": "okhttp/3.12.0"})
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        if not data["data"]:
            return ""
        real_url = data["data"]["videoplayurl"]
        if "alicdn" in real_url or "zzzhls" in real_url:
            # m3u8 格式, 该资源解析后访问一次立刻失效, 内部视频片段不会立刻失效
            return AnimeInfo(real_url, volatile=True)
        return AnimeInfo(real_url)


class ZZZFunProxy(AnimeProxy):

    def enforce_proxy(self, url: str) -> bool:
        if "alicdn" in url or "zzzhls" in url:
            return True  # 图片隐写视频流, 强制代理播放
        if "chaoxing.com" in url:  # 学习通视频
            return True
        return False

    def fix_chunk_data(self, url: str, chunk: bytes) -> bytes:
        if "pgc-image" in url:
            return chunk[0xd4:]  # 前面是 gif 文件
        return chunk

    def set_proxy_headers(self, url: str) -> dict:
        if "chaoxing.com" in url:  # 视频放在学习通网盘
            return {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Pro 7 Build/V417IR)"
            }
