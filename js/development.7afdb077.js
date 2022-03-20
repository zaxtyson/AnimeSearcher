(self["webpackChunkAnimeUI"]=self["webpackChunkAnimeUI"]||[]).push([[115],{43923:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return s}});var o=n(56598),l={id:"development"};function a(e,t,n,a,r,i){var d=(0,o.resolveComponent)("animeui-home"),c=(0,o.resolveComponent)("router-view");return(0,o.openBlock)(),(0,o.createElementBlock)("div",l,[(0,o.createVNode)(d,{animeTemp:e.animeTemp,class:"back-home"},null,8,["animeTemp"]),(0,o.createVNode)(c,{animeTemp:e.animeTemp},null,8,["animeTemp"])])}var r=n(97117),i=(0,o.defineComponent)({name:"Development",inheritAttrs:!1,components:{"animeui-home":r.Z},props:["animeTemp"]}),d=n(83744);const c=(0,d.Z)(i,[["render",a]]);var s=c},54156:function(e,t,n){"use strict";n.d(t,{Z:function(){return v}});var o=n(56598),l=n(46769),a=(0,o.createTextVNode)("mdi-file-upload-outline"),r=["multiple"];function i(e,t){return(0,o.openBlock)(),(0,o.createElementBlock)("div",{class:"aui-file-field",ref:"field",onDragenter:t[1]||(t[1]=function(){return e.onDragenter&&e.onDragenter.apply(e,arguments)}),onDragleave:t[2]||(t[2]=function(){return e.onDragleave&&e.onDragleave.apply(e,arguments)}),onDragover:t[3]||(t[3]=function(){return e.onDragover&&e.onDragover.apply(e,arguments)}),onDrop:t[4]||(t[4]=function(){return e.onDrop&&e.onDrop.apply(e,arguments)}),onPaste:t[5]||(t[5]=function(){return e.onPaste&&e.onPaste.apply(e,arguments)})},[(0,o.createElementVNode)("label",null,[(0,o.createVNode)(l.t,null,{default:(0,o.withCtx)((function(){return[a]})),_:1})]),(0,o.createElementVNode)("input",{type:"file",multiple:e.multiple,onChange:t[0]||(t[0]=function(){return e.fileChange&&e.fileChange.apply(e,arguments)})},null,40,r)],544)}var d=n(23176),c=n(35583),s=n(66252),u=n(2262),m=(0,s.aZ)({name:"aui-file-field",props:{multiple:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1},attributes:{type:Object,default:{}}},setup:function(e,t){var n=t.emit,o=(0,s.FN)(),l=o.proxy,a=(l.$magic,(0,u.qj)({droping:!1})),r=function(e){var t=e.target,n=t.files;i(n)},i=function(e){n("handleFiles",e)},m=function(e){var t=e.target;t.classList.add("field-drapover"),d.DEBUG&&console.log("dragEnterd!"),e.preventDefault()},p=function(e){d.DEBUG&&console.log("dragOvered",e),e.preventDefault()},f=function(e){d.DEBUG&&console.log("dragLeaved!",e);var t=l.$refs.field;(0,c.traceTopMatch)(e.relatedTarget||e.target,[function(){d.DEBUG&&console.log("mathched"),e.preventDefault(),e.stopPropagation()},function(n){d.DEBUG&&console.log("dismathched"),t.classList.remove("field-drapover"),e.preventDefault()}],(function(n,o){return d.DEBUG&&console.log({el:n,times:o}),0===o&&n===t||(e.preventDefault(),e.stopPropagation(),n===t)}),3)},v=function(e){var t=e.target;t.classList.remove("field-drapover"),d.DEBUG&&console.log("dragDropped!"),e.preventDefault(),e.stopPropagation();var n=e.dataTransfer;i(n.files)},h=function(e){};return{status:a,fileChange:r,onDragenter:m,onDragover:p,onDragleave:f,onDrop:v,onPaste:h}}}),p=(n(20073),n(83744));const f=(0,p.Z)(m,[["render",i]]);var v=f},24587:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return se}});n(68309),n(82526),n(41817);var o=n(56598),l=n(23369),a=n(46769),r=n(76924),i=n(20809),d={class:"layout lycontainer fullbox py-6"},c={class:"main layout resp-width vw-center"},s={class:"title"},u=(0,o.createElementVNode)("span",null," Theme-Blending ",-1),m={"data-balloon":"导入JSON主题配色","data-balloon-pos":"down"},p={class:"iconfont icon-upload"},f=(0,o.createTextVNode)("上传 "),v=(0,o.createElementVNode)("span",{class:"iconfont icon-download"},"保存",-1),h=[v],g=(0,o.createElementVNode)("hr",{class:"mb-4"},null,-1),b=(0,o.createElementVNode)("h4",null,"填充基本信息",-1),y={class:"blend-infos pa-4"},V={for:"name"},x=(0,o.createTextVNode)(" 配色名： "),N={for:"alias"},E=(0,o.createTextVNode)(" 配色昵称： "),w={for:"description"},k=(0,o.createTextVNode)(" 描述： "),C={for:"author"},D=(0,o.createTextVNode)(" 作者： "),T={for:"avatar"},B=(0,o.createTextVNode)(" 头像： "),_={for:"home"},M=(0,o.createTextVNode)(" 主页： "),A=(0,o.createElementVNode)("h4",null,"是否为暗色主题:",-1),U={class:"dark-set px-4"},J={class:"blending-dev-body mb-4"},S={class:"dev-intro mb-4"},j={for:"intro"},L=(0,o.createTextVNode)("mdi-file-document"),Z=(0,o.createTextVNode)(" 介绍文件： "),z=(0,o.createElementVNode)("input",{id:"dev-intro",type:"text",placeholder:"Markdown文件介绍路径："},null,-1),F={class:"blending"},G=(0,o.createElementVNode)("h2",null,"配色混合变量",-1),O=(0,o.createElementVNode)("div",{class:"hint mx-4"},"配色混合变量是应用变换配色的主体部分，采用通量命名，如primary、secondary等; 目前颜色只支持16进制表达式",-1),$={class:"content pa-4"},P=["for"],H=["onUpdate:modelValue"],I=(0,o.createElementVNode)("span",null,": ",-1),R=["onUpdate:modelValue"],K={class:"colors"},Q=(0,o.createElementVNode)("h2",null,"配色颜色变量",-1),W=(0,o.createElementVNode)("div",{class:"hint mx-4"},"配色颜色变量用于一些固定色彩的地方，通过配置基本的颜色的值来达到更改目的; 目前颜色只支持16进制表达式",-1),Y={class:"content pa-4"},q=["for"],X=["onUpdate:modelValue"],ee=(0,o.createElementVNode)("span",null,": ",-1),te=["onUpdate:modelValue"];function ne(e,t,n,v,ne,oe){return(0,o.openBlock)(),(0,o.createBlock)(l.K,{id:"theme-blending-dev",class:""},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.v,{theme:e.theme,"with-background":"",class:"rounded-lg"},{default:(0,o.withCtx)((function(){return[(0,o.createElementVNode)("div",d,[(0,o.createElementVNode)("div",c,[(0,o.createElementVNode)("div",s,[u,(0,o.createElementVNode)("span",null,[(0,o.createElementVNode)("button",m,[(0,o.createElementVNode)("label",p,[(0,o.createElementVNode)("input",{onChange:t[0]||(t[0]=function(t){return e.fileInputs(t)}),type:"file",name:"upload",id:"upload",accept:".json",hidden:""},null,32),f])]),(0,o.createElementVNode)("button",{onClick:t[1]||(t[1]=function(){return e.saveJson&&e.saveJson.apply(e,arguments)}),"data-balloon":"导出当前主题配色","data-balloon-pos":"down"},h)])]),g,b,(0,o.createElementVNode)("div",y,[(0,o.createElementVNode)("label",V,[x,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"name","onUpdate:modelValue":t[2]||(t[2]=function(t){return e.infos.name=t}),type:"text"},null,512),[[o.vModelText,e.infos.name]])]),(0,o.createElementVNode)("label",N,[E,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"alias","onUpdate:modelValue":t[3]||(t[3]=function(t){return e.infos.alias=t}),type:"text"},null,512),[[o.vModelText,e.infos.alias]])]),(0,o.createElementVNode)("label",w,[k,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"description","onUpdate:modelValue":t[4]||(t[4]=function(t){return e.infos.description=t}),type:"text"},null,512),[[o.vModelText,e.infos.description]])]),(0,o.createElementVNode)("label",C,[D,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"author","onUpdate:modelValue":t[5]||(t[5]=function(t){return e.infos.author.nick=t}),type:"text"},null,512),[[o.vModelText,e.infos.author.nick]])]),(0,o.createElementVNode)("label",T,[B,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"avatar","onUpdate:modelValue":t[6]||(t[6]=function(t){return e.infos.author.nick=t}),type:"text"},null,512),[[o.vModelText,e.infos.author.nick]])]),(0,o.createElementVNode)("label",_,[M,(0,o.withDirectives)((0,o.createElementVNode)("input",{name:"home",style:{width:"80%"},"onUpdate:modelValue":t[7]||(t[7]=function(t){return e.infos.home=t}),type:"text"},null,512),[[o.vModelText,e.infos.home]])])]),A,(0,o.createElementVNode)("div",U,[(0,o.createVNode)(r.G,{light:"",class:"ml-2",inset:"","hide-details":"",color:"black",modelValue:e.infos.isDark,"onUpdate:modelValue":t[8]||(t[8]=function(t){return e.infos.isDark=t})},null,8,["modelValue"]),(0,o.createElementVNode)("span",null,(0,o.toDisplayString)(e.infos.isDark?"暗系配色":"亮系配色"),1)]),(0,o.createElementVNode)("div",J,[(0,o.createElementVNode)("div",S,[(0,o.createElementVNode)("label",j,[(0,o.createVNode)(a.t,null,{default:(0,o.withCtx)((function(){return[L]})),_:1}),Z]),z])]),(0,o.createElementVNode)("div",F,[G,O,(0,o.createElementVNode)("ul",$,[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.readBlending,(function(t,n){return(0,o.openBlock)(),(0,o.createElementBlock)("li",{key:n},[(0,o.createElementVNode)("label",{for:t.key},[(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(e){return t.key=e}},null,8,H),[[o.vModelText,t.key]]),I,(0,o.createElementVNode)("span",{class:(0,o.normalizeClass)(["lump",{opacity:e.$magic.utils.is_Number(t.value)}]),style:(0,o.normalizeStyle)({"--bgcolor":t.value})},null,6),(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(e){return t.value=e}},null,8,R),[[o.vModelText,t.value]])],8,P)])})),128))])]),(0,o.createElementVNode)("div",K,[Q,W,(0,o.createElementVNode)("ul",Y,[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.readColors,(function(e,t){return(0,o.openBlock)(),(0,o.createElementBlock)("li",{key:t},[(0,o.createElementVNode)("label",{for:e.key},[(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(t){return e.key=t}},null,8,X),[[o.vModelText,e.key]]),ee,(0,o.createElementVNode)("span",{class:"lump",style:(0,o.normalizeStyle)({"--bgcolor":e.value})},null,4),(0,o.withDirectives)((0,o.createElementVNode)("input",{type:"text","onUpdate:modelValue":function(t){return e.value=t}},null,8,te),[[o.vModelText,e.value]])],8,q)])})),128))])])])])]})),_:1},8,["theme"])]})),_:1})}var oe=n(95082),le=(n(41539),n(54747),n(47941),n(74916),n(15306),n(38862),n(28157)),ae=n(35583),re=n(65490),ie=(0,o.defineComponent)({name:"Dev-blending",components:{},directives:{"color-visual":{mounted:function(e){e.style.backgroundColor=e.innerHTML,e.style.color="white",e.classList.add("fastcopy")}}},setup:function(){var e=(0,le.AW)();console.log(e);var t=(0,o.ref)([[],[]]);return{display:e,computedCache:t}},data:function(){return{theme:"light",infos:{name:"CustomBlending",alias:"自定义主题配色",description:"我的第一个自定义主题配色",author:{nick:"",avatar:"",link:""},home:"",thumbs:"",isDark:!1},blending:{},colors:{}}},computed:{readBlending:function(){var e=this;return Object.keys(this.blending).forEach((function(t){e.computedCache[0].push({key:t,value:e.blending[t]})})),this.computedCache[0]},readColors:function(){var e=this;return Object.keys(this.colors).forEach((function(t){e.computedCache[1].push({key:t,value:e.colors[t]})})),this.computedCache[1]}},methods:{fileInputs:function(e){var t=this,n=e.target,o=n.files[0];if(!o)return console.log("There are no selected files"),!1;o.text().then((function(e){try{var n=e.replace(/\/\*.*?\*\//g,"").replace(/\/\/.*?\n/g,"\n"),o=JSON.parse(n);(0,re.IM)(t.infos,o,null,["blending","colors"]),t.blending=o.blending||t.blending,t.colors=o.colors||t.colors}catch(l){console.error("The selected file is not a valid json file.",l)}}))},saveJson:function(){var e=(0,oe.Z)((0,oe.Z)({},this.infos),{},{blending:this.blending,colors:this.colors});(0,ae.fileExport)(JSON.stringify(e),"".concat(this.infos.name,".json"),"application/json")}},created:function(){var e=this.$magic.deposit.getThemeBlending("light");this.colors=e.colors,this.blending=e.variables},mounted:function(){}});n(81605);var de=n(83744);const ce=(0,de.Z)(ie,[["render",ne]]);var se=ce},30069:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return T}});var o=n(56598),l=n(52653),a=n(23369),r=n(16824),i=n(68521),d=n(20809),c=(0,o.createElementVNode)("h1",null,"我的开发调色板",-1),s=(0,o.createElementVNode)("h2",null,"颜色可视化：",-1),u=(0,o.createElementVNode)("h3",{style:{},for:"inputtedStr"},"输入一个或一组CSS颜色值并立即获取展示(可能是从一些地方复制过来的)自动过滤特殊符号",-1),m=(0,o.createElementVNode)("label",{for:"splitor"},"选择分隔符模式",-1),p=(0,o.createElementVNode)("option",{value:","},"英文逗号",-1),f=(0,o.createElementVNode)("option",{value:"."},"小圆点",-1),v=(0,o.createElementVNode)("option",{value:" "},"空格",-1),h=[p,f,v],g=(0,o.createTextVNode)("点击添加进入颜色列表"),b=(0,o.createTextVNode)("颜色可视："),y={class:"default-colorlump colorlump"},V=(0,o.createElementVNode)("h2",null,"默认颜色",-1),x={class:"default-colorlump colorlump"};function N(e,t,n,p,f,v){var N=(0,o.resolveDirective)("color-visual");return(0,o.openBlock)(),(0,o.createBlock)(a.K,{id:"main"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(d.v,{theme:e.theme,"with-background":"",class:"pa-10"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(r.o,{"no-gutters":"",class:"mb-12",justify:"center"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[c]})),_:1})]})),_:1}),(0,o.createVNode)(r.o,{"no-gutters":"",class:"mb-12",justify:"center"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[s]})),_:1}),(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[u]})),_:1}),(0,o.createVNode)(i.D,{cols:"4"},{default:(0,o.withCtx)((function(){return[m,(0,o.withDirectives)((0,o.createElementVNode)("select",{name:"splitor","onUpdate:modelValue":t[0]||(t[0]=function(t){return e.splitor=t})},h,512),[[o.vModelSelect,e.splitor]])]})),_:1})]})),_:1}),(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[(0,o.withDirectives)((0,o.createElementVNode)("textarea",{name:"inputtedStr",type:"text","onUpdate:modelValue":t[1]||(t[1]=function(t){return e.inputtedStr=t})},null,512),[[o.vModelText,e.inputtedStr]])]})),_:1}),(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(l.T,{onClick:e.addColor},{default:(0,o.withCtx)((function(){return[g]})),_:1},8,["onClick"])]})),_:1})]})),_:1})]})),_:1}),(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[b]})),_:1}),(0,o.createVNode)(r.o,{justify:"center"},{default:(0,o.withCtx)((function(){return[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.colorList,(function(e,t){return(0,o.openBlock)(),(0,o.createBlock)(i.D,{key:t,cols:"1"},{default:(0,o.withCtx)((function(){return[(0,o.withDirectives)(((0,o.openBlock)(),(0,o.createElementBlock)("div",y,[(0,o.createTextVNode)((0,o.toDisplayString)(e),1)])),[[N]])]})),_:2},1024)})),128))]})),_:1})]})),_:1})]})),_:1}),(0,o.createVNode)(r.o,{"no-gutters":"",class:"mb-12",justify:"center"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(i.D,null,{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(r.o,null,{default:(0,o.withCtx)((function(){return[V]})),_:1}),(0,o.createVNode)(r.o,{justify:"center"},{default:(0,o.withCtx)((function(){return[((0,o.openBlock)(!0),(0,o.createElementBlock)(o.Fragment,null,(0,o.renderList)(e.defaultColorList,(function(e,t){return(0,o.openBlock)(),(0,o.createBlock)(i.D,{key:t,cols:"1",md:"2",xs:"3"},{default:(0,o.withCtx)((function(){return[(0,o.withDirectives)(((0,o.openBlock)(),(0,o.createElementBlock)("div",x,[(0,o.createTextVNode)((0,o.toDisplayString)(e),1)])),[[N]])]})),_:2},1024)})),128))]})),_:1})]})),_:1})]})),_:1})]})),_:1},8,["theme"])]})),_:1})}n(74916),n(15306),n(24603),n(28450),n(88386),n(39714),n(68757),n(23123),n(92222);var E=n(28157),w=n(35583),k=(0,o.defineComponent)({name:"Pallet",directives:{"color-visual":{mounted:function(e){e.style.backgroundColor=e.innerHTML,e.style.color="white",e.classList.add("fastcopy")}}},data:function(){return{theme:"light",defaultColorList:["#cdfff5","#ffcdf0","#d7ffcd","#fff5cd","#cdf0ff","#ffdccd","#dccdff","#cdffdc","#ffcdd7"],inputtedColorList:[],splitor:",",inputtedStr:""}},computed:{colorList:function(){var e=this.inputtedStr.replace(new RegExp("/(".concat(this.splitor,")+/g")),"$1");return e=e.replaceAll(/["'“‘’”]/g,""),e.split(this.splitor)}},setup:function(){var e=(0,E.AW)();return console.log(e),{display:e}},methods:{addColor:function(){this.inputtedColorList.concat(this.colorList),this.inputtedStr=""}},created:function(){},mounted:function(){this.$el.addEventListener("click",(function(e){e.target.classList.contains("fastcopy")&&(0,w.copyTextToClipboard)(e.target.textContent||e.target.innerHTML)}))}});n(71034);var C=n(83744);const D=(0,C.Z)(k,[["render",N]]);var T=D},69488:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return $}});n(68309),n(82526),n(41817);var o=n(56598),l=n(16824),a=n(68521),r=n(46769),i={id:"theme-style-dev"},d=(0,o.createElementVNode)("h1",{class:"page-headline"},[(0,o.createElementVNode)("span",null,"Theme Style Development Helper")],-1),c={class:"main layout resp-width vw-center resp-padding pt-4 pb-6"},s={class:"style-dev-head mt-4 mb-3"},u=(0,o.createElementVNode)("h2",null,"主题风格配置编辑器",-1),m=(0,o.createElementVNode)("span",{class:"iconfont icon-download"},"保存",-1),p=[m],f={class:"style-dev-body mb-3"},v=(0,o.createElementVNode)("p",null,[(0,o.createElementVNode)("i",null,"(in developing)")],-1),h=(0,o.createElementVNode)("hr",null,null,-1),g={class:"dev-start mb-6"},b=(0,o.createElementVNode)("div",null," 上传主题配置文件(允许注释的json) ",-1),y=(0,o.createElementVNode)("p",null,"或者直接粘贴文本",-1),V={class:"dev-style"},x=(0,o.createElementVNode)("label",{for:"name",id:"dev-name"},"name: ",-1),N=(0,o.createElementVNode)("label",{for:"alias",id:"dev-alias"},"alias: ",-1),E={class:"style-desc mb-4"},w=(0,o.createElementVNode)("label",{for:"desc",id:"dev-desc"},"description: ",-1),k={class:"mb-4"},C=(0,o.createElementVNode)("label",{for:"home",id:"dev-home"},"home: ",-1),D={class:"style-intro mb-4"},T={for:"intro"},B=(0,o.createTextVNode)("mdi-file-document"),_=(0,o.createTextVNode)(" 介绍文件： "),M=(0,o.createElementVNode)("input",{id:"dev-intro",type:"text",placeholder:"Markdown文件介绍路径："},null,-1),A=(0,o.createElementVNode)("div",{class:"style-dev-footer mb-6"},null,-1);function U(e,t,n,m,U,J){var S=(0,o.resolveComponent)("aui-file-field");return(0,o.openBlock)(),(0,o.createElementBlock)("div",i,[d,(0,o.createElementVNode)("div",c,[(0,o.createElementVNode)("div",s,[u,(0,o.createElementVNode)("button",{onClick:t[0]||(t[0]=function(){return e.saveJson&&e.saveJson.apply(e,arguments)}),"data-balloon":"导出主题风格配置","data-balloon-pos":"down"},p)]),(0,o.createElementVNode)("div",f,[v,h,(0,o.createElementVNode)("div",g,[(0,o.createElementVNode)("div",null,[b,(0,o.createVNode)(S,{onHandleFiles:e.handleFiles,style:{height:"5em"}},null,8,["onHandleFiles"])]),y,(0,o.createElementVNode)("textarea",{onChange:t[1]||(t[1]=function(t){return e.importJson(t.target.value)}),rows:"5"},null,32)]),(0,o.createElementVNode)("div",V,[(0,o.createVNode)(l.o,{class:"mb-4"},{default:(0,o.withCtx)((function(){return[(0,o.createVNode)(a.D,null,{default:(0,o.withCtx)((function(){return[x,(0,o.withDirectives)((0,o.createElementVNode)("input",{id:"dev-name",type:"text",placeholder:"名称(唯一标识)","onUpdate:modelValue":t[2]||(t[2]=function(t){return e.EntryJson.name=t})},null,512),[[o.vModelText,e.EntryJson.name]])]})),_:1}),(0,o.createVNode)(a.D,null,{default:(0,o.withCtx)((function(){return[N,(0,o.withDirectives)((0,o.createElementVNode)("input",{id:"dev-alias",type:"text",placeholder:"别名","onUpdate:modelValue":t[3]||(t[3]=function(t){return e.EntryJson.alias=t})},null,512),[[o.vModelText,e.EntryJson.alias]])]})),_:1})]})),_:1}),(0,o.createElementVNode)("div",E,[w,(0,o.withDirectives)((0,o.createElementVNode)("textarea",{id:"dev-desc",type:"text",placehoder:"简介","onUpdate:modelValue":t[4]||(t[4]=function(t){return e.EntryJson.description=t})},"\r\n            ",512),[[o.vModelText,e.EntryJson.description]])]),(0,o.createElementVNode)("div",k,[C,(0,o.withDirectives)((0,o.createElementVNode)("input",{id:"dev-home",type:"text",placeholder:"主页链接","onUpdate:modelValue":t[5]||(t[5]=function(t){return e.EntryJson.home=t})},null,512),[[o.vModelText,e.EntryJson.home]])]),(0,o.createElementVNode)("div",D,[(0,o.createElementVNode)("label",T,[(0,o.createVNode)(r.t,null,{default:(0,o.withCtx)((function(){return[B]})),_:1}),_]),M])])]),A])])}n(38862),n(74916),n(15306),n(77601);var J=n(35583),S=n(5450),j=n.n(S),L=n(54156),Z=n(89745),z=n(23176),F=(0,o.defineComponent)({name:"Dev-style",inheritAttrs:!1,props:["animeTemp"],components:{"aui-file-field":L.Z},setup:function(e){var t=(0,o.reactive)({name:"",alias:"",description:"",author:{nick:"",avatar:"",link:""},home:"",thumbs:"",introduce:"",blending:{onLight:"",onDark:""},styles:[],scripts:[],async_script:!1}),n=new(j())("dev-style",{initStorage:t,localInterface:{database:window.sessionStorage}});return(0,o.watch)(t,(function(){n.save()}),{deep:!0}),(0,o.onUnmounted)((function(){n.destroy()})),{EntryJson:t}},methods:{saveJson:function(){this.EntryJson.name?(0,J.fileExport)(JSON.stringify(this.EntryJson),"entry.json","application/json"):this.$magic.utility.lzynotice({semantic:"warning",content:"名称为必填字段!"})},importJson:function(e){e=e.replace(/\/\*.*?\*\//g,"").replace(/\/\/.*?\n/g,"\n");try{var t=JSON.parse(e+"");(0,Z.deepRefresh)(this.EntryJson,t),this.$magic.utility.lzynotice({content:"导入配置数据成功",semantic:"success"})}catch(n){this.$magic.utility.lzynotice({content:"导入配置数据失败",semantic:"error"}),console.error(n)}},handleFiles:function(e){for(var t=this,n=0;n<e.length;n++){var o=e[n],l=/\/json/;if(z.DEBUG&&console.log(o),l.test(o.type)){var a=new FileReader;a.onload=function(e){var n,o=(null===(n=e.target)||void 0===n?void 0:n.result)+"";t.importJson(o)},a.readAsText(o)}}}},mounted:function(){},unmounted:function(){}}),G=(n(39119),n(83744));const O=(0,G.Z)(F,[["render",U]]);var $=O},97117:function(e,t,n){"use strict";n.d(t,{Z:function(){return f}});var o=n(56598),l={class:"animeui-home"},a={href:"#/",class:"animesearcher-icon",draggable:"false","data-balloon":"返回主页","data-balloon-pos":"down"},r={key:0,href:"#/",target:"_blank",draggable:"false",class:"animesearcher-title","data-balloon":"新窗口打开主页","data-balloon-pos":"down"},i=(0,o.createElementVNode)("div",{style:{"font-size":"1.25rem","line-height":"1rem"}},"Anime",-1),d=(0,o.createElementVNode)("div",{style:{"font-size":"1rem","line-height":"1rem"}},"Searcher",-1),c=[i,d];function s(e,t,n,i,d,s){var u=(0,o.resolveComponent)("svgicon");return(0,o.openBlock)(),(0,o.createElementBlock)("div",l,[(0,o.createElementVNode)("a",a,[(0,o.createElementVNode)("span",null,[(0,o.createVNode)(u,{name:"logo",color:"rgb(var(--v-theme-on-surface))"})])]),e.animeTemp.isMobile?(0,o.createCommentVNode)("",!0):((0,o.openBlock)(),(0,o.createElementBlock)("a",r,c))])}var u=(0,o.defineComponent)({name:"animeui-home",props:{animeTemp:{type:Object,default:{isMobile:!1}}},setup:function(){}}),m=(n(2235),n(83744));const p=(0,m.Z)(u,[["render",s]]);var f=p},69146:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),a=n(23645),r=n.n(a),i=r()(l());i.push([e.id,".colorlump{display:inline-block;margin:15px auto;padding:3px 5px;border-radius:3px;color:#fff;font-size:14px;font-weight:500;-webkit-user-select:all;-moz-user-select:all;user-select:all}.default-colorlump{border:1px solid gray}",""]),t["default"]=i},72921:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),a=n(23645),r=n.n(a),i=r()(l());i.push([e.id,".aui-file-field{display:flex;justify-content:center;align-items:center;width:100%;border:1px solid rgb(var(--v-lightgrey));border-radius:var(--v-layer-md-radius);transition:border .5s linear,background .5s linear;background-color:transparent}.aui-file-field.field-drapover{border:3px dashed rgb(var(--v-grey));background-color:rgba(var(--v-theme-on-surface),.6)}.aui-file-field input{cursor:pointer}",""]),t["default"]=i},22189:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),a=n(23645),r=n.n(a),i=n(61667),d=n.n(i),c=new URL(n(79457),n.b),s=r()(l()),u=d()(c);s.push([e.id,"#theme-blending-dev .main .title{display:flex;justify-content:space-between;align-content:center;font-size:24px;margin-top:12px;margin-bottom:16px}#theme-blending-dev .main .title span{margin:auto 12px}#theme-blending-dev .main .title span button{margin-left:8px}#theme-blending-dev .main .title span button label{cursor:pointer}#theme-blending-dev .main .title span button span{font-size:16px;cursor:pointer}#theme-blending-dev .main .blending>h2,#theme-blending-dev .main .colors>h2,#theme-blending-dev .main h4{margin:auto 12px}#theme-blending-dev .main .blend-infos{margin-bottom:16px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center}#theme-blending-dev .main .blend-infos label{flex:1 1 auto;width:22em;margin-bottom:.5em}#theme-blending-dev .main .blend-infos label input{display:inline-block;border:1px solid rgb(var(--v-theme-on-surface));border-radius:3px;max-width:100%}#theme-blending-dev .main .dark-set{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}#theme-blending-dev .main .blending,#theme-blending-dev .main .colors{margin-bottom:16px}#theme-blending-dev .main ul.content{display:flex;justify-content:space-between;align-content:center;align-items:center;flex-wrap:wrap}#theme-blending-dev .main ul.content li{list-style:none}#theme-blending-dev .main ul.content li input{display:inline-block;vertical-align:middle}#theme-blending-dev .main ul.content li label .lump{display:inline-block;width:20px;height:20px;margin-right:8px;vertical-align:middle;background-color:var(--bgcolor);box-shadow:1px 1px 3px var(--bgcolor),-2px -1px 3px gray;cursor:pointer}#theme-blending-dev .main ul.content li label .lump.opacity{background:url("+u+") repeat;border-radius:50%;border:1px solid gray}#theme-blending-dev .colorlump{display:inline-block;margin:15px auto;padding:3px 5px;border-radius:3px;color:#fff;font-size:14px;font-weight:500;-webkit-user-select:all;-moz-user-select:all;user-select:all}#theme-blending-dev .default-colorlump{border:1px solid gray}",""]),t["default"]=s},10564:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),a=n(23645),r=n.n(a),i=r()(l());i.push([e.id,"#theme-style-dev .style-dev-head{display:flex;justify-content:space-between}#theme-style-dev .style-dev-head button{margin-right:.5em}#theme-style-dev .style-dev-body{display:flex;flex-direction:column;color:rgb(var(--v-theme-on-background));border-width:0;border-color:rgb(var(--v-theme-on-background))}#theme-style-dev .style-dev-body .dev-start textarea{width:100%}#theme-style-dev .style-dev-body .dev-style .style-desc{display:flex;justify-content:space-between;align-items:flex-start}#theme-style-dev .style-dev-body .dev-style .style-desc textarea{flex:1 1 auto;width:100%}#theme-style-dev .style-dev-body input,#theme-style-dev .style-dev-body textarea{border-bottom:1px solid rgb(var(--v-theme-on-background));flex:1 1 auto;width:100%}#theme-style-dev .style-dev-body input{display:inline-block;padding:.125em .5em;border-radius:var(--v-layer-sm-radius)}#theme-style-dev .style-dev-body textarea{padding:.5em .75em;border-radius:var(--v-layer-md-radius)}",""]),t["default"]=i},46721:function(e,t,n){"use strict";n.r(t);var o=n(8081),l=n.n(o),a=n(23645),r=n.n(a),i=r()(l());i.push([e.id,".animeui-home{display:flex;align-items:center;justify-content:flex-start}.animeui-home a{text-decoration:none;color:inherit}.animeui-home a:visited{color:inherit}.animeui-home .animesearcher-icon{display:inline-block;padding:.375em .375em .25em .5em}.animeui-home .animesearcher-title{display:inline-block;padding:.375em .5em .375em .125em;text-align:center}",""]),t["default"]=i},71034:function(e,t,n){var o=n(69146);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("4290517f",o,!0,{sourceMap:!1,shadowMode:!1})},20073:function(e,t,n){var o=n(72921);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("1e8dba13",o,!0,{sourceMap:!1,shadowMode:!1})},81605:function(e,t,n){var o=n(22189);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("da75183e",o,!0,{sourceMap:!1,shadowMode:!1})},39119:function(e,t,n){var o=n(10564);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("7c98b332",o,!0,{sourceMap:!1,shadowMode:!1})},2235:function(e,t,n){var o=n(46721);o.__esModule&&(o=o.default),"string"===typeof o&&(o=[[e.id,o,""]]),o.locals&&(e.exports=o.locals);var l=n(54402).Z;l("948cd04e",o,!0,{sourceMap:!1,shadowMode:!1})},79457:function(e){"use strict";e.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAGElEQVQYlWNgYGCQwoKxgqGgcJA5h3yFAAs8BRWVSwooAAAAAElFTkSuQmCC"}}]);