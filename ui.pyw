import os
import sys
import webbrowser
from threading import Thread
from tkinter import Tk, Label, CENTER, Button

from api.config import Config
from api.router import app_run

PATH = os.path.dirname(os.path.realpath(sys.argv[0]))


class SimpleUI:

    def __init__(self):
        self.ui = Tk()
        self.init_ui()
        self.open_browser()  # 自动打开一次

    def init_ui(self):
        self.ui.title("AnimeSearcher")
        if os.name == "nt":
            self.ui.wm_iconbitmap(f"{PATH}/logo.ico")
        width, height = 350, 200
        screen_width = self.ui.winfo_screenwidth()
        screen_height = self.ui.winfo_screenheight()
        position = '%dx%d+%d+%d' % (width, height, (screen_width - width) / 2, (screen_height - height) / 2)
        self.ui.geometry(position)
        self.ui.resizable(width=False, height=False)
        tag = Config().get("version").get("tag")
        Label(self.ui, text=f"当前版本: {tag}", justify=CENTER, pady=20).pack()
        Label(self.ui, text="后台服务正在运行, 请不要关闭此窗口", justify=CENTER).pack()
        Label(self.ui, text="", pady=10).pack()
        btn = Button(self.ui, text="[ 打开浏览器 ]", relief="groove", command=self.open_browser)
        btn.pack()

    @staticmethod
    def open_browser():
        """打开一个浏览器窗口"""
        webbrowser.open(f"{PATH}/web/static/index.html")

    def run(self):
        self.ui.mainloop()


if __name__ == '__main__':
    ui = SimpleUI()
    Thread(target=app_run, daemon=True).start()
    ui.run()
