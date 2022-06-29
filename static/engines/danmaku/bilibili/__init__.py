import json
import re
from typing import AsyncIterator

from danmaku.bilibili import danmaku_pb2
from google.protobuf.json_format import MessageToDict

from core.engine import DanmakuEngine
from core.http_client import client
from models.danmaku import *


class BiliBili(DanmakuEngine):
    name = "哔哩哔哩"
    version = "2022-06-29"
    quality = 5
    notes = "提供B站官方番剧、用户上传的高播放视频的弹幕"

    async def search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        params1 = {"keyword": keyword, "search_type": "media_bangumi", "page": 1}  # 搜索番剧
        params2 = {"keyword": keyword, "search_type": "media_ft", "page": 1}  # 搜索影视
        params3 = {"keyword": keyword, "search_type": "video", "tids": 13, "order": "dm", "page": 1,
                   "duration": 4}  # 用户上传的 60 分钟以上的视频, 按弹幕数量排序

        async for meta in self.search_from_official(params1):
            yield meta
        async for meta in self.search_from_official(params2):
            yield meta
        async for meta in self.search_from_users(params3):
            yield meta

    async def search_with_params(self, params: dict):
        api = "https://api.bilibili.com/x/web-interface/search/type"
        async with client.get(api, params=params) as r:
            if r.status != 200:
                return
            data = await r.json(content_type=None)

        if data["code"] != 0 or data["data"]["numResults"] == 0:
            return

        for item in data["data"]["result"]:
            if '<em class="keyword">' not in item["title"]:  # 没有匹配关键字, 是B站的推广视频
                continue
            if "港澳台" in item["title"]:
                continue  # 港澳台地区弹幕少的可怜
            title = item["title"].replace(r'<em class="keyword">', "").replace("</em>", "")  # 番剧标题
            num = int(item.get("ep_size") or -1)  # 集数, 未知的时候用 -1 表示
            play_num = int(item.get("play") or -1)  # 用户投稿的视频播放数
            play_url = item.get("goto_url") or item.get("arcurl")  # 番剧播放页链接
            play_url = re.sub(r"https?://www.bilibili.com", "", play_url)  # 缩短一些, 只留关键信息
            yield title, num, play_num, play_url

    async def search_from_official(self, params: dict):
        """官方番剧区数据， 全部保留"""
        async for item in self.search_with_params(params):
            title, num, _, play_url = item
            meta = DanmakuMeta()
            meta.title = title
            meta.num = num
            meta.parse_args["url"] = play_url
            yield meta

    async def search_from_users(self, params: dict):
        """用户投稿的番剧, 说不定有好东西"""
        async for item in self.search_with_params(params):
            title, num, play_num, play_url = item
            if play_num > 100_000:  # 播放量大于 10w 的留着
                meta = DanmakuMeta()
                meta.title = title
                meta.num = num
                meta.parse_args["url"] = play_url
                yield meta

    async def parse_detail(self, **parse_args) -> DanmakuDetail:
        detail = DanmakuDetail()

        play_url = "https://www.bilibili.com" + parse_args.get("url")
        async with client.get(play_url) as r:
            if r.status != 200:
                return detail
            html = await r.text()

        data_json = re.search(r"window.__INITIAL_STATE__=({.+?});\(function\(\)", html)
        data_json = json.loads(data_json.group(1))

        if data_json.get("mediaInfo"):  # 官方番剧数据
            detail.title = data_json["mediaInfo"]["title"]
            for ep in data_json["epList"]:  # 正片
                dmk = Danmaku()
                dmk.name = ep["titleFormat"] + ep["longTitle"]
                dmk.parse_args["cid"] = ep["cid"]  # 新版api需要两个参数
                dmk.parse_args["aid"] = ep["aid"]
                detail.append_danmaku(dmk)
            # 番剧 PV 还是去掉算了
            # if data_json.get("sections"):
            #     for pv in data_json["sections"][0]["epList"]:  # PV
            #         dmk = Danmaku()
            #         dmk.name = pv["titleFormat"] + pv["longTitle"]
            #         dmk.parse_args["cid"] = pv["cid"]  # 新版api需要两个参数
            #         dmk.parse_args["aid"] = pv["aid"]
            #         detail.append_danmaku(dmk)
        else:  # 用户上传的视频
            detail.title = data_json["videoData"]["title"]
            for ep in data_json["videoData"]["pages"]:  # 用户上传的视频
                dmk = Danmaku()
                dmk.name = ep["part"]
                dmk.parse_args["cid"] = ep["cid"]
                dmk.parse_args["aid"] = data_json["aid"]
                detail.append_danmaku(dmk)

        return detail

    async def parse_data(self, **parse_args) -> DanmakuData:
        ret = DanmakuData()
        cid = parse_args.get("cid")
        aid = parse_args.get("aid")
        info_api_v2 = f"https://api.bilibili.com/x/v2/dm/web/view"
        params = {"oid": cid, "pid": aid, "type": 1}
        async with client.get(info_api_v2, params=params) as r:
            if r.status != 200:
                return ret
            rpc_stream = await r.read()

        pb2 = danmaku_pb2.DanmakuInfo()
        pb2.ParseFromString(rpc_stream)
        data = MessageToDict(pb2)
        total = int(data["seg"]["total"])

        for p in range(1, total + 1):
            async for bullet in self.get_one_page_bullets(params, p):
                ret.append_bullet(bullet)

        return ret

    async def get_one_page_bullets(self, params: dict, page: int):
        data_api_v2 = "https://api.bilibili.com/x/v2/dm/web/seg.so"
        params = params.copy()
        params.update({"segment_index": page})
        async with client.get(data_api_v2, params=params) as r:
            if r.status != 200:
                return
            rpc_stream = await r.read()

        pb2 = danmaku_pb2.DanmakuData()
        pb2.ParseFromString(rpc_stream)
        data = MessageToDict(pb2)

        # 哔哩哔哩: 1 飞行弹幕, 4 底部弹幕, 5 顶部弹幕, 6 逆向飞行弹幕
        # Dplayer: 0 飞行弹幕, 1 顶部弹幕, 2 底部弹幕
        pos_mapping = {1: 0, 5: 1, 4: 2, 6: 0}
        for item in data.get("bullet", []):  # 可能这一页没有数据
            bullet = Bullet()
            bullet.time = item.get("progress", 0) / 1000
            bullet.pos = pos_mapping.get(item["mode"], 0)
            bullet.color = item.get("color", 0xffffff)
            bullet.msg = item.get("content", "")
            yield bullet
