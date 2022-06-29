from functools import wraps

from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import html, json, Request

__all__ = ["template", "check_token"]

from models.resp import GenericResp

jinja_env = Environment(
    loader=PackageLoader("views", "../templates"),
    autoescape=select_autoescape(["html"])
)


def template(filename: str, **kwargs):
    tpl = jinja_env.get_template(filename)
    return html(tpl.render(kwargs))


def check_token(func):
    @wraps(func)
    async def wrapper(request: Request, token: str, *args, **kwargs):
        if not check_token(token):
            return json(GenericResp(code=1, msg="Url token invalid").to_dict())
        await func(request, token, *args, **kwargs)

    return wrapper
