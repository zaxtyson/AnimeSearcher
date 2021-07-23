<p align="center"><img src="https://ae01.alicdn.com/kf/U150c6f229b47468781c941fdd80545eak.png" width="200"></p>
<h3 align="center">- Anime Searcher -</h3>
<p align="center">
<img src="https://img.shields.io/github/v/release/zaxtyson/AnimeSearcher.svg?logo=bilibili">
</p>

## 简介

整合第三方网站的视频和弹幕资源, 提供最舒适的看番追剧体验

番剧、国漫、电影、美剧、日剧、韩剧、泰剧，应有尽有，甚至还可以看 CCTV 和地方卫视台~

资源丰富, 更新超快, 不用下载, 在线观看, 再也不用去那些飘满广告的网站或者网盘找资源了

自动匹配第三方网站的弹幕, 看番怎能少了弹幕, 就算是白嫖我们也要嫖出 VIP 一般的体验( •̀ ω •́ )✧

我们致力于成为全功能的资源检索工具， 接下来会加入漫画和音乐搜索功能， 敬请期待...

## 界面

*可能不是最新界面, 请以实物为准（笑）

![1.png](https://s1.ax1x.com/2020/10/25/BmtcfP.png)
![2.png](https://s1.ax1x.com/2020/10/25/BmtBeH.png)
![3.png](https://s1.ax1x.com/2020/10/25/BmtrTA.png)
![4.png](https://s1.ax1x.com/2020/10/25/BmtyFI.png)
![5.png](https://s1.ax1x.com/2020/10/25/Bmt6Yt.png)
![6.png](https://s1.ax1x.com/2020/10/25/BmtDwd.png)

## 下载

> Windows

[蓝奏云下载](https://zaxtyson.lanzoux.com/b0f1ukafc)  
[Gitee国内镜像](https://gitee.com/zaxtyson/AnimeSearcher/releases)

> Linux/MacOS

```
git clone https://github.com.cnpmjs.org/zaxtyson/AnimeSearcher.git
cd AnimeSearcher
pip install -r requirements.txt
python app.py
```

使用浏览器打开 `web/index.html` 即可

## 自建服务器

按注释提示修改 `config.py`

```
git clone https://github.com.cnpmjs.org/zaxtyson/AnimeSearcher.git
cd AnimeSearcher
python3.8 -m pip install -r requirements.txt
nohup python3.8 app.py &
```

- 服务器端可能存在多个 Python 版本，请使用 Python3.8+ 运行
- 本程序仅为本地运行设计, 在服务器端运行可能存在某些安全隐患, 请留意
- 如果视频存在防盗链或者存在跨域问题, 会切换至 API 代理, 此时服务器需要从远程读取数据流返回给用户, 
可能给服务器的带宽造成压力, 请不要公开您的 IP 或者域名
- API 使用 6001 端口， 请确保防火墙或者ECS安全组规则放行
- API 提供了的简易播放器, 但是 WebUI 提供了更好的交互性体验, 使用浏览器打开 `web/index.html`, 在主页最下方设置 API 服务地址即可使用 
- WebUI 暂未适配移动端， 界面等待下一个版本的重构, 敬请期待

## 模块扩展

程序目前包括视频、弹幕解析模块, 后面会加入音乐、漫画等解析模块

在 API 的支持下， 您可以很容易的编写一个资源解析模块， 扩展程序的功能

欢迎提交 PR, 但是请提交稳定优质的资源哦 :)

[Anime-API](https://github.com/zaxtyson/Anime-API)  

[API 文档](https://anime-api.readthedocs.io/zh_CN/latest/index.html)

## 维护

- [lozyue](https://github.com/Cangqifeng) : 前端 UI 界面
- [zaxtyson](https://github.com/zaxtyson) : 后端 API 框架

如果有建议或者吐槽, 请找对人哦~~

## 更新日志

## `v1.4.3`

- 新增视频引擎 `4K鸭奈菲(4Kya)`
- 新增视频引擎 `Lib在线(libvio)`  
- 新增视频引擎 `阿房影视(afang)`  
- 修复视频引擎 `AgeFans` 域名映射异常的问题
- 修复视频引擎 `ZzzFun` 部分视频无法播放的问题
- 修复视频引擎 `bimibimi` 无法搜索和播放的问题
- 修复视频引擎 `K1080` 部分视频无法播放的问题
- 弃用视频引擎 `Meijuxia`, 质量太差
- 弃用视频引擎 `bde4`

### `v1.4.2`

- 修复视频引擎 `K1080` 失效的问题

### `v1.4.1`

- 修复视频引擎 `ZzzFun` 资源迁移导致无法使用的问题
- 修复视频引擎 `K1080` 部分视频无法播放的问题
- 修复视频引擎 `樱花动漫(yhdm)` 域名变更的问题
- 视频视频引擎 `哔嘀影视(bde4)` 切换备用域名
- 过滤视频引擎 `AgeFans` 部分无效视频源
- 过滤弹幕引擎 `爱奇艺(iqiyi)` 和 `腾讯视频(tencent)` 无关搜索结果   
- 修复弹幕引擎  `哔哩哔哩(bilibili)` 部分番剧弹幕抓取失败的问题[#12](https://github.com/zaxtyson/AnimeSearcher/issues/12)
- 移除失效视频源 `eyunzhu` 和弹幕源 `哔咪哔咪(bimibimi)`

### `v1.4.0`

- 支持 HLS 格式视频流量代理, 支持混淆流量解码
- 对经常被墙的网站做了 A 记录, 防止域名失效, 加快 DNS 解析速度
- 新增视频搜索引擎 `哔嘀影视(bde4)`
- 新增弹幕搜索引擎 `爱奇艺(iqiyi)`
- 修复引擎 `k1080`, `meijuxia`, 与官方保存同步
- 修复 `优酷(youku)` 弹幕搜索无结果的问题
- 修复 `哔哩哔哩(bilibili)` 120分钟之后无弹幕的问题[#9](https://github.com/zaxtyson/AnimeSearcher/issues/9)
- 修复 `ZZZFun` 播放路线1

### `v1.3.1`

- 过滤了 k1080 部分无效视频
- 修复了[弹幕显示区域]设置项无法保存的问题
- 使用续命大法修复部分源播放途中直链失效的问题

### `v1.3.0`

- API 完全改用异步框架重构, 效率大幅提升, 支持服务器端部署
- 修复了几个番剧模块出现的问题, 与源网站同步更新
- 修复了弹幕库的一些问题, 结果更多更准, 过滤了弹幕中无关的内容
- 修复了直链有效期太短导致视频播到一半失败的问题
- UI 改进, 用户体验更佳, 支持连接远程服务器

### `v1.1.8`

- 新增引擎 k1080p
- 修复 youku 某些弹幕解析失败的问题
- 修复 bilibili 用户上传视频弹幕解析失败的问题
- 修复 bahamut 网站更新导致弹幕抓取失败的问题
- 搜索结果异步加载, 体验大幅上升
- 历史记录功能增强, 自动解析上次访问页面
- 界面、播放器、弹幕显示、快捷键等多处细节优化
- 程序主界面不再显示控制台

### `v1.0.0`

- 修复 agefans 无法访问的问题(被墙)
- 外挂弹幕支持
- 弹幕显示优化
- 支持播放历史记录

### `v0.9.9`

- 修复 Windows 安装版中弹幕源 bahamut 繁简体转换异常的问题
- 修复引擎 bimibimi 部分视频解析失败的问题和弹幕 undefined 的问题
- 修复 zzfun 接口变化导致无法播放视频的问题
- 修复 agefans 视频无法解析的问题
- 新增弹幕源 youku
- 新增弹幕源 tencent
- 新增资源引擎 meijuxia
- 补充 bilibili 影视区弹幕
- UI 美化, 新增一套主题
- 主页番剧更新列表
- IPTV 直播(CCTV/地方台)