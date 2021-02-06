from threading import Thread

from api.router import APIRouter
from config import *
from web.router import WebUI


class App(object):

    def __init__(self):
        self._api = APIRouter(host, api_port)
        self._web = WebUI(host, web_port)
        self._api.set_domain(domain)

    def run(self):
        api_thread = Thread(target=self._api.run)
        web_thread = Thread(target=self._web.run)
        api_thread.start()
        web_thread.start()


if __name__ == '__main__':
    app = App()
    app.run()
