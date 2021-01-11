import os
import sys
import webbrowser
from threading import Timer

from api.router import Router


def open_index():
    """打开浏览器"""
    index = "file://" + os.path.dirname(os.path.realpath(sys.argv[0])) + "/web/index.html"
    webbrowser.open(index)


if __name__ == '__main__':
    rt = Router()
    rt.listen("127.0.0.1", port=6001, ws_port=6002)
    rt.enable_debug()
    Timer(1, open_index).start()
    rt.run()
