import json
import re

from api.core.danmaku import *


class Tencent(DanmakuSearcher):

    async def search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        tasks = [self.search_one_page(keyword, p) for p in range(5)]  # 取前10页
        async for meta in self.as_iter_completed(tasks):
            yield meta

    async def search_one_page(self, keyword: str, page: int):
        api = f"http://node.video.qq.com/x/api/msearch"
        params = {
            "keyWord": keyword,
            "callback": f"jsonp{page}",
            "contextValue": f"last_end={page * 15}&response=1",
            "contextType": 2
        }
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return
        jsonp = await resp.text()
        data = re.search(r".+\(({.+})\)", jsonp).group(1)
        data = json.loads(data)
        data = data["uiData"]
        results = []
        for item in data:
            item = item["data"]
            if not item:  # 有时没有
                continue
            item = item[0]
            if not item.get("videoSrcName"):
                continue  # 没用的视频
            if "redirect" in item["webPlayUrl"]:
                continue  # 其它平台的
            title = item["coverTitle"].replace("\u0005", "").replace("\u0006", "")
            if not title:
                continue
            meta = DanmakuMeta()
            meta.title = item["coverTitle"].replace("\u0005", "").replace("\u0006", "")
            meta.play_url = re.search(r"/([^/]+?)\.html", item["webPlayUrl"]).group(1)
            meta.num = item["videoSrcName"][0]["totalEpisode"]
            results.append(meta)
        return results


class TencentDanmakuDetailParser(DanmakuDetailParser):

    async def parse(self, play_url: str) -> DanmakuDetail:
        detail = DanmakuDetail()
        api = "http://s.video.qq.com/get_playsource"
        params = {
            "id": play_url,
            "type": 4,
            "range": "1-99999",
            "otype": "json"
        }
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return detail
        text = await resp.text()
        data = text.lstrip("QZOutputJson=").rstrip(";")
        data = json.loads(data)
        data = data["PlaylistItem"]
        if not data:
            return detail
        data = data["videoPlayList"]
        for item in data:
            danmaku = Danmaku()
            danmaku.name = item["title"]
            if "预告片" in danmaku.name:
                continue  # 预告片不要
            danmaku.cid = item["id"]  # 视频id "j31520vrtpw"
            detail.append(danmaku)
        return detail


class TencentDanmakuDataParser(DanmakuDataParser):

    async def parse(self, cid: str) -> DanmakuData:
        """获取视频的全部弹幕"""
        result = DanmakuData()
        title, duration, target_id = await self.get_video_info(cid)
        if not target_id:
            return result
        count = duration // 30 + 1
        tasks = [self.get_30s_bullets(cid, target_id, t * 30) for t in range(count)]
        async for ret in self.as_iter_completed(tasks):
            result.append(ret)
        return result

    async def get_30s_bullets(self, video_id: str, target_id: str, start_at: int):
        """获取某个时间点后的 30s 弹幕数据
        :params video_id 视频 url 中的id
        :params target_id 视频的数字id
        :params start_at 弹幕起始时间点(s)
        """
        result = DanmakuData()
        api = "https://mfm.video.qq.com/danmu"
        params = {
            "otype": "json",
            "target_id": f"{target_id}&vid={video_id}",
            "session_key": "0,0,0",
            "timestamp": start_at
        }
        # sleep(0.1)  # 太快了有可能被 ban
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return result

        data = await resp.text()
        data = json.loads(data, strict=False)  # 可能有特殊字符
        for item in data["comments"]:
            play_at = item["timepoint"]  # 弹幕出现的时间点(s)
            content = item["content"].replace("\xa0", "").strip()  # 弹幕内容
            content = re.sub(r"^(.*?:)|^(.*?：)|\[.+?\]", "", content)
            if not content:
                continue
            style = item["content_style"]
            if not style:
                color = "ffffff"
                position = 0
            else:
                style = json.loads(style)
                color = style.get("color", "ffffff")  # 10 进制颜色
                position = style["position"]

            result.append_bullet(
                time=play_at,
                pos=position,
                color=int(color, 16),
                message=content
            )
        return result

    async def get_video_info(self, video_id: str):
        """获取视频的信息"""
        no_result = ("", 0, "")  # 视频标题, 时长, 对应的数字id
        api = "http://union.video.qq.com/fcgi-bin/data"
        params = {
            "tid": "98",
            "appid": "10001005",
            "appkey": "0d1a9ddd94de871b",
            "idlist": video_id,
            "otype": "json"
        }
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return no_result
        text = await resp.text()
        data = json.loads(text.lstrip("QZOutputJson=").rstrip(";"))
        data = data["results"][0]["fields"]
        title = data["title"]  # 视频标题 斗罗大陆_051
        duration = int(data["duration"])  # 视频时长 1256
        # 获取视频对应的 targetid
        api = "http://bullet.video.qq.com/fcgi-bin/target/regist"
        params = {"otype": "json", "vid": video_id}
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return no_result
        text = await resp.text()
        data = json.loads(text.lstrip("QZOutputJson=").rstrip(";"))
        target_id = data["targetid"]  # "3881562420"
        return title, duration, target_id
