from typing import AsyncIterator

from core.engine import AnimeEngine
from core.http_client import client
from core.proxy import VideoProxy
from models.anime import *
from utils.encode import md5, unquote
from utils.log import logger
from utils.misc import get_path


class AgeFans(AnimeEngine):
    name = "AgeFans"
    version = "2022-06-27"
    quality = 4
    maintainers = ["zaxtyson"]
    notes = "动漫挺多, 画质一般, 更新比较及时, 部分视频有广告"

    api_prefix = "https://api.agefans.app/v2"
    headers = {
        "Origin": "https://web.age-spa.com:8443",
        "Referer": "https://web.age-spa.com:8443/"
    }

    async def search(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        url = f"{self.api_prefix}/search?page=1&query={keyword}"

        async with client.get(url, headers=self.headers) as r:
            data = await r.json(content_type=None)

        data = data["AniPreL"]
        for item in data:
            meta = AnimeMeta()
            meta.title = item["R动画名称"]
            meta.categories = item["R剧情类型"]
            meta.description = item["R简介"]
            meta.cover_url = item["R封面图小"]
            meta.parse_args["aid"] = item["AID"]
            yield meta

    async def parse_detail(self, **parse_args) -> AnimeDetail:
        aid = parse_args.get("aid")
        detail = AnimeDetail()

        api = f"{self.api_prefix}/detail/{aid}"  # 20120029
        async with client.get(api, headers=self.headers) as r:
            data = await r.json(content_type=None)

        data = data["AniInfo"]
        detail.title = data["R动画名称"]
        detail.cover_url = data["R封面图"]
        detail.description = data["R简介"]
        detail.categories = data["R剧情类型2"]

        for rt in data["R在线播放All"]:
            if not rt:
                continue
            play_id = rt[0]["PlayId"]
            if self.drop_this(play_id):
                continue

            route = PlayRoute()
            route.name = play_id.replace("<play>", "").replace("</play>", "").upper()
            for v in rt:
                video = Video()
                video.name = v["Title_l"] or v["Title"]
                video.parse_args["pid"] = v["PlayId"]  # <play>web_mp4|tieba|...</play>
                video.parse_args["pvid"] = unquote(v["PlayVid"])  # url or token
                route.append_video(video)
            detail.append_route(route)

        return detail

    async def parse_video_link(self, **parse_args) -> str:
        play_id = parse_args.get("pid")
        play_vid = parse_args.get("pvid")

        if play_vid.startswith("http"):
            return play_vid  # 不用处理了

        url = f"{self.api_prefix}/_getplay"
        async with client.get(url, headers=self.headers) as r:
            data = await r.json(content_type=None)

        next_url = data.get("Location")
        if not next_url:
            return ""

        # 加密算法见: https://vip.cqkeb.com/agefans/js/chunk-69395a8f.aa99d182.js
        play_key = "agefans3382-getplay-1719"
        timestamp = data["ServerTime"]
        kp = md5(str(timestamp) + "{|}" + play_id + "{|}" + play_vid + "{|}" + play_key)
        params = {
            "playid": play_id,
            "vid": play_vid,
            "kt": timestamp,
            "kp": kp
        }

        async with client.get(next_url, params=params) as r:
            if r.status != 200:
                logger.error(f"Can't get next data: {r.status=}, {next_url=}")
                return ""
            data = await r.json(content_type=None)

        p_url = unquote(data.get("purlf", ""))
        v_url = unquote(data.get("vurl", ""))
        url = p_url + v_url
        logger.debug(f"{p_url=}, {v_url=}")
        if not url:
            return ""
        return url.split("url=")[-1]

    @staticmethod
    def drop_this(play_id: str) -> bool:
        key_list = ["接口", "QLIVE", "88jx", "zjm3u8"]
        for key in key_list:
            if key in play_id:
                logger.debug(f"Drop route, {play_id=}")
                return True
        return False

    async def parse_video_info(self, direct_link: str) -> VideoInfo:
        if "bdxiguavod.com" in direct_link:
            return VideoInfo("mp4", 3600)
        return await super().parse_video_info(direct_link)


class AgeFansProxy(VideoProxy):

    async def get_m3u8_text(self, index_url: str) -> str:
        if "szjal.cn" in index_url:
            # example: https://v6.szjal.cn/20201211/ckpQyxMN/index.m3u8
            return await self.get_m3u8_text_of_szjal(index_url)

        return await super().get_m3u8_text(index_url)

    async def get_m3u8_text_of_szjal(self, index_url: str) -> str:
        path = get_path(index_url)  # https://v6.szjal.cn/20201211/ckpQyxMN
        real_url = path + "/hls/index.m3u8"
        text = await self.read_text(real_url)
        lines = []
        for line in text.splitlines():
            if not line.startswith("#"):
                line = path + "/hls/" + line
                lines.append(line)
            else:
                lines.append(line)
        return "\n".join(lines)
