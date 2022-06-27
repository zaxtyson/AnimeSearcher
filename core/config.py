import json
from os.path import dirname, abspath
from typing import Any, List

from utils.log import logger

__all__ = ["config"]


class Config:

    def __init__(self):
        self._file = abspath(f"{dirname(__file__)}/../config.json")
        self._dict = {}
        self._load()

    def _load(self):
        logger.info(f"Loading config: {self._file}")
        with open(self._file, "r", encoding="utf-8") as f:
            self._dict = json.load(f)

    def _save(self):
        logger.info(f"Saving config: {self._file}")
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self._dict, f, indent=2, ensure_ascii=False)

    def get(self, key: str) -> Any:
        return self._dict.get(key)

    def get_remote_repo(self) -> str:
        return self.get("remote_repo")

    def get_cache_policy(self) -> dict:
        return self.get("cache_policy")

    def get_cache_policy_of(self, key: str) -> int:
        return self.get_cache_policy().get(key) or 0

    def get_http_client_config(self) -> dict:
        return self.get("http_client")

    def get_engine_status(self) -> List[dict]:
        return self.get("engine_status")

    def sync_engine_status(self, modules: List[str]):
        old_status = self.get_engine_status()
        now_status = [{"module": m, "enable": True} for m in modules]  # default status is enable
        for old in old_status:
            for now in now_status:
                if old["module"] == now["module"]:
                    now["enable"] = old["enable"]
        self._dict["engine_status"] = now_status
        self._save()

    def is_engine_enable(self, module: str) -> bool:
        for info in self.get_engine_status():
            if info["module"] == module:
                return info["enable"]
        return False

    def get_server_args(self) -> dict:
        info = self.get("server_info")
        args = {
            "host": info["bind"],
            "port": info["port"],
            "debug": info["debug"],
            "access_log": info["access_log"]
        }

        if info["https"]:
            cert_path = f"{dirname(__file__)}/../static/certs"
            args["ssl"] = {
                "cert": abspath(f"{cert_path}/cert.pem"),
                "key": abspath(f"{cert_path}/key.pem")
            }
            logger.info(f"Load ssl certs: {args['ssl']}")
        return args

    def get_base_url(self) -> str:
        info = self.get("server_info")
        protocol = "https" if info.get("https") else "http"
        host = info.get("host")
        port = info.get("port")
        return f"{protocol}://{host}:{port}"


# global config instance
config = Config()

if __name__ == '__main__':
    mods = ["a", "b", "c"]
    now = [{"module": m, "enable": True} for m in mods]
    old = [{"module": "a", "enable": False}, {"module": "e", "enable": True}]
    for o in old:
        for n in now:
            if o["module"] == n["module"]:
                n["enable"] = o["enable"]
    print(now)
