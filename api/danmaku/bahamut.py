from api.core.danmaku import *
from api.utils.tool import convert_to_zh, convert_to_tw


class Bahamut(DanmakuSearcher):
    """台湾动漫站巴哈姆特, 返回结果会转换为简体中文"""

    async def search(self, keyword: str):
        api = "http://ani.gamer.com.tw/search.php"
        keyword = convert_to_tw(keyword)  # 使用繁体搜索, 否则没什么结果
        resp = await self.get(api, params={"kw": keyword})
        if not resp or resp.status != 200:
            return

        html = await resp.text()
        anime_list = self.xpath(html, '//a[contains(@href, "animeRef")]')
        for anime in anime_list:
            meta = DanmakuMeta()
            meta.title = convert_to_zh(anime.xpath('div[@class="theme-info-block"]/p/text()')[0])  # 转简体
            meta.play_url = anime.xpath('@href')[0]  # /animeRef.php?sn=111487
            num_str = anime.xpath('.//span[@class="theme-number"]/text()')[0]  # 第14集
            meta.num = int(num_str.strip().replace("第", "").replace("集", ""))  # 14
            yield meta


class BahamutDetailParser(DanmakuDetailParser):

    async def parse(self, play_url: str):
        api = "http://ani.gamer.com.tw/animeRef.php"
        sn = play_url.split("=")[-1]  # 111487
        detail = DanmakuDetail()
        resp = await self.get(api, params={"sn": sn}, allow_redirects=True)  # 这里有一次重定向
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        season = self.xpath(html, '//section[@class="season"]//li')
        if season:  # 番剧播放列表存在的话
            for ep in season:
                danmaku = Danmaku()
                danmaku.name = convert_to_zh(ep.xpath("./a/text()")[0])
                sn_str = ep.xpath("./a/@href")[0]  # ?sn=16240
                danmaku.cid = sn_str.split("=")[-1]
                detail.append(danmaku)
            return detail

        # 电影等情况, 只有1集视频
        danmaku = Danmaku()
        name = self.xpath(html, '//div[@class="anime_name"]/h1/text()')[0]
        danmaku.name = convert_to_zh(name)
        this_url = self.xpath(html, '//meta[@property="og:url"]/@content')[0]
        danmaku.cid = this_url.split("=")[-1]
        detail.append(danmaku)
        return detail


class BahamutDanmakuDataParser(DanmakuDataParser):

    async def parse(self, cid: str):
        api = "http://ani.gamer.com.tw/ajax/danmuGet.php"
        result = DanmakuData()
        resp = await self.post(api, data={"sn": cid})
        if not resp or resp.status != 200:
            return result

        data = await resp.json(content_type=None)
        for item in data:
            message = convert_to_zh(item["text"])  # 弹幕繁体转简体
            if "签" in message:  # 一堆签到弹幕, 扔掉~~
                continue

            result.append_bullet(
                time=item["time"],
                pos=item["position"],
                color=int(item["color"][1:], 16),  # 16 进制颜色转 10 进制
                message=message
            )
        return result
