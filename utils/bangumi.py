from core.cache import cache
from core.config import config
from core.http_client import client

__all__ = ["get_bangumi"]


# B站更新不是很及时, 改用 bangumi 的接口
# bili_mainland = "https://bangumi.bilibili.com/web_api/timeline_cn"
# bili_overseas = "https://bangumi.bilibili.com/web_api/timeline_global"


async def get_bangumi() -> dict:
    data = cache.get("bangumi")
    if not data:
        bangumi_api = "https://api.bgm.tv/calendar"
        async with client.get(bangumi_api) as r:
            data = await r.json(content_type=None)
        if data:
            cache.set("bangumi", data, config.get_cache_policy_of("anime_bangumi"))
    return data
