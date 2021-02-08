from os.path import dirname

from quart import Quart, render_template, send_from_directory


class WebUI(object):

    def __init__(self, host: str, port: int):
        self._path = f"{dirname(__file__)}/static"
        self._host = host
        self._port = port
        self._app = Quart(
            import_name=__name__,
            static_folder=self._path,
            template_folder=self._path
        )

    def run(self):
        self._init_routers()
        self._app.run(host=self._host, port=self._port, debug=False, use_reloader=False)

    def _init_routers(self):
        @self._app.after_request
        async def apply_caching(resp):
            """设置响应的全局 headers, 允许跨域"""
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            return resp

        @self._app.route("/", methods=["GET"])
        async def index():
            return await render_template("index.html")

        @self._app.route("/favicon.ico", methods=["GET"])
        async def favicon():
            return await send_from_directory(self._path, f"favicon.ico", as_attachment=True)

        @self._app.route("/js/<path:file>", methods=["GET"])
        async def send_js_file(file):
            return await send_from_directory(self._path, f"js/{file}", as_attachment=True)

        @self._app.route("/img/<path:file>", methods=["GET"])
        async def send_img_file(file):
            return await send_from_directory(self._path, f"img/{file}", as_attachment=True)
