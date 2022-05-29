/**
 * Export some interface of Auiplayer to support communication via iframe.
 * Add a prop named "AuiController" to it parent window.
 * Do the initialization in `AuiController.onReady`
 */
// custom main
(function(){
  const parentWindow = window.parent;
  if(parentWindow===window){
    console.log("It is unnecessary to add iframe-helper support in current environment(not in an iframe)!");
    return false;
  }

  const ExposureVarName = "AuiController";

  // Add a prop of AuiController
  var controller = parentWindow[ExposureVarName] || (parentWindow[ExposureVarName] = {
    status: 'loading',
    path: '',
    // onReady: new Function(), // Read from parent window.
    // autoHeight, // Read from parent window.
  });

  // https://lozyue.github.io/AnimeSearcherUI/theme-dev/style/api-config.html
  $theme((utility, utils, { getRoute, getVue, revoke })=>{
  // Invoke
    const { watchEffect } = getVue();
    // update path
    var stopWatch = watchEffect(()=>{
      controller.path = getRoute().fullPath;
    });

    // Add an redundant prevent controller
    controller.addEpisodeByIndex = function(callback){
      var recorderMap = new Set();
      var resultMap = [];
      return (index)=>{
        if(recorderMap.has(index) ){
          return resultMap[index];
        };
        // Store the results
        resultMap[index] = callback(index);
        recorderMap.add(index);

        return resultMap[index];
      };
    }

    // Share the utils
    controller.utils = utils;
    controller.utility = utility;

    // Hook function. Do the revoke things.
    revoke(()=>{
      stopWatch(); // To stop the watchEffect.

      objectRefresh(controller, {
        utils: undefined,
        utility: undefined,
      });
    });
  }, (utility, utils)=>{
  // Revoke
  });

  // Export the auiplayer status and missions.
  $theme((utility, utils)=>{
  // Invoke when auiplayer ready

    // Export the methods
    utility.auiplayer((dlplayer, auiplayer)=>{
      controller["auiplayer"] = auiplayer;
      controller["dlplayer"] = dlplayer;

      // Auto justify the iframe height
      const iframeList = parentWindow.document.querySelectorAll("iframe");
      var iframeEle = null;
      for(let id in iframeList){
        if(utils.getHostName(iframeList[id].src) === utils.getHostName(window.host) ){
          iframeEle = iframeList[id];
          break;
        }
      }
      const adjustIframe = ()=>{
        if(iframeEle && controller.autoHeight!==false){
          var playingVideo = document.querySelector("video");
          if(playingVideo && playingVideo.videoHeight > 0){
            const ratio = iframeEle.offsetWidth / playingVideo.videoWidth;
            iframeEle.style.height = playingVideo.videoHeight* ratio + 'px';
          }
        }
      };
      dlplayer._on("loadedmetadata", adjustIframe);
    });

    controller["addPlayerHotkey"] = utility.addPlayerHotkey;
    controller["addToPlaylist"] = utility.addToPlaylist;
    controller["addPlaylist"] = utility.addPlaylist;

    // Call back the onReady.
    if(utils.is_Function(controller.onReady) ){
      controller.onReady(controller, utility, utils);
      controller.onReady = undefined;
    };

    // update status
    controller.status = "idle";
  }, (utility, utils)=>{
  // Revoke when leave auiplayer
    const { objectRefresh } = utils;
    // To reset the props for memory free.
    objectRefresh(controller, {
      dlplayer: undefined,
      auiplayer: undefined,
      addPlaylist: undefined,
      addToPlaylist: undefined,
      addPlayerHotkey: undefined,
    });
  }, {
    path: ["/aui-player", "/auiplayer"],
  });

})();
