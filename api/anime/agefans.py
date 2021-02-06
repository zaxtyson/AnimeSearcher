import time
from random import random

from yarl import URL

from api.core.anime import *
from api.utils.logger import logger


class AgeFans(AnimeSearcher):

    async def fetch_html(self, keyword: str, page: int) -> str:
        """获取网页 HTML 内容"""
        api = "https://www.agefans.net/search"
        resp = await self.get(api, params={'query': keyword, 'page': page})
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        if "0纪录" in html:
            return ""
        return html

    def parse_last_page_index(self, html: str) -> int:
        """提取尾页编号"""
        max_page = self.xpath(html, '//a[text()="尾页"]/@href')
        if not max_page:
            return 1
        max_page = int(max_page[0].split('=')[-1]) if "page=" in max_page[0] else 1  # 尾页编号
        return max_page

    def parse_anime_metas(self, html: str):
        """处理一页的所有番剧摘要信息"""
        results = []
        anime_meta_list = self.xpath(html, '//div[@class="cell blockdiff2"] | //div[@class="cell blockdiff"]')
        if not anime_meta_list:
            return results
        for meta in anime_meta_list:
            anime = AnimeMeta()
            anime.title = meta.xpath('.//a[@class="cell_imform_name"]/text()')[0]
            anime.cover_url = "https:" + meta.xpath('.//a[@class="cell_poster"]/img/@src')[0]
            anime.category = meta.xpath('//div[@class="cell_imform_kv"][7]/span[2]/text()')[0]
            anime.detail_url = meta.xpath("a/@href")[0]  # "/detail/20170172"
            results.append(anime)
        return results

    async def parse_one_page(self, keyword: str, page: int):
        html = await self.fetch_html(keyword, page)
        return self.parse_anime_metas(html)

    async def search(self, keyword: str):
        html = await self.fetch_html(keyword, 1)
        for item in self.parse_anime_metas(html):
            yield item

        pages = self.parse_last_page_index(html)
        if pages > 1:
            tasks = [self.parse_one_page(keyword, p) for p in range(2, pages + 1)]
            async for item in self.as_iter_completed(tasks):
                yield item


class AgeFansDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = "https://www.agefans.net" + detail_url
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return detail

        body = self.xpath(await resp.text(), '//div[@id="container"]')[0]  # 详细信息所在的区域
        detail.title = body.xpath(".//h4/text()")[0]
        detail.cover_url = "https:" + body.xpath('.//img[@class="poster"]/@src')[0]
        desc = body.xpath('.//div[@class="detail_imform_desc_pre"]//text()')
        detail.desc = "".join(desc).replace("\r\n", "").strip()
        detail.category = body.xpath('.//li[@class="detail_imform_kv"][9]/span[2]/text()')[0]
        play_list_blocks = body.xpath('.//div[@class="movurl"]')  # 播放列表所在的区域, 可能有多个播放列表
        idx = 1  # 播放列表编号
        for block in play_list_blocks:
            playlist = AnimePlayList()
            playlist.name = "播放列表 " + str(idx)
            for video_block in block.xpath('.//li'):
                anime = Anime()
                anime.name = video_block.xpath("a/@title")[0]
                anime.raw_url = video_block.xpath("a/@href")[0]  # /play/20170172?playid=1_1
                playlist.append(anime)
            if not playlist.is_empty():
                detail.append_playlist(playlist)
                idx += 1
        return detail


class AgeFansUrlParser(AnimeUrlParser):

    def set_cookie(self):
        # 计算 k2 的值, 算法需解析以下 js, 混淆方式 sojson.v5
        # https://cdn.jinfu.love/age/static/js/s_runtimelib2.js?ver=202010240154   __getplay_pck()
        domain = URL("https://www.agefans.net")
        t1 = self.session.cookie_jar.filter_cookies(domain).get("t1").value
        logger.debug(f"Get cookie t1={t1}")
        t = (int(t1) // 1000) >> 5
        k2 = (t * (t % 4096) * 3 + 83215) * (t % 4096) + t
        k2 = str(k2)
        # 计算 t2 的值, 生成一个后三位包含 k2 最后一位的数时间戳
        # https://cdn.jinfu.love/age/static/js/s_dett.js?ver=202010240154   __getplay_pck2()
        k2_last = k2[-1]
        t2 = ""
        while True:
            now = str(int(time.time() * 1000))
            last_3w = now[-3:]
            if 0 <= last_3w.find(k2_last):
                t2 = now
                break
        logger.debug(f"Set cookies, k2={k2}, t2={t2}")
        self.session.cookie_jar.update_cookies({"k2": k2, "t2": t2})

    async def parse(self, raw_url: str) -> str:
        domain = "https://www.agefans.net"
        play_page_url = domain + raw_url
        play_api = domain + "/_getplay"
        aid = play_page_url.split("?")[0].split("/")[-1]
        playindex, epindex = play_page_url.split("=")[-1].split("_")
        params = {"aid": aid, "playindex": playindex, "epindex": epindex, "r": random()}
        headers = {"Referer": domain}
        await self.head(play_page_url, headers=headers)  # 接受服务器设置的 cookie, 不需要 body, 加快速度
        self.set_cookie()  # 否则返回的数据与视频对不上
        resp = await self.get(play_api, params=params, headers=headers)
        if not resp or resp.status != 200:
            return ""
        while "err:timeout" in await resp.text():
            logger.debug("Response : err:timeout, retry...")
            self.set_cookie()
            resp = await self.get(play_api, params=params, headers=headers)

        data = await resp.json(content_type=None)
        if not data:
            logger.info("> " + await resp.text())
        real_url = data["purlf"] + data["vurl"]
        real_url = real_url.split("?")[-1].replace("url=", "")
        if real_url.startswith("//"):
            real_url = "http:" + real_url
        return real_url
