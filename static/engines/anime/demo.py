from typing import AsyncIterator, Optional

from core.engine import AnimeEngine
from core.proxy import VideoProxy
from models.anime import *


class DemoEngine(AnimeEngine):
    name = "Demo"
    quality = 5
    version = "2022-06-26"
    notes = "Demo anime engine"
    deprecated = True

    async def search(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        for i in range(3):
            meta = AnimeMeta()
            meta.title = f"{keyword} 第{i}季"
            meta.categories = ["测试"]
            meta.description = "简介信息"
            meta.cover_url = "https://tvax3.sinaimg.cn/large/008kBpBlgy1gw1s5tewhnj307409wgm4.jpg"
            meta.parse_args["aid"] = f"1234-{i}"
            yield meta

    async def parse_detail(self, **parse_args) -> AnimeDetail:
        aid = parse_args.get("aid")
        detail = AnimeDetail()
        detail.title = "视频标题"
        detail.cover_url = "https://tvax3.sinaimg.cn/large/008kBpBlgy1gw1s5tewhnj307409wgm4.jpg"
        detail.description = "简介信息"
        detail.categories = ["测试"]

        for rt_idx in range(2):
            route = PlayRoute()
            route.name = f"播放线路{rt_idx}"

            video = Video()
            video.name = f"第1集 MP4测试"
            video.parse_args["name"] = "earth.mp4"
            route.append_video(video)

            video = Video()
            video.name = f"第2集 FLV测试"
            video.parse_args["name"] = "hxl.flv"
            route.append_video(video)

            video = Video()
            video.name = f"第3集 M3U8测试"
            video.parse_args["name"] = "SPYFAMILY10.m3u8"
            route.append_video(video)

            detail.append_route(route)

        return detail

    async def parse_video_link(self, **parse_args) -> str:
        name = parse_args.get("name")
        # get the real url
        direct_link = "http://file.zaxtyson.cn/video/" + name
        return direct_link


class DemoVideoProxy(VideoProxy):

    def set_proxy_headers(self, request_url: str) -> Optional[dict]:
        if "zaxtyson.cn" in request_url:
            return {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Pro 7 Build/V417IR)"
            }

    def fix_chunk_data(self, chunk_url: str, chunk: bytes) -> bytes:
        # ...
        # #EXTINF:6.840167,
        # spy10/dacb8de7-9455-4181-947c-958f264823c9.jpg
        # #EXTINF:7.674333,
        # spy10/6999148534406965928
        # ...

        # 使用 binwalk 检测视频的起点, 去除头部的图片数据
        if "spy10" in chunk_url:
            return chunk[0x134:]
        return chunk
