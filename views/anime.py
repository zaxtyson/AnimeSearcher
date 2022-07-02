from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.server.websockets.impl import WebsocketImplProtocol

from core.agent import agent
from core.config import config
from models.resp import GenericResp
from utils.bangumi import get_bangumi
from utils.views import check_token
from utils.views import template

__all__ = ["bp_anime"]

bp_anime = Blueprint("anime", url_prefix="/anime", version=1)


@bp_anime.get("/bangumi")
async def bangumi(request: Request):
    return json(get_bangumi())


@bp_anime.websocket("/search")
async def ws_search(request: Request, ws: WebsocketImplProtocol):
    keyword = await ws.recv()
    async for meta in agent.get_anime_metas(keyword):
        await ws.send(meta.to_json())


@bp_anime.get("/search/<keyword:str>", unquote=True)
async def search(request: Request, keyword: str):
    ret = []
    async for meta in agent.get_anime_metas(keyword):
        ret.append(meta)
    return json(GenericResp(data=ret).to_dict())


@check_token
@bp_anime.get("/detail/<token:str>")
async def get_detail(request: Request, token: str):
    detail = await agent.get_anime_detail(token)
    if not detail:
        return json(GenericResp(code=2, msg="Parse anime detail failed").to_dict())
    return json(GenericResp(data=detail).to_dict())


@check_token
@bp_anime.get("/info/<token:str>/<route_idx:int>/<ep_idx:int>")
async def get_info(request: Request, token: str, route_idx: int, ep_idx: int):
    info = await agent.get_video_info(token, route_idx, ep_idx)
    if not info:
        return json(GenericResp(code=2, msg="Parse video info failed").to_dict())

    return json(GenericResp(data=info).to_dict())


@bp_anime.get("/player/<token:str>/<route_idx:int>/<ep_idx:int>")
async def test_player(request: Request, token: str, route_idx: int, ep_idx: int):
    info_url = f"{config.get_base_url()}/v1/anime/info/{token}/{route_idx}/{ep_idx}"
    return template("dplayer.html", info_url=info_url)
