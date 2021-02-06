import json
import re
from base64 import b64decode
from urllib.parse import unquote

from api.core.anime import *
from api.utils.logger import logger


class K1080(AnimeSearcher):

    async def search(self, keyword: str):
        html = await self.fetch_html(keyword, 1)
        for item in self.parse_anime_metas(html):
            yield item
        pages = self.parse_last_page_index(html)
        if pages > 1:
            tasks = [self.parse_one_page(keyword, p) for p in range(2, pages + 1)]
            async for item in self.as_iter_completed(tasks):
                yield item

    async def fetch_html(self, keyword: str, page: int):
        url = f"https://www.k1080.net/vodsearch/{keyword}----------{page}---.html"
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        if "请输入验证码" in html:
            logger.error("We are blocked by K1080P, need to enter the verification code.")
            return ""
        return html

    def parse_last_page_index(self, html: str) -> int:
        max_page_url = self.xpath(html, "//a[text()='尾页']/@href")
        if not max_page_url:
            return 1
        # 尾页链接 /vodsearch/xxxxx----------4---.html
        max_page = re.search(r"--(\d+?)--", max_page_url[0]).group(1)
        return int(max_page)

    def parse_anime_metas(self, html: str):
        ret = []
        meta_list = self.xpath(html, "//ul[@class='stui-vodlist__media col-pd clearfix']//li")
        for meta in meta_list:
            anime = AnimeMeta()
            cover_url = meta.xpath("./div[@class='thumb']/a/@data-original")[0]
            if not cover_url.startswith("http"):
                cover_url = "https://www.k1080.net" + cover_url
            anime.cover_url = cover_url
            anime.title = meta.xpath("./div[@class='detail']/h3/a/text()")[0]
            anime.detail_url = meta.xpath("./div[@class='detail']/h3/a/@href")[0]  # /voddetail/414362.html
            desc = meta.xpath("./div[@class='detail']//span[contains(text(),'简介')]/parent::p/text()")
            anime.desc = desc[0] if desc else "无简介"
            anime.category = meta.xpath("./div[@class='detail']//span[contains(text(),'类型')]/parent::p/text()")[0]
            ret.append(anime)
        return ret

    async def parse_one_page(self, keyword: str, page: int):
        html = await self.fetch_html(keyword, page)
        return self.parse_anime_metas(html)


class K1080DetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        domain = "https://www.k1080.net"
        resp = await self.get(domain + detail_url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        detail = self.xpath(html, "//div[@class='stui-pannel-box']")[0]
        cover_url = detail.xpath("div/a/img/@data-original")[0]
        if not cover_url.startswith("http"):
            cover_url = domain + cover_url
        detail.cover_url = cover_url
        detail.title = detail.xpath("div/a/@title")[0]
        detail.desc = detail.xpath(".//span[@class='detail-content']/text()")[0]
        detail.category = detail.xpath(".//span[contains(text(), '类型')]/parent::p/a[1]/text()")[0]
        play_list_blocks = self.xpath(html, "//div[@class='stui-pannel-box b playlist mb']")  # 播放列表所在的区域
        for block in play_list_blocks:
            playlist = AnimePlayList()
            playlist.name = block.xpath("div/div/h3/font/text()")[0].strip()
            for video_block in block.xpath('.//li'):
                video = Anime()
                video.name = video_block.xpath("a/text()")[0]
                video.raw_url = video_block.xpath("a/@href")[0]
                playlist.append(video)
            if not playlist.is_empty():
                detail.append_playlist(playlist)
        return detail


class K1080UrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        domain = "https://www.k1080.net"
        resp = await self.get(domain + raw_url)
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        player_data = re.search(r"player_data=({.+?\})", html).group(1)
        player_data = json.loads(player_data)
        video_url = unquote(b64decode(player_data.get("url")).decode("utf8"))
        if video_url.endswith(".mp4") or video_url.endswith(".m3u8"):
            return video_url
        if video_url.endswith(".html"):
            return ""
        # 需要再重定向一次
        resp = await self.head(video_url, allow_redirects=True)
        return resp.url
