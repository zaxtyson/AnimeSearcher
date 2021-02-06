import asyncio
from time import perf_counter
from typing import Callable, Coroutine, Type

from api.core.anime import *
from api.core.danmaku import *
from api.core.loader import ModuleLoader
from api.utils.logger import logger


class Scheduler:
    """
    调度器, 负责调度引擎搜索、解析资源
    """

    def __init__(self):
        self._loader = ModuleLoader()

    async def search_anime(
            self,
            keyword: str,
            *,
            callback: Callable[[AnimeMeta], None] = None,
            co_callback: Callable[[AnimeMeta], Coroutine] = None
    ) -> None:
        """
        异步搜索动漫
        :param keyword: 关键词
        :param callback: 处理搜索结果的回调函数
        :param co_callback: 处理搜索结果的协程函数
        """
        if not keyword.strip():
            return

        async def run(searcher: AnimeSearcher):
            if callback is not None:
                async for item in searcher._search(keyword):
                    callback(item)  # 每产生一个搜索结果, 通过回调函数处理
                return  # 如果设置了 callback, 忽视 co_callback
            if co_callback is not None:
                async for item in searcher._search(keyword):
                    await co_callback(item)

        searchers = self._loader.get_anime_searchers()
        if not searchers:
            logger.warning(f"No anime searcher enabled")
            return

        logger.info(f"Searching Anime -> [{keyword}], enabled engines: {len(searchers)}")
        start_time = perf_counter()
        await asyncio.wait([run(s) for s in searchers])
        end_time = perf_counter()
        logger.info(f"Searching anime finished in {end_time - start_time:.2f}s")

    async def search_danmaku(
            self,
            keyword: str,
            *,
            callback: Callable[[DanmakuMeta], None] = None,
            co_callback: Callable[[DanmakuMeta], Coroutine] = None
    ) -> None:
        """
        搜索弹幕库
        :param keyword:
        :param callback:
        :param co_callback:
        :return:
        """

        async def run(searcher: DanmakuSearcher):
            if callback is not None:
                async for item in searcher._search(keyword):
                    callback(item)
                return
            if co_callback is not None:
                async for item in searcher._search(keyword):
                    await co_callback(item)

        searchers = self._loader.get_danmaku_searcher()
        if not searchers:
            logger.warning(f"No danmaku searcher enabled")
            return

        logger.info(f"Searching Danmaku -> [{keyword}], enabled engines: {len(searchers)}")
        start_time = perf_counter()
        await asyncio.wait([run(s) for s in searchers])
        end_time = perf_counter()
        logger.info(f"Searching danmaku finished in {end_time - start_time:.2f}s")

    async def parse_anime_detail(self, meta: AnimeMeta) -> AnimeDetail:
        """解析番剧详情页信息"""
        detail_parser = self._loader.get_anime_detail_parser(meta.module)
        if detail_parser is not None:
            return await detail_parser._parse(meta.detail_url)
        return AnimeDetail()

    async def parse_anime_real_url(self, anime: Anime) -> DirectUrl:
        url_parser = self._loader.get_anime_url_parser(anime.module)
        if url_parser is not None:
            return await url_parser._parse(anime.raw_url)
        return DirectUrl()

    def get_anime_proxy_class(self, meta: AnimeMeta) -> Type[AnimeStreamProxy]:
        return self._loader.get_anime_proxy_class(meta.module)

    async def parse_danmaku_detail(self, meta: DanmakuMeta) -> DanmakuDetail:
        detail_parser = self._loader.get_danmaku_detail_parser(meta.module)
        if detail_parser is not None:
            return await detail_parser._parse(meta.play_url)
        return DanmakuDetail()

    async def parse_danmaku_data(self, danmaku: Danmaku) -> DanmakuData:
        data_parser = self._loader.get_danmaku_data_parser(danmaku.module)
        if data_parser is not None:
            start_time = perf_counter()
            data = await data_parser._parse(danmaku.cid)
            end_time = perf_counter()
            logger.info(f"Reading danmaku data finished in {end_time - start_time:.2f}s")
            return data
        return DanmakuData()
