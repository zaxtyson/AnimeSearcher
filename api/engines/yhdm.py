from api.base import AnimeEngine, VideoHandler, HtmlParseHelper
from api.logger import logger
from api.models import AnimeMetaInfo, AnimeDetailInfo, VideoCollection, Video


class YingHuaDongMan(AnimeEngine):
    def __init__(self):
        self._base_url = "http://www.yhdm.tv"
        self._search_api = self._base_url + "/search"

    def search(self, keyword: str):
        result = []
        ret, html = self.parse_one_page(keyword, 1)
        result += ret  # 保存第一页搜索结果
        max_page = self.xpath(html, '//div[@class="pages"]/a[@id="lastn"]/text()')  # ['12'] 或 []
        if not max_page:
            return result  # 搜索结果只有一页

        # 多线程处理剩下的页面
        max_page = int(max_page[0])
        all_task = [(self.parse_one_page, (keyword, i), {}) for i in range(2, max_page + 1)]
        for ret, _ in self.submit_tasks(all_task):
            result += ret
        return result

    def parse_one_page(self, keyword: str, page: int):
        logger.info(f"Searching for {keyword}, page {page}")
        resp = self.get(self._search_api + "/" + keyword, params={"page": page})
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {self._search_api}")
            return [], ""

        anime_meta_list = self.xpath(resp.text, '//div[@class="lpic"]//li')
        ret = []
        for meta in anime_meta_list:
            anime = AnimeMetaInfo()
            anime.title = " ".join(meta.xpath(".//h2/a/@title"))
            anime.cover_url = meta.xpath("./a/img/@src")[0]
            anime.category = " ".join(meta.xpath("./span[2]/a/text()"))
            anime.desc = meta.xpath("./p/text()")[0]
            anime.detail_page_url = meta.xpath("./a/@href")[0]  # /show/5031.html
            ret.append(anime)
        return ret, resp.text

    def get_detail(self, detail_page_url: str):
        url = self._base_url + detail_page_url
        logger.info(f"Parsing detail page: {url}")
        resp = self.get(url)
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {url}")
            return AnimeDetailInfo()

        body = self.xpath(resp.text, '//div[@class="fire l"]')[0]
        anime_detail = AnimeDetailInfo()
        anime_detail.title = body.xpath("./div/h1/text()")[0]
        anime_detail.category = " ".join(body.xpath('.//div[@class="sinfo"]/span[3]/a/text()'))
        anime_detail.desc = body.xpath('.//div[@class="info"]/text()')[0].replace("\r\n", "").strip()
        anime_detail.cover_url = body.xpath('.//div[@class="thumb l"]/img/@src')[0]
        vc = VideoCollection()
        vc.name = "播放列表"
        video_blocks = body.xpath('.//div[@class="movurl"]//li')
        for block in video_blocks:
            video = Video()
            video.name = block.xpath("./a/text()")[0]
            video.raw_url = block.xpath("./a/@href")[0]  # '/v/3849-162.html'
            video.handler = "YHDMVideoHandler"
            vc.append(video)
        anime_detail.append(vc)
        return anime_detail


class YHDMVideoHandler(VideoHandler, HtmlParseHelper):

    def get_real_url(self) -> str:
        url = "http://www.yhdm.tv/" + self.get_raw_url()
        logger.info(f"Parsing real url for {url}")
        resp = self.get(url)
        if resp.status_code != 200:
            logger.warning(f"Response error: {resp.status_code} {url}")
            return "error"
        video_url = self.xpath(resp.text, '//div[@id="playbox"]/@data-vid')[0]  # "url$format"
        video_url = video_url.split("$")[0]  # "http://quan.qq.com/video/1098_ae4be38407bf9d8227748e145a8f97a5"
        if not video_url.startswith("http"):  # 偶尔出现一些无效视频
            logger.warning(f"This video is not valid: {video_url}")
            return "error"

        logger.debug(f"Redirect for {video_url}")
        resp = self.head(video_url, allow_redirects=True)  # 获取直链时会重定向 2 次
        logger.info(f"Video real url: {resp.url}")
        return resp.url  # 重定向之后的视频直链
