from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib import import_module
from inspect import getmembers
from inspect import isclass
from typing import List

import requests

from api.base import BaseEngine
from api.base import VideoHandler
from api.config import GLOBAL_CONFIG
from api.logger import logger
from api.models import AnimeMetaInfo, AnimeDetailInfo, Video


class EngineManager(object):
    """引擎管理类, 负责调用引擎搜索视频、获取视频详情页、调用 Handler 处理视频"""

    def __init__(self):
        self._engines = {}
        self._handlers = {"VideoHandler": VideoHandler}  # 默认的 Handler

        for engine in GLOBAL_CONFIG.get_enabled_engines():
            self._load_engine(engine)

    def _load_engine(self, engine: str):
        """按照配置加载引擎和对应的 VideoHandler
        @engine: api.engine.xxx
        """
        em = import_module(engine)
        for cls_name, cls in getmembers(em, isclass):
            if issubclass(cls, VideoHandler):
                self._handlers.setdefault(cls_name, cls)  # 'xxHandler': <class 'api.engines.xx.xxHandler'>
                logger.info(f"Loading VideoHandler {cls_name}: {cls}")
            if issubclass(cls, BaseEngine) and cls != BaseEngine:
                self._engines.setdefault(cls.__module__, cls)  # 'api.engines.xx': <class 'api.engines.xx.xxEngine'>
                logger.info(f"Loading engine {cls.__module__}.{cls.__name__}: {cls}")

    def search(self, keyword: str) -> List[AnimeMetaInfo]:
        """搜索番剧, 返回番剧的摘要信息(不包括视频列表)"""
        if not keyword:
            return []
        result = []
        executor = ThreadPoolExecutor()
        engine_list = [e() for e in self._engines.values()]
        logger.info(f"Searching for {keyword}...")
        all_task = [executor.submit(obj._search, keyword) for obj in engine_list]
        for task in as_completed(all_task):
            result += task.result()
        logger.info(f"Searching result in total: {len(result)}")
        return result

    def get_detail(self, meta: AnimeMetaInfo) -> AnimeDetailInfo:
        """解析一部番剧的详情页，返回包含视频列表的详细信息"""
        if not meta:
            logger.error(f"Invalid request")
            return AnimeDetailInfo()
        target_engine = self._engines.get(meta.engine)
        if not target_engine:
            logger.error(f"Engine not found: {meta.engine}")
            return AnimeDetailInfo()
        return target_engine()._get_detail(meta.detail_page_url)

    def get_video_url(self, video: Video) -> str:
        """解析视频真实 url"""
        if not video:
            logger.error(f"Invalid request")
            return "error"
        target_handler = self._handlers.get(video.handler)
        if not target_handler:
            logger.error(f"VideoHandler not found: {video.handler}")
            return "error"
        target_handler = target_handler(video)
        return target_handler.get_real_url()

    def make_response_for(self, video: Video) -> requests.Response:
        """获取视频对应的 handler 对象, 用于代理访问数据并返回响应给客户端"""
        if not video:
            logger.error(f"Invalid request")
            return requests.Response()
        target_handler = self._handlers.get(video.handler)
        if not target_handler:
            logger.error(f"VideoHandler not found: {video.handler}")
            return requests.Response()
        return target_handler(video).make_response()

    def enabled_engine(self, engine: str) -> bool:
        """启用某个引擎"""
        if engine in self._engines:
            return True  # 已经启用了
        self._load_engine(engine)  # 动态加载引擎
        return GLOBAL_CONFIG.enabled_engine(engine)  # 更新配置文件

    def disable_engine(self, engine: str) -> bool:
        """禁用某个引擎, engine: api.engine.xxx"""
        if engine not in self._engines:
            return True  # 本来就没启用
        self._engines.pop(engine)
        return GLOBAL_CONFIG.disable_engine(engine)
