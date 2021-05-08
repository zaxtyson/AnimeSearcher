import re
from json import loads

from google.protobuf.json_format import MessageToDict

from api.core.danmaku import *
from . import danmaku_pb2


class BiliBili(DanmakuSearcher):
    """搜索哔哩哔哩官方和用户上传的番剧弹幕"""

    async def get_data_with_params(self, params: dict):
        api = "https://api.bilibili.com/x/web-interface/search/type"
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return

        data = await resp.json(content_type=None)
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
        """官方番剧区数据, 全部接收"""
        results = []
        async for item in self.get_data_with_params(params):
            title, num, _, play_url = item
            meta = DanmakuMeta()
            meta.title = title
            meta.play_url = play_url
            meta.num = num
            results.append(meta)
        return results

    async def search_from_users(self, params: dict):
        """用户投稿的番剧, 说不定有好东西"""
        results = []
        async for item in self.get_data_with_params(params):
            title, num, play_num, play_url = item
            if play_num > 100_000:  # 播放量大于 10w 的留着
                meta = DanmakuMeta()
                meta.title = title
                meta.play_url = play_url
                meta.num = num
                results.append(meta)
        return results

    async def search(self, keyword: str):
        params1 = {"keyword": keyword, "search_type": "media_bangumi", "page": 1}  # 搜索番剧
        params2 = {"keyword": keyword, "search_type": "media_ft", "page": 1}  # 搜索影视
        params3 = {"keyword": keyword, "search_type": "video", "tids": 13, "order": "dm",
                   "page": 1, "duration": 4}  # 用户上传的 60 分钟以上的视频, 按弹幕数量排序
        tasks = [
            self.search_from_official(params1),
            self.search_from_official(params2),
            self.search_from_users(params3)
        ]
        async for item in self.as_iter_completed(tasks):
            yield item


class BiliDanmakuDetailParser(DanmakuDetailParser):

    async def parse(self, play_url: str) -> DanmakuDetail:
        detail = DanmakuDetail()
        play_url = "https://www.bilibili.com" + play_url
        resp = await self.get(play_url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        data_json = re.search(r"window.__INITIAL_STATE__=({.+?});\(function\(\)", html)
        data_json = loads(data_json.group(1))
        ep_list = data_json.get("epList")  # 官方番剧数据
        if not ep_list and data_json.get("sections"):
            ep_list = data_json["sections"][0]["epList"]  # PV 的数据位置不一样
        if ep_list:  # 官方番剧
            for ep in ep_list:
                danmaku = Danmaku()
                danmaku.name = ep["titleFormat"] + ep["longTitle"]
                danmaku.cid = f'{ep["cid"]}|{ep["aid"]}'  # 新版api需要两个参数
                detail.append(danmaku)
            return detail
        # 用户上传的视频
        ep_list = data_json.get("videoData").get("pages")
        aid = data_json.get("aid")
        for ep in ep_list:  # 用户上传的视频
            danmaku = Danmaku()
            danmaku.name = ep.get("part") or ep.get("from")
            danmaku.cid = f'{ep["cid"]}|{aid}'
            detail.append(danmaku)
        return detail


class BiliDanmakuDataParser(DanmakuDataParser):

    async def parse(self, cid: str) -> DanmakuData:
        result = DanmakuData()
        cid, aid = cid.split('|')
        info_api_v2 = f"https://api.bilibili.com/x/v2/dm/web/view"
        params = {"oid": cid, "pid": aid, "type": 1}
        resp = await self.get(info_api_v2, params)
        if not resp or resp.status != 200:
            return result

        data = await resp.read()
        pb2 = danmaku_pb2.DanmakuInfo()
        pb2.ParseFromString(data)
        data = MessageToDict(pb2)
        total = int(data["seg"]["total"])
        tasks = [self.get_one_page_bullet(params, p) for p in range(1, total + 1)]
        async for ret in self.as_iter_completed(tasks):
            result.append(ret)
        result.data.sort(key=lambda x: x[0], reverse=True)
        return result

    async def get_one_page_bullet(self, params: dict, page: int):
        result = DanmakuData()
        data_api_v2 = "https://api.bilibili.com/x/v2/dm/web/seg.so"
        params = params.copy()
        params.update({"segment_index": page})
        resp = await self.get(data_api_v2, params=params)
        if not resp or resp.status != 200:
            return result
        data = await resp.read()
        pb2 = danmaku_pb2.DanmakuData()
        pb2.ParseFromString(data)
        data = MessageToDict(pb2)
        # 哔哩哔哩: 1 飞行弹幕, 4 底部弹幕, 5 顶部弹幕, 6 逆向飞行弹幕
        # Dplayer: 0 飞行弹幕, 1 顶部弹幕, 2 底部弹幕
        pos_fix = {1: 0, 5: 1, 4: 2, 6: 0}
        for bullet in data.get("bullet", []):  # 可能这一页没有数据
            result.append_bullet(
                time=bullet.get("progress", 0) / 1000,
                pos=pos_fix.get(bullet["mode"], 0),
                color=bullet.get("color", 16777215),
                message=bullet.get("content", "")
            )
        return result
