"""
阿房影视: https://bwl87.com/
后端接口与 K1080 一模一样
"""
import json
from json import JSONDecodeError

from api.core.anime import *
from api.core.proxy import AnimeProxy
from api.utils.logger import logger


def parse_response(data: str) -> dict:
    """处理接口响应数据"""
    try:
        # 3s内频繁搜索会导致接口返回异常提醒
        # 有时候部分数据未加载导致 json 格式错误
        data = data.replace("&comments&", "").replace("&is_fav&", "0")
        return json.loads(data)
    except JSONDecodeError:
        logger.info("Please wait for 3s...")
        return {}


class Afang(AnimeSearcher):
    async def search(self, keyword: str):
        api = "https://app.bwl87.com/search/result"
        payload = {
            "page_num": "1",  # 取一页即可, 不用太多数据
            "keyword": keyword,
            "page_size": "12"
        }
        resp = await self.post(api, json=payload, headers={"User-Agent": "okhttp/4.1.0"})
        if not resp or resp.status != 200:
            return
        data = parse_response(await resp.text())
        if not data:
            return
        data = data["data"]["list"]
        for item in data:
            meta = AnimeMeta()
            meta.cover_url = item["cover"]
            meta.title = item["video_name"]
            meta.detail_url = item["video_id"]
            meta.desc = item["intro"] or "无简介"
            meta.category = item["category"]
            yield meta


class AfangDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = "https://app.bwl87.com/video/info"
        payload = {"video_id": detail_url}
        resp = await self.get(api, json=payload, headers={"User-Agent": "okhttp/4.1.0"})
        if not resp or resp.status != 200:
            return detail
        data = parse_response(await resp.text())
        if not data:
            return
        info = data["data"]["info"]
        detail.title = info["video_name"]
        detail.cover_url = info["cover"]
        detail.desc = info["intro"].replace("<p>", "").replace("</p>", "")
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


class AfangUrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        api = "https://app.bwl87.com/video/parse"
        source_id, chapter_id, video_id = raw_url.split('|')
        payload = {
            "source_id": source_id,
            "chapter_id": chapter_id,
            "video_id": video_id
        }
        resp = await self.get(api, json=payload, headers={"User-Agent": "okhttp/4.1.0"})
        if not resp or resp.status != 200:
            return ""
        data = parse_response(await resp.text())
        if not data:
            return ""
        return data["data"]["url"]


class AfangProxy(AnimeProxy):

    def enforce_proxy(self, url: str) -> bool:
        if "hanmiys" in url:
            return True
        return False

    def fix_chunk_data(self, url: str, chunk: bytes) -> bytes:
        if "gtimg.com" in url:
            return chunk[0x303:]
        if "ydstatic.com" in url:
            return chunk[0x3BF:]
        if "pstatp.com" in url or "qpic.cn" in url:
            return chunk[0x13A:]
        return chunk
