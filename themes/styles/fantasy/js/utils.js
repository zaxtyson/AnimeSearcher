/**
 * To add some public function to share with others
 *   via utils Object.
 */
(function(){
  
  $theme((utility, utils)=>{
    // Share the function by the name of "XML_toObj"
    utils["XML_danmu"] = XML_danmu;
  }, (utility, utils)=>{
    // remove it when the theme uninstall.
    utils["XML_danmu"] = undefined;
  });

  
  // https://github.com/tiansh/us-danmaku/blob/master/bilibili/bilibili_ASS_Danmaku_Downloader.user.js
  function XML_danmu(content){
    var data = (new DOMParser()).parseFromString(content, 'text/xml');
    return Array.apply(Array, data.querySelectorAll('d')).map(function (line) {
      var info = line.getAttribute('p').split(','), text = line.textContent;
      return {
        'text': text,
        'time': Number(info[0]),
        'mode': [undefined, 'R2L', 'R2L', 'R2L', 'BOTTOM', 'TOP'][Number(info[1])],
        'size': Number(info[2]),
        color: parseInt(info[3], 10) & 0xffffff,
        // 'color': RRGGBB(parseInt(info[3], 10) & 0xffffff),
        'bottom': Number(info[5]) > 0,
        // 'create': new Date(Number(info[4])),
        // 'pool': Number(info[5]),
        // 'sender': String(info[6]),
        // 'dmid': Number(info[7]),
      };
    });
  };
  function RRGGBB(color) {
    var t = Number(color).toString(16).toUpperCase();
    return (Array(7).join('0') + t).slice(-6);
  };
})();
