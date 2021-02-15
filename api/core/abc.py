__all__ = ["Tokenizable", "singleton"]


def singleton(cls):
    """
    单例模式装饰器, 不考虑线程安全

    :param cls: 待装饰的类
    :return: 装饰的类
    """
    instance = cls()
    cls.__new__ = cls.__call__ = lambda cls: instance
    cls.__init__ = lambda self: None
    return instance


class Tokenizable(object):

    @property
    def token(self) -> str:
        """
        计算对象的唯一标识

        :return: 可唯一标识对象本身的字符串
        """
        return ""

    @classmethod
    def build_from(cls, token: str):
        """
        从标识逆向构建一个对象

        :param token: 对象标识
        :return: 本类对象(只含必要信息)
        """
        pass
