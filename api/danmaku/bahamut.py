from api.base import DanmakuEngine
from api.logger import logger
from api.models import Danmaku, DanmakuMetaInfo, DanmakuCollection


class DanmukaBahamt(DanmakuEngine):
    """这个网站是台湾的, 响应有点慢, 返回结果会转换为简体中文"""

    def __init__(self):
        self._host = "https://ani.gamer.com.tw"
        self._search_api = self._host + "/search.php"
        self._detail_api = self._host + "/animeRef.php"
        self._dm_api = self._host + "/ajax/danmuGet.php"

    def search(self, keyword: str):
        ret = []
        keyword = self.convert_to_tw(keyword)  # 使用繁体搜索, 否则没什么结果
        logger.info(f"Searching for danmaku: {keyword}")
        resp = self.get(self._search_api, params={"kw": keyword})
        if resp.status_code != 200:
            return ret
        anime_list = self.xpath(resp.text, '//ul[@class="anime_list"]/li')
        for anime in anime_list:
            meta = DanmakuMetaInfo()
            meta.title = self.convert_to_zh(anime.xpath('.//div[@class="info"]/b/text()')[0])  # 转简体
            meta.play_page_url = anime.xpath('.//a[@class="animelook"]/@href')[0]  # /animeRef.php?sn=111487
            num_str = anime.xpath('.//div[@class="info"]/text()')[0]  # 年份：2020/07 共8集
            meta.num = int(num_str[-2:-1])  # 8
            ret.append(meta)
        return ret

    def get_detail(self, play_page_url: str):
        sn = play_page_url.split("=")[-1]  # 111487
        collection = DanmakuCollection()
        resp = self.get(self._detail_api, params={"sn": sn}, allow_redirects=True)  # 这里有一次重定向
        if resp.status_code != 200:
            return collection
        season = self.xpath(resp.text, '//section[@class="season"]//li')
        for ep in season:
            dmk = Danmaku()
            dmk.name = ep.xpath("./a/text()")[0]
            sn_str = ep.xpath("./a/@href")[0]  # ?sn=16240
            dmk.cid = sn_str.split("=")[-1]
            collection.append(dmk)
        return collection

    def get_danmaku(self, cid: str):
        payload = {"sn": cid}
        ret = []
        resp = self.post(self._dm_api, data=payload, timeout=10)
        if resp.status_code != 200:
            return ret
        data = resp.json()
        for item in data:
            ret.append([
                item["time"],  # 弹幕的时间
                item["position"],  # 弹幕位置
                int(item["color"][1:], 16),  # 弹幕颜色 10 进制
                "",
                self.convert_to_zh(item["text"]),  # 弹幕繁体转简体
            ])
        return ret
