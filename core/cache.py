import asyncio
from datetime import datetime, timedelta
from threading import Lock
from typing import Any

from pympler.asizeof import asizeof

from utils.log import logger

__all__ = ["cache", "clear_expired_keys"]


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
        logger.debug(f"MemCache GET {key=}")
        return value

    def set(self, key: str, value: Any, expire: int):
        expire_tm = datetime.now() + timedelta(seconds=expire)
        value_ = (expire_tm, value)
        with self._lock:
            self._db[key] = value_
        logger.debug(f"MemCache SET {key=}, {expire_tm=}")

    def mem(self) -> int:
        return asizeof(self._db)  # bytes

    def clear(self):
        logger.warning("MemCache clear!")
        with self._lock:
            self._db.clear()

    def clear_expired(self):
        now = datetime.now()
        key_num = len(self._db)
        logger.debug(f"MemCache scan expired keys...")
        with self._lock:
            self._db = {k: v for k, v in self._db.items() if v[0] > now}
        expire_key_num = key_num - len(self._db)
        if expire_key_num > 0:
            logger.info(f"MemCache clear {expire_key_num} expired key(s)")


# global mem cache
cache = MemCache()


async def clear_expired_keys():
    while True:
        await asyncio.sleep(600)  # 10min
        cache.clear_expired()


if __name__ == '__main__':
    cache.set("k1", "v1", 1)
    print(cache.get("k1"))
    import time

    time.sleep(1.1)
    print(cache.get("k1"))
