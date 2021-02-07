__all__ = ["Tokenizable", "singleton"]


def singleton(cls):
    """
    单例模式装饰器, 不考虑线程安全
    """
    instance = cls()
    cls.__new__ = cls.__call__ = lambda cls: instance
    cls.__init__ = lambda self: None
    return instance


class Tokenizable(object):

    @property
    def token(self) -> str:
        """生成一个可唯一标识对象本身的字符串"""
        return ""

    @classmethod
    def build_from(cls, token: str):
        """从 token 字符串构建一个可用的对象"""
        pass
