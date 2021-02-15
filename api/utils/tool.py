from base64 import b64encode as _b64encode
from hashlib import md5 as _md5

from zhconv import convert

__all__ = ["convert_to_zh", "convert_to_tw", "md5", "b64encode"]


def convert_to_zh(text: str) -> str:
    """
    繁体中文转简体中文

    :param text: 繁体字符串
    :return: 简体字符串

    >>> convert_to_zh("從零開始的異世界")
    '从零开始的异世界'
    """
    return convert(text, "zh-cn")


def convert_to_tw(text: str) -> str:
    """
    简体中文转繁体中文

    :param text: 简体字符串
    :return: 繁体字符串

    >>> convert_to_tw("从零开始的异世界")
    '從零開始的異世界'
    """
    return convert(text, "zh-tw")


def md5(text: str) -> str:
    """
    计算字符串的 MD5 值

    :param text: 待计算的文本
    :return: md5 字符串

    >>> md5("从零开始的异世界")
    '6ce5c6d9c3c445e8ad93bcbb7453e590'
    """
    return _md5(text.encode("utf-8")).hexdigest()


def b64encode(text: str) -> str:
    """计算 Base64 值

    :param text: 待计算的文本
    :return: base64 字符串

    >>> b64encode("从零开始的异世界")
    '5LuO6Zu25byA5aeL55qE5byC5LiW55WM'
    """
    return _b64encode(text.encode("utf-8")).decode("utf-8")
