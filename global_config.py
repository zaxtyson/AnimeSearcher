"""
全局配置文件
"""

# 绑定的 IP, 服务器端请使用公网 IP
# 如果不确定可以使用 0.0.0.0
host = "127.0.0.1"

# API 服务的端口
port = 6001

# 设置资源路径的前缀, 结尾不加 "/"
# 反向代理或者需要设置域名时使用
# 如: http://www.foo.bar/anime-api
#     http://www.foo.bar:12345/anime-api
root_prefix = ""

# 强制代理图片资源， 服务器部署时遇到图片跨域请启用此项
enforce_proxy_images = True

# 强制代理全部视频流量， 通常使用默认策略即可
enforce_proxy_videos = False

# 缓存策略, 秒
cache_expire_policy = {
    "anime": 60 * 30,  # 视频详情和播放列表缓存
    "bangumi": 60 * 60 * 1,  # 番剧更新数据
    "danmaku": 60 * 60 * 12  # 弹幕库搜索结果及弹幕数据
}
