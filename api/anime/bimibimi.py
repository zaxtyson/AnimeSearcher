import re

from api.core.anime import *
from api.utils.logger import logger


class Bimibimi(AnimeSearcher):

    async def search(self, keyword: str):
        api = "https://proxy.app.maoyuncloud.com/app/video/search"
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        params = {"limit": "100", "key": keyword, "page": "1"}
        resp = await self.get(api, params=params, headers=headers)
        if not resp or resp.status != 200:
            return
        data = await resp.json()
        if data["data"]["total"] == 0:
            return

        for meta in data["data"]["items"]:
            anime = AnimeMeta()
            anime.title = meta["name"]
            anime.cover_url = meta["pic"]
            anime.category = meta["type"]
            anime.detail_url = meta["id"]
            yield anime


class BimiDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str) -> AnimeDetail:
        detail = AnimeDetail()
        api = "https://proxy.app.maoyuncloud.com/app/video/detail"
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        resp = await self.get(api, params={"id": detail_url}, headers=headers)
        if not resp or resp.status != 200:
            return detail

        data = await resp.json()
        data = data["data"]
        detail.title = data["name"]
        detail.cover_url = data["pic"]
        detail.desc = data["content"]  # 完整的简介
        detail.category = data["type"]
        for playlist in data["parts"]:
            pl = AnimePlayList()  # 番剧的视频列表
            pl.name = playlist["play_zh"]  # 列表名, 线路 I, 线路 II
            for name in playlist["part"]:
                video_params = f"?id={detail_url}&play={playlist['play']}&part={name}"
                pl.append(Anime(name, video_params))
            detail.append_playlist(pl)
        return detail


class BimiUrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        play_url = "https://proxy.app.maoyuncloud.com/app/video/play" + raw_url
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        resp = await self.get(play_url, headers=headers)
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        real_url = data["data"][0]["url"]

        if "parse" in data["data"][0]:  # 如果存在此字段, 说明上面不是最后的直链
            parse_js = data["data"][0]["parse"]  # 这里会有一段 js 用于进一步解析
            logger.debug(parse_js)
            parse_apis = re.findall(r'"(https?://.+?)"', parse_js)  # 可能存在多个解析接口
            for api in parse_apis:
                url = api + real_url
                resp = await self.get(url)
                json = await resp.json(content_type=None)
                real_url = json.get("url", "")
                if real_url:
                    break  # 已经得到了真正的直链

        # 这种链接还要再重定向之后才是直链
        if "quan.qq.com" in real_url:
            resp = await self.head(real_url, allow_redirects=True)
            real_url = resp.url.human_repr()

        return real_url
