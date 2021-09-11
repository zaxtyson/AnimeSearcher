from quart import Blueprint

mod = Blueprint("comic", __name__, url_prefix="/comic")


@mod.route("/")
async def index():
    return "The interface has not yet been implemented"
