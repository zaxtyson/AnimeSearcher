from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic.response import text, redirect

__all__ = ["bp_danmaku"]

bp_danmaku = Blueprint("danmaku", url_prefix="/danmaku", version=1)


@bp_danmaku.websocket("/search")
async def ws_search(request: Request, ws):
    msg = ws.recv()


@bp_danmaku.get("/search/<keyword:str>")
async def search(request: Request, keyword: str):
    return text("hello, " + keyword)


@bp_danmaku.get("/detail/<aid:str>")
async def get_detail(request: Request, aid: str):
    return text("hello, " + aid)


@bp_danmaku.get("/data/<aid:str>/<ep_idx:int>")
async def get_data(request: Request, aid: str, ep_idx: int):
    return text("hello, " + aid)


@bp_danmaku.get("/data/<aid:str>/<ep_idx:int>/v3/")
async def get_data_v3(request: Request, aid: str, ep_idx: int):
    return redirect(request.path)
