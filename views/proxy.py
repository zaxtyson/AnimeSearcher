from sanic.blueprints import Blueprint
from sanic.request import Request
from sanic.response import text

from core.agent import agent
from core.config import config
from core.http_client import client
from core.proxy import clean_resp_headers
from utils.encode import validate_token

__all__ = ["bp_proxy"]

bp_proxy = Blueprint("proxy", url_prefix="/proxy", version=1)


@bp_proxy.route("/image", methods=["GET", "HEAD"])
async def image(request: Request):
    url = request.args.get("url")
    if not url:
        return text("Url is invalid", status=400)

    async with client.get(url) as r:
        r_headers = clean_resp_headers(r.headers)
        r_headers["Server"] = "ImageProxy"
        resp = await request.respond(status=r.status, headers=r_headers)
        while chunk := await r.content.read(4096):
            await resp.send(chunk)


@bp_proxy.route("/anime/<token:str>/<route_idx:int>/<ep_idx:int>", methods=["GET", "HEAD"])
async def anime(request: Request, token: str, route_idx: int, ep_idx: int):
    if not validate_token(token):
        return text("Url token invalid", status=400)

    proxy = await agent.get_video_proxy(token, route_idx, ep_idx)
    if not proxy:
        return text("Parse video info failed", status=500)

    proxy.set_chunk_proxy_prefix(f"{config.get_base_url()}/v1/proxy/hls/{token}/{route_idx}/{ep_idx}?chunk=")
    await proxy.make_response(request)


@bp_proxy.route("/hls/<token:str>/<route_idx:int>/<ep_idx:int>", methods=["GET", "HEAD"])
async def hls(request: Request, token: str, route_idx: int, ep_idx: int):
    chunk_url = request.args.get("chunk")
    if not validate_token(token) or not chunk_url:
        return text("Url token invalid", status=400)

    proxy = await agent.get_video_proxy(token, route_idx, ep_idx)
    if not proxy:
        return text("Parse video info failed", status=500)

    await proxy.make_response_for_chunk(request, chunk_url)
