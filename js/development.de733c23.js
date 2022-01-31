(self["webpackChunkAnimeUI"]=self["webpackChunkAnimeUI"]||[]).push([[115],{44431:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return u}});var o=n(56598),l={id:"development"};function r(e,t,n,r,a,i){var c=(0,o.resolveComponent)("router-view");return(0,o.openBlock)(),(0,o.createElementBlock)("div",l,[(0,o.createVNode)(c)])}var a=(0,o.defineComponent)({name:"Development"}),i=n(83744);const c=(0,i.Z)(a,[["render",r]]);var u=c},92184:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return oe}});n(68309),n(82526),n(41817);var o=n(56598),l=n(23369),r=n(20809),a={class:"layout lycontainer fullbox"},i={class:"main layout resp-width vw-center"},c={class:"title"},u=(0,o.createElementVNode)("span",null," Theme-Blending ",-1),d={"data-balloon":"导入JSON主题配色","data-balloon-pos":"down"},s={class:"iconfont icon-upload"},f=(0,o.createTextVNode)("上传 "),p=(0,o.createElementVNode)("span",{class:"iconfont icon-download"},"保存",-1),m=[p],h=(0,o.createElementVNode)("hr",{class:"mb-4"},null,-1),x=(0,o.createElementVNode)("h4",null,"填充基本信息",-1),V={class:"blend-infos pa-4"},v={for:"name"},N=(0,o.createTextVNode)(" 配色名 "),g={for:"alias"},b=(0,o.createTextVNode)(" 配色昵称 "),k={for:"description"},y=(0,o.createTextVNode)(" 描述 "),E={for:"author"},w=(0,o.createTextVNode)(" 作者信息 "),C={for:"home"},B=(0,o.createTextVNode)(" 主页 "),A=(0,o.createElementVNode)("h4",null,"是否为暗色主题:",-1),T={class:"dark-set px-4"},_={for:"dark"},D=(0,o.createTextVNode)(" 暗系配色 "),M={class:"blending"},U=(0,o.createElementVNode)("h2",null,"配色混合变量",-1),S=(0,o.createElementVNode)("div",{class:"hint mx-4"},"配色混合变量是应用变换配色的主体部分，采用通量命名，如primary、secondary等",-1),L={class:"content pa-4"},j=["for"],z=["onUpdate:modelValue"],J=(0,o.createElementVNode)("span",null,": ",-1),Z=["onUpdate:modelValue"],F={class:"colors"},O=(0,o.createElementVNode)("h2",null,"配色颜色变量",-1),I=(0,o.createElementVNode)("div",{class:"hint mx-4"},"配色颜色变量用于一些固定色彩的地方，通过配置基本的颜色的值来达到更改目的",-1),K={class:"content pa-4"},G=["for"],Q=["onUpdate:modelValue"],R=(0,o.createElementVNode)("span",null,": ",-1),W=["onUpdate:modelValue"];function $(e,t,n,p,$,H){return(0,o.openBlock)(),(0,o.createBlock)(l.K,{id:"blending",class:""},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(r.v,{theme:e.theme,"with-background":"",class:""},{default:(0,o.withCtx)((function(){return[(0,o.createElementVNode)("div",a,[(0,o.createElementVNode)("div",i,[(0,o.createElementVNode)("div",c,[u,(0,o.createElementVNode)("span",null,[(0,o.createElementVNode)("button",d,[(0,o.createElementVNode)("label",s,[(0,o.createElementVNode)("input",{onChange:t[0]||(t[0]=function(t){return e.fileInputs(t)}),type:"file",name:"upload",id:"upload",accept:".json",hidden:""},null,32),f])]),(0,o.createElementVNode)("button",{onClick:t[1]||(t[1]=function(){return e.saveJson&&e.saveJson.apply(e,arguments)}),"data-balloon":"导出当前主题配色","data-balloon-pos":"down"},m)])]),h,x,(0,o.createElementVNode)("div",V,[(0,o.createElementVNode)("label",v,[N,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"name","onUpdate:modelValue":t[2]||(t[2]=function(t){return e.infos.name=t}),type:"text"},null,512),[[o.vModelText,e.infos.name]])]),(0,o.createElementVNode)("label",g,[b,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"alias","onUpdate:modelValue":t[3]||(t[3]=function(t){return e.infos.alias=t}),type:"text"},null,512),[[o.vModelText,e.infos.alias]])]),(0,o.createElementVNode)("label",k,[y,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"description","onUpdate:modelValue":t[4]||(t[4]=function(t){return e.infos.description=t}),type:"text"},null,512),[[o.vModelText,e.infos.description]])]),(0,o.createElementVNode)("label",E,[w,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"author","onUpdate:modelValue":t[5]||(t[5]=function(t){return e.infos.author.nick=t}),type:"text"},null,512),[[o.vModelText,e.infos.author.nick]])]),(0,o.createElementVNode)("label",C,[B,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"home","onUpdate:modelValue":t[6]||(t[6]=function(t){return e.infos.home=t}),type:"text"},null,512),[[o.vModelText,e.infos.home]])])]),A,(0,o.createElementVNode)("div",T,[(0,o.createElementVNode)("label",_,[(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"dark","onUpdate:modelValue":t[7]||(t[7]=function(t){return e.infos.isDark=t}),type:"checkbox"},null,512),[[o.vModelCheckbox,e.infos.isDark]]),D])]),(0,o.createElementVNode)("div",M,[U,S,(0,o.createElementVNode)("ul",L,[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.readBlending,(function(t,n){return(0,o.openBlock)(),(0,o.createElementBlock)("li",{key:n},[(0,o.createElementVNode)("label",{for:t.key},[(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(e){return t.key=e}},null,8,z),[[o.vModelText,t.key]]),J,(0,o.createElementVNode)("span",{class:(0,o.normalizeClass)(["lump",{opacity:e.$magic.utils.is_Number(t.value)}]),style:(0,o.normalizeStyle)({"--bgcolor":t.value})},null,6),(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(e){return t.value=e}},null,8,Z),[[o.vModelText,t.value]])],8,j)])})),128))])]),(0,o.createElementVNode)("div",F,[O,I,(0,o.createElementVNode)("ul",K,[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.readColors,(function(e,t){return(0,o.openBlock)(),(0,o.createElementBlock)("li",{key:t},[(0,o.createElementVNode)("label",{for:e.key},[(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(t){return e.key=t}},null,8,Q),[[o.vModelText,e.key]]),R,(0,o.createElementVNode)("span",{class:"lump",style:(0,o.normalizeStyle)({"--bgcolor":e.value})},null,4),(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(t){return e.value=t}},null,8,W),[[o.vModelText,e.value]])],8,G)])})),128))])])])])]})),_:1},8,["theme"])]})),_:1})}var H=n(95082),Y=(n(41539),n(54747),n(47941),n(74916),n(15306),n(38862),n(28157)),q=n(35583),P=n(65490),X=[[],[]],ee=(0,o.defineComponent)({name:"Blending",components:{},directives:{"color-visual":{mounted:function(e){e.style.backgroundColor=e.innerHTML,e.style.color="white",e.classList.add("fastcopy")}}},setup:function(){var e=(0,Y.AW)();return console.log(e),{display:e}},data:function(){return{theme:"light",infos:{name:"CustomBlending",alias:"自定义主题配色",description:"我的第一个自定义主题配色",author:{nick:"",avatar:"",link:""},home:"",thumbs:"",isDark:!1},blending:{},colors:{}}},computed:{readBlending:function(){var e=this;return Object.keys(this.blending).forEach((function(t){X[0].push({key:t,value:e.blending[t]})})),X[0]},readColors:function(){var e=this;return Object.keys(this.colors).forEach((function(t){X[1].push({key:t,value:e.colors[t]})})),X[1]}},methods:{fileInputs:function(e){var t=this,n=e.target;console.log(n);var o=n.files[0];if(!o)return console.log("There are no selected files"),!1;o.text().then((function(e){try{var n=e.replace(/\/\/.*?\n/g,""),o=JSON.parse(n);(0,P.IM)(t.infos,o,null,["blending","colors"]),t.blending=o.blending||t.blending,t.colors=o.colors||t.colors}catch(l){console.error("The selected file is not a valid json file.",l)}}))},saveJson:function(){var e=(0,H.Z)((0,H.Z)({},this.infos),{},{blending:this.blending,colors:this.colors});(0,q.fileExport)(JSON.stringify(e),"".concat(this.infos.name,".json"),"application/json")}},created:function(){var e=this.$magic.deposit.getThemeBlending("light");this.colors=e.colors,this.blending=e.variables},mounted:function(){}});n(27193);var te=n(83744);const ne=(0,te.Z)(ee,[["render",$]]);var oe=ne},30069:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return A}});var o=n(56598),l=n(52653),r=n(23369),a=n(16824),i=n(68521),c=n(20809),u=(0,o.createElementVNode)("h1",null,"我的开发调色板",-1),d=(0,o.createElementVNode)("h2",null,"颜色可视化：",-1),s=(0,o.createElementVNode)("h3",{style:{},for:"inputtedStr"},"输入一个或一组CSS颜色值并立即获取展示(可能是从一些地方复制过来的)自动过滤特殊符号",-1),f=(0,o.createElementVNode)("label",{for:"splitor"},"选择分隔符模式",-1),p=(0,o.createElementVNode)("option",{value:","},"英文逗号",-1),m=(0,o.createElementVNode)("option",{value:"."},"小圆点",-1),h=(0,o.createElementVNode)("option",{value:" "},"空格",-1),x=[p,m,h],V=(0,o.createTextVNode)("点击添加进入颜色列表"),v=(0,o.createTextVNode)("颜色可视："),N={class:"default-colorlump colorlump"},g=(0,o.createElementVNode)("h2",null,"默认颜色",-1),b={class:"default-colorlump colorlump"};function k(e,t,n,p,m,h){var k=(0,o.resolveDirective)("color-visual");return(0,o.openBlock)(),(0,o.createBlock)(r.K,{id:"main"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(c.v,{theme:e.theme,"with-background":"",class:"pa-10"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(a.o,{"no-gutters":"",class:"mb-12",justify:"center"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[u]})),_:1})]})),_:1}),(0,o.createVNode)(a.o,{"no-gutters":"",class:"mb-12",justify:"center"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[d]})),_:1}),(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[s]})),_:1}),(0,o.createVNode)(i.D,{cols:"4"},{default:(0,o.withCtx)((function(){return[f,(0,o.withDirectives)((0,o.createElementVNode)("select",{name:"splitor","onUpdate:modelValue":t[0]||(t[0]=function(t){return e.splitor=t})},x,512),[[o.vModelSelect,e.splitor]])]})),_:1})]})),_:1}),(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[(0,o.withDirectives)((0,o.createElementVNode)("textarea",{name:"inputtedStr",type:"text","onUpdate:modelValue":t[1]||(t[1]=function(t){return e.inputtedStr=t})},null,512),[[o.vModelText,e.inputtedStr]])]})),_:1}),(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(l.T,{onClick:e.addColor},{default:(0,o.withCtx)((function(){return[V]})),_:1},8,["onClick"])]})),_:1})]})),_:1})]})),_:1}),(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[v]})),_:1}),(0,o.createVNode)(a.o,{justify:"center"},{default:(0,o.withCtx)((function(){return[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.colorList,(function(e,t){return(0,o.openBlock)(),(0,o.createBlock)(i.D,{key:t,cols:"1"},{default:(0,o.withCtx)((function(){return[(0,o.withDirectives)(((0,o.openBlock)(),(0,o.createElementBlock)("div",N,[(0,o.createTextVNode)((0,o.toDisplayString)(e),1)])),[[k]])]})),_:2},1024)})),128))]})),_:1})]})),_:1})]})),_:1}),(0,o.createVNode)(a.o,{"no-gutters":"",class:"mb-12",justify:"center"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(a.o,null,{default:(0,o.withCtx)((function(){return[g]})),_:1}),(0,o.createVNode)(a.o,{justify:"center"},{default:(0,o.withCtx)((function(){return[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.defaultColorList,(function(e,t){return(0,o.openBlock)(),(0,o.createBlock)(i.D,{key:t,cols:"1",md:"2",xs:"3"},{default:(0,o.withCtx)((function(){return[(0,o.withDirectives)(((0,o.openBlock)(),(0,o.createElementBlock)("div",b,[(0,o.createTextVNode)((0,o.toDisplayString)(e),1)])),[[k]])]})),_:2},1024)})),128))]})),_:1})]})),_:1})]})),_:1})]})),_:1},8,["theme"])]})),_:1})}n(74916),n(15306),n(24603),n(28450),n(88386),n(39714),n(68757),n(23123),n(92222);var y=n(28157),E=n(35583),w=(0,o.defineComponent)({name:"Pallet",directives:{"color-visual":{mounted:function(e){e.style.backgroundColor=e.innerHTML,e.style.color="white",e.classList.add("fastcopy")}}},data:function(){return{theme:"light",defaultColorList:["#cdfff5","#ffcdf0","#d7ffcd","#fff5cd","#cdf0ff","#ffdccd","#dccdff","#cdffdc","#ffcdd7"],inputtedColorList:[],splitor:",",inputtedStr:""}},computed:{colorList:function(){var e=this.inputtedStr.replace(new RegExp("/(".concat(this.splitor,")+/g")),"$1");return e=e.replaceAll(/["'“‘’”]/g,""),e.split(this.splitor)}},setup:function(){var e=(0,y.AW)();return console.log(e),{display:e}},methods:{addColor:function(){this.inputtedColorList.concat(this.colorList),this.inputtedStr=""}},created:function(){},mounted:function(){this.$el.addEventListener("click",(function(e){e.target.classList.contains("fastcopy")&&(0,E.copyTextToClipboard)(e.target.textContent||e.target.innerHTML)}))}});n(71034);var C=n(83744);const B=(0,C.Z)(w,[["render",k]]);var A=B},69146:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),r=n(23645),a=n.n(r),i=a()(l());i.push([e.id,".colorlump{display:inline-block;margin:15px auto;padding:3px 5px;border-radius:3px;color:#fff;font-size:14px;font-weight:500;-webkit-user-select:all;-moz-user-select:all;user-select:all}.default-colorlump{border:1px solid gray}",""]),t["default"]=i},58666:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),r=n(23645),a=n.n(r),i=n(61667),c=n.n(i),u=new URL(n(65189),n.b),d=a()(l()),s=c()(u);d.push([e.id,".main .title{display:flex;justify-content:space-between;align-content:center;font-size:24px;margin-top:12px;margin-bottom:16px}.main .title span{margin:auto 12px}.main .title span button{margin-left:8px}.main .title span button label{cursor:pointer}.main .title span button span{font-size:16px;cursor:pointer}.main .blending>h2,.main .colors>h2,.main h4{margin:auto 12px}.main .blend-infos{margin-bottom:16px}.main .blend-infos label input{display:inline-block;border:1px solid rgb(var(--v-theme-on-surface));border-radius:3px}.main .blending,.main .colors,.main .dark-set{margin-bottom:16px}.main ul.content{display:flex;justify-content:space-between;align-content:center;align-items:center;flex-wrap:wrap}.main ul.content li{list-style:none}.main ul.content li input,.main ul.content li label .lump{display:inline-block;vertical-align:middle}.main ul.content li label .lump{width:20px;height:20px;margin-right:8px;background-color:var(--bgcolor);box-shadow:1px 1px 3px var(--bgcolor),-2px -1px 3px gray;cursor:pointer}.main ul.content li label .lump.opacity{background:url("+s+") repeat;border-radius:50%;border:1px solid gray}.colorlump{display:inline-block;margin:15px auto;padding:3px 5px;border-radius:3px;color:#fff;font-size:14px;font-weight:500;-webkit-user-select:all;-moz-user-select:all;user-select:all}.default-colorlump{border:1px solid gray}",""]),t["default"]=d},71034:function(e,t,n){var o=n(69146);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("4290517f",o,!0,{sourceMap:!1,shadowMode:!1})},27193:function(e,t,n){var o=n(58666);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("5751629b",o,!0,{sourceMap:!1,shadowMode:!1})},65189:function(e){"use strict";e.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAGElEQVQYlWNgYGCQwoKxgqGgcJA5h3yFAAs8BRWVSwooAAAAAElFTkSuQmCC"}}]);