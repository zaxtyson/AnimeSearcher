from api.core.anime import *
from api.utils.tool import md5


class AgeFans(AnimeSearcher):

    async def search(self, keyword: str):
        first_page = await self.fetch_one_page(keyword, 1)
        data = self.parse_one_page(first_page)
        for meta in data:
            yield meta
        pages = first_page["SeaCnt"] // 24 + 1
        if pages == 1:
            return  # 如果存在多页就继续
        tasks = [self.parse_one_page(await self.fetch_one_page(keyword, p))
                 for p in range(2, pages + 1)]
        async for meta in self.as_iter_completed(tasks):
            yield meta

    async def fetch_one_page(self, keyword: str, page: int):
        api = f"https://api.agefans.app/v2/search?page={page}&query={keyword}"
        headers = {
            "Origin": "https://web.age-spa.com:8443",
            "Referer": "https://web.age-spa.com:8443/"
        }
        resp = await self.get(api, headers=headers)
        if not resp or resp.status != 200:
            return
        return await resp.json(content_type=None)

    @staticmethod
    def parse_one_page(data: dict):
        data = data["AniPreL"]
        result = []
        for item in data:
            meta = AnimeMeta()
            meta.title = item["R动画名称"]
            meta.category = " ".join(item["R剧情类型"])
            meta.desc = item["R简介"]
            meta.cover_url = item["R封面图小"]
            meta.detail_url = item["AID"]
            result.append(meta)
        return result


class AgeFansAppDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str):
        detail = AnimeDetail()
        api = f"https://api.agefans.app/v2/detail/{detail_url}"  # 20120029
        headers = {
            "Origin": "https://web.age-spa.com:8443",
            "Referer": "https://web.age-spa.com:8443/"
        }
        resp = await self.get(api, headers=headers)
        if not resp or resp.status != 200:
            return detail
        data = await resp.json(content_type=None)
        data = data["AniInfo"]
        detail.title = data["R动画名称"]
        detail.cover_url = "http:" + data["R封面图"]
        detail.desc = data["R简介"]
        detail.category = data["R标签"]
        idx = 1
        for playlist in data["R在线播放All"]:
            if not playlist:
                continue
            if "PPTV" in playlist[0]["PlayId"]:
                continue  # 还要解析一次, 不要了
            pl = AnimePlayList()
            pl.name = f"播放路线 {idx}"
            for item in playlist:
                anime = Anime()
                anime.name = item["Title_l"] or item["Title"]
                play_id = item["PlayId"]  # <play>web_mp4|QLIVE|tieba|...</play>
                play_vid = item["PlayVid"]  # url or token
                anime.raw_url = play_id + "|" + play_vid
                pl.append(anime)
            detail.append_playlist(pl)
            idx += 1
        return detail


class AgeFansUrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        play_id, play_vid = raw_url.split("|")
        if play_vid.startswith("http"):
            return play_vid  # 不用处理了

        headers = {
            "Origin": "https://web.age-spa.com:8443",
            "Referer": "https://web.age-spa.com:8443/"
        }
        api = "https://api.agefans.app/v2/_getplay"
        resp = await self.get(api, headers=headers)
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        # 参数 kp 算法见 https://vip.cqkeb.com/agefans/js/chunk-3a9344fa.3f1985c3.js
        play_key = "agefans3382-getplay-1719"
        timestamp = data["ServerTime"]
        kp = md5(str(timestamp) + "{|}" + play_id + "{|}" + play_vid + "{|}" + play_key)
        next_api = data["Location"]
        params = {"playid": play_id, "vid": play_vid, "kt": timestamp, "kp": kp}
        resp = await self.get(next_api, params=params, headers=headers)
        if not resp or resp.status != 200:
            return ""
        data = await resp.json(content_type=None)
        v_url, p_url = data["vurl"], data["purlf"]
        if v_url or p_url:
            url = p_url + v_url
            url = url.split("?url=")[-1]
            return url
        return ""
