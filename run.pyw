import os
import sys
import webbrowser
from threading import Thread
from tkinter import Tk, Label, CENTER, Button

from api.config import CONFIG
from api.router import Router

PATH = os.path.dirname(os.path.realpath(sys.argv[0]))


class SimpleServer:

    def __init__(self):
        self.ui = Tk()
        self.init_ui()
        # self.open_browser()  # 自动打开一次

    def init_ui(self):
        self.ui.title("AnimeSearcher")
        self.ui.wm_iconbitmap(f"{PATH}/logo.ico")
        width, height = 350, 200
        screen_width = self.ui.winfo_screenwidth()
        screen_height = self.ui.winfo_screenheight()
        position = '%dx%d+%d+%d' % (width, height, (screen_width - width) / 2, (screen_height - height) / 2)
        self.ui.geometry(position)
        self.ui.resizable(width=False, height=False)
        Label(self.ui, text="后台服务正在运行, 请不要关闭此窗口", justify=CENTER, pady=50).pack()
        btn = Button(self.ui, text="[ 打开浏览器 ]", relief="groove", command=self.open_browser)
        btn.pack()

    def open_browser(self):
        """打开一个浏览器窗口"""
        webbrowser.open(f"file://{PATH}/web/index.html")

    def run(self):
        self.ui.mainloop()


if __name__ == '__main__':
    host = CONFIG.get("system", "host")
    port = CONFIG.get("system", "port")
    domain = CONFIG.get("system", "domain")

    server = SimpleServer()
    router = Router(host, int(port))
    router.set_domain(domain)  # if needed
    Thread(target=router.run, daemon=True).start()
    server.run()
