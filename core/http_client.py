import asyncio
import os
from typing import Optional

from aiohttp import ClientSession, ClientTimeout, AsyncResolver, TCPConnector

from core.config import config
from utils.log import logger
from utils.useragent import get_random_ua

__all__ = ["client"]

if os.name == "nt":
    # https://stackoverflow.com/questions/63653556/raise-notimplementederror-notimplementederror
    logger.info(f"Change eventloop policy: WindowsSelectorEventLoopPolicy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class HttpSession:

    def __init__(self):
        self._session: Optional[ClientSession] = None
        # https://docs.aiohttp.org/en/stable/client_advanced.html#proxy-support
        self._proxy = config.get_http_client_config().get("proxy")
        # https://docs.aiohttp.org/en/stable/client_quickstart.html#timeouts
        self._timeout = ClientTimeout(
            total=config.get_http_client_config().get("timeout").get("total"),
            sock_connect=config.get_http_client_config().get("timeout").get("connect")
        )
        self._dns_server = config.get_http_client_config().get("dns")

    async def init_session(self, loop):
        if self._dns_server:
            logger.info(f"Use custom DNS server: {self._dns_server}")
        if self._proxy:
            logger.info(f"Use proxy: {self._proxy}")

        resolver = AsyncResolver(nameservers=self._dns_server)
        con = TCPConnector(ttl_dns_cache=300, resolver=resolver)
        self._session = ClientSession(loop=loop, connector=con)

    async def close_session(self):
        await self._session.close()

    def _set_request_args(self, kwargs: dict):
        if self._proxy:
            kwargs.setdefault("proxy", self._proxy)
        # set timeout for per connection
        kwargs.setdefault("timeout", self._timeout)
        # ignore ssl error
        kwargs.setdefault("ssl", False)
        # set user-agent if user not specify this filed
        if headers := kwargs.get("headers"):
            headers.setdefault("User-Agent", get_random_ua())
        else:
            kwargs.setdefault("headers", {"User-Agent": get_random_ua()})

    def do(self, method: str, url: str, **kwargs):
        self._set_request_args(kwargs)
        logger.debug(f"{method} {url} {kwargs=}")
        if method == "HEAD":
            return self._session.head(url, **kwargs)
        elif method == "GET":
            return self._session.get(url, **kwargs)
        elif method == "POST":
            return self._session.post(url, **kwargs)
        else:
            logger.error(f"Method not support: {method}")

    def head(self, url: str, **kwargs):
        return self.do("HEAD", url, **kwargs)

    def get(self, url: str, **kwargs):
        return self.do("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.do("POST", url, **kwargs)


# global http session
client = HttpSession()
