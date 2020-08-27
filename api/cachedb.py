from hashlib import md5

from api.logger import logger


class CacheDB(object):
    """用于保存临时数据的简易对象数据库"""

    def __init__(self):
        self._db = {}

    def store(self, obj: object) -> str:
        """储存一个对象，返回其 key"""
        hash_str = str(id(obj))
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
        logger.warning(f"CacheDB cleaning, object in total: {len(self._db)}")
        self._db.clear()
