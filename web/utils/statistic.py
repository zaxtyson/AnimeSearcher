import re
from typing import Optional

from aiohttp import ClientSession
from quart import Response, Request

from api.core.abc import singleton


@singleton
class Statistics(object):
    """
    用户体验计划, 统计用户在各页面的访问次数和驻留时间
    """

    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._flag_domain = "client.wegather.world"
        self._hm_js = "https://hm.baidu.com/hm.js?9f472f02c404ee99590fa4402c1af609"
        self._hm_status_url = "https://hm.baidu.com/hm.gif"

    async def init_session(self):
        if not self._session:
            self._session = ClientSession()

    async def close_session(self):
        await self._session.close()

    async def _get_hm_js(self, request: Request) -> Response:
        await self.init_session()
        cookies_str = ""
        for key, value in request.cookies.items():
            cookies_str += f"{key}={value};"
        headers = {
            "Referer": self._flag_domain,
            "Cookie": cookies_str
        }
        resp = await self._session.get(self._hm_js, headers=headers)
        if not resp or resp.status != 200:
            return Response("error", mimetype="application/javascript")
        text = await resp.text()
        host = request.host.replace("http://", "")
        text = text.replace("https", "http") \
            .replace("hm.baidu.com/hm.gif", host + "/statistics") \
            .replace("hm.baidu.com", host) \
            .replace(f"{self._flag_domain}/statistics", host + "/statistics")
        return Response(text, mimetype="application/javascript")

    async def get_hm_js(self, request: Request):
        try:
            return await self._get_hm_js(request)
        except Exception as e:
            return Response(f"{e}", mimetype="application/javascript")

    async def _transmit(self, request: Request):
        """百度统计转发"""
        await self.init_session()
        args = dict(request.args)
        host = request.host
        ref_page_u = args.get("u", "")  # u = (file|http):///path/to/index.html#/
        ref_page_su = args.get("su", "")
        pat = re.compile(r".+?:///?.+?/index\.html#(?P<route>/[^/]+).*")  # route= index|detail|iptv|result
        args["u"] = pat.sub(rf"{self._flag_domain}\g<route>", ref_page_u)  # 替换 index 文件路径为域名 host/route
        args["su"] = pat.sub(rf"{self._flag_domain}\g<route>", ref_page_su)

        cookies_str = ""
        for key, value in request.cookies.items():
            cookies_str += f"{key}={value};"

        headers = {
            "User-Agent": request.headers.get("User-Agent"),
            "Referer": args["u"] or host,
            "Cookie": cookies_str,
        }
        resp = await self._session.get(self._hm_status_url, params=args, headers=headers)
        data = await resp.read()
        return Response(data, mimetype="image/gif")

    async def transmit(self, request: Request):
        try:
            return await self._transmit(request)
        except Exception as e:
            return Response(b"", mimetype="image/gif")
