from datetime import datetime, timedelta
from threading import Lock
from typing import Any

from pympler.asizeof import asizeof

from utils.log import logger

__all__ = ["cache"]


class MemCache:

    def __init__(self):
        self._db = {}
        self._lock = Lock()

    def get(self, key: str) -> Any:
        with self._lock:
            data = self._db.get(key)
        if not data or datetime.now() > data[0]:
            return None
        value = data[1]
        logger.debug(f"MemCache GET {key=}, {value=}")
        return value

    def set(self, key: str, value: Any, expire: int):
        expire_tm = datetime.now() + timedelta(seconds=expire)
        value_ = (expire_tm, value)
        with self._lock:
            self._db[key] = value_
        logger.debug(f"MemCache SET {key=}, {value=}, {expire_tm=}")

    def mem(self) -> int:
        return asizeof(self._db)  # bytes

    def clear(self):
        logger.warning("MemCache clear!")
        with self._lock:
            self._db.clear()


# global mem cache
cache = MemCache()

if __name__ == '__main__':
    cache.set("k1", "v1", 1)
    print(cache.get("k1"))
    import time

    time.sleep(1.1)
    print(cache.get("k1"))
