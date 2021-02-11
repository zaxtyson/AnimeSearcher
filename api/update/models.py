from typing import List


class AnimeUpdateInfo(object):
    """更新的番剧信息"""

    def __init__(self):
        self.title = ""  # 番剧名
        self.cover_url = ""  # 番剧封面
        self.update_time = ""  # 更新时间 %Y-%m-%d %H:%M:%S
        self.update_to = ""  # 更新到第几集


class BangumiOneDay(object):
    """一天更新的番剧信息"""

    def __init__(self):
        self.date = ""  # 这一天的日期 %Y-%m-%d
        self.day_of_week = ""  # 这一天是星期几
        self.is_today = False  # 是今天吗
        self.updates: List[AnimeUpdateInfo] = []  # 这一天更新的番剧列表

    def append(self, anime: AnimeUpdateInfo):
        self.updates.append(anime)

    def __iter__(self):
        return iter(self.updates)
