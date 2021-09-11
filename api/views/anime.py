from quart import Blueprint, jsonify, Response, redirect, websocket, render_template

from api import *
from api.core.anime import AnimeMeta

mod = Blueprint("anime", __name__, url_prefix="/anime")


def get_image_url(url: str) -> str:
    return f"{domain}/proxy/image/{url}" if enforce_proxy_images else url


@mod.route("/bangumi/updates")
async def bangumi_updates():
    """获取番剧更新时间表"""
    bangumi_list = await agent.get_bangumi_updates()
    data = []
    for bangumi in bangumi_list:
        one_day = {
            "date": bangumi.date,
            "day_of_week": bangumi.day_of_week,
            "is_today": bangumi.is_today,
            "updates": []
        }
        for info in bangumi:
            one_day["updates"].append({
                "title": info.title,
                "cover_url": get_image_url(info.cover_url),  # 图片一律走代理, 防止浏览器跨域拦截
                "update_time": info.update_time,
                "update_to": info.update_to
            })
        data.append(one_day)
    return jsonify(data)


@mod.route("/search/<path:keyword>")
async def search(keyword):
    """番剧搜索, 该方法回阻塞直到所有引擎数据返回"""
    result = await agent.get_anime_metas(keyword.strip())
    ret = []
    for meta in result:
        ret.append({
            "title": meta.title,
            "cover_url": get_image_url(meta.cover_url),
            "category": meta.category,
            "description": meta.desc,
            "score": 80,  # TODO: 番剧质量评分机制
            "module": meta.module,
            "url": f"{domain}/anime/{meta.token}"
        })
    return jsonify(ret)


@mod.websocket("/search")
async def ws_search():
    async def push(meta: AnimeMeta):
        await websocket.send_json({
            "title": meta.title,
            "cover_url": get_image_url(meta.cover_url),
            "category": meta.category,
            "description": meta.desc,
            "score": 80,
            "engine": meta.module,
            "url": f"{domain}/anime/{meta.token}"
        })

    # route path 不能有中文, 客户端 send 关键字
    keyword = await websocket.receive()
    await agent.get_anime_metas(keyword.strip(), co_callback=push)


@mod.route("/<token>")
async def anime_detail(token):
    """返回番剧详情页面信息"""
    detail = await agent.get_anime_detail(token)
    if not detail:
        return Response("Parse detail failed", status=404)

    ret = {
        "title": detail.title,
        "cover_url": get_image_url(detail.cover_url),
        "description": detail.desc,
        "category": detail.category,
        "module": detail.module,
        "play_lists": []
    }
    for idx, playlist in enumerate(detail):
        lst = {
            "name": playlist.name,
            "num": playlist.num,
            "video_list": []
        }  # 一个播放列表
        for episode, video in enumerate(playlist):
            video_path = f"{token}/{idx}/{episode}"
            lst["video_list"].append({
                "name": video.name,
                "info": f"{domain}/anime/{video_path}",
                "player": f"{domain}/anime/{video_path}/player",
            })
        ret["play_lists"].append(lst)
    return jsonify(ret)


@mod.route("/<token>/<playlist>/<episode>")
async def anime_info(token: str, playlist: str, episode: str):
    """获取视频信息"""
    url = await agent.get_anime_real_url(token, int(playlist), int(episode))
    info = {
        "raw_url": f"{domain}/anime/{token}/{playlist}/{episode}/url",
        "proxy_url": f"{domain}/proxy/anime/{token}/{playlist}/{episode}",
        "format": url.format,
        # "resolution": url.resolution,
        "size": url.size,
        "lifetime": url.left_lifetime
    }
    return jsonify(info)


@mod.route("/<token>/<playlist>/<episode>/url")
async def redirect_to_real_url(token: str, playlist: str, episode: str):
    """重定向到视频直链, 防止直链过期导致播放器无法播放"""
    proxy = await agent.get_anime_proxy(token, int(playlist), int(episode))
    if not proxy or not proxy.is_available():
        return Response("Resource not available", status=404)
    if proxy.is_enforce_proxy():  # 该资源启用了强制代理
        return redirect(f"/proxy/anime/{token}/{playlist}/{episode}")
    return redirect(proxy.get_real_url())


@mod.route("/<token>/<playlist>/<episode>/player")
async def player_without_proxy(token, playlist, episode):
    """视频直链播放测试"""
    url = f"{domain}/anime/{token}/{playlist}/{episode}"
    return await render_template("player.html", info_url=url)
