import logging
import os
from logging.handlers import TimedRotatingFileHandler

__all__ = ["logger"]

# 调试日志设置
logger = logging.getLogger('anime')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

# 输出日志到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# 输出日志到文件 保存最近 3 小时的日志
logging_path = os.path.dirname(__file__) + "/../logs"
if not os.path.exists(logging_path):
    os.makedirs(logging_path)
file_handler = TimedRotatingFileHandler(filename=logging_path + "/api.log", when="H", interval=1, backupCount=3,
                                        encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
