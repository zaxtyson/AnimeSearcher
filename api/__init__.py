from os.path import dirname

from api.config import Config
from api.core.agent import Agent
from api.core.proxy import RequestProxy
from global_config import *

# ＡＰＩ　根目录
root_path = dirname(__file__)

# 全局对象
agent = Agent()
config = Config()
request_proxy = RequestProxy()

# 资源的域名
domain = f"http://{host}:{port}"
domain = root_prefix if root_prefix else domain
