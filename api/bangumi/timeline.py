import time
from typing import List

from api.core.danmaku import HtmlParseHelper
from api.core.models import TimelineAnimeInfo, TimelineOneDay
from api.utils.translate import convert_to_zh


class Timeline(HtmlParseHelper):
    """新番更新时间表"""

    def __init__(self):
        super().__init__()
        self._bili_mainland = "https://bangumi.bilibili.com/web_api/timeline_cn"
        self._bili_overseas = "https://bangumi.bilibili.com/web_api/timeline_global"
        self._bimi_update = "https://proxy.app.maoyuncloud.com/app/video/list"

    async def get_bilibili_timeline(self, api: str) -> List[TimelineAnimeInfo]:
        """获取哔哩哔哩的番剧更新时间表"""
        result = []  # 结果
        resp = await self.get(api)
        if not resp or resp.status != 200:
            return result
        data = await resp.json(content_type=None)
        data = data.get("result") or []

        for item in data:
            for season in item["seasons"]:
                if season["delay"] == 1:  # 本周停更, 不记录
                    continue
                anime = TimelineAnimeInfo()
                title = season["title"].replace("（僅限台灣地區）", "").replace("（僅限港澳台地區）", "")
                anime.title = convert_to_zh(title)
                anime.cover = season["cover"]  # 番剧封面, season["square_cover"] 正方形小封面
                anime.update_time = self.time_format(str(season["pub_ts"]))
                anime.update_to = season["pub_index"]
                result.append(anime)
        return result

    async def get_bimibimi_timeline(self) -> List[TimelineAnimeInfo]:
        """获取 bimibimi 番剧的更新表"""
        result = []
        params = {"channel": "1", "sort": "addtime", "limit": "0", "page": "1"}
        headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
        resp = await self.get(self._bimi_update, params=params, headers=headers)
        if not resp or resp.status != 200:
            return result
        data = await resp.json(content_type=None)
        data = data["data"]["items"]

        for item in data:
            anime = TimelineAnimeInfo()
            anime.title = item["name"]
            anime.cover = item["pic"]
            anime.update_time = self.time_format(item["updated_at"])
            anime.update_to = item["continu"].replace("更新至", "")
            result.append(anime)
        return result

    async def get_all_update_anime(self) -> List[TimelineAnimeInfo]:
        """获取全部更新的番剧信息"""
        tasks = [
            self.get_bilibili_timeline(self._bili_mainland),
            self.get_bilibili_timeline(self._bili_overseas),
            self.get_bimibimi_timeline()
        ]

        task_ret = []
        async for item in self.submit_tasks(tasks):
            task_ret.append(item)

        # 信息合并去重
        title_list = []
        result = []
        for anime in task_ret:
            if anime.title not in title_list:
                result.append(anime)
                title_list.append(anime.title)

        return result

    async def get_timeline(self) -> List[TimelineOneDay]:
        """获取最近一段时间的新番更新时间表"""
        result = []
        update_dict = {}
        await self.init_session()
        update_info = await self.get_all_update_anime()
        await self.close_session()
        for anime in update_info:
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
    def time_format(time_str: str):
        """将时间处理成 %Y-%m-%d %H:%M:%S 的格式"""
        if time_str.isdigit():
            tm_struct = time.localtime(int(time_str))  # 哔哩哔哩
        else:
            tm_struct = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S+08:00")  # Bimibimi
        return time.strftime("%Y-%m-%d %H:%M:%S", tm_struct)
