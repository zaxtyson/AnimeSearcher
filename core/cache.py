from datetime import datetime, timedelta
from typing import Any

__all__ = ["cache"]


class MemCache:

    def __init__(self):
        self._db = {}

    def get(self, key: str) -> Any:
        data = self._db.get(key)
        if not data or datetime.now() > data[0]:
            return None
        return data[1]

    def set(self, key: str, value: Any, expire: int):
        expire_tm = datetime.now() + timedelta(seconds=expire)
        self._db[key] = (expire_tm, value)

    def clear(self):
        self._db.clear()


# global mem cache
cache = MemCache()

if __name__ == '__main__':
    cache.set("k1", "v1", 1)
    print(cache.get("k1"))
    import time

    time.sleep(1.1)
    print(cache.get("k1"))
