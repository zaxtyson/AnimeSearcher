from quart import Blueprint, Response, request, jsonify

from api import root_path, config, agent

mod = Blueprint("system", __name__, url_prefix="/system")


@mod.route("/logs")
async def logs():
    """获取运行日志"""
    file = root_path + "/logs/api.log"
    with open(file, encoding="utf-8") as f:
        text = f.read()
    return Response(text, mimetype="text/plain")


@mod.route("/version")
async def version():
    """获取版本信息"""
    return jsonify(config.get_version())


@mod.route("/clear")
async def clear():
    """清空 API 的临时缓存数据"""
    mem_free = agent.cache_clear()
    return jsonify({"clear": "success", "free": mem_free})


@mod.route("/modules", methods=["GET", "POST", "OPTIONS"])
async def modules():
    if request.method == "GET":
        return jsonify(config.get_modules_status())
    elif request.method == "POST":
        options = await request.json
        ret = {}
        for option in options:
            module = option.get("module")
            enable = option.get("enable")
            if not module:
                continue
            ok = agent.change_module_state(module, enable)
            ret[module] = "success" if ok else "failed"
        return jsonify(ret)
    elif request.method == "OPTIONS":
        return Response("")
