/**
 * Main Script of fantasy.
 * Entrance Script.
 */

(function(){
// Start from here.

$theme(
  // Invoke. The this points to the parsered options.
  function(utility, utils, context){
    console.log("%c 主题风格:[Fantasy] %c 应用成功！\n", "color:#fadfa3;background:#030307;padding:5px 0;","color:#000;background:#fadfa3;padding:5px 0;", {utility, utils, context, this: this});
    const { revoke } = context;

    // Add shortcut of AuiPlayer locatted in /anime/details/:
    function addIt(){
      // Should have the same action scope or there will cause memory leak.
      const jumpThrough90 = {
        name: "jump90",
        descriptions: "Anime分区视频播放前进90s",
        commonKey: 'A',
        // enable: true,
        invoke(dlpIns, eve){
          const nowTime = dlpIns.video.currentTime;
          if(nowTime+90 < dlpIns.video.duration){
            dlpIns.seek(nowTime + 90);
            // Given an notify
            dlpIns.notice("向前速降了90s");
          }
        }
      };
      // The impact of addPlayerHotkey will auto remove.
      utility.addPlayerHotkey(jumpThrough90);
      console.log("[Fantasy]: 已添加A键前进90s跳过片头片尾功能");
    }

    if(utility._isHappened("auiplayer-mounted") ) addIt();
    utility._on("auiplayer-mounted", addIt);
    // remove the impact
    revoke(()=>{
      utility._off("auiplayer-mounted", addIt);
    })
  },
  // On Revoke.
  function(){
    console.log("Theme-Style [Fantasy] is uninstalled.");
  },
  // options
  {
    path: '', // leave a blank or set it to vacant string is meaning match all. 
    onInvokeError: (utility, utils, error)=>{
      console.error(error);
    },
    onRemoveError: (utility, utils, error)=>{
      console.error(error);
    }
  }
);

/**
 * Add a notifycation on Navigator page.
 */
$theme(function(utility){
  utility.addNotifycation("示例主题 Fantasy: 磨砂风梦幻感受 ");
  utility.addNotifycation("欢迎使用Fantasy主题风格!");
  utility.addNotifycation("Fantasy 主题支持自定义背景API以及高斯模糊值啦");
}, (utility)=>{
  // nothing to do with remove
  console.log("Notifycation removed!")
}, {
  path: '/navigator', // only take effect on navigator page.
});

$theme(function(utility, utils){
  const toBottom = {
    name: "toBottom",
    descriptions: "快速向下滚到见底！",
    commonKey: 'B',
    statuKey: 'ctrl',
    invoke(eve){
      utils.lyscrollTo({
        top: 9999,
      });
    }
  };
  utility.registerShortcut(toBottom);
}, function(utility){
  // Remove the impact by the register name.
  utility.unregisterShortcut("toBottom");
}, {
  path: '/anime',
});

// All jobs Done!
})();