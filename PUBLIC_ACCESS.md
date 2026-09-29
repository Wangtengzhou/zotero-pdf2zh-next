# 访问与令牌管理

**简体中文** | [English](PUBLIC_ACCESS.en.md)

安全入口由“服务器地址 + 令牌路径”组成。内网、公网和多个反代域名都可使用同一条 `/access/<令牌>` 路径，不依赖客户端 IP，也不需要浏览器登录。

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

## 第一次获取

从 `0.1.3` 起，启动通过健康检查后，容器日志会显示：

```text
安全入口 / Access entry: /access/你的完整令牌
```

复制路径，接到 NAS 地址或反代域名后，填入 Zotero 的 **Python Server IP**。不要在插件地址末尾加 `/health` 或 `/`。

每次重启都会打印当前入口，令牌保持不变。`0.1.2` 及更早版本用下面的命令查看。

## 再次查看

在容器页面打开“终端”，选择“新建终端／执行命令”，启动命令填 `/bin/sh`，用户保留默认 `app`，然后执行：

```bash
pdf2zh-admin url show
```

如果使用的是 **NAS 系统终端／SSH**，改为：

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

<details>
<summary>可选：生成完整地址，或只查看令牌</summary>

以下命令在容器终端执行，地址换成实际值：

```bash
pdf2zh-admin url show --base-url http://192.168.1.10:8890
pdf2zh-admin url show --base-url https://pdf.example.com
pdf2zh-admin token show
```

`--base-url` 只影响本次显示。`PUBLIC_BASE_URL` 环境变量可设为长期显示偏好，但不是必填项，也不绑定反代域名。它只接受 HTTP(S) 地址和可选端口，不包含路径、令牌或查询参数。

</details>

## 更换令牌

先等当前翻译结束。在 **容器终端**执行：

```bash
pdf2zh-admin token reset
```

在 **NAS 系统终端／SSH** 中则使用：

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin token reset
```

命令显示新入口，立即生效，无需重启。把 Zotero 中的旧路径替换为新路径；旧令牌不能再发起请求，已授权的请求可以完成。

容器终端应使用默认 `app` 用户。如果界面固定以 root 连接，请使用上面的 NAS 命令，避免生成服务用户无法读取的令牌文件。

## 保存与分享

- 令牌保存在 `/app/gateway/state/auth.json`。升级和重建时保留 `auth` 挂载，即可保留原入口。
- 重置后历史日志仍可能显示旧入口，以查看命令的当前输出为准。
- **完整入口就是访问凭据。** 分享日志或截图前遮蔽令牌；所有持有者共享配置和文件，没有多用户隔离。
- 公网使用 HTTPS，反代保留路径与查询参数，并关闭或脱敏包含令牌的访问日志。
- 文件损坏或权限错误时先修复存储。服务不会静默替换令牌，重置命令也不能修复挂载权限。
- 管理命令仅通过容器或服务器终端提供，没有公网令牌管理接口。

相关文档：[部署指南](docs/DEPLOYMENT.md) · [升级与排错](docs/OPERATIONS.md)
