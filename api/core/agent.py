from typing import Callable, Coroutine

from api.config import Config
from api.core.anime import *
from api.core.cache import CacheDB
from api.core.danmaku import *
from api.core.scheduler import Scheduler
from api.iptv.iptv import TVSource, get_sources
from api.update.bangumi import Bangumi


class Agent:
    """
    代理人, 代理响应路由的请求
    从调度器获取、过滤、缓存数据, 发送给路由
    """

    def __init__(self):
        self._scheduler = Scheduler()
        self._bangumi = Bangumi()
        self._config = Config()
        # Memory Database for cache
        self._anime_db = CacheDB()
        self._danmaku_db = CacheDB()

    def get_global_config(self):
        return self._config.all_configs

    def set_module_status(self, module: str, enable: bool):
        pass

    async def get_anime_timeline(self):
        """获取番组表信息"""
        return await self._bangumi.get_bangumi_updates()

    def get_iptv_sources(self) -> List[TVSource]:
        """获取 IPTV 源列表"""
        return get_sources()

    async def get_anime_metas(
            self,
            keyword: str,
            *,
            callback: Callable[[AnimeMeta], None] = None,
            co_callback: Callable[[AnimeMeta], Coroutine] = None
    ) -> None:
        """搜索番剧, 返回摘要信息, 过滤相似度低的数据"""
        return await self._scheduler.search_anime(keyword, callback=callback, co_callback=co_callback)

    async def get_danmaku_metas(
            self,
            keyword: str,
            *,
            callback: Callable[[DanmakuMeta], None] = None,
            co_callback: Callable[[DanmakuMeta], Coroutine] = None
    ) -> None:
        """搜索弹幕库, 返回摘要信息, 过滤相似度低的数据"""
        # TODO: Implement data filter
        return await self._scheduler.search_danmaku(keyword, callback=callback, co_callback=co_callback)

    async def get_anime_detail(self, token: str) -> Optional[AnimeDetail]:
        """获取番剧详情信息, 如果有缓存, 使用缓存的值"""
        detail: AnimeDetail = self._anime_db.fetch(token)
        if detail is not None:
            logger.info(f"Using cached {detail}")
            return detail
        # 没有缓存, 通过 token 构建 AnimeMeta 对象, 解析一次
        meta = AnimeMeta.build_from(token)
        logger.debug(f"Build AnimeMeta from token: {meta.module} | {meta.detail_url}")
        detail = await self._scheduler.parse_anime_detail(meta)
        if not detail or detail.is_empty():  # 没解析出来或者解析出来是空信息
            logger.error(f"Parse anime detail info failed")
            return None
        self._anime_db.store(detail, token)  # 解析成功, 缓存起来
        return detail

    async def get_anime_real_url(self, token: str, playlist: int, episode: int) -> str:
        """获取资源直链, 如果存在未过期的缓存, 使用缓存的值, 否则重新解析"""
        url_token = f"{token}|{playlist}|{episode}"
        url: DirectUrl = self._anime_db.fetch(url_token)
        if url and url.is_available():  # 存在缓存且未过期
            logger.info(f"Using cached real url: {url}")
            return url.real_url
        # 没有发现缓存或者缓存的直链过期, 解析一次
        detail = await self.get_anime_detail(token)
        if detail is not None:
            anime: Anime = detail.get_anime(int(playlist), int(episode))
            if anime is not None:
                url = await self._scheduler.parse_anime_real_url(anime)
                if url.is_available():
                    self._anime_db.store(url, url_token)
                    return url.real_url
        # 其它各种情况, 解析失败
        return ""

    # TODO: get anime stream
    async def get_anime_stream(self, token: str, playlist: int, episode: int):
        real_url = self.get_anime_real_url(token, playlist, episode)
        if not real_url:
            return

    async def get_danmaku_detail(self, token: str) -> DanmakuDetail:
        """获取弹幕库详情信息, 如果存在缓存, 使用缓存的值"""
        detail: DanmakuDetail = self._danmaku_db.fetch(token)
        if detail is not None:
            logger.info(f"Using cached {detail}")
            return detail
        # 没有缓存, 通过 token 构建 AnimeMeta 对象, 解析一次
        meta = DanmakuMeta.build_from(token)
        logger.debug(f"Build DanmakuMeta from token: {meta.module} | {meta.play_url}")
        detail = await self._scheduler.parse_danmaku_detail(meta)
        if detail.is_empty():  # 没解析出来或者解析出来是空信息
            logger.error(f"Parse anime detail info failed")
            return detail
        self._danmaku_db.store(detail, token)  # 解析成功, 缓存起来
        return detail

    async def get_danmaku_data(self, token: str, episode: int) -> DanmakuData:
        """获取弹幕数据, 如果有缓存, 使用缓存的值"""
        danmaku_token = f"{token}|{episode}"
        data_token = f"{danmaku_token}|data"
        data: DanmakuData = self._danmaku_db.fetch(data_token)
        if data is not None:
            logger.info(f"Using cached danmaku data: {data}")
            return data
        detail: DanmakuDetail = await self.get_danmaku_detail(token)
        if not detail.is_empty():
            danmaku = detail.get_danmaku(int(episode))
            if danmaku is not None:
                data = await self._scheduler.parse_danmaku_data(danmaku)
                if not data.is_empty():  # 如果有数据就缓存起来
                    self._danmaku_db.store(data, data_token)
                return data
        return DanmakuData()
