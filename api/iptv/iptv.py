import json
from os.path import dirname

# TODO: 实现 m3u8 视频流代理播放, 寻找更优质的 IPTV 源

__all__ = ["get_sources", "TVSource"]

from typing import List


class TVSource(object):

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def __repr__(self):
        return f"<TV {self.name}>"


def get_sources() -> List[TVSource]:
    """获取 IPTV 源"""
    path = f"{dirname(__file__)}/bupt.edu.json"
    sources = []
    with open(path, encoding="utf-8") as f:
        for item in json.load(f):
            tv = TVSource(item["name"], item["url"])
            sources.append(tv)
        return sources
