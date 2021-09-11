from hashlib import md5
from time import time
from typing import Any

import pympler.asizeof as asizeof

from api.utils.logger import logger

__all__ = ["CacheDB"]


class CacheDB(object):
    """用于保存临时数据的键值对数据库"""

    def __init__(self, expire: int = -1):
        """
        存储的对象的过期时间, 秒
        如果 expire 为负数则不过期， 除非手动清空缓存
        """
        self._db = {}
        self._expire = expire

    def is_empty(self):
        return not self._db

    def _store(self, obj: Any, key: str):
        store_ts = int(time())  # s
        self._db[key] = (obj, store_ts)

    def _fetch(self, key: str):
        data = self._db.get(key)
        if not data:
            return None

        now = int(time())
        obj, store_ts = data
        if (self._expire >= 0) and (store_ts + self._expire < now):
            self._db.pop(key)  # 数据已经过期
            logger.info(f"Resources has expired: {key}")
            return None

        return obj

    def store(self, obj: Any, key: str = None, overwrite: bool = False) -> str:
        """
        存储一个对象, 返回其 key

        :param obj: 待存储的对象
        :param key: 若不指定, 随机生成一个运行期间不会重复的 key
        :param overwrite: 存在相同的 key 时是否覆盖
        :return: 对象的 key
        """
        if not key:
            hash_str = str(id(obj))
            key = md5(hash_str.encode("utf-8")).hexdigest()

        exist = key in self._db
        if (not exist) or (exist and overwrite):
            logger.debug(f"Store {obj} -> <Key {key}>")
            self._store(obj, key)
            return key

    def fetch(self, key: str) -> Any:
        """从数据库读取一个对象"""
        ret = self._fetch(key)
        logger.debug(f"Fetch <Key {key}> -> {ret if ret else 'Nothing Found'}")
        return ret

    def update(self, key: str, value: Any) -> str:
        """更新 key 绑定的对象"""
        if key in self._db:
            logger.debug(f"Update <Key {key}> -> {value}")
            self._store(value, key)
        return key

    def size(self) -> float:
        """获取缓存对象的大小(KB)"""
        return asizeof.asizeof(self._db) / 1024

    def clear(self) -> float:
        """清空数据, 返回清理的内存大小(KB)"""
        logger.warning(f"CacheDB has been cleared, object in total: {len(self._db)}")
        size = self.size()
        self._db.clear()
        return size
