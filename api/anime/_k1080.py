"""
新版本改名 闪电影视: https://www.ak1080.com/

旧版本视频详情接口于 2021/07/20 失效

新版本接口:
GET http://app.kssp.net/api.php/app/search?pg=1&text=从零开始的异世界&token=
GET http://app.kssp.net/api.php/app/video_detail?id=606&token=

请求返回的数据使用 Base64 加密后, 还需解密, 由于 APP 使用 flutter 开发,
具体逻辑在 libapp.so 中, 暂时无法逆向
Dart version: e4a09dbf2bb120fe4674e0576617a0dc
"""

from api.core.anime import *
from api.core.proxy import AnimeProxy


class K1080(AnimeSearcher):

    async def search(self, keyword: str):
        data, total_page = await self.get_one_page(keyword, 1)
        for item in self.parse_anime_metas(data):
            yield item
        if total_page > 1:
            tasks = [self.parse_one_page(keyword, p) for p in range(2, total_page + 1)]
            async for item in self.as_iter_completed(tasks):
                yield item

    async def get_one_page(self, keyword: str, page: int) -> (list, int):
        api = "http://myapp.hanmiys.net/search/result"
        payload = {
            "page_num": str(page),
            "keyword": keyword,
            "page_size": "12"
        }
        resp = await self.post(api, json=payload, headers={"User-Agent": "okhttp/4.1.0"})
        if not resp or resp.status != 200:
            return [], 0
        data = await resp.json(content_type=None)
        total_page = int(data["data"]["total_page"])
        data = data["data"]["list"]
        return data, total_page

    def parse_anime_metas(self, data: list):
        ret = []
        for item in data:
            meta = AnimeMeta()
            meta.cover_url = item["cover"]
            meta.title = item["video_name"]
            meta.detail_url = item["video_id"]  # such as "60014"
            meta.desc = item["intro"] or "无简介"
            meta.category = item["category"]
            ret.append(meta)
        return ret

    async def parse_one_page(self, keyword: str, page: int):
        data, _ = await self.get_one_page(keyword, page)
        return self.parse_anime_metas(data)


class K1080DetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = "http://myapp.hanmiys.net/video/info"
        payload = {"video_id": detail_url}
        resp = await self.post(api, json=payload, headers={"User-Agent": "okhttp/4.1.0"})
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        info = data["data"]["info"]
        detail.cover_url = info["cover"]
        detail.title = info["video_name"]
        detail.desc = info["intro"] or "无简介"
        detail.category = info["category"]

        videos = info["videos"]
        for source in info["source"]:
            playlist = AnimePlayList()
            playlist.name = source["name"]
            for video in videos:
                anime = Anime()
                anime.name = video["title"]
                anime.raw_url = str(source["source_id"]) + '|' + str(video["chapter_id"]) + '|' + str(video["video_id"])
                playlist.append(anime)
            if not playlist.is_empty():
                detail.append_playlist(playlist)
        return detail


class K1080UrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        api = "http://myapp.hanmiys.net/video/parse"
        source_id, chapter_id, video_id = raw_url.split('|')
        payload = {
            "source_id": source_id,
            "chapter_id": chapter_id,
            "video_id": video_id
        }
        resp = await self.post(api, json=payload, headers={"User-Agent": "okhttp/4.1.0"})
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        return data["data"]["url"]


class K1080Proxy(AnimeProxy):

    def fix_chunk_data(self, url: str, chunk: bytes) -> bytes:
        if "gtimg.com" in url:
            return chunk[0x303:]  # 前面是图片数据
        if "ydstatic.com" in url:
            return chunk[0x3BF:]
        if "pstatp.com" in url or "qpic.cn" in url:
            return chunk[0x13A:]
        return chunk

    def enforce_proxy(self, url: str) -> bool:
        if "byingtime.com" in url:
            return True
        if "paofans" in url:
            return True
        if "hanmiys" in url:
            return True
        return False
