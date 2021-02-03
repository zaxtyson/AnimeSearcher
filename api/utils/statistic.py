import re

from api.core.helper import HtmlParseHelper
from api.utils.logger import logger


class Statistics(HtmlParseHelper):
    # TODO: fix statistics
    def __init__(self):
        super().__init__()
        self._flag_domain = "client.wegather.world"
        self._hm_js_url = "https://hm.baidu.com/hm.js?9f472f02c404ee99590fa4402c1af609"
        self._hm_status_url = "https://hm.baidu.com/hm.gif"

    async def get_hm_js(self, localhost: str, cookies: dict) -> str:
        cookies_str = ""
        for key, value in cookies.items():
            cookies_str += f"{key}={value};"

        stat_headers = {
            "Referer": self._flag_domain,
            "Cookie": cookies_str,  # chrome blocked
        }
        logger.debug(stat_headers)
        resp = await self.get(self._hm_js_url, headers=stat_headers)
        if not resp or resp.status != 200:
            return ""
        localhost = localhost.replace("http://", "")  # ip:host
        text = await resp.text()
        text = text.replace("https", "http") \
            .replace("hm.baidu.com/hm.gif", localhost + "/statistics") \
            .replace("hm.baidu.com", localhost) \
            .replace(f"{self._flag_domain}/statistics", localhost + "/statistics")
        return text

    async def transmit(self, request):
        """百度统计转发"""
        args = dict(request.args)
        ref_page_u = args.get("u", "")  # u = (file|http):///path/to/index.html#/
        ref_page_su = args.get("su", "")
        pat = re.compile(r".+?:///.+?/index\.html#(?P<route>/[^/]+).*")  # route= index|detail|tvlive|result
        args["u"] = pat.sub(rf"{self._flag_domain}\g<route>", ref_page_u)  # 替换 index 文件路径为标记域名 host/route
        args["su"] = pat.sub(rf"{self._flag_domain}\g<route>", ref_page_su)

        cookies_str = ""
        for key, value in request.cookies.items():
            cookies_str += f"{key}={value};"

        stat_headers = {
            "User-Agent": request.headers.get("User-Agent"),
            "Referer": args["u"] or self._flag_domain,
            "Cookie": cookies_str,
        }
        logger.debug(args)
        logger.debug(stat_headers)
        resp = await self.get(self._hm_status_url, params=args, headers=stat_headers)
        return await resp.read()
