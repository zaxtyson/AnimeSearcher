from quart import Blueprint

mod = Blueprint("music", __name__, url_prefix="/music")


@mod.route("/")
async def index():
    return "The interface has not yet been implemented"
