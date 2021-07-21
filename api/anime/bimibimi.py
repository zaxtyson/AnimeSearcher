import json
import re
from base64 import b64decode

from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from api.core.anime import *


def rsa_decrypt(encrypted_text: str, private_key: str) -> bytes:
    """使用 RSA 解密, 模式 RSA/ECB/PKCS1Padding"""
    key = b64decode(private_key)
    key = RSA.importKey(key)
    cipher = PKCS1_v1_5.new(key)
    return cipher.decrypt(b64decode(encrypted_text), b"decrypt error")


def aes_decrypt(encrypted_text: str, aes_key: bytes, iv: bytes) -> str:
    """使用 AES 解密, 模式 AES/CBC/PKCS7Padding"""
    enc = b64decode(encrypted_text)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    text = cipher.decrypt(enc).decode()
    return text[0:-ord(text[-1])]  # 手动去除 padding, 因为 decrypt 方法不会自动去除


def decrypt_response(data: str) -> dict:
    """解密响应数据"""
    split0, split1 = data.split(".")
    # RSA 私钥
    private_key = """
        MIIEpQIBAAKCAQEAyNfIuJdlkgV+Loba/PrWW52i+DaQt2MYkHRRRCKM8JpOR85x
        mKwxOWiYeneuDmeM9uoen4emI0SmR0wA+oPPkvUpAiif9AmVpw4Gzoyq9YxprSvd
        HHplWtI75TOSeL83IkVl1+TLOp6lmHtX/nmMvS8lIUthHR2HrB6bxJ+qYooSEKtx
        USj47fJOgo18mRuZ+Hw7zDo0G70+3IqUUYkiUhKTb7Z+dhglY8Tg1VIQJIJXXvyA
        9UDT2jVAcX1UJSzjVVFjOgaaGYpHpVtFM9yB6MmqQiouv5xYzowiy/jDs56FmMTz
        snldZac4YPBlDg+hNZdSmLbSikWjt0Z6L7K5/QIDAQABAoIBADMcZuJC9QAyEah5
        fSVAGGj8Nsr/59gjic7JKx0xxbg9LIqtiM8XkvdPHO6dolfcFk2Hyv9CIA99must
        9lnKTXrSlPsNp5cNEV6P/T93INKYRxRgw0ZKB50TP1bWxwGfd8Jq8r38ZZOnZ/Dk
        AsKp4B0M8GAGtNIZ/7rXl0B0eYHVucl7Z1pzbALLGHJRuU6ViAvLGSFtdIOq3aVx
        dkIAFeonGKInp98M6CTrp0UOwtx946SSCwo25TMJTeZfxOpJ/oc8pKm8HgOB5gX1
        SuY5oAZagWoe+H8U5U/5C/12NU6XnmS71FUg15qpRmRc7rqAh2Aw0p1QxqwaGqr/
        DzuivmkCgYEA6Yf3YyM/VFf7hozYzXn4l4kO+P9Y80Y48tWXgxdXoGq2VTy2RgQ1
        F8G39o+7GHgc6qUJG4cUcvp59Yn6x1Xb41UkE7Eibk12v8sPQgNf+zUXg1H90wjK
        G/+eRJWXuLpTv23GKss6lKSZpDD1BJ40jqjB3GQJpv5B9h4FS6Ic6aMCgYEA3Cqv
        MS23cVh8w4R0QJmdB2NgC89jY0LgZ6bQQlLPDoCIj3inGbwi27/koow6WXYrhis8
        QE+oz5tTg+MIcJiwTujEKu+BqVTnVMWGLJRH/wMbPR/AQdV/vjEZdhqX4/FjYTFw
        SzTVqL4XqabUIGBlESB+WyCEN7iT3C7bCtbdR98CgYEA2VfDtC6fyB3CaC05sbKs
        3Eug9bigznkykz6arlTRJulqHNZORcewqhWO4xhN5q4TK4bBfS8wpvna+9yY22Bb
        L66TzwfypXnO5R1Va/i8IY39/igW9YuenoQ+hlI7TJ+NRgIihr1yHdk7bQZrYwri
        m0sQcc9g9Fx6g1bZUtTj18UCgYEApveD9xLJjJ7jt07q7tbQXHsDqtEzeWKNVm4O
        gE3WkxPs/IkuiHjCIs8LMC6STagtZ8nAHrGKvy73jgyOKP3Sr3Uc18bdGTK3YPWP
        RJ2LYBzV+mvq3MJx5yXLPmL6j7ZPfLUGiTJfWmIXBeTr+EXCP9PZn3gwbSWAlLnA
        Ch9anxcCgYEAiE/EDUjRJgmSCq5Vqe117uxZAXNPvkT0RJpWZkBCe30aVt4WfKtC
        kQQMrAu231SCQMCni1c8nm/EUDYwx+jBWHT88iDhWBps/aO9u69TQQHky1MzHgrD
        7Kx6g2MNJ6+lqCcCklMu8jJJK7M6KUKGiTX475GW8DnYp4wPEAlMHxc=
        """.replace("\n", "").replace(" ", "")

    # 先用 RSA 解密出 AES 的密钥
    aes_key = rsa_decrypt(split0, private_key)
    # 再用 AES 解密数据
    # 偏移量 iv 是 aes_key 倒转过来的, 长度 16 位
    iv = aes_key[::-1][:16]
    text = aes_decrypt(split1, aes_key, iv)
    return json.loads(text)


class Bimibimi(AnimeSearcher):

    async def search(self, keyword: str):
        api = "http://api.tianbo17.com/app/video/search"
        headers = {"User-Agent": "okhttp/3.14.2", "appid": "4150439554430555"}
        params = {"limit": "100", "key": keyword, "page": "1"}
        resp = await self.get(api, params=params, headers=headers)
        if not resp or resp.status != 200:
            return
        data = await resp.text()
        data = decrypt_response(data)
        if data["data"]["total"] == 0:
            return
        for meta in data["data"]["items"]:
            anime = AnimeMeta()
            anime.title = meta["name"]
            anime.cover_url = meta["pic"]
            anime.category = meta["type"]
            anime.detail_url = meta["id"]
            yield anime


class BimiDetailParser(AnimeDetailParser):

    async def parse(self, detail_url: str) -> AnimeDetail:
        detail = AnimeDetail()
        api = "http://api.tianbo17.com/app/video/detail"
        headers = {"User-Agent": "okhttp/3.14.2", "appid": "4150439554430555"}
        resp = await self.get(api, params={"id": detail_url}, headers=headers)
        if not resp or resp.status != 200:
            return detail
        data = await resp.text()
        data = decrypt_response(data)
        data = data["data"]
        detail.title = data["name"]
        detail.cover_url = data["pic"]
        detail.desc = data["content"]  # 完整的简介
        detail.category = data["type"]
        for playlist in data["parts"]:
            pl = AnimePlayList()  # 番剧的视频列表
            pl.name = playlist["play_zh"]  # 列表名, 线路 I, 线路 II
            for name in playlist["part"]:
                video_params = f"?id={detail_url}&play={playlist['play']}&part={name}"
                pl.append(Anime(name, video_params))
            detail.append_playlist(pl)
        return detail


class BimiUrlParser(AnimeUrlParser):

    async def parse(self, raw_url: str):
        play_url = "http://api.tianbo17.com/app/video/play" + raw_url
        headers = {"User-Agent": "okhttp/3.14.2", "appid": "4150439554430555"}
        resp = await self.get(play_url, headers=headers)
        if not resp or resp.status != 200:
            return ""
        data = await resp.text()
        data = decrypt_response(data)
        real_url = data["data"][0]["url"]

        if "parse" in data["data"][0]:  # 如果存在此字段, 说明上面不是最后的直链
            parse_js = data["data"][0]["parse"]  # 这里会有一段 js 用于进一步解析
            parse_apis = re.findall(r'"(https?://.+?)"', parse_js)  # 可能存在多个解析接口
            for api in parse_apis:
                url = api + real_url
                resp = await self.get(url, allow_redirects=True)
                if not resp or resp.status != 200:
                    return ""
                data = await resp.json(content_type=None)
                real_url = data.get("url", "")
                if real_url:
                    break  # 已经得到了真正的直链

        # 这种链接还要再重定向之后才是直链
        if "quan.qq.com" in real_url:
            resp = await self.head(real_url, allow_redirects=True)
            real_url = resp.url.human_repr()
        return real_url
