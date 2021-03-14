import json
import re
import time

from api.core.danmaku import *
from api.utils.logger import logger
from api.utils.tool import md5, b64encode


class Youku(DanmakuSearcher):

    async def search(self, keyword: str):
        api = "https://search.youku.com/search_video"
        resp = await self.get(api, params={"keyword": keyword})
        if not resp or resp.status != 200:
            return

        html = await resp.text()
        data = re.search(r"__INITIAL_DATA__\s*?=\s*?({.+?});\s*?window._SSRERR_", html)
        data = json.loads(data.group(1))  # 这是我见过最恶心的 json
        data = data["pageComponentList"]
        for item in data:
            info = item.get("commonData")
            if not info:
                continue
            meta = DanmakuMeta()
            meta.title = info["titleDTO"]["displayName"].replace("\t", "")
            play_url = info["leftButtonDTO"]["action"]["value"]
            if "youku.com" not in play_url:
                continue  # 有时候返回 qq 的播放链接, 有时候该字段为 null, 我的老天爷
            meta.play_url = play_url
            num = re.search(r"(\d+?)集", info.get("stripeBottom", ""))  # 该字段可能不存在
            meta.num = int(num.group(1)) if num else 0
            yield meta


class YoukuDanmakuDetailParser(DanmakuDetailParser):

    async def parse(self, play_url: str):
        """获取视频详情"""
        detail = DanmakuDetail()
        resp = await self.get(play_url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        data = re.search(r"__INITIAL_DATA__\s*?=\s*?({.+?});", html)
        if not data:  # 多半是碰到反爬机制了
            logger.warning("We are blocked by youku")
            return detail

        # 下面是 data 和 node 结点的疯狂套娃, 我们需要的数据在第 13 层
        # 我的圣母玛利亚, 这是一坨何其冗余庞杂的 shit
        # 写出这个代码的程序员应该被送上绞刑架, 然后用文火慢炖
        data = json.loads(data.group(1))
        data = data["data"]["data"]["nodes"][0]["nodes"]
        # nodes 是一个列表, 其中 type == 10013 的元素才是视频播放列表的数据
        data = list(filter(lambda x: x["type"] == 10013, data))[0]
        # 数据在这个结点的 nodes 节点下
        data = data["nodes"]
        for item in data:
            info = item["data"]
            if info["videoType"] != "正片":
                continue  # 可能混入预告片什么的
            danmaku = Danmaku()
            danmaku.name = info["title"]
            danmaku.cid = info["action"]["value"]  # 视频id  "XMzk4NDE2Njc4OA=="
            detail.append(danmaku)
        return detail


class YoukuDanmakuDataParser(DanmakuDataParser):

    async def parse(self, cid: str):
        vid = cid
        title, duration = await self.get_video_info(vid)
        token = await self.get_token()
        minutes = int(duration) // 60  # 视频分钟数
        tasks = [self.get_60s_bullets(vid, token, m) for m in range(minutes + 1)]
        result = DanmakuData()
        async for ret in self.as_iter_completed(tasks):
            result.append(ret)
        return result

    async def get_token(self):
        """获取 cookie 中的必要参数"""
        cna_api = "https://log.mmstat.com/eg.js"
        cookie_api = "https://acs.youku.com/h5/mtop.com.youku.aplatform.weakget/1.0/?jsv=2.5.1&appKey=24679788"
        tokens = {"_m_h5_tk": "", "_m_h5_tk_enc": "", "cna": ""}
        resp = await self.head(cna_api)
        if not resp or resp.status != 200:
            return tokens
        tokens["cna"] = resp.cookies.get("cna").value
        resp = await self.get(cookie_api)
        if not resp or resp.status != 200:
            return tokens
        # 只要 Cookie 的 _m_h5_tk 和 _m_h5_tk_enc 就行
        tokens["_m_h5_tk"] = resp.cookies.get("_m_h5_tk").value
        tokens["_m_h5_tk_enc"] = resp.cookies.get("_m_h5_tk_enc").value
        return tokens

    async def get_video_info(self, vid: str):
        """获取视频 vid, 标题, 时长信息"""
        api = "https://openapi.youku.com/v2/videos/show.json"
        params = {"client_id": "53e6cc67237fc59a", "package": "com.huawei.hwvplayer.youku", "video_id": vid}
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return "", 0
        data = await resp.json(content_type=None)
        duration = float(data.get("duration", 0))  # 视频时长(s)
        title = data.get("title", "")  # 视频标题
        return title, duration

    async def get_60s_bullets(self, vid: str, tokens: dict, min_at: int):
        """获取一分钟的弹幕"""
        app_key = "24679788"
        api = "https://acs.youku.com/h5/mopen.youku.danmu.list/1.0/"
        timestamp = str(int(time.time() * 1000))
        msg = {
            "ctime": timestamp,
            "ctype": 10004,
            "cver": "v1.0",
            "guid": tokens["cna"],
            "mat": min_at,
            "mcount": 1,
            "pid": 0,
            "sver": "3.1.0",
            "type": 1,
            "vid": vid
        }
        # 将 msg 转换为 base64 后作为 msg 的一个键值对
        msg_b64 = b64encode(json.dumps(msg, separators=(',', ':')))
        sign = md5(msg_b64 + "MkmC9SoIw6xCkSKHhJ7b5D2r51kBiREr")  # 计算签名
        msg.update({"msg": msg_b64, "sign": sign})
        timestamp = str(int(time.time() * 1000))
        data = json.dumps(msg, separators=(',', ':'))
        sign = md5(f"{tokens['_m_h5_tk'][:32]}&{timestamp}&{app_key}&{data}")

        params = {
            "jsv": "2.5.6",
            "appKey": app_key,
            "t": timestamp,
            "sign": sign,
            "api": "mopen.youku.danmu.list",
            "v": "1.0",
            "type": "originaljson",
            "dataType": "jsonp",
            "timeout": "20000",
            "jsonpIncPrefix": "utility"
        }
        self.session.cookie_jar.update_cookies(tokens)
        headers = {"Referer": "https://v.youku.com"}
        resp = await self.post(api, params=params, data={"data": data}, headers=headers)
        data = await resp.json(content_type=None)
        comments = data["data"]["result"]  # 带转义的 json 串
        comments = json.loads(comments)["data"]["result"]  # 返回的数据层层套娃 :(

        result = DanmakuData()
        for comment in comments:
            properties = json.loads(comment["propertis"])  # 弹幕的属性(官方拼写错误)
            color = properties["color"]
            position = properties["pos"]
            # size = properties["size"]
            result.append_bullet(
                time=comment["playat"] // 1000,
                pos=position,
                color=color,
                message=comment["content"]
            )
        return result
