/**
 * Background customization.
 */
(function(){
  var rmHandle = {
    class: 'fantasy-bg',
    style: {},
  };
  $theme(function(utility){
    // Add effection. Alter the background
    rmHandle = utility.setBackground(rmHandle);
    console.log("[Fantasy]: Custome background is applied.");
  }, function(utility){
    // The second param true to alter remove Mode. 
    // Restore its original background.
    utility.setBackground(rmHandle, true);
    console.log("[Fantasy]: Custome background is hidden.");
  }, {
    excludePath: ['/not-found','/details'],
  });
  
  // Register the background Options.
  $theme(function(utility, utils, { axios, getRoute }){
    utility.addThemeOptions({
      name: "back_url",
      viewType: "textfieldBox",
      // https://tva1.sinaimg.cn/large/005BYqpgly1frn9445odej31hc0u0kjl.jpg
      // Set the initial value.
      rawValue: "https://api.mtyqx.cn/api/random.php?r=91f275ab",
      /**
      * The onChange options will be automaticly called when the settings change.
       * @param {*} nVal The new value of changes.
       * @param {*} oVal The old value before changes.
       */
      onChange: (nVal, oVal)=>{
        console.log("[fantasy]: Background Changed!");
        rmHandle.style["background-image"] = `url(${nVal})`;
        // refresh the background; May cause background confrontation without correctly remove.
        let isSuccess = utility.setBackground(rmHandle, true); // remove
        if(isSuccess) rmHandle = utility.setBackground(rmHandle); // re-apply
      },
      // Make the onChange method apply on inited
      onInitial: true,
      viewData: {
        title: "自定义背景图像链接: ",
        hint: "填写API链接或者固定图像链接",
      },
    });

    utility.addThemeOptions({
      name: "back_blur",
      viewType: "numbersBox", // "selectsBox"|"switchBox"|"textareaBox"|"textfieldBox",
      // Set the initial value. Support value-return function.
      rawValue: ()=>{
        return 10;
      },
      /**
       * The onChange options will be automaticly called when the settings is changed. 
       * @param {*} nVal The new value of changes.
       * @param {*} oVal The old value before changes.
       */
      onChange: (nVal, oVal)=>{
        rmHandle.style.filter = `blur(${nVal}px) brightness(var(--v-layer-darken))`;
        // refresh the background; May cause backgroun confrontation without correctly remove.
        let isSuccess = utility.setBackground(rmHandle, true); // remove
        if(isSuccess) rmHandle = utility.setBackground(rmHandle); // re-apply
      },
      // Make the onChange method apply on inited
      onInitial: true,
      viewData: {
        title: "设定高斯模糊值: ",
        hint: "建议范围0-100",
        step: 2,
      },
    });

    // Some random API:
    // http://api.mtyqx.cn/api/random.php?r=91f275ab&return=json
    // https://www.dmoe.cc/random.php?return=json
    
    // Valid
    // axios.get("https://api.vvhan.com/api/acgimg?type=json").then((resp)=>{
    //   console.log(resp, resp.data.imgurl);
    // }).catch((e)=>{
    //   console.warn(e);
    // });
  
  },function(){
    // 
  }, {});

  // END
})();
