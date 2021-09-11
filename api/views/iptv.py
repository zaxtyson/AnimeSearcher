from quart import Blueprint, jsonify

from api import agent

mod = Blueprint("iptv", __name__, url_prefix="/iptv")


@mod.route("/list")
async def iptv_list():
    """IPTV 直播源"""
    sources = agent.get_iptv_sources()
    data = []
    for source in sources:
        data.append({
            "name": source.name,
            "url": source.url
        })
    return jsonify(data)
