import json
from os.path import dirname
from typing import List

from api.models import Video


class IPTV:
    def __init__(self):
        self._data_file = "sources.json"
        self._sources = None
        self._cache = None

        self._read_data()

    def _read_data(self):
        data = open(f"{dirname(__file__)}/{self._data_file}", encoding="utf-8")
        self._sources = json.load(data)
        data.close()

    def get_tv_list(self) -> List[Video]:
        result = []
        if not self._cache:
            for tv in self._sources:
                video = Video(tv["name"], tv["url"])
                result.append(video)
            self._cache = result
        return self._cache
