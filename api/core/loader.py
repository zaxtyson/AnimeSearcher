from importlib import import_module
from inspect import getmembers
from inspect import isclass
from typing import Dict, Type

from api.config import Config
from api.core.abc import singleton
from api.core.anime import *
from api.core.danmaku import *
from api.utils.logger import logger


@singleton
class ModuleLoader(object):
    """
    模块加载器, 负责动态加载/卸载各个模块
    """

    def __init__(self):
        # Anime
        self._anime_searchers: Dict[str, AnimeSearcher] = {}
        self._anime_detail_parsers: Dict[str, AnimeDetailParser] = {}
        self._anime_url_parsers: Dict[str, AnimeUrlParser] = {}
        self._anime_proxy_cls: Dict[str, Type[AnimeStreamProxy]] = {}
        # Danmaku
        self._danmaku_searchers: Dict[str, DanmakuSearcher] = {}
        self._danmaku_detail_parsers: Dict[str, DanmakuDetailParser] = {}
        self._danmaku_data_parsers: Dict[str, DanmakuDataParser] = {}

        for module in Config.get_enabled_modules():
            self.load_module(module)

    def load_module(self, module: str):
        """
        :param module: 资源引擎引擎模块名, api.anime.xxx
        """
        py_module = import_module(module)
        for name, cls in getmembers(py_module, isclass):

            if issubclass(cls, AnimeSearcher) and cls != AnimeSearcher \
                    and module not in self._anime_searchers:
                self._anime_searchers[module] = cls()  # 创建 Searcher 对象, 程序执行期间一直使用
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, AnimeDetailParser) and cls != AnimeDetailParser \
                    and module not in self._anime_detail_parsers:
                self._anime_detail_parsers[module] = cls()
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, AnimeUrlParser) and \
                    name not in self._anime_url_parsers:
                self._anime_url_parsers[module] = cls()
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, AnimeStreamProxy) and cls != AnimeStreamProxy \
                    and name not in self._anime_proxy_cls:
                self._anime_proxy_cls[module] = cls  # 只加载 class, 动态创建
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, DanmakuSearcher) and cls != DanmakuSearcher \
                    and name not in self._danmaku_searchers:
                self._danmaku_searchers[module] = cls()
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, DanmakuDetailParser) and cls != DanmakuDetailParser \
                    and module not in self._danmaku_detail_parsers:
                self._danmaku_detail_parsers[module] = cls()
                logger.info(f"Loading {name}: {cls}")

            if issubclass(cls, DanmakuDataParser) and cls != DanmakuDataParser \
                    and module not in self._danmaku_data_parsers:
                self._danmaku_data_parsers[module] = cls()
                logger.info(f"Loading {name}: {cls}")

    def unload_module(self, module: str) -> None:
        """卸载模块名对应的引擎"""
        if module.startswith("api.anime"):
            # 只移除 Searcher, Parser 类驻留继续使用
            self._anime_searchers.pop(module, None)
        if module.startswith("api.danmaku"):
            self._danmaku_searchers.pop(module, None)
        # if module.startswith("api.comic"):
        #     self._comic_engines.pop(module, None)

    def change_module_state(self, module: str, enable: bool) -> bool:
        """动态加载/卸载引擎, 并更新配置文件"""
        if enable:  # 加载引擎
            self.load_module(module)
            return Config.change_module_state(module, True)
        else:  # 卸载引擎
            self.unload_module(module)
            return Config.change_module_state(module, False)

    def get_anime_searchers(self) -> List[AnimeSearcher]:
        return list(self._anime_searchers.values())

    def get_anime_detail_parser(self, module: str) -> Optional[AnimeDetailParser]:
        return self._anime_detail_parsers.get(module)

    def get_anime_url_parser(self, module: str) -> Optional[AnimeUrlParser]:
        return self._anime_url_parsers.get(module)

    def get_anime_proxy(self, module: str) -> Type[AnimeStreamProxy]:
        return self._anime_proxy_cls.get(module) or AnimeStreamProxy

    def get_danmaku_searcher(self) -> List[DanmakuSearcher]:
        return list(self._danmaku_searchers.values())

    def get_danmaku_detail_parser(self, module: str) -> Optional[DanmakuDetailParser]:
        return self._danmaku_detail_parsers.get(module)

    def get_danmaku_data_parser(self, module: str) -> Optional[DanmakuDataParser]:
        return self._danmaku_data_parsers.get(module)
