import traceback
from typing import AsyncIterator, Optional

from models.anime import *
from models.danmaku import *
from utils.log import logger

__all__ = ["AnimeEngine", "DanmakuEngine"]


class BaseEngine:
    name = "BaseEngine"
    version = "2022-06-23"
    quality = 3  # [1, 5]
    maintainers = ["zaxtyson"]
    notes = "The base engines of all custom engines"
    deprecated = False

    # module name will be set automatically
    module = ""

    @classmethod
    def info(cls) -> dict:
        return {
            "name": cls.name,
            "module": cls.module,
            "version": cls.version,
            "quality": cls.quality,
            "maintainers": cls.maintainers,
            "notes": cls.notes,
            "deprecated": cls.deprecated
        }


class AnimeEngine(BaseEngine):
    name = "AnimeEngine"

    async def search(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        """
        Override this method to search anime

        :param keyword: title of the anime to be searched
        :return: asynchronous generator for generating anime meta information
        """
        yield

    async def parse_detail(self, **parse_args) -> AnimeDetail:
        """
        Override this method to parse the detail page of anime

        :param parse_args: the args related to the detail page, e.g., url, id number of page, ...
        :return: AnimeDetail object which contains the information about the anime we interest
        """
        pass

    async def parse_video_link(self, **parse_args) -> str:
        """
        Override this method to parse the direct link of video

        :param parse_args: the args related to the player page of the video
        :return: the direct link of video
        """
        pass

    async def parse_video_info(self, direct_link: str) -> VideoInfo:
        """
        Override this method to parse the video info, e.g., format, byte size, lifetime, ...

        :param direct_link: the direct link of video
        :return: VideoInfo object
        """
        if ".flv" in direct_link:
            return VideoInfo("flv", 3600)
        if ".mp4" in direct_link:
            return VideoInfo("mp4", 3600)
        if ".m3u" in direct_link:
            return VideoInfo("hls", 3600)
        return VideoInfo("unknown", 3600)

    def normalize_meta(self, meta: AnimeMeta):
        if meta.cover_url.startswith("//"):
            meta.cover_url = "http:" + meta.cover_url
        meta.description = meta.description.replace("\r\n", "\n").replace("\t", "").replace("\n\n", "\n")

    def normalize_detail(self, detail: AnimeDetail):
        if detail.cover_url.startswith("//"):
            detail.cover_url = "http:" + detail.cover_url
        detail.description = detail.description.replace("\r\n", "\n").replace("\t", "").replace("\n\n", "\n")

    # called by agent, don't override the following methods
    async def do_search(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        try:
            logger.info(f"AnimeEngine [{self.module}] is searching, {keyword=}")
            async for meta in self.search(keyword):
                meta.module = self.module  # set producer info
                meta.engine_name = self.name
                self.normalize_meta(meta)
                yield meta
        except Exception:
            logger.error(traceback.format_exc())

    async def do_parse_detail(self, **parse_args) -> Optional[AnimeDetail]:
        try:
            logger.info(f"AnimeEngine [{self.module}] is parsing the detail page, {parse_args=}")
            detail = await self.parse_detail(**parse_args)
            detail.engine_name = self.name
            detail.module = self.module
            self.normalize_detail(detail)
            return detail
        except Exception:
            logger.error(traceback.format_exc())

    async def do_parse_video_info(self, **parse_args) -> Optional[VideoInfo]:
        try:
            logger.info(f"AnimeEngine [{self.module}] is detecting the video info, {parse_args=}")
            direct_link = await self.parse_video_link(**parse_args)
            if not direct_link:
                logger.error(f"Parse video direct link failed, module={self.module}, {parse_args=}")
                return None
            info = await self.parse_video_info(direct_link)
            info.raw_url = direct_link  # direct_link is attach to video info
            return info
        except Exception:
            logger.error(traceback.format_exc())


class DanmakuEngine(BaseEngine):
    name = "DanmakuEngine"

    async def search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        """
        Override this method to search danmaku

        :param keyword: title of the anime to be searched
        :return: asynchronous generator for generating danmaku meta information
        """
        yield

    async def parse_detail(self, **parse_args) -> DanmakuDetail:
        """
        Override this method to parse the detail page of danmaku

        :param parse_args: the args related to the detail page, e.g., url, id number of page, ...
        :return: DanmakuDetail object
        """
        pass

    async def parse_data(self, **parse_args) -> DanmakuData:
        """
        Override this method to parse danmaku data
        :param parse_args: the args related to the danmaku page
        :return: DanmakuData object which contains all bullets of a specific episode
        """
        pass

    # called by agent, don't override the following methods
    async def do_search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        try:
            logger.info(f"DanmakuEngine [{self.module}] is searching, {keyword=}")
            async for meta in self.search(keyword):
                meta.module = self.module  # set producer info
                meta.engine_name = self.name
                yield meta
        except Exception as e:
            logger.error(e)

    async def do_parse_detail(self, **parse_args) -> Optional[DanmakuDetail]:
        try:
            logger.info(f"DanmakuEngine [{self.module}] is parsing the detail page, {parse_args=}")
            detail = await self.parse_detail(**parse_args)
            detail.engine_name = self.name
            detail.module = self.module
            return detail
        except Exception as e:
            logger.error(e)

    async def do_parse_data(self, **parse_args) -> DanmakuData:
        try:
            logger.info(f"DanmakuEngine [{self.module}] is parsing the bullets, {parse_args=}")
            return await self.parse_data(**parse_args)
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    base = BaseEngine()
    anime = AnimeEngine()
    print(base.info())
    print(anime.info())
