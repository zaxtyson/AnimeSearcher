import re
from gzip import decompress

from api.core.anime import *
from api.core.proxy import AnimeProxy


class BDE4(AnimeSearcher):

    async def fetch_html(self, keyword: str, page: int):
        api = f"https://bde4.cc/search/{keyword}/{page}"
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return ""
        return await resp.text()

    def parse_anime_metas(self, keyword: str, html: str):
        ret = []
        meta_list = self.xpath(html, '//div[@class="card"]')
        if not meta_list:
            return ret
        for meta in meta_list:
            title = "".join(meta.xpath('div[@class="content"]/a//text()')[1:])
            if keyword not in title:
                continue  # 无关结果一大堆
            anime = AnimeMeta()
            anime.title = title.replace('《', '').replace('》', '')
            anime.cover_url = meta.xpath("a/img/@src")[0]
            info = meta.xpath('//div[@class="description"]/text()')
            anime.category = info[3].replace("类型:\xa0", "")
            anime.detail_url = meta.xpath('//a[@class="header"]/@href')[0].split(";")[0]
            ret.append(anime)
        return ret

    async def parse_one_page(self, keyword: str, page: int):
        # 网站搜索的关键词匹配功能有 bug, 搜索结果后面会返回各种无关视频
        html = await self.fetch_html(keyword, page)
        return self.parse_anime_metas(keyword, html)

    async def search(self, keyword: str):
        # 只要前两页就行, 剩下的多半是垃圾数据
        tasks = [self.parse_one_page(keyword, p) for p in range(1, 3)]
        async for item in self.as_iter_completed(tasks):
            yield item


class BDE4DetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        url = "https://bde4.cc" + detail_url
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        info = self.xpath(html, '//div[@class="info0"]')[0]
        detail.title = info.xpath("//h2/text()")[0]
        desc = "".join(info.xpath('div[@class="summary"]/text()'))
        detail.desc = desc.replace("\u3000", "").replace("剧情简介：", "").strip()
        detail.cover_url = info.xpath('img/@src')[0]
        playlist = AnimePlayList()
        playlist.name = "在线播放"
        video_blocks = self.xpath(html, '//div[@class="info1"]/a')
        for block in video_blocks:
            video = Anime()
            video.name = block.xpath("text()")[0]
            video.raw_url = block.xpath("@href")[0].split(';')[0]
            playlist.append(video)
        detail.append_playlist(playlist)
        return detail


class BDE4UrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        url = "https://bde4.cc" + raw_url
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        url = re.search(r"(http.+?\.m3u8)", html).group(1)
        url = url.replace(r"\/", "/")
        return url


class BDE4Proxy(AnimeProxy):

    async def get_m3u8_text(self, index_url: str) -> str:
        data = await self.read_data(index_url)
        if not data:
            return ""
        gzip_data = data[3354:]  # 前面是二维码的图片数据
        m3u8_text = decompress(gzip_data).decode("utf-8")
        return m3u8_text

    def fix_chunk_data(self, url: str, chunk: bytes) -> bytes:
        if "bde4.cc" in url:
            return chunk[120:]
        return chunk
