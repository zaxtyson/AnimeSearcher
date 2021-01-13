import time
from typing import List

from zhconv import convert

from api.core.base import HtmlParseHelper
from api.core.models import TimelineAnimeInfo, TimelineOneDay


class Timeline(HtmlParseHelper):
    """新番更新时间表"""

    def __init__(self):
        self._bili_mainland = "https://bangumi.bilibili.com/web_api/timeline_cn"
        self._bili_overseas = "https://bangumi.bilibili.com/web_api/timeline_global"
        self._bimi_update = "https://proxy.app.maoyuncloud.com/app/video/list"

    def get_bilibili_timeline(self, api: str) -> List[TimelineAnimeInfo]:
        """获取哔哩哔哩的番剧更新时间表"""
        result = []  # 结果
        resp = self.get(api)
        if resp.status_code != 200:
            return result
        data = resp.json().get("result") or []

        for item in data:
            for season in item["seasons"]:
                if season["delay"] == 1:  # 本周停更, 不记录
                    continue
                anime = TimelineAnimeInfo()
                anime.title = self.convert_to_zh(season["title"])
                anime.cover = season["cover"]  # 番剧封面, season["square_cover"] 正方形小封面
                anime.update_time = self.time_format(str(season["pub_ts"]))
                anime.update_to = season["pub_index"]
                result.append(anime)
        return result

    def get_bimibimi_timeline(self) -> List[TimelineAnimeInfo]:
        """获取 bimibimi 番剧的更新表"""
        result = []
        params = {"channel": "1", "sort": "addtime", "limit": "0", "page": "1"}
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        resp = self.get(self._bimi_update, params=params, headers=headers)
        if resp.status_code != 200:
            return result
        data = resp.json()["data"]["items"]

        for item in data:
            anime = TimelineAnimeInfo()
            anime.title = item["name"]
            anime.cover = item["pic"]
            anime.update_time = self.time_format(item["updated_at"])
            anime.update_to = item["continu"].replace("更新至", "")
            result.append(anime)
        return result

    def get_all_update_anime(self) -> List[TimelineAnimeInfo]:
        """获取全部更新的番剧信息"""
        result = []

        task_ret = self.submit_tasks([
            (self.get_bilibili_timeline, (self._bili_mainland,), {}),
            (self.get_bilibili_timeline, (self._bili_overseas,), {}),
            (self.get_bimibimi_timeline, (), {})
        ])

        # 信息合并去重
        title_list = []
        for ret in task_ret:
            for anime in ret:
                if anime.title not in title_list:
                    result.append(anime)
                    title_list.append(anime.title)

        return result

    def get_full_timeline(self) -> List[TimelineOneDay]:
        """获取最近一段时间的新番更新时间表"""
        result = []
        update_dict = {}
        for anime in self.get_all_update_anime():
            up_date = anime.update_time.split()[0]  # %Y-%m-%d
            update_dict.setdefault(up_date, [])
            update_dict[up_date].append(anime)

        for up_date, anime_list in update_dict.items():
            one_day = TimelineOneDay()
            one_day.date = up_date
            one_day.day_of_week = time.strftime("%w", time.strptime(up_date, "%Y-%m-%d"))
            one_day.is_today = True if up_date == time.strftime("%Y-%m-%d", time.localtime()) else False
            one_day.updates = anime_list
            result.append(one_day)
        result.sort(key=lambda x: x.date)
        return result

    @staticmethod
    def convert_to_zh(title: str) -> str:
        """繁体转简体"""
        title = title.replace("（僅限台灣地區）", "").replace("（僅限港澳台地區）", "")
        return convert(title, "zh-cn")

    @staticmethod
    def time_format(time_str: str):
        """将时间处理成 %Y-%m-%d %H:%M:%S 的格式"""
        if time_str.isdigit():
            tm_struct = time.localtime(int(time_str))  # 哔哩哔哩
        else:
            tm_struct = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S+08:00")  # Bimibimi
        return time.strftime("%Y-%m-%d %H:%M:%S", tm_struct)
