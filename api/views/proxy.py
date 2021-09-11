from quart import Blueprint, Response, request

from api import request_proxy, agent, domain

mod = Blueprint("proxy", __name__, url_prefix="/proxy")


@mod.route("/image/<path:raw_url>")
async def image_proxy(raw_url):
    """对跨域图片进行代理访问, 返回数据"""
    return await request_proxy.make_response(raw_url)


@mod.route("/anime/<token>/<playlist>/<episode>")
async def anime_stream_proxy(token, playlist, episode):
    """代理访问普通的视频数据流"""
    proxy = await agent.get_anime_proxy(token, int(playlist), int(episode))
    if not proxy:
        return Response("proxy error", status=404)

    if proxy.get_stream_format() == "hls":  # m3u8 代理
        proxy.set_chunk_proxy_router(f"{domain}/proxy/hls/{token}/{playlist}/{episode}")
        return await proxy.make_response_for_m3u8()
    else:  # mp4 代理
        range_field = request.headers.get("range")
        return await proxy.make_response_with_range(range_field)


@mod.route("/hls/<token>/<playlist>/<episode>/<path:url>")
async def m3u8_chunk_proxy(token, playlist, episode, url):
    """代理访问视频的某一块数据"""
    proxy = await agent.get_anime_proxy(token, int(playlist), int(episode))
    if not proxy:
        return Response("m3u8 chunk proxy error", status=404)
    return await proxy.make_response_for_chunk(url, request.args.to_dict())
