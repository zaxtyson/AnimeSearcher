from json import dumps

__all__ = ["DataClass"]


class DataClass:
    HIDE_PRIVATE_FIELD = True
    HIDE_FILED = []

    def to_dict(self) -> dict:
        d = {}
        for k, v in self.__dict__.items():
            if self.HIDE_PRIVATE_FIELD and k.startswith("_"):
                continue
            if k in self.HIDE_FILED:
                continue
            if isinstance(v, DataClass):
                d[k] = v.to_dict()
            elif isinstance(v, dict):
                d[k] = v
                for sk, sv in v.items():
                    # if self.HIDE_PRIVATE_FIELD and sk.startswith("_"):
                    #     continue
                    d[k][sk] = sv
            elif hasattr(v, "__iter__") and not isinstance(v, str):
                d[k] = []
                for item in v:
                    if isinstance(item, DataClass):
                        d[k].append(item.to_dict())
                    else:
                        d[k].append(item)
            else:
                d[k] = v
        return d

    def to_json(self) -> str:
        return dumps(self.to_dict(), ensure_ascii=False)


if __name__ == '__main__':
    class Kv(DataClass):

        def __init__(self, key, value):
            self.key = key
            self.value = value


    class Test(DataClass):

        def __init__(self):
            self.name = "jack"
            self.age = 18
            self.dict1 = {"xx": "xxx", "_yy": "yyy"}
            self.list1 = [80, 90, 99]
            self.list2 = [Kv(1, 2), Kv("key", "value")]
            self._prop1 = "xx"
            self.__prop2 = "yy"


    t = Test()
    print(t.to_dict())

    Test.HIDE_PRIVATE_FIELD = False
    print(t.to_dict())
