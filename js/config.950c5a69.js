"use strict";
(self["webpackChunkAnimeUI"] = self["webpackChunkAnimeUI"] || []).push([
  [497],
  {
    4516: function (e, r, a) {
      a.r(r),
        a.d(r, {
          AjaxAddress: function () {
            return o;
          },
          NOTIFYS: function () {
            return i;
          },
          USAGETIPS: function () {
            return n;
          },
          BlendingDefaultLight: function () {
            return h;
          },
          BlendingDefaultDark: function () {
            return b;
          },
          StyleDefault: function () {
            return m;
          },
          PublicConsistentCabinetName: function () {
            return g;
          },
          PublicTemporaryCabinetName: function () {
            return F;
          },
          LocalConsistentCabinetName: function () {
            return f;
          },
          ConsistentThemeOptionCabinet: function () {
            return k;
          },
        });
      var t = a(95082),
        o = {
          baseURL: "http://127.0.0.1:6001/",
          $baseSocket: "ws://127.0.0.1:6001/",
          CHECKFILESOURCE: !0,
        },
        i = [
          "高度定制的主题系统支持，配色和风格双重加成，分离亮暗模式，全新视觉，全新体验！",
          "顶端架构多端适配支持，PWA支持移动端提升体验！",
          "主题风格加成丰富的API支持，轻松实现高度定制！",
          "偏好设定模型视图存储深度解耦，轻松扩展",
        ],
        n = [
          "[小细节]: 在点击搜索框的搜索历史条目的空白处时会填充搜索词并搜素，而点击历史搜索词上仅会进行填充",
        ],
        c = {
          primary: "#0088f4",
          secondary: "#03DAC6",
          tertiary: "#f0917e",
          quaternary: "#dfb7d6",
        },
        u = {
          pink: "#f294c6",
          purple: "#dfb7d6",
          green: "#d5e751",
          blue: "#9bdef5",
          orange: "#f0917e",
          yellow: "#fbe765",
          cream: "#fce2ce",
          "on-grey": "#fff",
        },
        d = { grey: "#808080", lightgrey: "#d3d3d3" },
        s = { grey: "#d3d3d3", lightgrey: "#808080" },
        p = {
          "layer-opacity": 0.75,
          "layer-sm-radius": "3px",
          "layer-md-radius": "5px",
          "layer-lg-radius": "10px",
        },
        l = { "layer-darken": 1 },
        y = { "layer-darken": 0.75 },
        h = {
          name: "light",
          description: "默认亮色主题配色",
          author: {
            nick: "Lozyue",
            avatar: "avatar.png",
            link: "http://github.com/lozyue",
          },
          home: "http://github.com/lozyue/animesearcherui/",
          thumbs: "/thumb-blending-light.jpg",
          blending: (0, t.Z)(
            {
              background: "#FFFFFF",
              surface: "#FFFFFF",
              "primary-darken-1": "#3700B3",
              "secondary-darken-1": "#018786",
              error: "#B00020",
              info: "#2196F3",
              success: "#4CAF50",
              warning: "#FB8C00",
            },
            c
          ),
          colors: (0, t.Z)(
            (0, t.Z)((0, t.Z)((0, t.Z)((0, t.Z)({}, u), d), p), l),
            {},
            {
              "border-color": "#000000",
              "border-opacity": 0.12,
              "high-emphasis-opacity": 0.87,
              "medium-emphasis-opacity": 0.6,
              "disabled-opacity": 0.38,
              "activated-opacity": 0.12,
              "idle-opacity": 0.04,
              "hover-opacity": 0.12,
              "focus-opacity": 0.12,
              "selected-opacity": 0.08,
              "dragged-opacity": 0.08,
              "pressed-opacity": 0.16,
              "kbd-background-color": "#212529",
              "kbd-color": "#FFFFFF",
              "code-background-color": "#C2C2C2",
            }
          ),
          dark: !1,
        },
        b = {
          name: "dark",
          description: "默认暗色主题配色",
          author: {
            nick: "Lozyue",
            avatar: "avatar.png",
            link: "http://github.com/lozyue",
          },
          home: "http://github.com/lozyue/animesearcherui/",
          thumbs: "/thumb-blending-dark.jpg",
          blending: (0, t.Z)(
            (0, t.Z)({}, c),
            {},
            {
              background: "#121212",
              surface: "#212121",
              primary: "#BB86FC",
              "primary-darken-1": "#3700B3",
              secondary: "#03DAC5",
              "secondary-darken-1": "#03DAC5",
              error: "#CF6679",
              info: "#2196F3",
              success: "#4CAF50",
              warning: "#FB8C00",
            }
          ),
          colors: (0, t.Z)(
            (0, t.Z)((0, t.Z)((0, t.Z)((0, t.Z)({}, u), s), p), y),
            {},
            {
              "border-color": "#FFFFFF",
              "border-opacity": 0.12,
              "high-emphasis-opacity": 0.87,
              "medium-emphasis-opacity": 0.6,
              "disabled-opacity": 0.38,
              "activated-opacity": 0.12,
              "idle-opacity": 0.1,
              "hover-opacity": 0.04,
              "focus-opacity": 0.12,
              "selected-opacity": 0.08,
              "dragged-opacity": 0.08,
              "pressed-opacity": 0.16,
              "kbd-background-color": "#212529",
              "kbd-color": "#FFFFFF",
              "code-background-color": "#B7B7B7",
            }
          ),
          dark: !0,
        },
        m = {
          name: "default",
          description: "默认主题风格",
          author: {
            nick: "Lozyue",
            avatar: "avatar.png",
            link: "http://github.com/lozyue",
          },
          home: "http://github.com/lozyue/animesearcherui",
          thumbs: "/thumb-style.jpg",
          styles: [],
          scripts: [],
        },
        g = "animeUI",
        F = "animeTemp",
        f = "locsys",
        k = "locTheme";
    },
  },
]);
