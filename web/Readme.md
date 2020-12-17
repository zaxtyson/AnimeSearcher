# Web UI

AnimeSearcher前端UI项目

By Lozyue


## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

Year, Nothing need to do haha！

It's just a simple Vue3.0 project. Easy to Modify & Build.


## 技术依赖

- 核心基于非完全MVVM框架 `Vue`
- 前端路由`vue-router`
- Material Design Component `Vuetify`
- Promise 的 HTTP 通信组件库 `axios`
- H5弹幕播放器 `DPlayer`
- 加载条 `NProgress`


### Release

- v1.0.0 @2020-14-25

- v0.9.9 @2020-10-25

- v0.9.8 差点正式版

- v0.9.6 体验版

- v0.9.5 不正式体验版

- v0.9.3 beta弹幕体验版

- v0.9.0 beta体验版


### Process

- v1.0.0 Updated @2020-12-15
	- √ 增加观看记录提示消息条回调点击事件，支持直接跳转
	- √ 增加快捷键F、W切换网页全屏和页面全屏，全屏时鼠标中键滚动可调整音量
	- √ 修复了增强了更新检测算法，可检测到子版本
	- √ 加入首页观看历史记录展示修改面板
	- √ 合并弹幕player消息条hover滚动
	- √ 修复读取存储播放设置为空时产生的中断

- v1.0.0-beta 
	- 优化了播放器设置项
	- 修改Dplayer样式，移除多余按钮，弹幕样式速度和UI显示优化，倍速移动到外部
	- 增加本地观看历史记录，最多保存16个
	- 自动检测跳转上次播放进度并提示;搜索结果组件home也结果卡片比例调整，强制等高（Description部分可能会部分遮挡,等待重构）

- fixed bugs 弹幕自动匹配去掉了每轮进行的准确度过低数字搜索匹配，修改了footerMsg错序的问题；修正排序或逆序时右侧选集框定位滞留问题；优化换集显示 @2020-10-21

- v0.9.9 更新！增加了TV板块，优化各种设置项，集成消息队列核心支持搜索弹幕源，增加沉浸模式，增加弹幕的分类开关，增加新番表 @2020-10-21

- 增加了主题切换美化界面，增加了点击定位，追海贼王等长剧不用再苦翻列表了；修复选择弹幕，工具栏设置不同步等一些bug，增强弹幕匹配规则 @2020-10-01

- fixed some bugs @2020-09-11

- v0.9.8优化了排序的实现方法。为搜索记录增加单条删除键。视频页回车搜索新窗口打开。重构了搜索结果路由，前后前进更流畅。

- v0.9.7增加简单搜索记录，更新了HelloWorld页，为Home页卡片增加默认图（手动PS的哦）,更改了排序方式,补充了弹幕引擎设置

- v0.9.6修复限流造成的切换代理失败及代理时手动选择弹幕卡住的bugs

- v0.9.5完成了工具栏的各小按钮功能，选择弹幕功能。优化细节，修复几个bugs

- v0.9.4再次增强了自动匹配，增加了nprogress加载条，选集按钮标题修改，Dplayer出错回调增加节流限制，增加视频底部工具栏，选择弹幕功能暂未完成。

- v0.9.3增加了视频弹幕，自动匹配当前弹幕。略优化了Dplayer错误处理（暂未做限流throttle处理）@2020-08-30

- v0.9.1增加了配置项，修复代理通道无法切换的bug，任存在切换卡住的dplayer内部bug，再次手动选集可缓解。
