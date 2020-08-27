from random import random
from time import sleep

import requests

from api.base import AnimeEngine, VideoHandler, HtmlParseHelper
from api.logger import logger
from api.models import AnimeMetaInfo, AnimeDetailInfo, Video, VideoCollection


class AgeFans(AnimeEngine):
    def __init__(self):
        self._base_url = "https://www.agefans.tv"
        self._search_api = self._base_url + "/search"

    def search(self, keyword: str):
        result = []
        ret, html = self.parse_one_page(keyword, 1)
        result += ret  # 保存第一页搜索结果

        max_page = self.xpath(html, '//a[text()="尾页"]/@href')[0]  # 'javascript:void(0);' 或 /search?query=A&page=38
        max_page = int(max_page.split('=')[-1]) if "page=" in max_page else 1  # 尾页编号 38
        if max_page == 1:
            return result  # 搜索结果只有一页

        # 多线程处理剩下的页面
        all_task = [(self.parse_one_page, (keyword, i), {}) for i in range(2, max_page + 1)]
        for ret, _ in self.submit_tasks(all_task):
            result += ret
        return result

    def parse_one_page(self, keyword: str, page: int):
        """处理一页的所有番剧摘要信息"""
        logger.info(f"Searching for: {keyword}, page: {page}")
        resp = self.get(self._search_api, params={'query': keyword, 'page': page})
        if resp.status_code != 200 or "0纪录" in resp.text:
            logger.info(f"No search result for {keyword}")
            return [], ""

        ret = []
        anime_meta_list = self.xpath(resp.text, '//div[@class="cell blockdiff2"] | //div[@class="cell blockdiff"]')
        for meta in anime_meta_list:
            anime = AnimeMetaInfo()
            anime.title = meta.xpath('.//a[@class="cell_imform_name"]/text()')[0]
            anime.cover_url = "https:" + meta.xpath('.//a[@class="cell_poster"]/img/@src')[0]
            anime.category = meta.xpath('//div[@class="cell_imform_kv"][7]/span[2]/text()')[0]
            anime.detail_page_url = meta.xpath("a/@href")[0]  # "/detail/20170172"
            ret.append(anime)
        return ret, resp.text

    def get_detail(self, detail_page_url: str):
        detail_api = self._base_url + detail_page_url
        resp = self.get(detail_api)
        if resp.status_code != 200:
            return AnimeDetailInfo()

        body = self.xpath(resp.text, '//div[@id="container"]')[0]  # 详细信息所在的区域
        anime_detail = AnimeDetailInfo()
        anime_detail.title = body.xpath(".//h4/text()")[0]
        anime_detail.cover_url = "https:" + body.xpath('.//img[@class="poster"]/@src')[0]
        anime_detail.desc = "".join(body.xpath('.//div[@class="detail_imform_desc_pre"]//text()')).replace("\r\n",
                                                                                                           "").strip()
        anime_detail.category = body.xpath('.//li[@class="detail_imform_kv"][9]/span[2]/text()')[0]
        play_list_blocks = body.xpath('.//div[@class="movurl"]')  # 播放列表所在的区域, 可能有多个播放列表
        for i, block in enumerate(play_list_blocks, 1):
            vc = VideoCollection()
            vc.name = "播放列表 " + str(i)
            for video_block in block.xpath('.//li'):
                video = Video()
                video.name = video_block.xpath("a/@title")[0]
                video.raw_url = video_block.xpath("a/@href")[0]  # /play/20170172?playid=1_1
                video.handler = "AgeFansVideoHandler"  # 绑定视频处理器
                vc.append(video)
            anime_detail.append(vc)
        return anime_detail


class AgeFansVideoHandler(VideoHandler, HtmlParseHelper):

    def get_real_url(self):
        host = "https://www.agefans.tv"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4033.0 Safari/537.36 Edg/81.0.403.1",
            "Referer": host
        }
        play_page_url = host + self.get_raw_url()  # "https://www.agefans.tv/play/20170172?playid=1_1"
        logger.info(f"Parse page: {play_page_url}")
        play_api = host + "/_getplay"  # _getplay?aid=20170172&playindex=1&epindex=66&r=0.28174977677245283"
        aid = play_page_url.split("?")[0].split("/")[-1]
        playindex, epindex = play_page_url.split("=")[-1].split("_")
        params = {"aid": aid, "playindex": playindex, "epindex": epindex, "r": random()}
        logger.info(f"Args: {params}")
        client = requests.Session()
        client.get(play_page_url, headers=headers)  # 接受服务器设置的 cookie, 不需要 body, 加快速度
        logger.debug(client.cookies)

        while True:
            resp = client.get(play_api, params=params, headers=headers, verify=False)
            resp.encoding = "utf-8"
            params = {"aid": aid, "playindex": playindex, "epindex": epindex, "r": random()}  # 更换随机数
            logger.info(f"URL1: {resp.url}")
            if resp.text != "err:timeout":
                logger.debug(f"{resp.status_code}")
                logger.info(f"URL1: {resp.url}")
                try:
                    data = resp.json()
                    logger.debug(data)
                except:
                    sleep(0.5)
                    continue
                if "mp4" in data["playid"]:
                    return "https:" + data["vurl"]
                elif "tieba" in data["playid"]:
                    return data["purlf"] + data["vurl"]
                else:
                    return data["purlf"] + data["vurl"]
                break
        return "no url"
