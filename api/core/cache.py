from hashlib import md5
from typing import Any

import pympler.asizeof as asizeof

from api.utils.logger import logger

__all__ = ["CacheDB"]


class CacheDB(object):
    """用于保存临时数据的键值对数据库"""

    def __init__(self):
        self._db = {}

    def is_empty(self):
        return not self._db

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
            self._db[key] = obj
            return key

    def fetch(self, key: str) -> Any:
        """从数据库读取一个对象"""
        ret = self._db.get(key)
        logger.debug(f"Fetch <Key {key}> -> {ret if ret else 'Nothing Found'}")
        return ret

    def update(self, key: str, value: Any) -> str:
        """更新 key 绑定的对象"""
        if key in self._db:
            logger.debug(f"Update <Key {key}> -> {value}")
            self._db[key] = value
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
