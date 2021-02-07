import json
from os.path import dirname
from typing import List

from api.core.abc import singleton
from api.utils.logger import logger

__all__ = ["Config"]


@singleton
class Config:
    """
    配置管理
    """

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

    def get_version(self) -> dict:
        """系统版本信息"""
        version = self._dict["version"]  # 替换当前版本链接的 tag
        tag_name = version["tag"]
        cur_url = version["current"]
        version["current"] = cur_url.replace("#tag", tag_name)
        return version

    def get_modules_status(self) -> dict:
        """获取模块信息"""
        status = {
            "anime": self._dict["anime"],
            "danmaku": self._dict["danmaku"],
            "comic": self._dict["comic"],
            "music": self._dict["music"]
        }
        return status

    def get_all_modules(self) -> List[str]:
        """
        获取已经启用的引擎模块名
        :return: ["api.xxx.foo", "api.xxx.bar"]
        """
        engines = []
        for e_type in ["anime", "danmaku", "comic", "music"]:
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

    def update_module_state(self, module: str, enable: bool) -> bool:
        """
        启用或禁用指定引擎模块
        :param module: 模块名, 如 api.anime.xxx
        :param enable: 目标状态
        :return: 若模块已经处于目标状态返回 True
        """
        if module not in self.get_all_modules():  # 模块名非法
            return False

        module_types = ["anime", "danmaku", "comic", "music"]
        for module_type in module_types:
            for info in self._dict[module_type]:
                if info["module"] == module and info["enable"] != enable:  # 与目标状态不一致时更新配置文件
                    info["enable"] = enable
                    logger.info(f"<module '{module}'> has {'loaded' if enable else 'unloaded'}")
                    self._save_config()
        return True

    def disable_engine(self, module: str) -> bool:
        """禁用某个引擎"""
        return self.update_module_state(module, False)

    def enable_engine(self, module: str) -> bool:
        """启用某个引擎"""
        return self.update_module_state(module, True)
