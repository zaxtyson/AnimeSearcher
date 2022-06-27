from jinja2 import Environment, PackageLoader, select_autoescape
from sanic import Sanic, html
from sanic_cors import CORS

jinja_env = Environment(
    loader=PackageLoader("views", "../templates"),
    autoescape=select_autoescape(["html"])
)


def template(filename: str, **kwargs):
    tpl = jinja_env.get_template(filename)
    return html(tpl.render(kwargs))


# register routers
from views.anime import bp_anime
from views.danmaku import bp_danmaku
from views.proxy import bp_proxy
from views.system import bp_system

app = Sanic(__name__)
CORS(app)

app.blueprint(bp_anime)
app.blueprint(bp_danmaku)
app.blueprint(bp_system)
app.blueprint(bp_proxy)


@app.get("/")
async def index(_):
    return template("index.html")
