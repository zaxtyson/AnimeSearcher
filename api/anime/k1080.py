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
        meta_list = self.xpath(html, "//ul[@id='searchList']/li")
        for item in meta_list:
            meta = AnimeMeta()
            meta.cover_url = item.xpath("div/a/@data-original")[0]
            meta.title = item.xpath("div/a/@title")[0]
            meta.detail_url = item.xpath("div/a[1]/@href")[0]  # /voddetail/414362.html
            desc = item.xpath("div[@class='detail']/p[4]/text()")[0]
            meta.desc = desc if desc else "无简介"
            meta.category = item.xpath("//p[3]/text()")[0]
            ret.append(meta)
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
        detail.cover_url = self.xpath(html, "//img[@class='lazyload']/@src")[0]
        detail.title = self.xpath(html, "//h1[@class='title']/text()")[0]
        detail.desc = self.xpath(html, "//a[@href='#desc']/parent::p/text()")[1]
        detail.category = self.xpath(html, "//p[@class='data'][1]/a/text()")[0]
        playlist_blocks = self.xpath(html, "//div[@class='tab-content myui-panel_bd']/div")  # 播放列表所在的区域
        playlist_names = self.xpath(html, "//a[@data-toggle='tab']/text()")
        for idx, block in enumerate(playlist_blocks):
            if playlist_names[idx] in ["超清备用", "Y播"]:
                continue  # m3u8 图片隐写传输数据流, 太麻烦了, 丢弃
            playlist = AnimePlayList()
            playlist.name = playlist_names[idx]
            for anime_block in block.xpath('ul/li'):
                anime = Anime()
                anime.name = anime_block.xpath("a/text()")[0]
                anime.raw_url = anime_block.xpath("a/@href")[0]
                playlist.append(anime)
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
        if "v.qq.com" in video_url:
            return await self.parse_qq_video(video_url)
        # 需要再重定向一次
        if "app.yiranleng.top" in video_url:
            resp = await self.get(video_url, allow_redirects=True)
            if not resp or resp.status != 200:  # CDN 回源失败返回了 564
                return ""
            return resp.url.human_repr()
        return video_url

    async def parse_qq_video(self, url: str):
        api = f"https://jx.k1080.net/analysis.php?v={url}"
        headers = {"Referer": "https://www.k1080.net/"}
        resp = await self.get(api, headers=headers)
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        url = re.search(r'var url\s*=\s*"(https?://.+?)";', html)
        url = url.group(1) if url else ""
        return url
