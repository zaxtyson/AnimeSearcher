import asyncio
from time import perf_counter
from typing import Callable, Coroutine, Type

from api.core.anime import *
from api.core.danmaku import *
from api.core.loader import ModuleLoader
from api.core.proxy import StreamProxy
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
        if not keyword:
            return

        async def run(searcher: AnimeSearcher):
            logger.info(f"{searcher.__class__.__name__} is searching for [{keyword}]")
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
        """

        async def run(searcher: DanmakuSearcher):
            logger.info(f"{searcher.__class__.__name__} is searching for [{keyword}]")
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
        if not detail_parser:  # 直接访问直链, 且配置文件已关闭模块, 把工具类加载起来完成解析
            self._loader.load_utils_module(meta.module)
            detail_parser = self._loader.get_anime_detail_parser(meta.module)
        logger.info(f"{detail_parser.__class__.__name__} parsing {meta.detail_url}")
        if detail_parser is not None:
            return await detail_parser._parse(meta.detail_url)
        return AnimeDetail()

    async def parse_anime_real_url(self, anime: Anime) -> DirectUrl:
        """解析一集视频的直链"""
        url_parser = self._loader.get_anime_url_parser(anime.module)
        logger.info(f"{url_parser.__class__.__name__} parsing {anime.raw_url}")
        for _ in range(3):  # 3 次解析机会, 再不行就真的不行了
            url = await url_parser._parse(anime.raw_url)
            if url.is_available():
                return url
            logger.warning(f"Parse real url failed, retry...")
        logger.warning(f"Parse real url failed 3 times, maybe this resource is not available")
        return DirectUrl()

    def get_anime_proxy_class(self, meta: AnimeMeta) -> Type[StreamProxy]:
        """获取视频代理器类"""
        return self._loader.get_anime_proxy_class(meta.module)

    async def parse_danmaku_detail(self, meta: DanmakuMeta) -> DanmakuDetail:
        """解析弹幕库详情信息"""
        detail_parser = self._loader.get_danmaku_detail_parser(meta.module)
        if not detail_parser:
            self._loader.load_utils_module(meta.module)
            detail_parser = self._loader.get_danmaku_detail_parser(meta.module)
        logger.info(f"{detail_parser.__class__.__name__} parsing {meta.play_url}")
        if detail_parser is not None:
            return await detail_parser._parse(meta.play_url)
        return DanmakuDetail()

    async def parse_danmaku_data(self, danmaku: Danmaku) -> DanmakuData:
        """解析一集弹幕的数据"""
        data_parser = self._loader.get_danmaku_data_parser(danmaku.module)
        logger.debug(f"{data_parser.__class__.__name__} parsing {danmaku.cid}")
        if data_parser is not None:
            start_time = perf_counter()
            data = await data_parser._parse(danmaku.cid)
            end_time = perf_counter()
            logger.info(f"Reading danmaku data finished in {end_time - start_time:.2f}s")
            return data
        return DanmakuData()

    def change_module_state(self, module: str, enable: bool):
        """设置模块启用状态"""
        return self._loader.change_module_state(module, enable)
