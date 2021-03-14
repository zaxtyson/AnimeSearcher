import asyncio
from typing import Optional, AsyncIterable, List, Dict
from typing import TypeVar, Iterable, Coroutine, AsyncIterator, Any
from urllib.parse import urlparse

from aiohttp import ClientSession, ClientResponse, TCPConnector, CookieJar, ClientTimeout
from aiohttp.resolver import AsyncResolver
from lxml import etree

from api.config import Config
from api.utils.logger import logger
from api.utils.useragent import get_random_ua

__all__ = ["HtmlParseHelper"]


class HtmlParseHelper:
    """
    提供网页数据获取、解析、并行处理的工具
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._domain_mapping: Dict[str, str] = Config().get("domain_mapping")
        self._dns_server = []

    def set_dns_server(self) -> List[str]:
        """设置自定义的 DNS 服务器地址"""
        return []

    async def _before_init(self):
        """session 初始化之前的操作"""
        self._dns_server = self.set_dns_server()

    async def init_session(self, session: Optional[ClientSession] = None):
        """
        初始化 ClientSession, 使用 get/post/head 方法之前需要调用一次,
        ClientSession 内部维护了连接池, 因此不建议每一个请求创建一个 session,
        这里默认为每一个类创建一个 persistent session, 或者手动设置一个, 以实现复用,
        在 __init__.py 中初始化 session 会出现 warning, 官方在 aiohttp 4.0 之后将只允许在协程中创建 session,
        See:

            https://github.com/aio-libs/aiohttp/issues/3658
            https://github.com/aio-libs/aiohttp/issues/4932

        :param session: 用于复用的 ClientSession 对象
        """
        if not self.session:
            if session:
                self.session = session
                return

            if self._dns_server:
                logger.debug(f"Use custom DNS Server: {self._dns_server}")
                resolver = AsyncResolver(nameservers=self._dns_server)
                con = TCPConnector(ssl=False, ttl_dns_cache=300, resolver=resolver)
            else:
                con = TCPConnector(ssl=False, ttl_dns_cache=300)

            jar = CookieJar(unsafe=True)
            self.session = ClientSession(connector=con, cookie_jar=jar)

    async def close_session(self):
        """关闭 ClientSession"""
        if self.session:
            await self.session.close()
            self.session = None

    def _url_mapping(self, raw_url: str) -> (str, str):
        """
        URL 域名映射(含端口号), 为那些域名经常被 ban 的网站和 DNS 解析
        非常慢的网站单独设置了 A 记录, 这里将请求中的 URL 替换掉

        :param raw_url: 原始 URL
        :return: (映射后的 URL, 原始 host:port)
        """
        url = urlparse(raw_url)
        netloc = url.netloc  # www.foo.bar:1234
        new_netloc = self._domain_mapping.get(netloc)
        if not new_netloc:
            return raw_url, netloc  # 无需映射
        return raw_url.replace(netloc, new_netloc), netloc

    def set_headers(self, url: str, kwargs: dict) -> str:
        """为请求设置 headers, 使用随机 User-Agent"""
        kwargs.setdefault("timeout", ClientTimeout(total=30, sock_connect=5))  # 连接超时

        if "headers" not in kwargs:  # 没有设置 Headers
            kwargs["headers"] = {"User-Agent": get_random_ua()}
        else:
            keys = [key.lower() for key in kwargs.get("headers")]
            if "user-agent" not in keys:  # 有 Header, 无 User-Agent
                kwargs["headers"]["user-agent"] = get_random_ua()

        new_url, netloc = self._url_mapping(url)
        if new_url != url:  # 需要映射
            kwargs["headers"]["host"] = netloc
        return new_url

    async def head(self, url: str, params: dict = None, **kwargs) -> Optional[ClientResponse]:
        """
        HEAD 方法, 使用随机 User-Agent, 出现异常时返回 None
        """
        try:
            url = self.set_headers(url, kwargs)
            logger.debug(f"HEAD {url} | Params: {params} | Args: {kwargs}")
            resp = await self.session.head(url, params=params, **kwargs)
            logger.debug(f"Code: {resp.status} | Type: {resp.content_type} | Length: {resp.content_length} ({url})")
            return resp
        except Exception as e:
            logger.warning(f"Exception in {self.__class__}: {e}")

    async def get(self, url: str, params: dict = None, **kwargs) -> Optional[ClientResponse]:
        """
        GET 方法, 使用随机 User-Agent, 出现异常时返回 None
        """
        try:
            url = self.set_headers(url, kwargs)
            logger.debug(f"GET {url} | Params: {params} | Args: {kwargs}")
            resp = await self.session.get(url, params=params, **kwargs)
            logger.debug(f"Code: {resp.status} | Type: {resp.content_type} | Length: {resp.content_length} ({url})")
            return resp
        except Exception as e:
            logger.warning(f"Exception in {self.__class__}: {e}")

    async def post(self, url: str, data: dict = None, **kwargs) -> Optional[ClientResponse]:
        """
        POST 方法, 使用随机 User-Agent, 出现异常时返回 None
        """
        try:
            url = self.set_headers(url, kwargs)
            logger.debug(f"POST {url} | Data: {data} | Args: {kwargs}")
            resp = await self.session.post(url, data=data, **kwargs)
            logger.debug(f"Code: {resp.status} | Type: {resp.content_type} | Length: {resp.content_length} ({url})")
            return resp
        except Exception as e:
            logger.warning(f"Exception in {self.__class__}: {e}")

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

    @staticmethod
    def xml_xpath(xml_text: Any, xpath: str) -> Optional[etree.Element]:
        """支持 XPath 方便处理 Xml"""
        if not xml_text:
            return None
        try:
            return etree.XML(xml_text).xpath(xpath)
        except Exception as e:
            logger.exception(e)
            return None

    T = TypeVar("T")  # 提交任务的返回类型
    Task = Coroutine[Any, Any, T]
    IterTask = Coroutine[Any, Any, Iterable[T]]
    AsyncIterTask = Coroutine[Any, Any, AsyncIterable[T]]

    @staticmethod
    async def as_completed(tasks: Iterable[Task]) -> AsyncIterator[T]:
        """
        将多个协程任务加入事件循环并发运行, 返回异步生成器
        每次迭代返回一个已经完成的协程结果, 返回结果不保证顺序

        :param tasks: 协程列表, 协程返回类型为 T
        :return: 异步生成器, 元素类型为 T
        """
        for task in asyncio.as_completed(tasks):
            yield await task

    @staticmethod
    async def as_iter_completed(tasks: Iterable[IterTask]) -> AsyncIterator[T]:
        """
        将多个协程任务加入事件循环并发运行, 返回异步生成器
        每次迭代返回一个已经完成的协程``结果中的元素``, 返回结果不保证顺序

        :param tasks: 协程列表, 协程的返回类型为 Iterable[T]
        :return: 异步生成器, 元素类型为 T
        """
        for task in asyncio.as_completed(tasks):
            for item in await task:
                yield item
