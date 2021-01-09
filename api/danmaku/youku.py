import base64
import hashlib
import json
import re
import time
from typing import List

from api.base import DanmakuEngine
from api.logger import logger
from api.models import DanmakuMetaInfo, DanmakuCollection, Danmaku


class DanmukuYouku(DanmakuEngine):
    """抓取优酷的弹幕"""

    def search(self, keyword: str) -> List[DanmakuMetaInfo]:
        """搜索视频"""
        result = []
        search_api = "https://search.youku.com/search_video"
        resp = self.get(search_api, params={"keyword": keyword})
        if resp.status_code != 200:
            return result
        data = re.search(r"__INITIAL_DATA__\s*?=\s*?({.+?});\s*?window._SSRERR_", resp.text)
        data = json.loads(data.group(1))  # 这是我见过最恶心的 json
        data = data["pageComponentList"]
        for item in data:
            info = item.get("commonData")
            if not info:
                continue
            meta = DanmakuMetaInfo()
            meta.title = info["titleDTO"]["displayName"].replace("\t", "")
            meta.play_page_url = info["leftButtonDTO"]["action"]["value"]
            if meta.play_page_url and ("youku.com" not in meta.play_page_url):
                continue  # 有时候返回 qq 的播放链接, 有时候该字段为 null
            num = re.search(r"(\d+?)集", info.get("stripeBottom", ""))  # 该字段可能不存在
            meta.num = int(num.group(1)) if num else 0
            result.append(meta)
        return result

    def get_detail(self, play_page_url: str) -> DanmakuCollection:
        """获取视频详情"""
        ret = DanmakuCollection()
        resp = self.get(play_page_url)
        if resp.status_code != 200:
            return ret
        data = re.search(r"__INITIAL_DATA__\s*?=\s*?({.+?});", resp.text)
        if not data:  # 多半是碰到反爬机制了
            logger.error("We are blocked by youku")
            return ret
        data = json.loads(data.group(1))
        # 我们需要的数据在第 13 层! 写出这种代码的程序员应该被绑到绞刑架上
        data = data["data"]["data"]["nodes"][0]["nodes"]
        # nodes 是一个列表, 其中 type == 10013 的元素才是视频播放列表的数据
        data = list(filter(lambda x: x["type"] == 10013, data))[0]
        # 数据在这个结点的 nodes 节点下
        data = data["nodes"]
        for item in data:
            info = item["data"]
            if info["videoType"] != "正片":
                continue  # 可能混入预告片什么的
            dmk = Danmaku()
            dmk.name = info["title"]
            dmk.cid = info["action"]["value"]  # 视频id  "XMzk4NDE2Njc4OA=="
            ret.append(dmk)
        return ret

    def get_danmaku(self, video_id: str):
        """提供视频 url 获取对应弹幕库"""
        video_url = f"https://v.youku.com/v_show/id_{video_id}.html"
        vid, title, duration = self.get_video_info(video_url)
        token = self.get_token()
        minutes = int(duration) // 60  # 视频分钟数
        tasks = self.submit_tasks([
            (self.get_one_min_danmu, (vid, token, m), {}) for m in range(minutes + 1)
        ])
        result = [i for ret in tasks for i in ret]
        result.sort(key=lambda x: x[0])
        return result

    def get_token(self):
        """获取 cookie 中的必要参数"""
        cna_api = "https://log.mmstat.com/eg.js"
        cookie_api = "https://acs.youku.com/h5/mtop.com.youku.aplatform.weakget/1.0/?jsv=2.5.1&appKey=24679788"

        no_results = {"_m_h5_tk": "", "_m_h5_tk_enc": "", "cna": ""}
        resp = self.head(cna_api)
        if resp.status_code != 200:
            return no_results
        cna = resp.cookies.get("cna")

        resp = self.get(cookie_api)
        if resp.status_code != 200:
            return no_results
        result = dict(resp.cookies)
        result["cna"] = cna
        return result

    def get_video_info(self, url: str):
        """获取视频 vid, 标题, 时长信息"""
        vid = re.search(r"video/id_(/+?)\.html", url) or \
              re.search(r"v_show/id_(.+?)\.html", url)
        vid = vid.group(1) if vid else ""  # 视频id "XNDg5MDY0MDA3Ng=="
        api = f"https://openapi.youku.com/v2/videos/show.json"
        params = {"client_id": "53e6cc67237fc59a", "package": "com.huawei.hwvplayer.youku", "video_id": vid}
        resp = self.get(api, params=params)
        if resp.status_code != 200:
            return vid, "", 0
        data = resp.json()
        duration = float(data.get("duration", 0))  # 视频时长(s)
        title = data.get("title", "")  # 视频标题
        return vid, title, duration

    def get_one_min_danmu(self, vid: str, token: dict, min_at: int):
        """获取一分钟的弹幕
        :param min_at: 弹幕开始的分钟数
        """
        app_key = "24679788"
        api = "https://acs.youku.com/h5/mopen.youku.danmu.list/1.0/"
        timestamp = str(int(time.time() * 1000))
        msg = {"ctime": timestamp, "ctype": 10004, "cver": "v1.0", "guid": token["cna"], "mat": min_at, "mcount": 1,
               "pid": 0,
               "sver": "3.1.0", "type": 1, "vid": vid}
        msg_b64 = base64.b64encode(json.dumps(msg, separators=(',', ':')).encode("utf-8")).decode(
            "utf-8")  # 将 msg 转换为 base64 后作为 msg 的一个键值对
        sign = hashlib.md5(bytes(msg_b64 + "MkmC9SoIw6xCkSKHhJ7b5D2r51kBiREr", "utf-8")).hexdigest()  # 计算签名
        msg.update({"msg": msg_b64, "sign": sign})
        # 只要 Cookie 的 _m_h5_tk 和 _m_h5_tk_enc 就行
        cookie = ";".join([f"{k}={v}" for k, v in token.items()])
        headers = {
            "Cookie": cookie,
            "Referer": "https://v.youku.com"
        }
        timestamp = str(int(time.time() * 1000))
        data = json.dumps(msg, separators=(',', ':'))
        token = f"{token['_m_h5_tk'][:32]}&{timestamp}&{app_key}&{data}"
        token = hashlib.md5(bytes(token, "utf-8")).hexdigest()

        params = {
            "jsv": "2.5.6",
            "appKey": app_key,
            "t": timestamp,
            "sign": token,
            "api": "mopen.youku.danmu.list",
            "v": "1.0",
            "type": "originaljson",
            "dataType": "jsonp",
            "timeout": "20000",
            "jsonpIncPrefix": "utility"
        }

        resp = self.post(api, params=params, data={"data": data}, headers=headers)
        comments = resp.json()["data"]["result"]  # 带转义的 json 串
        comments = json.loads(comments)["data"]["result"]  # 返回的数据层层套娃 :(

        result = []
        for comment in comments:
            content = comment["content"]
            play_time = comment["playat"] // 1000  # 弹幕出现的时间点(s)
            properties = json.loads(comment["propertis"])  # 弹幕的属性(官方拼写错误)
            color = properties["color"]
            position = properties["pos"]
            # size = properties["size"]
            result.append([play_time, position, color, "", content])  # Dplayer 格式
        return result
