import time
from typing import List

from api.core.danmaku import HtmlParseHelper
from api.update.models import AnimeUpdateInfo, BangumiOneDay
from api.utils.tool import convert_to_zh

__all__ = ["Bangumi"]


class Bangumi(HtmlParseHelper):
    """新番更新时间表"""

    def __init__(self):
        super().__init__()
        self._bili_mainland = "https://bangumi.bilibili.com/web_api/timeline_cn"
        self._bili_overseas = "https://bangumi.bilibili.com/web_api/timeline_global"
        # self._bimi_update = "http://api.tianbo17.com/app/video/list"   # 接口变更, 数据已加密

    async def get_bangumi_updates(self) -> List[BangumiOneDay]:
        """获取最近一段时间的新番更新时间表"""
        results = []
        update_dict = {}
        await self.init_session()
        update_info = await self._get_all_bangumi()
        await self.close_session()
        for anime in update_info:
            up_date = anime.update_time.split()[0]  # %Y-%m-%d
            update_dict.setdefault(up_date, [])
            update_dict[up_date].append(anime)

        for up_date, anime_list in update_dict.items():
            one_day = BangumiOneDay()
            one_day.date = up_date
            one_day.day_of_week = time.strftime("%w", time.strptime(up_date, "%Y-%m-%d"))
            one_day.is_today = True if up_date == time.strftime("%Y-%m-%d", time.localtime()) else False
            one_day.updates = anime_list
            results.append(one_day)
        results.sort(key=lambda x: x.date)
        return results

    async def _get_bili_bangumi(self, api: str) -> List[AnimeUpdateInfo]:
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
                anime = AnimeUpdateInfo()
                title = season["title"].replace("（僅限台灣地區）", "").replace("（僅限港澳台地區）", "")
                anime.title = convert_to_zh(title)
                anime.cover_url = season["cover"]  # 番剧封面, season["square_cover"] 正方形小封面
                anime.update_time = self._time_format(str(season["pub_ts"]))
                anime.update_to = season["pub_index"]
                result.append(anime)
        return result

    # async def _get_bimi_bangumi(self) -> List[AnimeUpdateInfo]:
    #     """获取 bimibimi 番剧的更新表"""
    #     result = []
    #     params = {"channel": "1", "sort": "addtime", "limit": "0", "page": "1"}
    #     headers = {"User-Agent": "Dart/2.7 (dart:io)", "appid": "4150439554430555"}
    #     resp = await self.get(self._bimi_update, params=params, headers=headers)
    #     if not resp or resp.status != 200:
    #         return result
    #     data = await resp.json(content_type=None)
    #     data = data["data"]["items"]
    #
    #     for item in data:
    #         anime = AnimeUpdateInfo()
    #         anime.title = item["name"]
    #         anime.cover_url = item["pic"]
    #         anime.update_time = self._time_format(item["updated_at"])
    #         anime.update_to = item["continu"].replace("更新至", "")
    #         result.append(anime)
    #     return result

    async def _get_all_bangumi(self) -> List[AnimeUpdateInfo]:
        """获取全部更新的番剧信息"""
        tasks = [
            self._get_bili_bangumi(self._bili_mainland),
            self._get_bili_bangumi(self._bili_overseas),
            # self._get_bimi_bangumi()
        ]

        task_ret = []
        async for item in self.as_iter_completed(tasks):
            task_ret.append(item)

        # 信息合并去重
        title_list = []
        result = []
        for anime in task_ret:
            if anime.title not in title_list:
                result.append(anime)
                title_list.append(anime.title)

        return result

    @staticmethod
    def _time_format(time_str: str):
        """将时间处理成 %Y-%m-%d %H:%M:%S 的格式"""
        if time_str.isdigit():
            tm_struct = time.localtime(int(time_str))  # 哔哩哔哩
        else:
            tm_struct = time.strptime(time_str, "%Y-%m-%dT%H:%M:%S+08:00")  # Bimibimi
        return time.strftime("%Y-%m-%d %H:%M:%S", tm_struct)
