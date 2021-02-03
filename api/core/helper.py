import asyncio
from asyncio.exceptions import TimeoutError
from typing import TypeVar, Optional, Iterable, Coroutine, AsyncIterator, Any

from aiohttp import ClientSession, ClientResponse, TCPConnector, CookieJar, ClientTimeout
from lxml import etree

from api.utils.logger import logger
from api.utils.useragent import get_random_ua

__all__ = ["HtmlParseHelper"]


class HtmlParseHelper:
    """
    提供网页获取和解析的工具
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None

    async def init_session(self, session: Optional[ClientSession] = None):
        """
        初始化 ClientSession, 使用 get/post/head 方法之前需要调用一次

        ClientSession 内部维护了连接池, 因此不建议每一个请求创建一个 session
        这里默认为每一个类创建一个 persistent session, 或者手动设置一个, 以实现复用
        在 __init__ 中初始化 session 会出现 warning, 官方在 aiohttp 4.0 之后将只允许在协程中创建 session

        See: https://github.com/aio-libs/aiohttp/issues/3658
             https://github.com/aio-libs/aiohttp/issues/4932
        """
        if not self.session:
            if session:
                self.session = session
            else:
                con = TCPConnector(ssl=False)
                jar = CookieJar(unsafe=True)
                self.session = ClientSession(connector=con, cookie_jar=jar)

    async def close_session(self):
        """关闭 ClientSession"""
        if self.session:
            await self.session.close()
            self.session = None

    @staticmethod
    def set_headers(kwargs: dict):
        """为请求设置 headers, 使用随机 User-Agent"""
        kwargs.setdefault("timeout", ClientTimeout(sock_connect=5))  # 连接超时 5s

        if "headers" not in kwargs:  # 没有设置 Headers
            kwargs["headers"] = {"User-Agent": get_random_ua()}
            return

        keys = [key.lower() for key in kwargs.get("headers")]
        if "user-agent" not in keys:  # 有 Header, 无 User-Agent
            kwargs["headers"]["user-agent"] = get_random_ua()

    async def head(self, url: str, params: dict = None, **kwargs) -> Optional[ClientResponse]:
        """
        HEAD 方法, 连接超时 5s, 不会自动重定向, 使用随机 User-Agent, 出现异常时返回 None
        """
        try:
            self.set_headers(kwargs)
            logger.debug(f"HEAD {url} | Params: {params} | Args: {kwargs}")
            resp = await self.session.head(url, params=params, **kwargs)
            logger.debug(f"Code: {resp.status} | Type: {resp.content_type} | Length: {resp.content_length} ({url})")
            return resp
        except TimeoutError:
            logger.warning(f"Connection timed out: {url}")
        except Exception as e:
            logger.exception(e)

    async def get(self, url: str, params: dict = None, **kwargs) -> Optional[ClientResponse]:
        """
        GET 方法, 连接超时 5s, 使用随机 User-Agent, 出现异常时返回 None
        """
        try:
            self.set_headers(kwargs)
            logger.debug(f"GET {url} | Params: {params} | Args: {kwargs}")
            resp = await self.session.get(url, params=params, **kwargs)
            logger.debug(f"Code: {resp.status} | Type: {resp.content_type} | Length: {resp.content_length} ({url})")
            return resp
        except TimeoutError:
            logger.warning(f"Connection timed out: {url}")
        except Exception as e:
            logger.exception(e)

    async def post(self, url: str, data: dict = None, **kwargs) -> Optional[ClientResponse]:
        """
        POST 方法, 连接超时 5s, 使用随机 User-Agent, 出现异常时返回 None
        """
        try:
            self.set_headers(kwargs)
            logger.debug(f"POST {url} | Data: {data} | Args: {kwargs}")
            resp = await self.session.post(url, data=data, **kwargs)
            logger.debug(f"Code: {resp.status} | Type: {resp.content_type} | Length: {resp.content_length} ({url})")
            return resp
        except TimeoutError:
            logger.warning(f"Connection timed out: {url}")
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def xpath(html: str, xpath: str) -> Optional[etree.Element]:
        """支持 XPath 方便处理网页"""
        if not html:
            return None
        try:
            return etree.HTML(html).xpath(xpath)
        except Exception as e:
            logger.exception(e)
            return None

    T = TypeVar("T")  # 提交任务的返回类型
    Task = Coroutine[Any, Any, Iterable[T]]

    @staticmethod
    async def submit_tasks(tasks: Iterable[Task]) -> AsyncIterator[T]:
        """
        异步处理多个任务, 返回它们的结果
        :param tasks: 协程列表, 协程的返回类型为 Iterable[T]
        :return: 异步生成器, 元素类型为 T
        """
        for task in asyncio.as_completed(tasks):
            for item in await task:
                yield item
