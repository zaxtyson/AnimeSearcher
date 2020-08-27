import json
import os
from typing import List, Dict

from api.logger import logger

__all__ = ["GLOBAL_CONFIG"]


class Config:

    def __init__(self):
        self._file = os.path.dirname(__file__) + os.sep + "config.json"
        self._dict = {}

        logger.info(f"Loading config from {self._file}")

        with open(self._file, "r") as f:
            self._dict = json.load(f)

    def _save(self):
        logger.info(f"Save config to {self._file}")
        with open(self._file, "w") as f:
            json.dump(self._dict, f, indent=4)

    def get_all_configs(self) -> dict:
        """获全部配置信息"""
        return self._dict

    def get_all_engines(self) -> Dict[str, bool]:
        """获取所有引擎的状态"""
        return self._dict.get("engines")

    def get_enabled_engines(self) -> List[str]:
        """获取已启用的引擎列表"""
        enabled_engines = []
        for engine, status in self._dict.get("engines").items():
            if status:
                enabled_engines.append(engine)
        return enabled_engines

    def disable_engine(self, engine: str) -> bool:
        """禁用某个引擎"""
        if engine in self.get_all_engines():
            logger.warning(f"Engine {engine} disabled")
            self._dict["engines"][engine] = False
            self._save()
            return True
        return False

    def enabled_engine(self, engine: str) -> bool:
        """启用某个引擎"""
        if engine in self.get_all_engines():
            logger.info(f"Engine {engine} enabled")
            self._dict["engines"][engine] = True
            self._save()
            return True
        return False

    def get_all_danmaku(self) -> Dict[str, bool]:
        """获取所有弹幕引擎的状态"""
        return self._dict.get("danmaku")

    def get_enabled_danmaku(self) -> List[str]:
        """获取已启用的弹幕引擎列表"""
        enabled_danmaku = []
        for engine, status in self._dict.get("danmaku").items():
            if status:
                enabled_danmaku.append(engine)
        return enabled_danmaku

    def disable_danmaku(self, danmaku: str) -> bool:
        """禁用某个弹幕引擎"""
        if danmaku in self.get_all_danmaku():
            logger.warning(f"Danmaku {danmaku} disabled")
            self._dict["danmaku"][danmaku] = False
            self._save()
            return True
        return False

    def enabled_danmaku(self, danmaku: str) -> bool:
        """启用某个弹幕引擎"""
        if danmaku in self.get_all_danmaku():
            logger.info(f"Danmaku {danmaku} enabled")
            self._dict["danmaku"][danmaku] = True
            self._save()
            return True
        return False


# 全局配置对象
GLOBAL_CONFIG = Config()
