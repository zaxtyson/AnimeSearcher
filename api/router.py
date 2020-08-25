from flask import Flask, jsonify, request, render_template

from api.cachedb import CacheDB
from api.config import GLOBAL_CONFIG
from api.engine_mgr import EngineManager


class Router(object):

    def __init__(self):
        self._app = Flask(__name__)
        self._port = 80
        self._host = "127.0.0.1"
        self._domain = f"http://{self._host}:{self._port}"
        # self._server = None
        self._engine_mgr = EngineManager()
        self._db = CacheDB()
        self._proxy_clients = {}

    def listen(self, host: str, port: int):
        self._host = host
        self._port = port
        self._domain = f"http://{self._host}:{self._port}"

    def set_domain(self, domain: str):
        self._domain = f"{domain}:{self._port}"

    def _init_routes(self):
        """初始化 API 路由接口"""

        @self._app.route("/")
        def index():
            return "Hello, Anime! See useage: https://github.com/zaxtyson/anime-api"

        @self._app.route("/search/<name>")
        def search(name):
            """搜索番剧, 返回番剧摘要信息列表"""
            ret = []
            anime_list = self._engine_mgr.search(name)
            for meta in anime_list:
                hash_key = self._db.store(meta)
                anime_meta = {"name": meta.title, "cover_url": meta.cover_url, "category": meta.category,
                              "description": meta.desc, "engine": meta.engine,
                              "url": f"{self._domain}/detail/" + hash_key}
                ret.append(anime_meta)
            return jsonify(ret)

        @self._app.route("/detail/<hash_key>")
        def detail(hash_key):
            """返回番剧详情页面信息"""
            meta = self._db.fetch(hash_key)
            detail = self._engine_mgr.get_detail(meta)
            ret = {
                "title": detail.title,
                "cover_url": detail.cover_url,
                "description": detail.desc,
                "category": detail.category,
                "play_lists": []  # 一部番剧可能有多个播放列表(播放线路)
            }
            for vc in detail.play_lists:
                lst = {"name": vc.name, "num": vc.num, "video_list": []}  # 一个播放列表
                for video in vc.video_list:
                    hash_key = self._db.store(video)  # 存起来备用
                    lst["video_list"].append({
                        "name": video.name,
                        "url": f"{self._domain}/video/{hash_key}/url",
                        "proxy_url": f"{self._domain}/video/{hash_key}/proxy",
                        "simple_player": f"{self._domain}/video/{hash_key}/player",
                        "proxy_player": f"{self._domain}/video/{hash_key}/proxy_player"
                    })
                ret["play_lists"].append(lst)
            return jsonify(ret)

        @self._app.route("/video/<hash_key>/url")
        def get_video_format(hash_key):
            """获取视频直链"""
            video = self._db.fetch(hash_key)
            if video.real_url:  # 已经解析过了
                return video.real_url
            real_url = self._engine_mgr.get_video_url(video)
            video.real_url = real_url  # 存起来备用, 减少重复解析
            self._db.update(hash_key, video)
            return real_url

        @self._app.route("/video/<hash_key>/proxy")
        def get_video_data(hash_key: str):
            """通过API代理访问, 获取视频数据流"""
            video = self._db.fetch(hash_key)
            if not video.real_url:
                real_url = self._engine_mgr.get_video_url(video)
                video.real_url = real_url
                self._db.update(hash_key, video)
            return self._engine_mgr.make_response_for(video)

        @self._app.route("/video/<hash_key>/player")
        def simple_player(hash_key):
            """简易播放器测试用"""
            video = self._db.fetch(hash_key)
            if video.real_url:
                return render_template("player.html", real_url=video.real_url, video_name=video.name)
            real_url = self._engine_mgr.get_video_url(video)
            video.real_url = real_url
            self._db.update(hash_key, video)
            return render_template("player.html", real_url=real_url, video_name=video.name)

        @self._app.route("/video/<hash_key>/proxy_player")
        def simple_proxy_player(hash_key):
            """简易代理播放器测试用"""
            video = self._db.fetch(hash_key)
            real_url = f"/video/{hash_key}/proxy"
            return render_template("player.html", real_url=real_url, video_name=video.name)

        @self._app.route("/settings", methods=["GET", "POST"])
        def update_settings():
            if request.method == "GET":
                return jsonify(GLOBAL_CONFIG.get_all_configs())
            # 使用 POST 更新设置
            return "not implemented"

        @self._app.after_request
        def apply_caching(response):
            """设置响应的全局 headers, 允许跨域(前端播放器和api端口不同)"""
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Server"] = "Anime-API/0.5.0"
            return response

    def run(self):
        """后台运行"""
        self._init_routes()
        # self._server = Thread(target=self._app.run, kwargs={"host": self._host, "port": self._port})
        # self._server.start()
        self._app.run(host=self._host, port=self._port, debug=True)

    # def stop(self):
    #     self._server.join()
