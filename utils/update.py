from datetime import datetime, timedelta

from core.http_client import client
from models.system import ReleaseInfo, ReleaseAsset, SystemVersion
from version import VERSION

__all__ = ["get_system_version"]

repo_api = "https://api.github.com/repos/zaxtyson/AnimeSearcher/releases"


async def get_system_version() -> SystemVersion:
    async with client.get(repo_api) as r:
        data = await r.json()

    latest_data = data[0]
    current_data = list(filter(lambda x: x["tag_name"] == VERSION, data))
    current_data = current_data[0] if current_data else latest_data

    sys_info = SystemVersion()
    sys_info.current = get_release_info(current_data)
    sys_info.latest = get_release_info(latest_data)

    current_ver = get_ver_num(sys_info.current.version)
    latest_ver = get_ver_num(sys_info.latest.version)
    if latest_ver > current_ver:
        sys_info.need_update = True

    return sys_info


def get_ver_num(tag_name: str) -> int:
    major, minor, patch = [int(i) for i in tag_name.split(".")]
    return major * 10000 + minor * 100 + patch


def get_release_info(data: dict) -> ReleaseInfo:
    info = ReleaseInfo()
    info.version = data["tag_name"].replace("v", "")  # v1.2.3
    info.release_url = data["html_url"]
    info.release_log = data["body"]
    info.release_time = format_time(data["published_at"])

    for item in data["assets"]:
        asset = ReleaseAsset()
        asset.name = item["name"]
        asset.size = item["size"]
        asset.url = item["browser_download_url"]
        info.assets.append(asset)

    return info


def format_time(tm: str) -> str:
    d = datetime.strptime(tm, "%Y-%m-%dT%H:%M:%SZ")
    d += timedelta(hours=8)
    return datetime.strftime(d, "%Y-%m-%d %H:%M:%S")
