from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic.response import redirect, json
from sanic.server.websockets.impl import WebsocketImplProtocol

from core.agent import agent
from models.resp import GenericResp, DplayerResp
from utils.views import check_token

__all__ = ["bp_danmaku"]

bp_danmaku = Blueprint("danmaku", url_prefix="/danmaku", version=1)


@bp_danmaku.websocket("/search")
async def ws_search(request: Request, ws: WebsocketImplProtocol):
    while True:
        keyword = (await ws.recv()).strip()
        if keyword:
            async for meta in agent.get_danmaku_metas(keyword):
                await ws.send(meta.to_json())


@bp_danmaku.get("/search/<keyword:str>", unquote=True)
async def search(request: Request, keyword: str):
    ret = []
    async for meta in agent.get_danmaku_metas(keyword):
        ret.append(meta)
    return json(GenericResp(data=ret).to_dict())


@check_token
@bp_danmaku.get("/detail/<token:str>")
async def get_detail(request: Request, token: str):
    detail = await agent.get_danmaku_detail(token)
    if not detail:
        return json(GenericResp(code=2, msg="Parse danmaku detail failed").to_dict())
    return json(GenericResp(data=detail).to_dict())


@check_token
@bp_danmaku.get("/data/<token:str>/<idx:int>")
async def get_data(request: Request, token: str, idx: int):
    data = await agent.get_danmaku_data(token, idx)
    if not data:
        return json(GenericResp(code=2, msg="Parse danmaku data failed").to_dict())
    return json(DplayerResp(data=data).to_dict())


@check_token
@bp_danmaku.get("/data/<token:str>/<idx:int>/v3/")
async def get_data_v3(request: Request, token: str, idx: int):
    return redirect(request.path.rstrip("/").replace("/v3", ""))
