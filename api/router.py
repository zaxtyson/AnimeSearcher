from os.path import dirname

from quart import Quart, jsonify, request, render_template, \
    Response, redirect, websocket

from api.config import Config
from api.core.agent import Agent
from api.core.anime import *
from api.core.danmaku import *
from api.utils.statistic import Statistics


class APIRouter:

    def __init__(self, host: str, port: int):
        self._root = dirname(__file__)
        self._app = Quart(__name__)
        self._debug = False
        self._host = host
        self._port = port
        self._domain = f"http://{host}:{port}"
        self._agent = Agent()
        self._config = Config()
        self._statistics = Statistics()

    def set_domain(self, domain: str):
        """
        设置 API 返回的资源链接的域名, 域名含协议头不含端口号
        如: http://www.foo.bar
        """
        self._domain = f"{domain}:{self._port}" if domain else self._domain

    def run(self):
        """启动 API 解析服务"""
        self._init_routers()
        self._app.run(host=self._host, port=self._port, debug=False, use_reloader=False)

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
            file = f"{self._root}/templates/interface.txt"
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

        @self._app.route("/anime/update/timeline")
        async def get_bangumi_timeline():
            """获取番剧更新时间表"""
            bangumi = await self._agent.get_anime_timeline()
            return jsonify([item.to_dict() for item in bangumi])

        @self._app.route("/anime/search/<path:keyword>")
        async def search_anime(keyword):
            """番剧搜索, 该方法回阻塞直到所有引擎数据返回"""
            result: List[AnimeMeta] = []
            await self._agent.get_anime_metas(keyword, callback=lambda m: result.append(m))
            ret = []
            for meta in result:
                ret.append({
                    "title": meta.title,
                    "cover_url": meta.cover_url,
                    "category": meta.category,
                    "description": meta.desc,
                    "score": 80,  # TODO: 番剧质量评分机制
                    "module": meta.module,
                    "url": f"{self._domain}/anime/{meta.token}"
                })
            return jsonify(ret)

        @self._app.websocket("/anime/search")
        async def ws_search_anime():
            async def push(meta: AnimeMeta):
                await websocket.send_json({
                    "title": meta.title,
                    "cover_url": meta.cover_url,
                    "category": meta.category,
                    "description": meta.desc,
                    "score": 80,
                    "engine": meta.module,
                    "url": f"{self._domain}/anime/{meta.token}"
                })

            # route path 不能有中文, 客户端 send 关键字
            keyword = await websocket.receive()
            await self._agent.get_anime_metas(keyword, co_callback=push)

        @self._app.route("/anime/<token>")
        async def get_anime_detail(token):
            """返回番剧详情页面信息"""
            detail = await self._agent.get_anime_detail(token)
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
            for idx, playlist in enumerate(detail):
                lst = {
                    "name": playlist.name,
                    "num": playlist.num,
                    "video_list": []
                }  # 一个播放列表
                for episode, video in enumerate(playlist):
                    video_path = f"{token}/{idx}/{episode}"
                    lst["video_list"].append({
                        "name": video.name,
                        "raw_url": f"{self._domain}/anime/{video_path}/raw",
                        "proxy_url": f"{self._domain}/anime/{video_path}/proxy",
                        "player": f"{self._domain}/anime/player/{video_path}/raw",
                        "proxy_player": f"{self._domain}/anime/player/{video_path}/proxy"
                    })
                ret["play_lists"].append(lst)
            return jsonify(ret)

        @self._app.route("/anime/<token>/<playlist>/<episode>/raw")
        async def redirect_to_video_real_url(token, playlist, episode):
            """通过 302 重定向到视频直链"""
            real_url = await self._agent.get_anime_real_url(token, int(playlist), int(episode))
            if not real_url:
                return Response(f"Parse video real url failed", status=502)
            return redirect(real_url)

        @self._app.route("/anime/<token>/<playlist>/<episode>/proxy")
        async def get_video_stream(token, playlist, episode):
            """通过API代理访问, 获取视频数据流"""
            headers = request.headers  # 客户端的请求头, 需要其中的 Range 信息
            handler = await self._agent.get_anime_stream(token, int(playlist), int(episode))
            if not handler:
                return Response("Can't find handler", status=500)
            return await handler.make_response(headers)

        @self._app.route("/anime/player/<token>/<playlist>/<episode>/raw")
        async def player_without_proxy(token, playlist, episode):
            """视频直链播放测试"""
            url = f"{self._domain}/anime/{token}/{playlist}/{episode}/raw"
            return await render_template("player.html", video_url=url, title="DUrl")

        @self._app.route("/anime/player/<token>/<playlist>/<episode>/proxy")
        async def player_with_proxy(token, playlist, episode):
            """视频代理播放测试"""
            url = f"{self._domain}/anime/{token}/{playlist}/{episode}/proxy"
            return await render_template("player.html", video_url=url, title="Proxy")

        # ======================== Danmaku Interface ===============================

        @self._app.route("/danmaku/search/<path:keyword>")
        async def search_danmaku(keyword):
            """搜索番剧弹幕库"""
            result: List[DanmakuMeta] = []
            await self._agent.get_danmaku_metas(keyword, callback=lambda m: result.append(m))
            data = []
            for meta in result:
                data.append({
                    "title": meta.title,
                    "num": meta.num,
                    "module": meta.module,
                    "score": 80,  # TODO: 弹幕质量评分机制
                    "url": f"{self._domain}/danmaku/{meta.token}"
                })
            return jsonify(data)

        @self._app.route("/danmaku/search")
        async def ws_search_danmaku():
            """搜索番剧弹幕库"""

            async def push(meta: DanmakuMeta):
                await websocket.send_json({
                    "title": meta.title,
                    "num": meta.num,
                    "module": meta.module,
                    "score": 80,
                    "url": f"{self._domain}/danmaku/{meta.token}"
                })

            keyword = await websocket.receive()
            await self._agent.get_danmaku_metas(keyword, co_callback=push)

        @self._app.route("/danmaku/<token>")
        async def get_danmaku_detail(token):
            """获取番剧各集对应的弹幕库信息"""
            detail = await self._agent.get_danmaku_detail(token)
            if detail.is_empty():
                return Response("Parse danmaku detail failed", status=502)

            data = []
            for episode, danmaku in enumerate(detail):
                data.append({
                    "name": danmaku.name,
                    "url": f"{self._domain}/danmaku/{token}/{episode}",  # Dplayer 会自动添加 /v3/
                    "data": f"{self._domain}/danmaku/{token}/{episode}/v3/"  # 调试用
                })
            return jsonify(data)

        @self._app.route("/danmaku/<token>/<episode>/v3/")
        async def get_danmaku_data(token, episode):
            """解析视频的弹幕库信息, 返回 DPlayer 支持的弹幕格式"""
            data = await self._agent.get_danmaku_data(token, int(episode))
            ret = {"code": 0, "data": data.data, "num": data.num}
            return jsonify(ret)

        # ======================== IPTV Interface ===============================

        @self._app.route("/iptv/list")
        async def get_iptv_list():
            """IPTV 直播源"""
            sources = self._agent.get_iptv_sources()
            data = []
            for source in sources:
                data.append({
                    "name": source.name,
                    "url": source.url
                })
            return jsonify(data)

        # ======================== System Interface ===============================

        @self._app.route("/system/logs")
        async def show_logs():
            file = f"{self._root}/logs/api.log"
            with open(file, encoding="utf-8") as f:
                text = f.read()
            return Response(text, mimetype="text/plain")

        @self._app.route("/system/version")
        async def show_system_version():
            return jsonify(self._config.get_version())

        @self._app.route("/system/modules", methods=["GET", "PUT"])
        async def show_global_settings():
            if request.method == "GET":
                return jsonify(self._config.get_modules_status())
            if request.method == "PUT":
                data = await request.json
                ret = {}
                for module, enable in data.items():
                    ok = self._agent.set_module_status(module, enable)
                    ret[module] = "success" if ok else "failed"
                return jsonify(ret)
