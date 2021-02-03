from os.path import dirname

from quart import Quart, jsonify, request, render_template, Response, redirect, websocket

from api.bangumi.timeline import Timeline
from api.config import CONFIG
from api.core.anime import *
from api.core.cachedb import AnimeDB, DanmakuDB, IPTVDB
from api.core.manager import EngineManager
from api.core.models import *
from api.iptv.iptv import IPTV
from api.utils.statistic import Statistics


class Router:

    def __init__(self, host: str, port: int):
        self._app = Quart(__name__)
        self._debug = False
        self._host = host
        self._port = port
        self._domain = f"http://{host}:{port}"
        self._engine_mgr = EngineManager()
        self._anime_db = AnimeDB()
        self._danmaku_db = DanmakuDB()
        self._bangumi = Timeline()
        self._iptv_db = IPTVDB()
        self._statistics = Statistics()

    def set_domain(self, domain: str):
        """
        设置 API 返回的资源链接的域名, 域名不含端口号
        如: http://www.foo.bar
        """
        self._domain = f"{domain}:{self._port}" if domain else self._domain

    def run(self):
        """启动 API 解析服务"""
        self._init_routers()
        self._app.run(host=self._host, port=self._port, debug=False, use_reloader=False)

    async def _get_cached_anime_detail(self, token: str) -> Optional[AnimeDetail]:
        """获取缓存的详情页信息, 避免重复解析"""
        detail: AnimeDetail = self._anime_db.fetch(token)
        if detail is not None:
            return detail
        detail = await self._engine_mgr.parse_anime_detail(AnimeMeta(token))
        if not detail or detail.is_empty():
            return
        self._anime_db.store(detail, token)  # 详情页信息暂存
        return detail

    async def _get_cached_anime_handler(self, token: str, playlist: int, episode: int) -> Optional[AnimeHandler]:
        """获取缓存的 Handler, 避免重复解析直链"""
        handler_token = f"{token}|{playlist}|{episode}"  # 一个 handler 对应一个 video 资源
        handler: AnimeHandler = self._anime_db.fetch(handler_token)
        if handler:
            return handler
        detail = await self._get_cached_anime_detail(token)
        if detail is not None:
            video: Video = detail.get_video(playlist, episode)
            if video is not None:
                handler = self._engine_mgr.get_anime_handler(video)
                if handler is not None:
                    self._anime_db.store(handler, handler_token)
                    return handler

    def _init_routers(self):
        """创建路由接口"""

        @self._app.after_request
        async def apply_caching(resp: Response):
            """设置响应的全局 headers, 允许跨域"""
            resp.headers["Server"] = "Anime-API"
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            return resp

        @self._app.route("/")
        async def index():
            """API 主页显示帮助信息"""
            file = f"{dirname(__file__)}/templates/interface.txt"
            with open(file, encoding="utf-8") as f:
                text = f.read()
            return Response(text, mimetype="text/plain")

        @self._app.route("/statistics")
        async def statistics():
            """百度统计转发, 用户体验计划"""
            data = await self._statistics.transmit(request)
            return Response(data, mimetype="image/gif")

        @self._app.route("/statistics/<js_url>")
        async def get_statistics_js(js_url):
            js_text = await self._statistics.get_hm_js(self._domain, request.cookies)
            return Response(js_text, mimetype="application/javascript")

        # ======================== Anime Interface ===============================

        @self._app.route("/anime/search/<path:keyword>")
        async def search_anime(keyword):
            """番剧搜索, 该方法回阻塞直到所有引擎数据返回"""
            result: List[AnimeMeta] = []
            self._anime_db.clear()  # 每次搜索清空缓存数据库
            await self._engine_mgr.search_anime(keyword, callback=lambda m: result.append(m))
            ret = []
            for meta in result:
                ret.append({
                    "title": meta.title,
                    "cover_url": meta.cover_url,
                    "category": meta.category,
                    "description": meta.desc,
                    "module": meta.module,
                    "url": f"{self._domain}/anime/{meta.token}"
                })
            return jsonify(ret)

        @self._app.websocket("/anime/search")
        async def ws_anime_search():
            async def push(meta: AnimeMeta):
                await websocket.send_json({
                    "title": meta.title,
                    "cover_url": meta.cover_url,
                    "category": meta.category,
                    "description": meta.desc,
                    "engine": meta.module,
                    "url": f"{self._domain}/anime/{meta.token}"
                })

            # route path 不能有中文, 客户端 send 关键字
            keyword = await websocket.receive()
            self._anime_db.clear()
            await self._engine_mgr.search_anime(keyword, co_callback=push)

        @self._app.route("/anime/<token>")
        async def get_anime_detail(token):
            """返回番剧详情页面信息"""
            detail = await self._get_cached_anime_detail(token)
            if not detail:
                return Response("Parse detail failed", status=500)

            ret = {
                "title": detail.title,
                "cover_url": detail.cover_url,
                "description": detail.desc,
                "category": detail.category,
                "module": detail.module,
                "play_lists": []
            }

            for pidx, playlist in enumerate(detail):
                lst = {
                    "name": playlist.name,
                    "num": playlist.num,
                    "video_list": []
                }  # 一个播放列表
                for episode, video in enumerate(playlist):
                    video_path = f"{token}/{pidx}/{episode}"
                    lst["video_list"].append({
                        "name": video.name,
                        "raw_url": f"{self._domain}/anime/{video_path}/raw",
                        "proxy_url": f"{self._domain}/anime/{video_path}/proxy",
                        "player": f"{self._domain}/player/{video_path}/raw",
                        "proxy_player": f"{self._domain}/player/{video_path}/proxy"
                    })
                ret["play_lists"].append(lst)
            return jsonify(ret)

        @self._app.route("/anime/<token>/<playlist>/<episode>/raw")
        async def redirect_to_video_real_url(token, playlist, episode):
            """通过 302 重定向到视频直链"""
            handler = await self._get_cached_anime_handler(token, int(playlist), int(episode))
            if not handler:
                return Response("Request url invalid", status=404)

            real_url = await handler.get_real_url()
            if not real_url:
                return Response(f"Parse video real url failed", status=502)

            return redirect(real_url)

        @self._app.route("/anime/<token>/<playlist>/<episode>/proxy")
        async def get_video_stream(token, playlist, episode):
            """通过API代理访问, 获取视频数据流"""
            headers = request.headers  # 客户端的请求头, 需要其中的 Range 信息
            handler = await self._get_cached_anime_handler(token, int(playlist), int(episode))
            if not handler:
                return Response("Can't find handler", status=500)
            return await handler.make_response(headers)

        @self._app.route("/bangumi/timeline")
        async def get_bangumi_timeline():
            """获取番剧更新时间表"""
            tl_list = await self._bangumi.get_timeline()
            data_json = [tl.to_dict() for tl in tl_list]
            return jsonify(data_json)

        # ======================== Danmaku Interface ===============================

        # @app.route("/danmaku/search/<path:name>")
        # async def search_danmaku(name):
        #     """搜索番剧弹幕库"""
        #     self._danmaku_db.clear()  # 每次搜索清空上一次搜索结果
        #     ret = []
        #     meta_list = self._engine_mgr.search_danmaku(name)
        #     for meta in meta_list:
        #         key = self._danmaku_db.store(meta)
        #         ret.append({
        #             "title": meta.title,
        #             "num": meta.num,
        #             "danmaku": meta.dm_engine,
        #             "url": f"{self._domain}/danmaku/detail/{key}"
        #         })
        #     return jsonify(ret)

        # @app.route("/danmaku/detail/<key>")
        # async def danmaku_detail(key):
        #     """获取番剧各集对应的弹幕库信息"""
        #     ret = []
        #     danmaku_meta = self._danmaku_db.fetch(key)
        #     dmk_collection = self._engine_mgr.get_danmaku_detail(danmaku_meta)
        #     for dmk in dmk_collection:
        #         key = self._danmaku_db.store(dmk)
        #         ret.append({
        #             "name": dmk.name,
        #             "url": f"{self._domain}/danmaku/data/{key}",  # Dplayer 会自动添加 /v3
        #             "real_url": f"{self._domain}/danmaku/data/{key}/v3/"  # 调试用
        #         })
        #     return jsonify(ret)
        #
        # @app.route("/danmaku/data/<key>/v3/")
        # async def get_danmaku_data(key):
        #     """解析视频的弹幕库信息, 返回 DPlayer 支持的弹幕格式
        #     前端 Dplayer 请求地址填 /danmaku/data/<key> 没有 v3
        #     """
        #     dmk = self._danmaku_db.fetch(key)
        #     data = self._engine_mgr.get_danmaku_data(dmk)
        #     ret = {"code": 0, "data": data}
        #     return jsonify(ret)

        # ======================== Settings Interface ===============================

        @self._app.route("/settings", methods=["GET"])
        async def show_global_settings():
            return jsonify(CONFIG.all_configs)

        @self._app.route("/settings/engine", methods=["PUT"])
        async def modify_engine_status():
            """动态启用或者禁用某些模块"""
            data = await request.json
            ret = {}
            for module, enable in data.items():
                ok = self._engine_mgr.set_engine_status(module, enable)
                ret[module] = "success" if ok else "failed"
            return jsonify(ret)

        # ======================== IPTV Interface ===============================

        @self._app.route("/iptv/list")
        async def get_iptv_list():
            """直播源"""
            ret = []
            # TODO: upgrade iptv interface
            for tv in IPTV().get_tv_list():
                key = self._iptv_db.store(tv)
                ret.append({
                    "name": tv.name,
                    "url": tv.raw_url,
                    "player": f"{self._domain}/player/iptv/{key}"
                })
            return jsonify(ret)

        # ======================== Player Interface ===============================

        @self._app.route("/player/<token>/<playlist>/<episode>/raw")
        async def player_without_proxy(token, playlist, episode):
            """视频直链播放测试"""
            url = f"{self._domain}/anime/{token}/{playlist}/{episode}/raw"
            return await render_template("player.html", video_url=url, title="DUrl")

        @self._app.route("/player/<token>/<playlist>/<episode>/proxy")
        async def player_with_proxy(token, playlist, episode):
            """视频代理播放测试"""
            url = f"{self._domain}/anime/{token}/{playlist}/{episode}/proxy"
            return await render_template("player.html", video_url=url, title="Proxy")

        @self._app.route("/player/iptv/<token>")
        async def player_iptv(token):
            """IPTV播放测试"""
            tv = self._iptv_db.fetch(token)
            return await render_template("player.html", video_url=tv.raw_url, title=tv.name)


if __name__ == '__main__':
    host = CONFIG.get("system", "host")
    port = CONFIG.get("system", "port")
    domain = CONFIG.get("system", "domain")

    router = Router(host, int(port))
    router.set_domain(domain)
    router.run()
