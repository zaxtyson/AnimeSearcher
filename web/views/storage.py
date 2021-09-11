from quart import Blueprint, request, Response, jsonify

from web.utils.storage import Storage

mod = Blueprint("storage", __name__, url_prefix="/system")
storage = Storage()


@mod.route("/storage", methods=["POST", "OPTIONS"])
async def web_storage():
    """给前端持久化配置用"""
    if request.method == "OPTIONS":
        return Response("")
    if request.method == "POST":
        payload = await request.json
        if not payload:
            return jsonify({"msg": "payload format error"})

        action: str = payload.get("action", "")
        key: str = payload.get("key", "")
        data: str = payload.get("data", "")

        if not key:
            return jsonify({"msg": "key is invalid"})

        if action.lower() == "get":
            return jsonify({
                "msg": "ok",
                "key": key,
                "data": storage.get(key)
            })
        elif action.lower() == "set":
            storage.set(key, data)
            return jsonify({
                "msg": "ok",
                "key": key,
                "data": data,
            })
        elif action.lower() == "del":
            return jsonify({
                "msg": "ok" if storage.delete(key) else "no data binds this key",
                "key": key
            })
        else:
            return jsonify({
                "msg": "action is not supported",
                "action": action
            })
