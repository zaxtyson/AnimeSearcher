from zhconv import convert

__all__ = ["convert_to_zh", "convert_to_tw"]


def convert_to_zh(text: str) -> str:
    """将繁体转换为简体"""
    return convert(text, "zh-cn")


def convert_to_tw(text: str) -> str:
    """简体转繁体"""
    return convert(text, "zh-tw")
