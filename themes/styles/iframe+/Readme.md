
# Iframe+

增强AuiPlayer播放器被作为iframe引入时的功能。

如果你不需要使用iframe来嵌入AuiPlayer，则你使用不到此主题。同时该主题也未被添加到主题列表中进行识别。

> 将使用iframe引入AuiPlayer的窗口称为父窗口，被引入的AuiPlayer窗口称为子窗口
> 以下都将使用`AuiController`作为这个全局变量的名称（可以到`aui-export.js`中修改）。

## 介绍

启用或引入该主题script文件`aui-export.js`后，
如果播放器被作为iframe嵌入使用，则会利用一个全局变量(默认名为`AuiController`)
来帮助子父窗口进行跨iframe通信。

> 这只是一个副本主题，用于留存可选功能，我们仍然建议部署时直接将其中的`aui-export.js`文件
> 添加入全局子主题风格custom中以进行默认加载。
> 具体的方式是复制`aui-export.js`到/themes/styles/custom目录下，然后打开该目录的entry.json添加"aui-export.js"到 "scripts" 数组中。

## 功能

- 构建全局变量`AuiController`至父窗口

该全局变量可以用来配置相关拓展功能，
你可以直接在父窗口提前配置该对象：(此时iframe还未加载完成)
```js
if(!window.AuiController){ // window 可以省略
  window.AuiController = {
    onReady: new Function(), // 当播放加载完成调用
    autoHeight, // 配置是否启用autoHeight调整
  };
}
```

而在AuiPlayer iframe加载完成后，保持iframe的src加载的页面在"/aui-player"则aui-export.js将会始终
将一系列操控AuiPlayer的方法作为对象添加到AuiController上:
```js
console.log(AuiController);
// > Object { onReady: undefined, path: "/aui-player?sort=0", addEpisodeByIndex: addEpisodeByIndex(), utils: {…}, utility: {…}, auiplayer: {…}, dlplayer: {…}, addPlayerHotkey: setup(), addToPlaylist: c(), addPlaylist: y(), … }
// onReady: undefined
// path: "/aui-player?sort=0"
// status: "idle"
// addEpisodeByIndex: function addEpisodeByIndex()
// addPlayerHotkey: function setup()
// addPlaylist: function y()
// addToPlaylist: function c()
// auiplayer: Object { loadListData: y(), toggleMetaList: y(), toggleVideo: y(), … }
// dlplayer: Object { options: {…}, events: {…}, arrow: false, … }
// utility: Object { _on: _on(), _once: _once(), _off: _off(), … }
// utils: Object { CasualMode: Getter, arbitraryFree: Getter, arbitraryWrap: Getter, … }
// <prototype>: Object { … }
```
通过暴露在其上的方法，你将很容易的对播放器进行各种操控，视频播放控制，播放列表控制，添加切换视频，添加弹幕等。

这里可以找到使用的相关信息： [API-Config](https://lozyue.github.io/AnimeSearcherUI/theme-dev/style/api-config.html#utility)

- 完成初始化加载工作

加载播放完成时要做的总可以写在onReady回调中进行，
并使用以下方式能保证会被在正确的时机调用且仅调用一次。

```js
// 最快的执行初始化操作，同时可以不用管理当前文档与iframe的加载顺序
function init(){
  // 初始化工作写在这 ...
}
if(AuiController&& AuiController.status == "idle"){
  init();
}else{
  AuiController = {
    onReady: init,
  };
}
```
这主要就是利用了加载完成后主题script会添加一个`status=idle`属性到AuiController全局变量中。

- 增加根据视频分辨率自动调整iframe高度

因此在布局上你只需要关注创建iframe的宽度即可。

建议如下方式引用：
```html
<iframe id="auiplayer"
  src="https://your.deploy.address/#/aui-player?webfull=true"
  width="100%" height="0" allow="fullscreen" frameborder="0"
></iframe>
```
如果你不需要设定初始的高度，可以总是设置为0.

当一个有效的视频加载以后将会自动调整合适的高度。

要禁用这个功能来总是保持播放器在一个固定高度的话初始配置`AuiController.autoHeight=false`即可

- addEpisodeByIndex

增加一个工厂函数用于辅助防止重复添加视频到播放队列。
