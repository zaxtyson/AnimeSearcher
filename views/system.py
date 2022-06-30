from sanic import json
from sanic.blueprints import Blueprint
from sanic.request import Request

from core.agent import agent
from core.cache import cache
from core.config import config
from models.resp import GenericResp
from utils.update import get_system_version

__all__ = ["bp_system"]

bp_system = Blueprint("system", url_prefix="/system", version=1)


@bp_system.websocket("/log")
async def get_log(request: Request, ws):
    pass


@bp_system.get("/version")
async def system_version(request: Request):
    info = await get_system_version()
    return json(GenericResp(data=info).to_dict())


@bp_system.get("/engine/update")
async def check_engine_update(request: Request):
    agent.load_engine_in_thread()
    return json(GenericResp(msg="Update task has been submitted").to_dict())


@bp_system.get("/engine/info")
async def get_engine_info(request: Request):
    data = {
        "anime": [],
        "danmaku": []
    }
    for engine in agent.get_loaded_anime_engine():
        info = engine.info()
        info["enable"] = config.is_engine_enable(engine.module)
        data["anime"].append(info)
    for engine in agent.get_loaded_danmaku_engine():
        info = engine.info()
        info["enable"] = config.is_engine_enable(engine.module)
        data["danmaku"].append(info)
    return json(GenericResp(data=data).to_dict())


@bp_system.post("/engine/status")
async def set_engine_status(request: Request):
    module = request.json.get("module")
    enable = request.json.get("enable")
    if not module or enable is None:
        return json(GenericResp(code=1, msg=f"Data format error: {request.json}").to_dict())
    if config.set_engine_status(module, enable):
        return json(GenericResp(code=0).to_dict())
    else:
        return json(GenericResp(code=2, msg=f"Update engine status failed: {module}").to_dict())


@bp_system.get("/cache")
async def get_mem_usage(request: Request):
    data = {
        "usage": cache.mem()
    }
    return json(GenericResp(data=data).to_dict())


@bp_system.delete("/cache")
async def clear_cache(request: Request):
    cache.clear()
    return json(GenericResp(code=0).to_dict())
