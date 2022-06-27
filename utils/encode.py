import base64
import hashlib
import json
from urllib.parse import unquote_plus as unquote
from typing import Tuple

__all__ = ["encode_token", "decode_token", "validate_token", "md5", "b64encode", "unquote"]


# TODO: optimize token length

def encode_token(module: str, kwargs: dict) -> str:
    data = module + "|" + json.dumps(kwargs)
    return base64.urlsafe_b64encode(data.encode()).decode()


def decode_token(token: str) -> Tuple[str, dict]:
    try:
        data = base64.urlsafe_b64decode(token).decode()
        module, kwargs = data.split("|", 1)
        return module, json.loads(kwargs)
    except ValueError:
        return "", {}


def validate_token(token: str) -> bool:
    mod, args = decode_token(token)
    return mod != 0 and len(args) != 0


def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def b64encode(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode()


if __name__ == '__main__':
    # print(encode_token("anime.zzzfun.ZzzFun", {"next": "/xxxxxxxxxx.html"}))
    # print(decode_token("YW5pbWUuenp6ZnVuLlp6ekZ1bnx7Im5leHQiOiAiL3h4eHh4eHh4eHguaHRtbCJ9"))
    # print(decode_token("YW5pbWUuZGVtb3x7ImFpZCI6ICIxMjM0LTEifQ=="))
    print(validate_token("YW5pbWUuZGVtb3x7ImFpZCI6ICIxMjM0LTEifQ=="))
