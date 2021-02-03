from typing import Iterator, Dict

from api.core.helper import HtmlParseHelper
from api.core.models import DanmakuMeta, DanmakuCollection
from api.utils.logger import logger


class DanmakuEngine(HtmlParseHelper):
    """
    弹幕库引擎基类, 用户自定义的引擎应该继承它
    """

    async def search(self, keyword: str) -> Iterator[DanmakuMeta]:
        """搜索相关番剧, 返回指向番剧详情页的信息"""
        pass

    async def get_detail(self, play_page_url: str) -> DanmakuCollection:
        """处理一部番剧的播放页面, 解析所有视频的弹幕 id 信息"""
        pass

    async def get_danmaku(self, cid: str) -> Dict:
        """提供弹幕的 id, 解析出弹幕的内容, 并处理成 DPlayer 支持的格式"""
        pass

    async def _search(self, keyword: str) -> Iterator[DanmakuMeta]:
        """引擎管理器负责调用, 捕获异常"""
        try:
            yield self.search(keyword)
        except Exception as e:
            logger.exception(e)
            return

    async def _get_detail(self, play_page_url: str) -> DanmakuCollection:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return await self.get_detail(play_page_url)
        except Exception as e:
            logger.exception(e)
            return DanmakuCollection()

    async def _get_danmaku(self, cid: str) -> Dict:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return await self.get_danmaku(cid)
        except Exception as e:
            logger.exception(e)
            return {}
