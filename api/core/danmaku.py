from base64 import b16encode, b16decode
from inspect import currentframe
from typing import AsyncIterator, Optional
from typing import List

from api.core.abc import Tokenizable
from api.core.helper import HtmlParseHelper
from api.utils.logger import logger


class Danmaku(object):
    """视频的弹幕库, 包含弹幕的 id 信息, 用于进一步解析出弹幕数据"""

    def __init__(self):
        self.name = ""  # 视频名
        self.cid = ""  # 弹幕 id, 用于解析出弹幕
        self.module = ""

    def __repr__(self):
        return f"<Danmaku {self.name}>"


class DanmakuMeta(Tokenizable):
    """番剧弹幕的元信息, 包含指向播放页的链接, 用于进一步处理"""

    def __init__(self):
        self.title = ""  # 弹幕库名字(番剧名)
        self.num = 0  # 视频数量
        self.play_url = ""  # 播放页的链接或者参数
        self.module = currentframe().f_back.f_globals["__name__"]

    @property
    def token(self) -> str:
        """通过引擎名和详情页信息生成, 可唯一表示本资源位置"""
        name = self.module.split('.')[-1]
        sign = f"{name}|{self.play_url}".encode("utf-8")
        return b16encode(sign).decode("utf-8").lower()

    @classmethod
    def build_from(cls, token: str) -> "DanmakuMeta":
        name, play_url = b16decode(token.upper()).decode("utf-8").split("|")
        meta = DanmakuMeta()
        meta.module = "api.danmaku." + name
        meta.play_url = play_url
        return meta

    def __repr__(self):
        return f"<DanmakuMeta {self.title}[{self.num}]>"


class DanmakuDetail(object):
    """一部番剧所有视频的 Danmaku 集合"""

    def __init__(self):
        self.title = ""  # 弹幕库名字(番剧名)
        self.num = 0  # 视频数量
        self.module = currentframe().f_back.f_globals["__name__"]
        self._dmk_list: List[Danmaku] = []  # 弹幕对象列表

    def append(self, danmaku: Danmaku):
        danmaku.module = self.module
        self._dmk_list.append(danmaku)
        self.num += 1

    def is_empty(self) -> bool:
        return not self._dmk_list

    def get_danmaku(self, index: int) -> Optional[Danmaku]:
        try:
            return self._dmk_list[index]
        except IndexError:
            logger.error(f"IndexError, danmaku index: {index}")
            return None

    def __iter__(self):
        return iter(self._dmk_list)

    def __repr__(self):
        return f"<DanmakuDetail {self.title}[{self.num}]>"


class DanmakuData(object):
    """
    一集视频的弹幕内容
    按照 Dplayer v1.26.0 格式设计
    弹幕格式为: [time, pos, color, user, message]
    距离视频开头的秒数(float), 位置参数(0右边, 1上边, 2底部), 颜色码 10 进制, 用户名, 弹幕内容
    """

    def __init__(self):
        self.num = 0  # 弹幕条数
        self.data = []

    def append_bullet(self, time: float, pos: int, color: int, message: str):
        """
        添加一条弹幕
        :param time: 此条弹幕出现的时间点(秒)
        :param pos: 弹幕出现的位置(0右边, 1上边, 2底部)
        :param color: 弹幕颜色码(10进制表示)
        :param message: 弹幕内容
        """
        self.data.append([time, pos, color, "", message])
        self.num += 1

    def append(self, bullet: List):
        """添加一条弹幕"""
        self.data.append(bullet)
        self.num += 1

    def extend(self, other):
        """合并另一个弹幕数据"""
        for bullet in other:
            self.data.append(bullet)
        self.num += other.num

    def is_empty(self):
        return self.num == 0

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return f"<DanmakuData [{self.num}]>"


class DanmakuSearcher(HtmlParseHelper):
    """
    弹幕库引擎基类, 用户自定义的引擎应该继承它
    """

    async def search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        """搜索相关番剧, 返回指向番剧详情页的信息"""
        yield

    async def _search(self, keyword: str) -> AsyncIterator[DanmakuMeta]:
        """引擎管理器负责调用, 捕获异常"""
        try:
            await self.init_session()
            async for item in self.search(keyword):
                yield item
        except Exception as e:
            logger.exception(e)
            return
        finally:
            await self.close_session()


class DanmakuDetailParser(HtmlParseHelper):

    async def parse(self, play_url: str) -> DanmakuDetail:
        pass

    async def _parse(self, play_url: str) -> DanmakuDetail:
        try:
            await self.init_session()
            return await self.parse(play_url)
        except Exception as e:
            logger.exception(e)
            return DanmakuDetail()
        finally:
            await self.close_session()


class DanmakuDataParser(HtmlParseHelper):

    async def parse(self, cid: str) -> DanmakuData:
        """
        提供弹幕的 id, 解析出弹幕的内容, 并处理成 DPlayer 支持的格式
        """
        pass

    async def _parse(self, cid: str) -> DanmakuData:
        """引擎管理器负责调用, 捕获异常"""
        try:
            await self.init_session()
            return await self.parse(cid)
        except Exception as e:
            logger.exception(e)
            return DanmakuData()
        finally:
            await self.close_session()
