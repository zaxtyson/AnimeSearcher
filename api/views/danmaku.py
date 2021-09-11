from typing import List

from quart import Blueprint, jsonify, Response, websocket

from api import agent, domain
from api.core.danmaku import DanmakuMeta

mod = Blueprint("danmaku", __name__, url_prefix="/danmaku")


@mod.route("/search/<path:keyword>")
async def search(keyword):
    """搜索番剧弹幕库"""
    result: List[DanmakuMeta] = []
    await agent.get_danmaku_metas(keyword.strip(), callback=lambda m: result.append(m))
    data = []
    for meta in result:
        data.append({
            "title": meta.title,
            "num": meta.num,
            "module": meta.module,
            "score": 80,  # TODO: 弹幕质量评分机制
            "url": f"{domain}/danmaku/{meta.token}"
        })
    return jsonify(data)


@mod.websocket("/search")
async def ws_search():
    """搜索番剧弹幕库"""

    async def push(meta: DanmakuMeta):
        await websocket.send_json({
            "title": meta.title,
            "num": meta.num,
            "module": meta.module,
            "score": 80,
            "url": f"{domain}/danmaku/{meta.token}"
        })

    keyword = await websocket.receive()
    await agent.get_danmaku_metas(keyword.strip(), co_callback=push)


@mod.route("/<token>")
async def get_detail(token):
    """获取番剧各集对应的弹幕库信息"""
    detail = await agent.get_danmaku_detail(token)
    if detail.is_empty():
        return Response("Parse danmaku detail failed", status=404)

    data = []
    for episode, danmaku in enumerate(detail):
        data.append({
            "name": danmaku.name,
            "url": f"{domain}/danmaku/{token}/{episode}",  # Dplayer 会自动添加 /v3/
            "data": f"{domain}/danmaku/{token}/{episode}/v3/"  # 调试用
        })
    return jsonify(data)


@mod.route("/<token>/<episode>/v3/")
async def get_data(token, episode):
    """解析视频的弹幕库信息, 返回 DPlayer 支持的弹幕格式"""
    data = await agent.get_danmaku_data(token, int(episode))
    ret = {"code": 0, "data": data.data, "num": data.num}
    return jsonify(ret)
