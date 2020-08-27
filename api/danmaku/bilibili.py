import re
from json import loads
from typing import List

from api.base import DanmakuEngine
from api.models import DanmakuMetaInfo, DanmakuCollection, Danmaku


class BiliBili(DanmakuEngine):
    def __init__(self):
        self._host = "https://api.bilibili.com"
        self._search_api = self._host + "/x/web-interface/search/type"
        self._dm_api = self._host + "/x/v1/dm/list.so"

    def search(self, keyword: str) -> List[DanmakuMetaInfo]:
        """搜索番剧信息"""
        ret = []
        params = {"keyword": keyword, "search_type": "media_bangumi"}
        resp = self.get(self._search_api, params)  # 官方番剧弹幕
        if resp.status_code != 200:
            return ret
        data = resp.json()
        if data["code"] != 0 or data["data"]["numResults"] == 0:
            return ret
        for item in data["data"]["result"]:
            dm_mate = DanmakuMetaInfo()
            dm_mate.title = item["title"].replace(r'<em class="keyword">', "").replace("</em>", "")  # 番剧标题
            dm_mate.play_page_url = item["goto_url"]  # 番剧播放页
            dm_mate.num = item["ep_size"]
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
        ep_list = data_json["epList"]
        for ep in ep_list:
            dmk = Danmaku()
            dmk.name = ep["titleFormat"] + ep["longTitle"]
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

    # def get_info_from_user(name):
    #     """从视频分区获取弹幕列表
    #     一些番剧哔哩哔哩没有版权，番剧区找不到相关信息，但是视频区可能存在用户投稿的番剧
    #     下面搜索 60 分钟以上的视频，分区"番剧"，按弹幕数量排序，保留前 3 条数据
    #     """
    #     result = []
    #     params = {"keyword": name, "search_type": "video", "tids": 13, "order": "dm", "page": 1, "duration": 4}
    #     data = BiliBili.search(params)[:3]  # 取弹幕数量前三的结果
    #     for item in data:
    #         title = item["title"].replace(r"<em class="keyword">", "").replace("</em>", "")
    #         aid = int(item["aid"])
    #         cid_api = "https://api.bilibili.com/x/player/pagelist"
    #         req = requests.get(cid_api, {"aid": aid})
    #         if req.status_code != 200 or req.json()["code"] != 0:
    #             continue
    #         dmk = Danmaku(title)
    #         for ep in req.json()["data"]:
    #             dmk.add(ep["part"], int(ep["cid"]))
    #         result.append(dmk)
    #     return result


if __name__ == "__main__":
    bl = BiliBili()
    # print(bl.search("异世界")[0].play_url)
    dmc = bl.get_detail("https://www.bilibili.com/bangumi/play/ss33802/")
    a = dmc.dm_list[0]
    print(a.name, a.cid)
    print(bl.get_danmaku(a.cid))
