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

    def _load_remote_mods(self, pack_name: str) -> List[ModuleType]:
        mods = []
        try:
            logger.info(f"Loading the package [{pack_name}] from {self.repo_url}")
            pack = httpimport.load(pack_name, self.repo_url)
            # `__all__` defined in `__init__.py`
            if not hasattr(pack, "__all__"):
                logger.error(f"Attribute '__all__' is not defined in package [{pack_name}]")
                return mods
            for mod_name in pack.__all__:
                mod = httpimport.load(mod_name, self.repo_url + "/" + pack_name)
                mods.append(mod)
        except ImportError as e:
            logger.error(e)
        logger.info(f"Loaded {len(mods)} module(s) from [{pack_name}]: {mods}")
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
                    setattr(cls, "module", "anime." + cls.__module__)
                    engines.append(cls())  # create an instance of engine
                if issubclass(cls, VideoProxy) and cls != VideoProxy:
                    setattr(cls, "module", "anime." + cls.__module__)
                    proxies.append(cls)
        if engines:
            engines = sorted(engines, key=lambda e: e.quality, reverse=True)  # sort by quality
            logger.info(f"Create {len(engines)} instance(s) of anime engine: {engines}")
        if proxies:
            logger.info(f"Create {len(proxies)} instance(s) of anime proxy: {proxies}")
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
                    setattr(cls, "module", "danmaku." + cls.__module__)
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
