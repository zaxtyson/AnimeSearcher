import importlib
from inspect import getmembers, isclass
from types import ModuleType
from typing import List, Type, Tuple

import httpimport

from core.config import config
from core.engine import AnimeEngine, DanmakuEngine
from core.proxy import VideoProxy
from utils.log import logger

httpimport.INSECURE = True  # MUST be set

__all__ = ["engine_loader"]


class RemoteEngineLoader:
    repo_url = config.get_remote_repo()
    assert repo_url != ""

    def _load_remote_mods(self, pkg_name: str) -> List[ModuleType]:
        mods = []
        try:
            logger.info(f"Loading the package [{pkg_name}] from {self.repo_url}")
            with httpimport.remote_repo(pkg_name, self.repo_url):
                pkg = importlib.import_module(pkg_name)
                for mod in pkg.__all__:
                    m = importlib.import_module(f"{pkg_name}.{mod}")
                    mods.append(m)
                return mods
        except ImportError as e:
            logger.error(e)

        logger.info(f"Loaded {len(mods)} module(s) from [{pkg_name}]: {mods}")
        return mods

    @staticmethod
    def _get_classes_of_mod(mod: ModuleType) -> List[Type]:
        classes = []
        for name, cls in getmembers(mod, isclass):
            classes.append(cls)
        return classes

    def pull_anime_engines(self) -> Tuple[List[AnimeEngine], List[Type[VideoProxy]]]:
        """
        Load the anime engine modules from remote server and create the instance of them

        :return: the instance list of anime engine which are sorted by `quality` filed,
        ATTENTION: engines marked as `deprecated` will be filtered out
        """
        engines = []
        proxies = []
        for mod in self._load_remote_mods("anime"):
            for cls in self._get_classes_of_mod(mod):
                if issubclass(cls, AnimeEngine) and cls != AnimeEngine and not cls.deprecated:
                    setattr(cls, "module", cls.__module__)
                    engines.append(cls())  # create an instance of engine
                if issubclass(cls, VideoProxy) and cls != VideoProxy:
                    setattr(cls, "module", cls.__module__)
                    proxies.append(cls)
        if engines:
            engines = sorted(engines, key=lambda e: e.quality, reverse=True)  # sort by quality
            logger.info(f"Create {len(engines)} instance(s) of anime engine: {engines}")
        if proxies:
            logger.info(f"Found {len(proxies)} type(s) of anime proxy: {proxies}")
        return engines, proxies

    def pull_danmaku_engines(self) -> List[DanmakuEngine]:
        """
        Load the danmaku engine modules from remote server and create the instance of them

        :return: the instance list of anime engine which are sorted by `quality` filed,
        ATTENTION: engines marked as `deprecated` will be filtered out
        """
        engines = []
        for mod in self._load_remote_mods("danmaku"):
            for cls in self._get_classes_of_mod(mod):
                if issubclass(cls, DanmakuEngine) and cls != DanmakuEngine and not cls.deprecated:
                    setattr(cls, "module", cls.__module__)
                    engines.append(cls())
        if engines:
            engines = sorted(engines, key=lambda e: e.quality, reverse=True)
            logger.info(f"Create {len(engines)} instance(s) of danmaku engine: {engines}")
        return engines


# global engine loader instance
engine_loader = RemoteEngineLoader()

if __name__ == '__main__':
    engines, proxies = engine_loader.pull_anime_engines()
    for engine in engines:
        print(engine.info())
    for engine in engine_loader.pull_danmaku_engines():
        print(engine.info())
