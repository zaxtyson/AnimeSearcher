import json
import re
from base64 import b64decode

import requests
from requests.utils import unquote

from api.core.base import BaseEngine, VideoHandler
from api.core.models import AnimeMetaInfo, AnimeDetailInfo, VideoCollection, Video
from api.utils.logger import logger


class K1080(BaseEngine):

    def __init__(self):
        self._base_url = "https://www.k1080.net"

    def parse_one_page(self, keyword: str, page: int):
        url = f"{self._base_url}/vodsearch/{keyword}----------{page}---.html"
        resp = self.get(url)
        if resp.status_code != 200:
            return [], ""
        if "请输入验证码" in resp.text:
            logger.error("We are blocked by K1080P, need to enter the verification code.")
            return [], ""

        ret = []
        meta_list = self.xpath(resp.text, "//ul[@class='stui-vodlist__media col-pd clearfix']//li")
        for meta in meta_list:
            anime = AnimeMetaInfo()
            cover_url = meta.xpath("./div[@class='thumb']/a/@data-original")[0]
            if not cover_url.startswith("http"):
                cover_url = self._base_url + cover_url
            anime.cover_url = cover_url
            anime.title = meta.xpath("./div[@class='detail']/h3/a/text()")[0]
            anime.detail_page_url = meta.xpath("./div[@class='detail']/h3/a/@href")[0]  # /voddetail/414362.html
            desc = meta.xpath("./div[@class='detail']//span[contains(text(),'简介')]/parent::p/text()")
            anime.desc = desc[0] if desc else "无简介"
            anime.category = meta.xpath("./div[@class='detail']//span[contains(text(),'类型')]/parent::p/text()")[0]
            ret.append(anime)
        return ret, resp.text

    def search(self, keyword: str):
        ret, html = self.parse_one_page(keyword, 1)
        yield from ret
        max_page_url = self.xpath(html, "//a[text()='尾页']/@href")
        if not max_page_url:
            return
        # 尾页链接 /vodsearch/xxxxx----------4---.html
        max_page = re.search(r"--(\d+?)--", max_page_url[0]).group(1)
        max_page = int(max_page)
        if max_page == 1:
            return  # 搜索结果只有一页

        # 多线程处理剩下的页面
        all_task = [(self.parse_one_page, (keyword, i), {}) for i in range(2, max_page + 1)]
        for ret, _ in self.submit_tasks(all_task):
            yield from ret

    def get_detail(self, detail_page_url: str) -> AnimeDetailInfo:
        detail_api = self._base_url + detail_page_url
        resp = self.get(detail_api)
        if resp.status_code != 200:
            return AnimeDetailInfo()

        anime_detail = AnimeDetailInfo()
        detail = self.xpath(resp.text, "//div[@class='stui-pannel-box']")[0]
        cover_url = detail.xpath("div/a/img/@data-original")[0]
        if not cover_url.startswith("http"):
            cover_url = self._base_url + cover_url
        anime_detail.cover_url = cover_url
        anime_detail.title = detail.xpath("div/a/@title")[0]
        anime_detail.desc = detail.xpath(".//span[@class='detail-content']/text()")[0]
        anime_detail.category = detail.xpath(".//span[contains(text(), '类型')]/parent::p/a[1]/text()")[0]

        play_list_blocks = self.xpath(resp.text, "//div[@class='stui-pannel-box b playlist mb']")  # 播放列表所在的区域
        for block in play_list_blocks:
            vc = VideoCollection()
            vc.name = block.xpath("div/div/h3/font/text()")[0].strip()
            for video_block in block.xpath('.//li'):
                video = Video()
                video.name = video_block.xpath("a/text()")[0]
                video.raw_url = self._base_url + video_block.xpath("a/@href")[0]
                video.handler = "K1080VideoHandler"  # 绑定视频处理器
                vc.append(video)
            if vc.num != 0:
                anime_detail.append(vc)
        return anime_detail


class K1080VideoHandler(VideoHandler):

    def get_real_url(self) -> str:
        # detail_page_url: https://www.k1080.net/vodplay/410172-1-12.html
        sessions = requests.Session()
        resp = sessions.get(self.get_raw_url())
        if resp.status_code != 200:
            return ""
        player_data = re.search(r"player_data=({.+?\})", resp.text).group(1)
        player_data = json.loads(player_data)
        video_url = unquote(b64decode(player_data.get("url")).decode("utf8"))
        logger.debug(f"Video URL: {video_url}")
        if video_url.endswith(".mp4") or video_url.endswith(".m3u8"):
            return video_url
        if video_url.endswith(".html"):
            return ""
        # 需要再重定向一次
        resp = sessions.head(video_url, allow_redirects=False)
        if resp.status_code != 302:
            return ""
        return resp.headers.get("location", "")
