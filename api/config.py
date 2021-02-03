import json
from copy import deepcopy
from os.path import dirname
from typing import List

from api.utils.logger import logger

__all__ = ["CONFIG"]


class Config:

    def __init__(self):
        self._file = f"{dirname(__file__)}/config.json"
        self._dict = {}
        self._load_config()

    def _load_config(self):
        logger.info(f"Loading config from {self._file}")
        with open(self._file, "r", encoding="utf-8") as f:
            self._dict = json.load(f)

    def _save_config(self):
        logger.info(f"Save config to {self._file}")
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self._dict, f, indent=4, ensure_ascii=False)

    @property
    def all_configs(self) -> dict:
        """获全部配置信息"""
        config = deepcopy(self._dict)  # 替换当前版本链接的 tag
        tag_name = config["version"]["tag"]
        cur_url = config["version"]["current"]
        config["version"]["current"] = cur_url.replace("#tag", tag_name)
        return config

    def get_all_modules(self) -> List[str]:
        """
        获取已经启用的引擎模块名
        :return: ["api.xxx.foo", "api.xxx.bar"]
        """
        engines = []
        for e_type in ["anime", "danmaku", "comic"]:
            for item in self._dict.get(e_type):
                engines.append(item["module"])
        return engines

    def get_enabled_modules(self) -> List[str]:
        """获取已经启用的引擎模块名"""
        engines = []
        for e_type in ["anime", "danmaku", "comic"]:
            for item in self._dict.get(e_type):
                if item["enable"]:
                    engines.append(item["module"])
        return engines

    def get(self, part: str, key: str):
        """获取指定配置项"""
        if part in self._dict:
            if key in self._dict[part]:
                return self._dict[part][key]

    def set_engine_status(self, module: str, enable: bool) -> bool:
        """
        启用或禁用指定引擎模块
        :param module: 模块名, 如 api.anime.xxx
        :param enable: 目标状态
        :return: 若模块已经处于目标状态返回 True
        """
        if module not in self.get_all_modules():  # 模块名非法
            return False

        module_types = ["anime", "danmaku", "comic"]
        for module_type in module_types:
            for info in self._dict[module_type]:
                if info["module"] == module and info["enable"] != enable:  # 与目标状态不一致时更新配置文件
                    info["enable"] = enable
                    logger.info(f"<module '{module}'> has {'loaded' if enable else 'unloaded'}")
                    self._save_config()
        return True

    def disable_engine(self, module: str) -> bool:
        """禁用某个引擎"""
        return self.set_engine_status(module, False)

    def enable_engine(self, module: str) -> bool:
        """启用某个引擎"""
        return self.set_engine_status(module, True)


# 全局配置对象
CONFIG = Config()
