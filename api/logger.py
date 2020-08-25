import logging
import os
import time

__all__ = ["logger"]

# 调试日志设置
logger = logging.getLogger('anime')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

# 输出日志到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# 输出日志到文件
time_now = time.strftime("%Y-%m-%d")
logging_path = os.path.dirname(__file__) + "/logs"
if not os.path.exists(logging_path):
    os.makedirs(logging_path)
file_handler = logging.FileHandler(f"{logging_path}/{time_now}.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)


