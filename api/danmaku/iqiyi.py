import re
from zlib import decompress

from api.core.danmaku import *


class IQIYI(DanmakuSearcher):

    async def search(self, keyword: str):
        api = "https://search.video.iqiyi.com/o"
        params = {
            "if": "html5",
            "key": keyword,
            "pageNum": 1,
            "pageSize": 100,
            "video_allow_3rd": 0  # 似乎没有用
        }
        resp = await self.get(api, params=params)
        if not resp or resp.status != 200:
            return
        data = await resp.json(content_type=None)
        data = data["data"]
        if "search result is empty" in data:
            return  # 没有结果
        data = data["docinfos"]
        for item in data:
            item = item["albumDocInfo"]
            if item.get("siteId", "") != "iqiyi":
                continue  # 其它平台的
            num = item.get("itemTotalNumber")
            if not num:
                continue  # 没有用的视频
            meta = DanmakuMeta()
            meta.num = int(num)
            meta.title = item["albumTitle"]
            # 这里可以拿到 albumId 值, 但是对于老旧资源, 下一步无法获取详情数据
            meta.play_url = str(item["albumId"]) + '|' + item["albumLink"]
            yield meta


class IQIYIDanmakuDetailParser(DanmakuDetailParser):

    async def parse(self, play_url: str):
        aid, url = play_url.split('|')
        detail = await self.get_detail_with_aid(aid)
        if not detail.is_empty():
            return detail  # 通过参数拿到了数据

        # 对于电影, 无法获取到播放列表的详细情况
        detail = await self.get_movie_detail(aid)
        if not detail.is_empty():
            return detail

        # 老旧资源, aid 无效, 需要去网页提取
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        aid = re.search(r'albumId:\s*"(\d+?)"', html)
        if not aid:
            return detail  # 没搞头
        return await self.get_detail_with_aid(aid.group(1))

    async def get_detail_with_aid(self, aid: str):
        detail = DanmakuDetail()
        api = "https://pub.m.iqiyi.com/h5/main/videoList/album/"
        params = {"albumId": aid, "size": 500, "page": 1}
        resp = await self.get(api, params=params)
        data = await resp.json(content_type=None)
        data = data["data"]
        if not data:
            return detail

        for item in data["videos"]:
            danmaku = Danmaku()
            danmaku.name = item["subTitle"]
            danmaku.cid = f'{item["id"]}|{item["duration"]}'  # id|duration
            detail.append(danmaku)
        return detail

    async def get_movie_detail(self, aid: str):
        detail = DanmakuDetail()
        api = f"https://pcw-api.iqiyi.com/video/video/baseinfo/{aid}"
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        data = data["data"]
        if not data:
            return detail
        danmaku = Danmaku()
        danmaku.name = data["name"]
        danmaku.cid = str(data["albumId"]) + "|" + data["duration"]
        detail.append(danmaku)
        return detail


class IQIYIDanmakuDataParser(DanmakuDataParser):

    async def parse(self, cid: str):
        result = DanmakuData()
        vid, duration = cid.split('|')
        arg = f"{vid[-4:-2]}/{vid[-2:]}/{vid}"
        count = self.duration2sec(duration) // 300 + 1
        tasks = [self.get_5_min_bullets(arg, i) for i in range(1, count + 1)]
        async for ret in self.as_iter_completed(tasks):
            result.append(ret)
        return result

    @staticmethod
    def duration2sec(duration: str):
        # "24:15"  "01:31:46" => seconds
        tm = duration.split(':')
        if len(tm) == 2:
            tm.insert(0, "0")  # 小时为 0
        tm = list(map(int, tm))
        return tm[0] * 3600 + tm[1] * 60 + tm[2]

    async def get_5_min_bullets(self, arg: str, start_at: int):
        result = DanmakuData()
        # 一次拿 5 分钟的弹幕
        api = f"https://cmts.iqiyi.com/bullet/{arg}_300_{start_at}.z"
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return
        data = await resp.read()
        data = decompress(data)
        for item in self.xml_xpath(data, "//bulletInfo"):
            time = float(item.xpath("showTime/text()")[0])
            position = int(item.xpath("position/text()")[0])
            content = item.xpath("content/text()")[0]
            color = int(item.xpath("color/text()")[0], 16)
            result.append_bullet(time=time, pos=position, message=content, color=color)

        return result
