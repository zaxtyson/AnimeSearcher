from quart import Blueprint, request

from web.utils.statistic import Statistics

mod = Blueprint("statistics", __name__, url_prefix="/statistics")
stat = Statistics()


@mod.route("/")
async def statistics():
    """百度统计转发, 用户体验计划"""
    return await stat.transmit(request)


@mod.route("/<hm_js>")
async def get_statistics_js(hm_js):
    return await stat.get_hm_js(request)
