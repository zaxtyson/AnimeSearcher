<p align="center"><img src="https://ae01.alicdn.com/kf/U150c6f229b47468781c941fdd80545eak.png" width="200"></p>
<h3 align="center">- Anime Searcher -</h3>
<p align="center">
<img src="https://img.shields.io/github/v/release/zaxtyson/AnimeSearcher.svg?logo=bilibili">
</p>

## 简介

通过整合第三方网站的视频和弹幕资源, 提供最舒适的看番体验~

番剧、国漫、电影、美剧、日剧、韩剧、泰剧，应有尽有，甚至还可以看 CCTV 和地方卫视台~

目前有 6 个资源搜索引擎和 5 个弹幕搜索引擎, 资源丰富, 更新超快, 不用下载, 在线观看,
再也不用去那些飘满广告的网站或者网盘找资源了

自动匹配第三方网站的弹幕, 看番怎能少了弹幕, 就算是白嫖我们也要嫖出 VIP 一般的体验
( •̀ ω •́ )✧

Tips: 因为资源引擎 `eyunzhu` 时常有不雅水印~~荷官在线发牌~~，默认关闭。 弹幕引擎 `bahamut` 服务器位于台湾,
访问速度可能较慢慢，也默认关闭。

## 界面
![](https://s1.ax1x.com/2020/09/02/wS2JO0.png)

![](https://s1.ax1x.com/2020/09/02/wS4giT.png)

![](https://s1.ax1x.com/2020/09/02/wSIgv4.png)

![](https://s1.ax1x.com/2020/09/02/wSo2Jf.png)

## 维护
- [lozyue](https://github.com/Cangqifeng) : 前端 UI 界面
- [zaxtyson](https://github.com/zaxtyson) : 后端 API 框架

## 下载

- Linux 用户 clone 后运行 `run.py` 即可
- Windows 用户[点这里下载](https://zaxtyson.lanzous.com/b0f1ukafc)

## 扩展

如果你有好康的网站, 可以编写资源引擎添加到本项目, [详情](https://github.com/zaxtyson/Anime-API)

## 更新日志

### `v0.9.9`

- 修复 Windows 安装版中弹幕源 bahamut 繁简体转换异常的问题
- 修复引擎 bimibimi 部分视频解析失败的问题和弹幕 undefined 的问题
- 修复 zzfun 接口变化导致无法播放视频的问题
- 新增弹幕源 youku
- 新增弹幕源 tencent
- 新增资源引擎 meijuxia
- 补充 bilibili 影视区弹幕
- UI 美化, 新增一套主题

### TODO
- [ ] 主页番剧更新列表
- [ ] IPTV 直播(CCTV/地方台)