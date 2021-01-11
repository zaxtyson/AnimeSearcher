from base64 import b16decode
from hashlib import md5

from api.logger import logger
from api.models import AnimeMetaInfo

__all__ = ["AnimeDB", "DanmakuDB"]


class CacheDB(object):
    """用于保存临时数据的简易对象数据库"""

    def __init__(self):
        self._db = {}

    def is_empty(self):
        """判空"""
        return not self._db

    def store(self, obj: object) -> str:
        """储存一个对象，返回其 key"""
        if hasattr(obj, "hash"):
            key = obj.hash  # 如果对象自定义了 hash
        else:
            hash_str = str(id(obj))  # 临时计算一个
            key = md5(hash_str.encode("utf-8")).hexdigest()
        if key not in self._db:
            logger.debug(f"Store {obj} -> {key}")
            self._db[key] = obj
        return key

    def fetch(self, key: str):
        ret = self._db.get(key)
        logger.debug(f"Fetch {key} -> {ret}")
        return ret

    def update(self, key: str, value: object):
        if key in self._db:
            logger.debug(f"Update {key} -> {value}")
            self._db[key] = value
        return key

    def clear(self):
        logger.warning(f"{self.__class__.__name__} cleaning, object in total: {len(self._db)}")
        self._db.clear()


class AnimeDB(CacheDB):
    """储存番剧信息用的临时数据库"""

    def build_anime_meta(self, hash_str: str):
        """尝试通过 hash 生成一个 AnimeMetaInfo"""
        try:
            engine, detail_page_url = b16decode(hash_str.upper()).decode("utf-8").split("|")
            meta = AnimeMetaInfo()
            meta.engine = engine
            meta.detail_page_url = detail_page_url
            logger.debug(f"Build AnimeMetaInfo from hash {hash_str}")
            logger.debug(f"engine: {engine} detail_page_url: {detail_page_url}")
            return meta
        except Exception:
            return

    def fetch(self, key: str):
        ret = super().fetch(key)
        if ret is not None:
            return ret
        return self.build_anime_meta(key)


class DanmakuDB(CacheDB):
    """储存弹幕库用的临时数据库"""
    pass


class IPTVDB(CacheDB):
    """报错直播源的临时数据库"""
    pass
