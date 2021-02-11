from base64 import b64encode as _b64encode
from hashlib import md5 as _md5

from zhconv import convert

__all__ = ["convert_to_zh", "convert_to_tw", "md5", "b64encode"]


def convert_to_zh(text: str) -> str:
    """将繁体转换为简体"""
    return convert(text, "zh-cn")


def convert_to_tw(text: str) -> str:
    """简体转繁体"""
    return convert(text, "zh-tw")


def md5(text: str) -> str:
    """计算 MD5"""
    return _md5(text.encode("utf-8")).hexdigest()


def b64encode(text: str) -> str:
    """计算base64"""
    return _b64encode(text.encode("utf-8")).decode("utf-8")
