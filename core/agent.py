from typing import AsyncIterator, Optional, Type

from core.cache import cache
from core.config import config
from core.engine import AnimeEngine, DanmakuEngine
from core.loader import engine_loader
from core.proxy import VideoProxy
from models.anime import *
from models.danmaku import *
from utils.encode import *
from utils.log import logger

__all__ = ["agent"]


class Agent:

    def __init__(self):
        engines, proxies = engine_loader.pull_anime_engines()
        self._anime_engines = engines
        self._video_proxies = proxies
        self._danmaku_engines = engine_loader.pull_danmaku_engines()
        config.sync_engine_status(e.module for e in [*self._anime_engines, *self._danmaku_engines])

    def _get_anime_engine(self, module: str) -> Optional[AnimeEngine]:
        for engine in self._anime_engines:
            if engine.module == module:
                return engine
        return None

    def _get_video_proxy(self, module: str) -> Optional[Type[VideoProxy]]:
        for proxy in self._video_proxies:
            if proxy.module == module:
                return proxy
        return VideoProxy  # default proxy

    def _get_danmaku_engine(self, module: str) -> Optional[DanmakuEngine]:
        for engine in self._danmaku_engines:
            if engine.module == module:
                return engine
        return None

    @staticmethod
    def _complete_anime_meta(meta: AnimeMeta):
        token = encode_token(meta.module, meta.parse_args)
        meta.cover_url = f"{config.get_base_url()}/v1/proxy/image?url={meta.cover_url}"
        meta.detail_url = f"{config.get_base_url()}/v1/anime/detail/{token}"

    @staticmethod
    def _complete_anime_detail(detail: AnimeDetail, token: str):
        detail.cover_url = f"{config.get_base_url()}/v1/proxy/image?url={detail.cover_url}"
        for route_idx, route in enumerate(detail.routes, 1):
            for ep_idx, video in enumerate(route.videos, 1):
                video.info_url = f"{config.get_base_url()}/v1/anime/info/{token}/{route_idx}/{ep_idx}"
                video.player_url = f"{config.get_base_url()}/v1/anime/player/{token}/{route_idx}/{ep_idx}"

    @staticmethod
    def _complete_video_info(info: VideoInfo, token: str, route_idx: int, ep_idx: int):
        info.proxy_url = f"{config.get_base_url()}/v1/proxy/anime/{token}/{route_idx}/{ep_idx}"

    @staticmethod
    def _complete_danmaku_meta(meta: DanmakuMeta):
        token = encode_token(meta.module, meta.parse_args)
        meta.detail_url = f"{config.get_base_url()}/v1/danmaku/detail/{token}"

    @staticmethod
    def _complete_danmaku_detail(detail: DanmakuDetail, token: str):
        for idx, dmk in enumerate(detail.playlist, 1):
            dmk.data_url = f"{config.get_base_url()}/v1/danmaku/data/{token}/{idx}"

    async def get_anime_metas(self, keyword: str) -> AsyncIterator[AnimeMeta]:
        for engine in self._anime_engines:
            if not config.is_engine_enable(engine.module):
                logger.debug(f"AnimeEngine [{engine.module}] is not enable")
                continue  # ignore the disabled engines
            async for meta in engine.do_search(keyword):
                self._complete_anime_meta(meta)
                yield meta

    async def get_anime_detail(self, token: str) -> Optional[AnimeDetail]:
        # find cache
        if detail := cache.get(token):
            logger.info(f"Use cached anime detail: {detail}")
            return detail

        # do parse
        module, parse_args = decode_token(token)
        engine = self._get_anime_engine(module)
        if not engine:
            logger.error(f"Engine not found: {module}")
            return None

        detail = await engine.do_parse_detail(**parse_args)
        if not detail.routes:
            logger.error(f"Parse anime detail failed, {module=}, {parse_args=}")
            return None

        self._complete_anime_detail(detail, token)
        cache.set(token, detail, config.get_cache_policy_of("anime_detail"))
        return detail

    async def get_video_info(self, token: str, route_idx: int, ep_idx: int) -> Optional[VideoInfo]:
        # find cache
        info_key = f"{token}/{route_idx}/{ep_idx}"
        if info := cache.get(info_key):
            logger.info(f"Use cached video info: {info}")
            return info

        # do parse
        module, _ = decode_token(token)  # `parse_args` of detail page is useless
        engine = self._get_anime_engine(module)
        assert engine is not None

        detail = await self.get_anime_detail(token)
        if not detail:
            return None

        video = detail.get_video(route_idx, ep_idx)
        info = await engine.do_parse_video_info(**video.parse_args)
        if not info:
            return None

        self._complete_video_info(info, token, route_idx, ep_idx)
        cache.set(info_key, info, info.lifetime)
        return info

    async def get_video_proxy(self, token: str, route_idx: int, ep_idx: int) -> Optional[VideoProxy]:
        if info := await self.get_video_info(token, route_idx, ep_idx):
            module, _ = decode_token(token)
            proxy = self._get_video_proxy(module)
            return proxy(info)

    async def get_danmaku_metas(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        for engine in self._danmaku_engines:
            if not config.is_engine_enable(engine.module):
                logger.debug(f"DanmakuEngine [{engine.module}] is not enable")
                continue
            async for meta in engine.do_search(keyword):
                self._complete_danmaku_meta(meta)
                yield meta

    async def get_danmaku_detail(self, token: str) -> Optional[DanmakuDetail]:
        # find cache
        if detail := cache.get(token):
            logger.info(f"Use cached danmaku detail: {detail}")
            return detail

        # do parse
        module, parse_args = decode_token(token)
        engine = self._get_danmaku_engine(module)
        if not engine:
            logger.error(f"Engine not found: {module}")
            return None

        detail = await engine.do_parse_detail(**parse_args)
        if not detail:
            logger.error(f"Parse danmaku detail failed, {module=}, {parse_args=}")
            return None

        self._complete_danmaku_detail(detail, token)
        cache.set(token, detail, config.get_cache_policy_of("danmaku_detail"))
        return detail

    async def get_danmaku_data(self, token: str, idx: int) -> Optional[DanmakuData]:
        # find cache
        data_key = f"{token}/{idx}"
        if data := cache.get(data_key):
            logger.info(f"Use cached danmaku data, contains {data.size()} bullet(s): {data}")
            return data

        # do parse
        module, _ = decode_token(token)
        engine = self._get_danmaku_engine(module)
        assert engine is not None

        detail = await self.get_danmaku_detail(token)
        if not detail:
            return None

        dmk = detail.get_danmaku(idx)
        data = await engine.do_parse_data(**dmk.parse_args)
        if not data:
            return None

        cache.set(data_key, data, config.get_cache_policy_of("danmaku_data"))
        return data


# global agent instance
agent = Agent()
