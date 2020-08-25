import requests
import re
from json import loads
from concurrent.futures import ThreadPoolExecutor, as_completed


class BiliBiliDanmaku(object):

    @staticmethod
    def _search(params):
        """哔哩哔哩搜索接口"""
        result = []
        search_api = "https://api.bilibili.com/x/web-interface/search/type"
        try:
            req = requests.get(search_api, params)
        except requests.RequestException:
            return result
        if req.status_code != 200:
            return result
        data = req.json()
        if data['code'] != 0 or data['data']['numResults'] == 0:
            return result
        return data['data']['result']

    @staticmethod
    def get_info_from_official(name):
        """从官方番剧区获取相关弹幕列表"""
        result = []
        params = {"keyword": name, "search_type": "media_bangumi"}
        data = BiliBiliDanmaku._search(params)[:3]  # 只要前 3 个番剧的数据
        for item in data:
            title = item['title'].replace(r'<em class="keyword">', '').replace('</em>', '')  # 番剧名
            try:
                first_ep_url = item['eps'][0]['url']
            except IndexError:
                continue
            req = requests.get(first_ep_url)
            if req.status_code != 200:
                continue
            ep_list = re.findall(r',"cid":(\d{5,}).+?titleFormat":"(.+?)",', req.text, re.M)
            dmk = Danmaku(title)
            for cid, title in ep_list:
                dmk.add(title, int(cid))
            result.append(dmk)
        return result

    @staticmethod
    def get_info_from_user(name):
        """从视频分区获取弹幕列表
        一些番剧哔哩哔哩没有版权，番剧区找不到相关信息，但是视频区可能存在用户投稿的番剧
        下面搜索 60 分钟以上的视频，分区"番剧"，按弹幕数量排序，保留前 3 条数据
        """
        result = []
        params = {"keyword": name, "search_type": "video", "tids": 13, "order": "dm", "page": 1, "duration": 4}
        data = BiliBiliDanmaku._search(params)[:3]  # 取弹幕数量前三的结果
        for item in data:
            title = item['title'].replace(r'<em class="keyword">', '').replace('</em>', '')
            aid = int(item['aid'])
            cid_api = "https://api.bilibili.com/x/player/pagelist"
            req = requests.get(cid_api, {'aid': aid})
            if req.status_code != 200 or req.json()['code'] != 0:
                continue
            dmk = Danmaku(title)
            for ep in req.json()['data']:
                dmk.add(ep['part'], int(ep['cid']))
            result.append(dmk)
        return result

    @staticmethod
    def search_danmaku(name) -> list:
        """搜索可能的弹幕列表
        :return {
            '番剧名1': [{'name': '第1集', 'cid': 12345}, {'name': '第2集', 'cid': 12346}, ...],
            '番剧名2': [...],
             }
        """
        result = []
        executor = ThreadPoolExecutor(max_workers=2)
        all_task = [
            executor.submit(BiliBiliDanmaku.get_info_from_official, name),
            executor.submit(BiliBiliDanmaku.get_info_from_user, name)
        ]
        for task in as_completed(all_task):
            result += task.result()
        return result

    @staticmethod
    def get_danmaku(cid) -> dict:
        """通过视频 cid 获取本集的弹幕,输出 DPlayer 可接受的格式
        :return {'code': 0,
                 'data' [
                         [time, pos, color, message],  # 一条弹幕: float 时间,位置参数(0右边,1上边,2底部),颜色码 10 进制,弹幕内容
                         [time, pos, color, message],
                        ]}
        """
        result = {'code': 0, 'data': []}
        api = f"https://comment.bilibili.com/{cid}.xml"
        req = requests.get(api)
        if req.status_code != 200:
            return result
        req.encoding = 'utf-8'
        dm_list = re.findall(r'p="(\d+\.?\d*?),\d,\d\d,(\d+?),\d+,(\d),.+?>(.+?)</d>', req.text)
        result['data'] = [[float(dm[0]), int(dm[2]), int(dm[1]), "", dm[3]] for dm in dm_list]
        return result
