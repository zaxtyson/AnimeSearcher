import asyncio
from importlib import import_module
from inspect import getmembers
from inspect import isclass
from time import perf_counter
from typing import Callable, Optional, Coroutine, Dict, Type

from api.config import CONFIG
from api.core.anime import *
from api.core.danmaku import DanmakuEngine
from api.core.models import AnimeMeta, AnimeDetail, Video
from api.utils.logger import logger


class EngineManager:
    """
    引擎管理类, 负责调用引擎搜索视频、弹幕、漫画, 动态加载、卸载引擎模块
    """

    def __init__(self):
        self._anime_engines: Dict[str, AnimeSearcher] = {}
        self._anime_detail_parsers: Dict[str, AnimeDetailParser] = {}
        self._anime_handlers: Dict[str, Type[AnimeHandler]] = {}
        self._danmaku_engines = {}
        self._comic_engines = {}

        for module_name in CONFIG.get_enabled_modules():
            self.load_engine(module_name)

    def _load_anime_engine(self, module: str):
        """
        加载番剧搜索引擎和对应的 DetailParser、UrlParser
        :param module: 资源引擎引擎模块名, api.anime.xxx
        """
        py_module = import_module(module)
        for name, cls in getmembers(py_module, isclass):
            if issubclass(cls, AnimeSearcher) and cls != AnimeSearcher \
                    and module not in self._anime_engines:
                self._anime_engines[module] = cls()  # 创建 Searcher 对象, 程序执行期间一直使用
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, AnimeDetailParser) and cls != AnimeDetailParser \
                    and module not in self._anime_detail_parsers:
                self._anime_detail_parsers[module] = cls()  # 创建 Parser 对象, 程序执行期间一直使用
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, AnimeHandler) and \
                    name not in self._anime_handlers:
                self._anime_handlers[name] = cls  # 只加载 class, 解析一个视频创建一个对象
                logger.info(f"Loading {name}: {cls}")

    def _load_danmaku_engine(self, module: str):
        """
        加载弹幕库引擎
        :param module: 模块名, api.danmaku.xxx
        """
        py_module = import_module(module)
        for _, cls in getmembers(py_module, isclass):
            if issubclass(cls, DanmakuEngine) and cls != DanmakuEngine:
                self._danmaku_engines[module] = cls
                logger.info(f"Loading DanmakuEngine: {cls}")

    def _load_comic_engine(self, module: str):
        """
        加载漫画引擎
        :param module: 模块名, api.comic.xxx
        """
        pass

    def load_engine(self, module: str) -> None:
        """加载模块名对于的引擎"""
        if module.startswith("api.anime"):
            self._load_anime_engine(module)
        if module.startswith("api.danmaku"):
            self._load_danmaku_engine(module)
        if module.startswith("api.comic"):
            self._load_comic_engine(module)

    def unload_engine(self, module: str) -> None:
        """卸载模块名对应的引擎"""
        if module.startswith("api.anime"):
            self._anime_engines.pop(module, None)
        if module.startswith("api.danmaku"):
            self._danmaku_engines.pop(module, None)
        if module.startswith("api.comic"):
            self._comic_engines.pop(module, None)

    def set_engine_status(self, module: str, enable: bool) -> bool:
        """动态加载/卸载引擎, 并更新配置文件"""
        if enable:  # 加载引擎
            self.load_engine(module)
            return CONFIG.set_engine_status(module, True)
        else:  # 卸载引擎
            self.unload_engine(module)
            return CONFIG.set_engine_status(module, False)

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

        async def _run(engine: AnimeSearcher):
            if callback is not None:
                async for item in engine._search(keyword):
                    callback(item)  # 每产生一个搜索结果, 通过回调函数处理
                return  # 如果设置了 callback, 忽视 co_callback

            if co_callback is not None:
                async for item in engine._search(keyword):
                    await co_callback(item)

        logger.info(f"Searching for [{keyword}], enabled engines: {list(self._anime_engines.keys())}")
        start_time = perf_counter()
        await asyncio.wait([
            _run(e) for e in self._anime_engines.values()
        ])
        end_time = perf_counter()
        logger.info(f"Searching tasks finished in {end_time - start_time:.2f}s")

    async def parse_anime_detail(self, meta: AnimeMeta) -> Optional[AnimeDetail]:
        """解析番剧详情页，返回包含播放列表在内的详细信息"""
        detail_parser = self._anime_detail_parsers.get(meta.module)
        if detail_parser is not None:
            return await detail_parser._parse(meta.detail_url)

        # 正常情况用户应该先搜索, 再获取番剧详情信息, 此时引擎应是启用状态
        # 若引擎没有加载, 则临时加载一次引擎完成详情页的解析工作
        logger.info(f"Module not loaded: {meta.module}, it will be loaded temporarily.")
        self.load_engine(meta.module)

        if not detail_parser:
            logger.error(f"Can't find detail parser in module {meta.module}")
            return

        detail = await detail_parser._parse(meta.detail_url)
        logger.info(f"Unloading module: {meta.module}")
        self.unload_engine(meta.module)
        return detail

    def get_anime_handler(self, video: Video) -> Optional[AnimeHandler]:
        """获取视频对应的 Handler 对象"""
        url_parser = self._anime_handlers.get(video.handler)
        if not url_parser:
            logger.error(f"Can't find anime handler: {video.handler}")
            return
        return url_parser(video)

    # def search_danmaku(self, keyword: str) -> Iterator[DanmakuMetaInfo]:
    #     """
    #     搜索番剧, 返回番剧弹幕的元信息
    #     """
    #     if not keyword:
    #         return ()
    #     executor = ThreadPoolExecutor()
    #     all_task = [executor.submit(engine()._search, keyword) for engine in self._danmaku_engine.values()]
    #     for task in as_completed(all_task):
    #         yield from task.result()
    #
    # def get_danmaku_detail(self, meta: DanmakuMetaInfo) -> DanmakuCollection:
    #     """解析一部番剧的详情页，返回包含视频列表的详细信息"""
    #     if not meta:
    #         logger.error(f"Invalid request")
    #         return DanmakuCollection()
    #     target_engine = self._danmaku_engine.get(meta.dm_engine)
    #     if not target_engine:
    #         logger.error(f"Danmaku Engine not found: {meta.dm_engine}")
    #         return DanmakuCollection()
    #     return target_engine()._get_detail(meta.play_page_url)
    #
    # def get_danmaku_data(self, dmk: Danmaku) -> List:
    #     """解析一部番剧的详情页，返回包含视频列表的详细信息"""
    #     if not dmk:
    #         logger.error(f"Invalid request")
    #         return []
    #     target_engine = self._danmaku_engine.get(dmk.dm_engine)
    #     if not target_engine:
    #         logger.error(f"Danmaku Engine not found: {dmk.dm_engine}")
    #         return []
    #     return target_engine()._get_danmaku(dmk.cid)
