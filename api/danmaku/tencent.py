import json
import re
from typing import List

from api.base import DanmakuEngine
from api.models import DanmakuCollection, DanmakuMetaInfo, Danmaku


class DanmakuTencent(DanmakuEngine):
    """腾讯视频的弹幕"""

    def search(self, keyword: str) -> List[DanmakuMetaInfo]:
        """搜索相关的电视剧/番剧"""
        # 先通过接口搜索, 没有结果再解析网页数据
        return self.search_from_api(keyword) or self.search_from_web(keyword)

    def search_from_api(self, keyword: str) -> List[DanmakuMetaInfo]:
        """通过接口搜索同一系列的剧集"""
        result = []
        api = "https://s.video.qq.com/load_poster_list_info"
        params = {
            "otype": "json",
            "num": 100,
            "plat": 2,
            "pver": 0,
            "query": keyword,
            "intention_id": 0
        }
        resp = self.get(api, params=params)
        if resp.status_code != 200:
            return result
        data = resp.text.lstrip("QZOutputJson=").rstrip(";").replace("\u0005", "").replace("\u0006", "")
        data = json.loads(data)
        data = data["PosterListMod"]["posterList"]
        for item in data:
            url = item["url"]
            if "qq.com" not in url:
                continue  # 不是腾讯平台的视频
            meta = DanmakuMetaInfo()
            meta.title = item["title"]
            meta.play_page_url = url
            # 提取剧集数
            for i in item["markLabelList"]:
                num_str = i.get("primeText") or ""
                num = re.search(r"(\d+)", num_str)
                if num:
                    meta.num = num.group(1)
                else:
                    meta.num = 1
            result.append(meta)
        return result

    def search_from_web(self, keyword: str) -> List[DanmakuMetaInfo]:
        """从网页版提取数据"""
        result = []
        api = "http://m.v.qq.com/x/search.html"  # PC 版数据过于杂乱, 所以抓移动版
        resp = self.get(api, params={"keyWord": keyword})
        if resp.status_code != 200:
            return result
        data = self.xpath(resp.text, '//div[@class="search_item"]')
        for node in data[:-1]:  # 最后一个是搜索推荐, 丢弃
            url = node.xpath("./a/@href")
            if not url or "qq.com" not in url[0]:  # 不是电视剧/番剧, 或者不是腾讯平台的视频
                continue
            meta = DanmakuMetaInfo()
            meta.play_page_url = url[0]
            title = "".join(node.xpath("./a/div/strong//text()"))
            meta.title = title.replace("\n", "").strip()
            ep_num = node.xpath('./a//em[@class="mask_txt"]/text()')
            if not ep_num:  # 没有集数信息就是只有 1 集
                meta.num = 1
            else:
                num = re.search(r"(\d+)", ep_num[0]).group(1)
                meta.num = int(num)
            result.append(meta)
        return result

    def get_detail(self, play_page_url: str) -> DanmakuCollection:
        result = DanmakuCollection()
        detail_id = re.search(r"/([^/]+?)\.html", play_page_url).group(1)
        api = "http://s.video.qq.com/get_playsource"
        params = {
            "id": detail_id,
            "type": 4,
            "range": "1-99999",
            "otype": "json"
        }
        resp = self.get(api, params=params)
        if resp.status_code != 200:
            return result
        data = resp.text.lstrip("QZOutputJson=").rstrip(";")
        data = json.loads(data)
        data = data["PlaylistItem"]["videoPlayList"]
        for item in data:
            dmk = Danmaku()
            dmk.name = item["title"]
            if "预告片" in dmk.name:
                continue  # 预告片不要
            dmk.cid = item["id"]  # 视频id "j31520vrtpw"
            result.append(dmk)
        return result

    def get_danmaku(self, video_id: str):
        """获取视频的全部弹幕"""
        result = []
        title, duration, target_id = self.get_video_info(video_id)
        if not target_id:
            return result
        count = duration // 30 + 1
        tasks = [(self.get_30s_danmu, (video_id, target_id, t * 30), {}) for t in range(count)]
        for ret in self.submit_tasks(tasks):
            result.extend(ret)
        return result

    def get_30s_danmu(self, video_id: str, target_id: str, start_at: int):
        """获取某个时间点后的 30s 弹幕数据
        :params video_id 视频 url 中的id
        :params target_id 视频的数字id
        :params start_at 弹幕起始时间点(s)
        """
        result = []
        api = "https://mfm.video.qq.com/danmu"
        params = {
            "otype": "json",
            "target_id": f"{target_id}&vid={video_id}",
            "session_key": "0,0,0",
            "timestamp": start_at
        }
        resp = self.get(api, params=params)
        if resp.status_code != 200:
            return []
        data = json.loads(resp.text, strict=False)  # 可能有特殊字符
        for item in data["comments"]:
            play_at = item["timepoint"]  # 弹幕出现的时间点(s)
            content = item["content"].replace("\xa0", "").strip()  # 弹幕内容
            if "我收到了" in content or "感谢爱你哟" in content:  # 过滤赠送礼品的弹幕
                continue
            style = item["content_style"]
            if not style:
                color = "ffffff"
                position = 0
            else:
                style = json.loads(style)
                color = style.get("color", "ffffff")  # 10 进制颜色
                position = style["position"]

            result.append([play_at, position, int(color, 16), "", content])
        return result

    def get_video_info(self, video_id: str):
        """获取视频的信息"""
        no_result = ("", 0, "")  # 视频标题, 时长, 对应的数字id
        api = "http://union.video.qq.com/fcgi-bin/data"
        params = {
            "tid": "98",
            "appid": "10001005",
            "appkey": "0d1a9ddd94de871b",
            "idlist": video_id,
            "otype": "json"
        }
        resp = self.get(api, params=params)
        if resp.status_code != 200:
            return no_result
        data = json.loads(resp.text.lstrip("QZOutputJson=").rstrip(";"))
        data = data["results"][0]["fields"]
        title = data["title"]  # 视频标题 斗罗大陆_051
        duration = int(data["duration"])  # 视频时长 1256
        # 获取视频对应的 targetid
        api = "http://bullet.video.qq.com/fcgi-bin/target/regist"
        params = {"otype": "json", "vid": video_id}
        resp = self.get(api, params=params)
        if resp.status_code != 200:
            return no_result
        data = json.loads(resp.text.lstrip("QZOutputJson=").rstrip(";"))
        target_id = data["targetid"]  # "3881562420"
        return title, duration, target_id
