from sanic.blueprints import Blueprint
from sanic.request import Request

__all__ = ["bp_system"]

bp_system = Blueprint("system", url_prefix="/system", version=1)


@bp_system.websocket("/log")
async def get_log(request: Request, ws):
    pass


@bp_system.get("/version")
async def get_app_version(request: Request):
    pass


@bp_system.get("/engine/info")
async def get_engine_info(request: Request):
    pass


@bp_system.get("/engine/update")
async def check_engine_update(request: Request):
    pass


@bp_system.post("/engine/status")
async def set_engine_status(request: Request):
    pass


@bp_system.get("/cache")
async def get_cache_policy(request: Request):
    pass


@bp_system.post("/cache")
async def set_cache_policy(request: Request):
    pass


@bp_system.get("/proxy")
async def get_proxy_policy(request: Request):
    pass


@bp_system.post("/proxy")
async def set_proxy_policy(request: Request):
    pass
