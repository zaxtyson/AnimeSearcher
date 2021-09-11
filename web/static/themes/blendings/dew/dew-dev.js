const blending = {
  // Name is Case sensitive! Must be the same with configuration.
  "name": "Dew", // blending name. should be unique and recommend in English. Required. 
  "Alias": "配色小清新", // nickname 昵称. Required
  "description": "享受缤纷多彩与小清新结合吧！", // blending descriptions.
  "author": { // author infors
    "nick": "Lozyue",
    "avatar": "avatar.png",
    "link": "http://github.com/lozyue"
  },
  "home": "http://github.com/lozyue/animesearcherui/#public/themes/fantasy", // Blend HOME
  "thumbs": "thumb.jpg", // Blending thumbnails.
  "blending": { // blending contents. Required
    
    "background": "lightblue", // Not supported. please use #add8e6 instead.
    "surface": "#fff",

    // normal colors
    "pink": "#f294c6",
    "light-purple": "#dfb7d6",
    "green": "#d5e751",
    "blue": "#9bdef5",
    "light-orange": "#f0917e",
    "yellow" : "#fbe765",
    "amber": "#f6c54b", // 橙黄色 琥珀色
    "cyan": "#00BCD4", // 蓝绿色

    // color contrary
    "on-background": "#fff", // 默认在背景上显示的颜色
    "on-surface": "#000", // 默认在表面上显示的颜色
    "on-pink": "#fff", // 默认在 pink 颜色上显示的颜色
    "on-light-purple": "#fff",
    "on-green": "#fff",
    "on-blue": "#fff",
    "on-light-orange": "#fff",
    "on-yellow": "#fff",
    "on-amber": "#fff",
    "on-cyan": "#fff",
    
    "on-primary": "#fff",
    "on-secondary": "#fff",
    "on-tertiary": "", // 第三 子配色
    "on-quaternary": "", // 第四 子配色
    "on-success": "#fff",
    "on-warning": "#fff",
    "on-danger": "#fff",
    "on-info": "#fff",
    
    // main color configurations.
    "primary": "#234b12",
    "secondary": "purple",
    "tertiary": "", // 第三 子配色
    "quaternary": "", // 第四 子配色
    "quinary": "", // 第五
    "senary": "", // 第六
    "septenary": "", // 七的，第七
    "octonary": "", // 八进制 第八
    "nonary": "", // 九进制 第九
    "denary": "", // 十的 第十

    "success": "rgb(33,186,46)", // 也不行，使用十六进制代替.
    "warning": "raba(46,188,213)", // 不支持带透明度的主题配色
    "danger": "",
    "info": ""
  },
  "dark": false, // whether this is a dark blending.
}