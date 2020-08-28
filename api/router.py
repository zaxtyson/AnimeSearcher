from os.path import dirname

from flask import Flask, jsonify, request, render_template, Response

from api.cachedb import AnimeDB, DanmakuDB
from api.config import GLOBAL_CONFIG
from api.manager import EngineManager


class Router(object):

    def __init__(self):
        self._app = Flask(__name__)
        self._port = 80
        self._host = "127.0.0.1"
        self._domain = f"http://{self._host}:{self._port}"
        # self._server = None
        self._engine_mgr = EngineManager()
        self._anime_db = AnimeDB()
        self._danmaku_db = DanmakuDB()
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
            with open(f"{dirname(__file__)}/templates/interface.txt") as f:
                text = f.read()
            return Response(text, mimetype="text/plain")

        @self._app.route("/search/<name>")
        def search_anime(name):
            """搜索番剧, 返回番剧摘要信息列表"""
            ret = []
            self._anime_db.clear()  # 每次搜索清空缓存数据库
            anime_list = self._engine_mgr.search_anime(name)
            for meta in anime_list:
                hash_key = self._anime_db.store(meta)
                anime_meta = {"title": meta.title, "cover_url": meta.cover_url, "category": meta.category,
                              "description": meta.desc, "engine": meta.engine,
                              "url": f"{self._domain}/detail/" + hash_key}
                ret.append(anime_meta)
            return jsonify(ret)

        @self._app.route("/detail/<hash_key>")
        def detail(hash_key):
            """返回番剧详情页面信息"""
            meta = self._anime_db.fetch(hash_key)
            anime_detail = self._engine_mgr.get_anime_detail(meta)
            ret = {
                "title": anime_detail.title,
                "cover_url": anime_detail.cover_url,
                "description": anime_detail.desc,
                "category": anime_detail.category,
                "play_lists": []  # 一部番剧可能有多个播放列表(播放线路)
            }
            for video_collection in anime_detail:
                lst = {"name": video_collection.name, "num": video_collection.num, "video_list": []}  # 一个播放列表
                for video in video_collection:
                    hash_key = self._anime_db.store(video)  # 存起来备用
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
            video = self._anime_db.fetch(hash_key)
            if video.real_url:  # 已经解析过了
                return video.real_url
            real_url = self._engine_mgr.get_video_url(video)
            video.real_url = real_url  # 存起来备用, 减少重复解析
            self._anime_db.update(hash_key, video)
            return real_url

        @self._app.route("/video/<hash_key>/proxy")
        def get_video_data(hash_key: str):
            """通过API代理访问, 获取视频数据流"""
            video = self._anime_db.fetch(hash_key)
            if not video.real_url:
                real_url = self._engine_mgr.get_video_url(video)
                video.real_url = real_url
                self._anime_db.update(hash_key, video)
            return self._engine_mgr.make_response_for(video)

        @self._app.route("/video/<hash_key>/player")
        def simple_player(hash_key):
            """简易播放器测试用"""
            video = self._anime_db.fetch(hash_key)
            if video.real_url:
                return render_template("player.html", real_url=video.real_url, video_name=video.name)
            real_url = self._engine_mgr.get_video_url(video)
            video.real_url = real_url
            self._anime_db.update(hash_key, video)
            return render_template("player.html", real_url=real_url, video_name=video.name)

        @self._app.route("/video/<hash_key>/proxy_player")
        def simple_proxy_player(hash_key):
            """简易代理播放器测试用"""
            video = self._anime_db.fetch(hash_key)
            real_url = f"/video/{hash_key}/proxy"
            return render_template("player.html", real_url=real_url, video_name=video.name)

        @self._app.route("/danmaku/search/<name>")
        def search_danmaku(name):
            """搜索番剧弹幕库"""
            self._danmaku_db.clear()  # 每次搜索清空上一次搜索结果
            ret = []
            meta_list = self._engine_mgr.search_danmaku(name)
            for meta in meta_list:
                hash_key = self._danmaku_db.store(meta)
                ret.append({
                    "title": meta.title,
                    "num": meta.num,
                    "danmaku": meta.dm_engine,
                    "url": f"{self._domain}/danmaku/detail/{hash_key}"
                })
            return jsonify(ret)

        @self._app.route("/danmaku/detail/<hash_key>")
        def danmaku_detail(hash_key):
            """获取番剧各集对应的弹幕库信息"""
            ret = []
            danmaku_meta = self._danmaku_db.fetch(hash_key)
            dmk_collection = self._engine_mgr.get_danmaku_detail(danmaku_meta)
            for dmk in dmk_collection:
                hash_key = self._danmaku_db.store(dmk)
                ret.append({
                    "name": dmk.name,
                    "url": f"{self._domain}/danmaku/data/{hash_key}",
                    "real_url": f"{self._domain}/danmaku/data/{hash_key}/v3"
                })
            return jsonify(ret)

        @self._app.route("/danmaku/data/<hash_key>/v3")
        def get_danmaku_data(hash_key):
            """解析视频的弹幕库信息, 返回 DPlayer 支持的弹幕格式
            前端 Dplayer 请求地址填 /danmaku/data/<hash_key> 没有 v3
            """
            dmk = self._danmaku_db.fetch(hash_key)
            data = self._engine_mgr.get_danmaku_data(dmk)
            ret = {"code": 0, "data": data}
            return jsonify(ret)

        @self._app.route("/settings")
        def show_settings():
            if request.method == "GET":
                return jsonify(GLOBAL_CONFIG.get_all_configs())

        @self._app.route("/settings/engine", methods=["POST"])
        def update_engine_status():
            """动态启用或者禁用资源引擎"""
            name = request.form.get("name")
            enable = request.form.get("enable")
            if enable == "true":
                ret = self._engine_mgr.enable_engine(name)
            elif enable == "false":
                ret = self._engine_mgr.disable_engine(name)
            else:
                ret = False
            return jsonify(ret)

        @self._app.route("/settings/danmaku", methods=["POST"])
        def update_danmaku_status():
            """动态启用或者禁用弹幕搜索引擎"""
            name = request.form.get("name")
            enable = request.form.get("enable")
            if enable == "true":
                ret = self._engine_mgr.enable_danmaku(name)
            elif enable == "false":
                ret = self._engine_mgr.disable_danmaku(name)
            else:
                ret = False
            return jsonify(ret)

        @self._app.after_request
        def apply_caching(response):
            """设置响应的全局 headers, 允许跨域(前端播放器和api端口不同)"""
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
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
