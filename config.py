"""
全局配置文件
"""

# 绑定的 IP, 服务器端请使用公网 IP
# 如果不确定可以使用 0.0.0.0
host = "127.0.0.1"

# API 服务的端口
port = 6001

# 设置资源路径的域名部分, 端口使用 port
# 如: http://www.foo.bar
domain = "http://localhost"

# 设置资源路径的前缀, 结尾不加 "/"
# 反向代理时使用, 该选项会覆盖 domain 的设置
# 如: http://www.foo.bar/anime-api
proxy_prefix = ""
