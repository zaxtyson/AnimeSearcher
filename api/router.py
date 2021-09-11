import asyncio
import os

from quart import Quart, Response

from api import *
from api.core.danmaku import *
from api.views import anime, danmaku, comic, music, iptv, proxy, system

__all__ = ["app", "app_run"]

app = Quart(__name__)

# API 蓝图
app.register_blueprint(anime.mod)
app.register_blueprint(danmaku.mod)
app.register_blueprint(comic.mod)
app.register_blueprint(music.mod)
app.register_blueprint(iptv.mod)
app.register_blueprint(proxy.mod)
app.register_blueprint(system.mod)


@app.after_request
async def apply_caching(resp: Response):
    """设置响应的全局 headers, 允许跨域"""
    resp.headers["Server"] = "Anime-API"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp


@app.route("/")
async def index():
    """API 主页显示帮助信息"""
    file = root_path + "/templates/interface.txt"
    with open(file, encoding="utf-8") as f:
        text = f.read()
    return Response(text, mimetype="text/plain")


def app_run():
    # 为了解决事件循环内部出现的异常
    loop = asyncio.new_event_loop()
    loop.set_exception_handler(lambda _loop, ctx: logger.debug(ctx))
    asyncio.set_event_loop(loop)

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app.run(host, port, debug=False, loop=loop)
