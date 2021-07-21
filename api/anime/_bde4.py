"""
哔嘀影视新域名: https://www.mp4er.com/
网页端加入了验证码, 考虑到验证码形式容易改变, 故未使用机器学习识别

新版本接口:
GET https://www.mp4er.com/api/v1/search/$(keyword)/1
token: B92506BB0E76A7A4BDC6581...(需计算)

token := encrypt(timestamp, key)
timestamp 为时间戳字符串经过 UTF-8 编码的二进制数组
key 为 { 73, 76, 79, 86, 69, 66, 73, 68, 73, 89, 73, 78, 71, 82, 72, 73 }, 即 "ILOVEBIDIYINGRHI"

Response 返回的 JSON 中 data 段需用 Base64 解码, 再经过 zlib 解压二进制流,
再经过某个算法解密, 最后得到数据. 该算法来自于 微信 内部使用的加密算法(似乎有所修改):

See: https://github.com/save95/WeChatRE/blob/4b249bce4062e1f338f3e4bbee273b2a88814bf3/src/com/tencent/qqpim/utils/Cryptor.java

反汇编的 Smali 码看吐了, 不管了
"""

import re
from gzip import decompress

from api.core.anime import *
from api.core.proxy import AnimeProxy


class BDE4(AnimeSearcher):

    async def search(self, keyword: str):
        api = f"https://bde4.icu/search/{keyword}/1"  # 只要第一页数据, 垃圾数据太多
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return
        html = await resp.text()
        meta_list = self.xpath(html, '//div[@class="card"]')
        if not meta_list:
            return

        for meta in meta_list:
            content = meta.xpath('div[@class="content"]')[0]
            title = content.xpath('a[@class="header"]/@title')[0]
            info = "|".join(content.xpath('div[@class="description"]//text()'))
            if keyword not in title or "◎" in info:
                continue  # 无关结果或者无法播放的老旧资源
            anime = AnimeMeta()
            anime.title = title
            cat_str = re.search(r'类型:\s?(.+?)\|', info)
            cat_str = cat_str.group(1) if cat_str else ""
            anime.category = cat_str.replace("\xa0", "").replace(" / ", "/")
            anime.cover_url = meta.xpath("a/img/@src")[0]
            anime.detail_url = meta.xpath('a[@class="image"]/@href')[0].split(";")[0]
            yield anime


class BDE4DetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        url = "https://bde4.icu" + detail_url
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return detail

        html = await resp.text()
        info = self.xpath(html, '//div[@class="info0"]')[0]
        title = info.xpath("//h2/text()")[0]
        title_ = re.search(r'《(.+?)》', title)
        detail.title = title_.group(1) if title_ else title
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
        url = "https://bde4.icu" + raw_url
        resp = await self.get(url)
        if not resp or resp.status != 200:
            return ""
        html = await resp.text()
        m3u8_url = re.search(r"(http.+?\.m3u8)", html)
        if m3u8_url:
            return m3u8_url.group(1).replace(r"\/", "/")
        # 没有 m3u8 视频, 还需要跳转一次
        token = re.search(r'ptoken\s?=\s?"(\w+?)"', html)
        if not token:
            return ""  # 没搞头
        token = token.group(1)
        next_url = f"https://bde4.icu/god/{token}"
        resp = await self.get(next_url, allow_redirects=True)
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        url = data.get("url", "")
        if "?rkey=" in url:
            # 该链接访问后立刻失效, url会发生细微变化(rkey几个大小变化)
            # H.265 编码的视频, 可能网页端无法播放
            return AnimeInfo(url=url, volatile=True)
        return AnimeInfo(url=url)


class BDE4Proxy(AnimeProxy):

    def enforce_proxy(self, url: str) -> bool:
        if url.endswith(".m3u8"):
            return True  # 正常访问行不通, 强制代理
        return False

    async def get_m3u8_text(self, index_url: str) -> str:
        data = await self.read_data(index_url)
        if not data:
            return ""
        gzip_data = data[3354:]  # 前面是二维码的图片数据
        m3u8_text = decompress(gzip_data).decode("utf-8")
        return m3u8_text

    def fix_chunk_data(self, url: str, chunk: bytes) -> bytes:
        if "bde4" in url:
            return chunk[120:]
        return chunk
