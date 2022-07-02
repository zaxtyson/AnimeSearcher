# 说明

## engines

> `engines` 目录存放各类引擎模块, 该目录需部署到服务器上, 以供程序启动时动态加载

### Why?

资源网站是经常变化的, 对应的解析引擎也需要实时跟进, 因此用户需要经常更新程序.

为了提供更好的使用体验, 引擎模块被抽离出来, 程序每次启动时从服务器加载引擎, 这使得用户可以在无感知的情况下使用到最新引擎!

### 配置

`config.json` 中 `remote_repo` 为引擎仓库地址, 默认为 `https://engines.zaxtyson.cn`

该地址与本项目 [master](https://github.com/zaxtyson/AnimeSearcher/tree/master) 分支保持同步
(原打算用 Cloudflare Worker 加速, 结果被墙了. 国内 Gitee 仓库又遇到审核而且 API 速度也不是很稳定)

**为了安全起见, 请不要随意使用第三方引擎仓库**

### 部署

将 `engines` 目录作为 ***根目录*** 部署到静态资源服务器上即可

比如, 我们可以在本地启动一个简单的 server

```shell
cd AnimeSearcher/static/engines
python -m http.server 8081
```

将 `remote_repo` 设置为 `http://127.0.0.1:8081` 即可

# certs

> `certs` 目录存放域名的证书文件

如需启用 https, 请在 `config.json` 设置 `https` 为 `true`, 将 `host` 设置为真实域名

同时将域名的证书、私钥放到`certs`目录下, 域名证书命名为 `cert.pem`, 私钥命名为 `key.pem`

项目提供的证书和私钥仅用于测试, 使用 [mkcert](https://github.com/FiloSottile/mkcert) 生成:

```shell
mkcert.exe -install                 # 在系统中安装本地 CA 证书
mkcert.exe localhost 127.0.0.1 ::1  # 生成证书+私钥
```

现在可以通过 `https://localhost:6001`、`https://127.0.0.1:6001` 访问了
