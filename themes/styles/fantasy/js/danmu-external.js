/**
 * Add external danmu support for Auiplayer
 * Nowtime the xml danmaku is supported as local file import and danmaku api(returns xml).
 */
(function(){
  // Associate change with vue instantiation.
  let canRun = null;
  let autorun = function(callback){
    if(canRun!==null)
      if(canRun)
        callback();
  };

  // Register the danmu enable Options. 添加主题选项
  $theme(function(utility, utils, { axios, getRoute }){
    utility.addThemeOptions({
      name: "ext-danmu",
      viewType: "switchBox",
      // Set the initial value.
      rawValue: false,
      /**
      * The onChange options will be automaticly called when the settings change.
       * @param {*} nVal The new value has changed.
       * @param {*} oVal The old value before changes.
       */
      onChange: (nVal, oVal)=>{
        console.info(`Fantasy extra danmaku module is changes with enable: ${nVal}`);
        canRun = nVal;
      },
      // Make the onChange method applying on inited
      onInitial: true,
      viewData: {
        title: "是否启用外部弹幕支持: ",
        hint: "开启后将在 Auiplayer和Anime分区 增加自定义弹幕导入选项, 目前支持xml格式",
      },
    });
  });

  /**
   * 增加表单控制 UI
   */
  let appDiv=null, VueApp = null;
  $theme((utility, utils, {axios, getVue})=>{
    const { auiplayer, lzynotice } = utility;
    const { createApp, reactive } = getVue();

    // console.log({utility, utils});

    // 预先创建节点 并追加到页面中
    appDiv = document.createElement("div");
    appDiv.setAttribute("id", "fantasy-danmu");
    appDiv.innerHTML=`
      <small><i>
        外部弹幕载入模块由
        <a target="_blank" href="https://github.com/lozyue/AnimeSearcherUI/tree/main/AnimeUI/themes/styles/fantasy">
        主题风格Fantasy
        </a>
        提供：
      </i></small>
      <h4 class="link-head"></h4>
      <div class="link-input" @drop="onDrop">
        <label>上传本地弹幕文件：</label>
        <input type="file" @change="fileChange">
      </div>
      <p>OR import from url: </p>
      <div class="link-input">
        <label>填写xml弹幕格式API链接：</label>
        <input type="text" v-model="xmlURL">
      </div>
      <div class="link-action">
        <div></div>
        <button @click="goShoot">点击载入</button>
        <button @click="clearDanmu">清空弹幕池</button>
        <div></div>
      </div>
    `;
    var vueOption = {
      data:()=>({
        xmlURL: "",
      }),
      methods: {
        // 绑定该方法到按钮点击事件上
        goShoot: function(){
          let entryHref = this.xmlURL.trim();

          // Check
          if(utils.is_Empty(entryHref) || !entryHref.startsWith("http") ){
            lzynotice({
              content: "当前链接无效！",
              semantic: "error",
            });
            return;
          }

          axios.get(entryHref).then(({data})=>{
            this.handleXMLDanmu(data);
          }).catch(err=>console.error(err));
        },
        clearDanmu(){
          utility.auiplayer((dlpIns, auiplayer)=>{
            auiplayer.applyDanmu({
              address: "", // Pass an empty danmaku URL to clear the danmu pool.
            });
          });
        },
        handleXMLDanmu(xmlString){
          var danmuBullets = utils.XML_danmu(xmlString).map(item=>{
            // Transform the danmu format.
            return {
              text: item.text,
              time: item.time,
              mode: item.mode==='TOP'? 2: item.mode==='BOTTOM'? 1: 0,
              color: item.color,
            };
          });
          if(!danmuBullets.length){
            lzynotice({
              content: "载入弹幕格式失败！",
              semantic: "error",
              duration: 10,
            });
          };
          utility.auiplayer((dlpIns, auiplayer)=>{
            auiplayer.contactDanmu({
              addition: "",
              bullets: danmuBullets,
            });
          });
          // Send a message
          lzynotice({
            content: `成功载${danmuBullets.length}条临时弹幕！`,
            semantic: "success",
            duration: 8,
          });
        },
        handleFiles(files){
          for (var i = 0; i < files.length; i++) {
            var file = files[i];
            var targetType = /\/xml/;
            
            if (!targetType.test(file.type)) {
              continue;
            }
    
            var reader = new FileReader();
            reader.onload = (eve)=>{
              const XML_Result = eve.target?.result;
              this.handleXMLDanmu(XML_Result);
            };
            reader.readAsText(file);
          }
        },
        onDrop: function($eve){
          $eve.preventDefault();
          $eve.stopPropagation();
    
          const transfer = $eve.dataTransfer;
          this.handleFiles(transfer.files);
        },
        fileChange: function($eve){
          const fileInput = $eve.target;
          const files = fileInput.files;
          this.handleFiles(files);
        }
      },
    };

    // Wait the changes just once (or initial invoke)
    autorun(function(){
      setupApp(appDiv, vueOption);
    });

    function setupApp(appDiv, vueOption){
      let mountTarget = document.body.querySelector(".lzyplayer-container");
      if(!mountTarget){ console.error("意外错误！没有找到合适挂载的节点！"); return; };
      mountTarget.appendChild(appDiv);
  
      // Create Vue Instances.
      VueApp = createApp(vueOption);
      // Mount the app.
      VueApp.mount("#fantasy-danmu");
    }
  }, ()=>{
    // 消除副作用
    // 当主题被禁用或者匹配页面切换时的动作
    if(VueApp) VueApp.unmount();
    if(appDiv) appDiv.remove();
  }, { 
    path: ['/aui-player', '/anime/details/'],
  });

  // END
})();
