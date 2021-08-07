import json
from os.path import dirname
from typing import Any

from api.core.abc import singleton
from api.utils.logger import logger

__all__ = ["Storage"]


@singleton
class Storage:
    """给前端持久化配置用"""

    def __init__(self):
        self._file = f"{dirname(__file__)}/storage.json"
        self._dict = {}
        self._load_storage()

    def _load_storage(self):
        logger.info(f"Loading storage from {self._file}")
        with open(self._file, "r", encoding="utf-8") as f:
            self._dict = json.load(f)

    def _save_config(self):
        logger.info(f"Save storage to {self._file}")
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self._dict, f, indent=4, ensure_ascii=False)

    def get(self, key: str) -> Any:
        return self._dict.get(key)

    def set(self, key: str, value: Any):
        self._dict[key] = value
        self._save_config()
