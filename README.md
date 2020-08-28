<p align="center"><img src="https://ae01.alicdn.com/kf/U150c6f229b47468781c941fdd80545eak.png" width="200"></p>
<h3 align="center">- Anime Searcher -</h3>

# 还在开发中...

## 简介

通过整合第三方网站的视频和弹幕资源, 给白嫖党提供最舒适的看番体验~

目前有 4 个资源搜索引擎和 1 个弹幕搜索引擎, 资源丰富, 更新超快, 不用下载, 在线观看, 
再也不用去那些飘满广告的网站或者网盘找资源了

自动匹配第三方网站的弹幕, 没有弹幕还看啥番, 就算是白嫖我们也要嫖出 VIP 一般的用户体验 
( •̀ ω •́ )✧

## 维护
- [lozyue](https://github.com/Cangqifeng) : 前端 UI 界面
- [zaxtyson](https://github.com/zaxtyson) : 后端 API 框架 

## 下载

- Linux
- Windows

## 扩展

Q: 我有个好康的网站, 如何把它添加到本项目?  

A: 为它编写一个资源引擎, 放到 `api/engines` 目录下, 在配置文件 `api/config.json` 中将其启用即可  

Q: 如何编写资源引擎?

A: API 提供了解析框架, 你只需要按它给的流程一步一步提取网页数据即可, 剩下的事情交给框架去做, 详情见项目 Wiki 页