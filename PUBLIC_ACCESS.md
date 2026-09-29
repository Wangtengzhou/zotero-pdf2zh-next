# 公网访问与令牌管理

## 访问地址

内网和公网统一使用令牌入口。Zotero PDF2zh 插件可使用以下服务器地址：

```text
https://pdf.example.com/access/<随机访问令牌>
http://192.168.1.10:8890/access/<随机访问令牌>
```

插件在此地址后追加连接检查、上传、轮询和下载路径，网关逐次验证令牌。客户端无需浏览器登录或绑定固定 IP。

Lucky 等反向代理需保留完整路径与查询参数。网关验证令牌后剥离 `/access/<令牌>` 前缀，将业务请求转发到容器内部服务端。所有业务接口均受认证保护。

## 获取地址与令牌

在服务器终端执行：

```bash
docker exec zotero-pdf2zh-next pdf2zh-admin url show
docker exec zotero-pdf2zh-next pdf2zh-admin token show
```

使用 Portainer 或 NAS 容器管理器时，打开容器终端，选择 `/bin/sh`，使用镜像默认的 `app` 用户（UID `10001`），直接执行：

```bash
pdf2zh-admin url show
pdf2zh-admin token show
```

未配置域名时，`url show` 输出 `/access/<令牌>`；将它接在服务器地址之后即可使用。可以通过命令参数临时生成完整地址：

```bash
pdf2zh-admin url show --base-url http://192.168.1.10:8890
pdf2zh-admin url show --base-url https://pdf.example.com
pdf2zh-admin url show --base-url https://another.example.com
```

`PUBLIC_BASE_URL` 是可选的显示偏好，支持 HTTP(S) 地址及可选端口，不包含令牌或 `/access` 路径。网关不依赖它启动，也不绑定任何域名；多个 Lucky 反代域名可同时使用同一令牌。

## 重置令牌

```bash
# 服务器终端
docker exec zotero-pdf2zh-next pdf2zh-admin token reset

# 或容器内部终端
pdf2zh-admin token reset
```

命令生成新令牌并显示新地址，无需重启容器。重置后更新 Zotero 的服务器地址；旧令牌对后续请求立即失效。已经授权的请求和正在进行的流式响应可以继续完成。

未配置地址时显示新的令牌路径；也可使用 `pdf2zh-admin token reset --base-url https://pdf.example.com` 显示所选域名的完整地址。

容器内部的重置命令使用 `app` 用户执行。如果管理器的终端固定为 root，请改用上面的服务器终端命令，它默认沿用镜像的服务用户。

## 持久化

首次启动自动生成令牌，保存到 `/app/gateway/state/auth.json`。普通重启、重建与镜像升级读取同一文件；保留 `auth` 卷即可保持客户端地址不变。

令牌文件损坏、无法读取或格式不正确时，服务拒绝启动。查看命令不会生成或更改令牌。重置通过文件锁与原子写入更新文件；失败时保留原凭据。

启动日志显示令牌管理命令，不输出真实令牌。管理员执行 `show` 或 `reset` 时，凭据只输出到执行该命令的终端；终端审计或录制仍可能保存输出。

## 访问边界

- 完整地址属于 bearer 凭据，持有者可访问后端业务数据与配置。不要将其公开发布。
- 公网入口使用 HTTPS，关闭或脱敏包含令牌的访问日志，关闭业务响应缓存。
- 插件可能在诊断日志及连接弹窗中显示服务器地址，分享材料前遮蔽令牌。
- 令牌不因客户端 IP 或网络变化而失效；有效期由管理员通过重置控制。
- 管理命令仅通过服务器或容器终端使用，不提供公网查看与重置接口。
- 首版使用一个共享令牌，不提供用户之间的配置与文件隔离。
- 只对外提供网关端口 `8890`，内部上游 `127.0.0.1:8891` 不发布到宿主机。

反向代理、容器网络及端口配置见 [部署指南](docs/DEPLOYMENT.md#lucky-反向代理)。
