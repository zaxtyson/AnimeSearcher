if(!self.define){let e,s={};const n=(n,i)=>(n=new URL(n+".js",i).href,s[n]||new Promise((s=>{if("document"in self){const e=document.createElement("script");e.src=n,e.onload=s,document.head.appendChild(e)}else e=n,importScripts(n),s()})).then((()=>{let e=s[n];if(!e)throw new Error(`Module ${n} didn’t register its module`);return e})));self.define=(i,a)=>{const r=e||("document"in self?document.currentScript.src:"")||location.href;if(s[r])return;let l={};const f=e=>n(e,r),o={module:{uri:r},exports:l,require:f};s[r]=Promise.all(i.map((e=>o[e]||f(e)))).then((e=>(a(...e),l)))}}define(["./workbox-904edfb9"],(function(e){"use strict";e.setCacheNameDetails({prefix:"AnimeUI"}),self.addEventListener("message",(e=>{e.data&&"SKIP_WAITING"===e.data.type&&self.skipWaiting()})),e.precacheAndRoute([{url:"favicon.ico",revision:"24b7b6836393dc6facabfe8aab9542b5"},{url:"fonts/iconfont.5fff961f.woff",revision:null},{url:"fonts/iconfont.ac81ba93.ttf",revision:null},{url:"fonts/iconfont.c5074dbf.woff2",revision:null},{url:"fonts/materialdesignicons-webfont.21f691f0.ttf",revision:null},{url:"fonts/materialdesignicons-webfont.54b0f60d.woff2",revision:null},{url:"fonts/materialdesignicons-webfont.5d875350.eot",revision:null},{url:"fonts/materialdesignicons-webfont.d671cbf6.woff",revision:null},{url:"img/404.78c1dca5.jpg",revision:null},{url:"img/bg-default.jpg",revision:"e511b4dd3c77bcfb5ac815fe3cb8d5fa"},{url:"img/blending-dark-thumb.png",revision:"815840d4d8bd53fc516166bc9b6230ee"},{url:"img/blending-light-thumb.png",revision:"bf79ae180faaec9be42bdd9b2892929c"},{url:"img/default-cover.7ccf8463.png",revision:null},{url:"img/heart_fly.45ff2efe.png",revision:null},{url:"img/icons/favicon.svg",revision:"5c1d58ab21916321749d3e826ed54d14"},{url:"img/style-default-thumb.png",revision:"84b92c9b8ad7df62bc83bcc050aa6400"},{url:"img/svg/sprite.svg",revision:"caa25229a83ebf3abfd86377f0551b6e"},{url:"index.html",revision:"774236b17077a0fe2f3a3cd5f4aa90fb"},{url:"js/10.e7795a37.js",revision:null},{url:"js/184.1a77e919.js",revision:null},{url:"js/719.2c1ba7f1.js",revision:null},{url:"js/76.f72f4f65.js",revision:null},{url:"js/anime.d0df2fc4.js",revision:null},{url:"js/app.b580be2f.js",revision:null},{url:"js/basement.11c261a0.js",revision:null},{url:"js/body.667dce62.js",revision:null},{url:"js/chunck-exlibs.c96dca4b.js",revision:null},{url:"js/chunck-flv.21cea021.js",revision:null},{url:"js/chunck-hls.c8586aba.js",revision:null},{url:"js/chunck-webtorrent.bbb349ea.js",revision:null},{url:"js/chunk-vendors.549cfe86.js",revision:null},{url:"js/development.7afdb077.js",revision:null},{url:"js/fragment-async.2b0d43cb.js",revision:null},{url:"js/global-async.6b0b92a1.js",revision:null},{url:"js/irrelevant.4e7429a5.js",revision:null},{url:"js/mobile.6090acac.js",revision:null},{url:"js/quotations.f8cf7ccc.js",revision:null},{url:"js/theme.ae709864.js",revision:null},{url:"js/tvlive.7efb2a14.js",revision:null},{url:"manifest/animeui.png",revision:"24b7b6836393dc6facabfe8aab9542b5"},{url:"manifest/favicon.ico",revision:"24b7b6836393dc6facabfe8aab9542b5"},{url:"manifest/icons/standard/android-chrome-192x192.png",revision:"46c0bb69b9aa62723f3a95a716772e37"},{url:"manifest/icons/standard/android-chrome-512x512.png",revision:"ddff45e6a153aba28976c5a58f1ae80b"},{url:"manifest/icons/standard/android-chrome-maskable-192x192.png",revision:"46c0bb69b9aa62723f3a95a716772e37"},{url:"manifest/icons/standard/android-chrome-maskable-512x512.png",revision:"ddff45e6a153aba28976c5a58f1ae80b"},{url:"manifest/icons/standard/animeui-150x150.png",revision:"3ec49c3b1aad56bc72d1ffde7c3ab586"},{url:"manifest/icons/standard/apple-touch-icon-120x120.png",revision:"81f1ca988e934e8dba12bc91d6d6b452"},{url:"manifest/icons/standard/apple-touch-icon-152x152.png",revision:"b514f02edd75834f047cd52f1b28fe58"},{url:"manifest/icons/standard/apple-touch-icon-180x180.png",revision:"a88dbd22e9ae0a60494ea53b211cdd84"},{url:"manifest/icons/standard/apple-touch-icon-60x60.png",revision:"206e2253c334bd0b1f4e6d356e226950"},{url:"manifest/icons/standard/apple-touch-icon-76x76.png",revision:"948c8f84fef771e33f18fe8aae3d5c17"},{url:"manifest/icons/standard/apple-touch-icon.png",revision:"a88dbd22e9ae0a60494ea53b211cdd84"},{url:"manifest/icons/standard/favicon-16x16.png",revision:"98af99b6ad2498d5fbaece982dd1b414"},{url:"manifest/icons/standard/favicon-32x32.png",revision:"711e989595a8df07a934dced41be7b9c"},{url:"manifest/icons/standard/msapplication-icon-144x144.png",revision:"f65b65d818589dfc47e300643a5428a0"},{url:"manifest/icons/standard/mstile-150x150.png",revision:"ce3c0a96bffd3b21e52bb4602b8bca90"},{url:"manifest/icons/standard/safari-pinned-tab.svg",revision:"5c1d58ab21916321749d3e826ed54d14"},{url:"manifest/manifest.json",revision:"9b4d1b7730233930e52c61ba0d5b1821"},{url:"statics/images/favicon.png",revision:"6f819f18dfee23b2703c43016518af0f"},{url:"themes/blendings/custom/custom.json",revision:"eb79f37f7c5acbc8b87c1fe922e4e4e5"},{url:"themes/blendings/dew-dark/dew-dark.json",revision:"a9e3a1e5865e4efefdf67d721a6b24a3"},{url:"themes/blendings/dew/dew.json",revision:"523c27ce233ae5445f26f726f3f503d9"},{url:"themes/config.json",revision:"374e890cb72900c8783bd366a5c94c2a"},{url:"themes/styles/custom/entry.json",revision:"2b14739c3caf656dc1291ced780b02f7"},{url:"themes/styles/custom/main.js",revision:"d78dbd43a2cdad263e92c92eb96ff577"},{url:"themes/styles/custom/privilege.js",revision:"636c0e5b224c9db3e14d873fa20f9cee"},{url:"themes/styles/fantasy/css/fantasy.css",revision:"2ceffce290fdf0faa6e95a2ed5758df3"},{url:"themes/styles/fantasy/css/fantasy.scss",revision:"c332cd2a8f5590f6e6d206be8de32e79"},{url:"themes/styles/fantasy/css/override.css",revision:"aa3d35d24cdf85035996c72456c1ad4a"},{url:"themes/styles/fantasy/css/override.scss",revision:"dc1e96184836b6110165d909c136e28f"},{url:"themes/styles/fantasy/entry.json",revision:"7d2bf7cb30f35d5337ea4d991435f923"},{url:"themes/styles/fantasy/images/404.jpg",revision:"676abb897e664b89562589582b8a3141"},{url:"themes/styles/fantasy/images/bilibili.jpg",revision:"75fad07584a4f07173d5b06b5989d218"},{url:"themes/styles/fantasy/images/cloud.png",revision:"601f4fe39b3cd73f7c3fdfcf4f9c8a95"},{url:"themes/styles/fantasy/images/hello.webp",revision:"f29087e9218b0fc93da5baeb389f3165"},{url:"themes/styles/fantasy/images/moon.png",revision:"a8924dbbf9b376a752aca1a509cedecb"},{url:"themes/styles/fantasy/images/thumb.jpg",revision:"852ac5eed4e15a92262c8fc701594a68"},{url:"themes/styles/fantasy/js/background.js",revision:"a85168227976847dafdfca858b95dbc1"},{url:"themes/styles/fantasy/js/decorations.js",revision:"311b004153659db25a0909f1dcb3091d"},{url:"themes/styles/fantasy/js/main.js",revision:"1c6747d884150df768cf0e160d8ae512"},{url:"themes/styles/fantasy/js/quotation.js",revision:"08285245ea247820815052a5e515f3b9"}],{ignoreURLParametersMatching:[/\.md$/,/\.txt$/]}),e.registerRoute(/\.(?:js|css|html|json|svg)$/,new e.StaleWhileRevalidate,"GET")}));
