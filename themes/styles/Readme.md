# 主题风格

进行主题超越配色外的风格和功能美化。

这个文件夹下是主题风格文件夹，不要搞错了哟


## 简介

可以用自定义css和注入JavaScript充分利用资源文件等的方式来进行主题美化，更接近真正意义上的主题

为了丰富主题的功能，主题风格除了支持自定义css进行样式美化外

UI系统还为主题提供了可选的JavaScript辅助支持，并提供部分API供开发者调用。

欢迎定制和分享贡献你的主题！


## 添加一个自定义主题

以主题名称新建一个主题文件夹

在主题风格文件夹下配置entry.json内容如下既可以初始化一个主题风格的基本信息
```js
{
  "name": "fantasy", // 主题名称 供显示 请尽可能保持与主题文件夹名称相同
  "description": "磨砂风梦幻主题", // 简介，可选
  "author": {
    "nick": "Lozyue", // 作者，可选
    "avatar": "avatar.png", // 头像，可选
    "link": "http://github.com/lozyue", // 可以留个主页，可选
  },
  "home": "http://github.com/lozyue/animesearcherui/#public/themes/fantasy", // 可以留一个主题介绍链接，可选
  "thumbs": "/thumbs.jpg" , // 缩撸图，可选 可以是路径字符串或者路径字符串数组，按顺序靠前的缩略图为主
  "blending": "dew", // 指定与主题风格配合食用的主题配色为 dew, 若用户安装了相应主题配色，则在启用该主题风格是应用相应配色.
  "style": "/main.css", // 主题css样式，可以使路径字符串或者路径字符串数组，按顺序加载 支持超链接
  "script": "/main.js", // 主题script辅助，可选 按顺序加载，写法同 style 配置项
  "async_script": false // 可选，多个主题js文件时，同步加载（按顺序加载） 还是异步加载（取决于网络或储存）
}
```

其中，加载文件的路径字符串可以以`/`开头也可以省略，值为相对于主题文件夹的路径字符串，支持超链接，超链接等网络地址请包括协议部分。


## 全部配置项

为方便开发，这里按json格式写一下entry文件的完整部分方便配置：

entry.json
```json
{
  "name": "fantasy",
  "description": "磨砂风梦幻主题",
  "author": {
    "nick": "Lozyue",
    "avatar": "avatar.png",
    "link": "http://github.com/lozyue",
  },
  "home": "http://github.com/lozyue/animesearcherui/#public/themes/fantasy",
  "thumbs": "/thumbs.jpg" ,
  "style": ["/main.css"],
  "script": ["/main.js"],
  "async_script": false
}
```
不需要的配置项可以留空或者删除，但编写后时请注意检查json文件格式的正确性。



### 全局CSS类架构

下面给出CSS骨架类分布表，用以开发主题设定样式参考。

表中推荐的CSS类在未来的更新中将较少发生改变。

- #app
  - #app-root
    - #app-main
      - #main-container
        - #[rootPageName]
         - .main ?
           - [inner...]

### 主题风格Script API系统

要使用主题风格的Script，

仅需在文件夹中放置编写好的JavaScript文件，将需要加载的JS文件相对路径

使用 `window` 下的全局函数 `$theme` 来载入主题风格script

Function `$theme` @param 
```ts
// 函数原型
function $theme(func: (utility: Utility)=>any, options ): null{}
```
通过传递一个回调函数, 可以方便的根据 `options` 进行配置 实现在UI加载不同恰当的时机自动执行相应回调函数设置。

其中回调函数可以接收一个参数，该参数为一个Utility对象，提供了供主题开发支持的各种API和功能接口

回调参数文档：

| `utility`的属性 | type | description |
| :------: | :------: | :------ |
| setUserOpiton | Function | 用于增加供用户选择的主题设置项，根据格式配置即可正确显示在主题设置之中 |
| 稍微长一点的文本 | 短文本 | 中等文本 |


目前支持的API有限

主要包括以下几类：

#### 设置项API




### 动态主题风格开发建议

- 谨慎直接使用LocalStorage

未防止与程序主体冲突的原因。并且UI系统提供了设置项与存储一体的API

- 不建议使用大量消耗性能的JS动画

Canvas、animation等； 原因不言而喻

- 不建议在 `$theme` 方法下定义使用大量的函数

最好将全部功能都放到 `$theme` 函数中进行实现
