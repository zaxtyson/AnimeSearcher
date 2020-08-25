<p align="center"><img src="https://ae01.alicdn.com/kf/U150c6f229b47468781c941fdd80545eak.png" width="200"></p>
<h3 align="center">- Anime API -</h3>

# 还在开发中...

## 简介

这是一个用于动漫、弹幕数据抓取的框架, 用于解析视频直链、搜索视频匹配的弹幕库、代理访问视频资源。
它提供了一系列 Web 接口, 可供前端播放器使用。当视频直链无法播放时, API 可以代理访问原始视频, 
返回视频数据流给前端播放器, 以绕过视频的防盗链。

## 示例

> 很简单就可以启用一个路由
```
from api.router import Router

if __name__ == '__main__':
    rt = Router()
    rt.listen("127.0.0.1", 6001)
    rt.run()
```

> Demo

http://hnyz.fun:6001/

## Web 接口

https://zaxtyson.gitbook.io/anime-api/

## 如何编写资源搜索引擎

待编辑

## 如何编写弹幕搜索引擎

待编辑

