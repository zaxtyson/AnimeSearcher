from sanic import Sanic
from sanic_cors import CORS

from utils.views import template
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
