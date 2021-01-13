import re

import requests

from api.utils.logger import logger


class Statistics:

    def __init__(self):
        self._flag_domain = "client.wegather.world"
        self._hm_js_url = "https://hm.baidu.com/hm.js?77d4810f1ecfdcdc46eb18a3ee36bc49"
        self._hm_status_url = "https://hm.baidu.com/hm.gif"

    def get_hm_js(self, localhost: str, ref_page: str, cookies: dict, user_agent: str) -> str:
        pat = re.compile(r"file:///.+?/index\.html(?P<route>.*)")
        if pat.search(ref_page):
            ref_page = pat.sub(rf"{self._flag_domain}\g<route>", ref_page)  # 替换文件路径为标记域名

        cookies_str = ""
        for key, value in cookies.items():
            cookies_str += f"{key}={value};"

        stat_headers = {
            "User-Agent": user_agent,
            "Referer": ref_page or self._flag_domain,
            "Cookie": cookies_str,
        }
        logger.debug(stat_headers)
        resp = requests.get(self._hm_js_url, headers=stat_headers)
        if resp.status_code != 200:
            return ""
        localhost = localhost.replace("http://", "")  # ip:host
        text = resp.text.replace("https", "http") \
            .replace("hm.baidu.com/hm.gif", localhost + "/statistics") \
            .replace("hm.baidu.com", localhost) \
            .replace(f"{self._flag_domain}/statistics", localhost + "/statistics")
        return text

    def transmit(self, request) -> bool:
        """百度统计转发"""
        args = dict(request.args)
        ref_page = args.get("u", "")  # u = file:///path/to/index.html#/route
        pat = re.compile(r"file:///.+?/index\.html#(?P<route>.*)")
        if pat.search(ref_page):
            ref_page = pat.sub(rf"{self._flag_domain}\g<route>", ref_page)  # 替换 index 文件路径为标记域名
            args["u"] = ref_page

        cookies_str = ""
        for key, value in request.cookies.items():
            cookies_str += f"{key}={value};"

        stat_headers = {
            "User-Agent": request.headers.get("User-Agent"),
            "Referer": ref_page or self._flag_domain,
            "Cookie": cookies_str,
        }
        logger.debug(args)
        logger.debug(stat_headers)
        resp = requests.get(self._hm_status_url, params=args, headers=stat_headers)
        return resp.status_code == 200
