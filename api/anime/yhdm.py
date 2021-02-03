from api.core.anime import *
from api.core.models import AnimeMeta, AnimeDetail, PlayList, Video
from api.utils.logger import logger


class SakuraAnime(AnimeSearcher):

    async def fetch_html(self, keyword: str, page: int):
        logger.info(f"Searching for {keyword}, page {page}")
        api = f"http://www.yhdm.io/search/{keyword}"
        resp = await self.get(api, params={"page": page})
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        if "文件不存在" in html:  # 网站日常抛锚
            return ""
        return html

    def parse_last_page_index(self, html: str) -> int:
        max_page = self.xpath(html, '//div[@class="pages"]/a[@id="lastn"]/text()')  # ['12'] 或 []
        if not max_page:
            return 1  # 搜索结果只有一页
        return int(max_page[0])

    def parse_anime_metas(self, html: str):
        meta_list = self.xpath(html, '//div[@class="lpic"]//li')
        ret = []
        for meta in meta_list:
            anime = AnimeMeta()
            anime.title = " ".join(meta.xpath(".//h2/a/@title"))
            anime.cover_url = meta.xpath("./a/img/@src")[0]
            anime.category = " ".join(meta.xpath("./span[2]/a/text()"))
            anime.desc = meta.xpath("./p/text()")[0]
            anime.detail_url = meta.xpath("./a/@href")[0]  # /show/5031.html
            ret.append(anime)
        return ret

    async def parse_one_page(self, keyword: str, page: int):
        html = await self.fetch_html(keyword, page)
        return self.parse_anime_metas(html)

    async def search(self, keyword: str):
        html = await self.fetch_html(keyword, 1)
        if not html:
            return
        for item in self.parse_anime_metas(html):
            yield item

        pages = self.parse_last_page_index(html)
        if pages > 1:
            tasks = [self.parse_one_page(keyword, p) for p in range(2, pages + 1)]
            async for item in self.submit_tasks(tasks):
                yield item


class SakuraDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        url = "http://www.yhdm.io" + detail_url
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        body = self.xpath(html, '//div[@class="fire l"]')[0]
        detail.title = body.xpath("./div/h1/text()")[0]
        detail.category = " ".join(body.xpath('.//div[@class="sinfo"]/span[3]/a/text()'))
        detail.desc = body.xpath('.//div[@class="info"]/text()')[0].replace("\r\n", "").strip()
        detail.cover_url = body.xpath('.//div[@class="thumb l"]/img/@src')[0]
        playlist = PlayList()
        playlist.name = "播放列表"
        video_blocks = body.xpath('.//div[@class="movurl"]//li')
        for block in video_blocks:
            video = Video()
            video.name = block.xpath("./a/text()")[0]
            video.raw_url = block.xpath("./a/@href")[0]  # '/v/3849-162.html'
            video.handler = "SakuraHandler"
            playlist.append(video)
        detail.append(playlist)
        return detail


class SakuraHandler(AnimeHandler):

    async def parse(self, raw_url: str):
        url = "http://www.yhdm.io/" + raw_url
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        video_url = self.xpath(html, '//div[@id="playbox"]/@data-vid')[0]  # "url$format"
        video_url = video_url.split("$")[0]  # "http://quan.qq.com/video/1098_ae4be38407bf9d8227748e145a8f97a5"
        if not video_url.startswith("http"):  # 偶尔出现一些无效视频
            return ""
        # resp = await self.head(video_url, allow_redirects=True)  # 获取直链时会重定向 2 次
        # return resp.url  # 重定向之后的视频直链
        return video_url
