import re
from json import loads
from typing import List

from api.base import DanmakuEngine
from api.logger import logger
from api.models import DanmakuMetaInfo, DanmakuCollection, Danmaku


class BiliBili(DanmakuEngine):
    """搜索哔哩哔哩官方和用户上传的番剧弹幕"""

    def __init__(self):
        self._host = "https://api.bilibili.com"
        self._search_api = self._host + "/x/web-interface/search/type"
        self._dm_api = self._host + "/x/v1/dm/list.so"
        self._cid_api = self._host + "/x/player/pagelist"

    def search(self, keyword: str) -> List[DanmakuMetaInfo]:
        """搜索番剧信息"""
        logger.info(f"Searching for danmaku: {keyword}")
        ret = []
        params = {"keyword": keyword, "search_type": "media_bangumi"}
        params2 = {"keyword": keyword, "search_type": "video", "tids": 13, "order": "dm", "page": 1, "duration": 4}
        task_list = [
            (self.get, (self._search_api, params), {}),
            (self.get, (self._search_api, params2), {})  # 用户上传的60 分钟以上的视频, 按弹幕数量排序
        ]
        resp_list = self.submit_tasks(task_list)  # 多线程同时搜索
        for resp in resp_list:
            if resp.status_code != 200:
                continue
            data = resp.json()
            if data["code"] != 0 or data["data"]["numResults"] == 0:
                continue
            for item in data["data"]["result"]:
                if '<em class="keyword">' not in item["title"]:  # 没有匹配关键字, 是B站的推广视频
                    continue
                dm_mate = DanmakuMetaInfo()
                dm_mate.title = item["title"].replace(r'<em class="keyword">', "").replace("</em>", "")  # 番剧标题
                dm_mate.play_page_url = item.get("goto_url") or item.get("arcurl")  # 番剧播放页链接
                dm_mate.num = int(item.get("ep_size") or -1)
                logger.debug(f"Match danmaku: {dm_mate}")
                ret.append(dm_mate)
        return ret

    def get_detail(self, play_url: str) -> DanmakuCollection:
        """解析番剧播放页, 提取所有视频的弹幕信息"""
        ret = DanmakuCollection()
        resp = self.get(play_url)
        if resp.status_code != 200:
            return ret
        data_json = re.search(r"window.__INITIAL_STATE__=({.+?});\(function\(\)", resp.text)
        data_json = loads(data_json.group(1))
        ep_list = data_json.get("epList")
        if ep_list:  # 官方番剧
            for ep in ep_list:
                dmk = Danmaku()
                dmk.name = ep["titleFormat"] + ep["longTitle"]
                dmk.cid = str(ep["cid"])  # cid 号
                ret.append(dmk)
        else:
            ep_list = data_json.get("videoData").get("pages")
            for ep in ep_list:  # 用户上传的视频
                dmk = Danmaku()
                dmk.name = ep.get("part") or ep.get("from")
                dmk.cid = str(ep["cid"])  # cid 号
                ret.append(dmk)
        return ret

    def get_danmaku(self, cid: str):
        """解析一集视频的弹幕, 输出 DPlayer 可接受的格式
        :return {"code": 0,
                 "data" [
                         [time, pos, color, message],  # 一条弹幕: float 时间,位置参数(0右边,1上边,2底部),颜色码 10 进制,弹幕内容
                         [time, pos, color, message],
                        ]}
        """
        ret = {"code": 0, "data": []}
        params = {"oid": cid}
        resp = self.get(self._dm_api, params=params)
        if resp.status_code != 200:
            return ret
        dm_list = re.findall(r'p="(\d+\.?\d*?),\d,\d\d,(\d+?),\d+,(\d),.+?>(.+?)</d>', resp.text)
        ret["data"] = [[float(dm[0]), int(dm[2]), int(dm[1]), "", dm[3]] for dm in dm_list]
        return ret
