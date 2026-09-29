# 访问与令牌管理

**简体中文** | [English](PUBLIC_ACCESS.en.md)

## 地址规则

内网与公网统一使用 `/access/<令牌>`。插件在完整地址后追加连接检查、上传、轮询和下载路径，网关对每次请求验证令牌，不依赖客户端 IP 或浏览器登录。

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

反代保留完整路径与查询参数。网关验证后剥离令牌前缀，转发到内部服务端，所有业务接口均受保护。多个域名可使用同一个令牌。

## 第一次获取安全入口

从 `0.1.3` 起，打开容器的“日志”，等待出现“服务已就绪 / Service ready”。其下一行会显示：

```text
安全入口 / Access entry: /access/你的完整令牌
```

把 `/access/` 开头的整段接到 `http://你的NAS内网IP:8890` 或 `https://你的反代域名` 后，在 Zotero 的 **Python Server IP** 中填写完整地址，不加 `/health`，末尾不加 `/`。多个域名可以复用同一段路径。

每次启动通过完整健康检查后打印一次，重启使用原令牌，不会自动换令牌。如果设置了可选的 `PUBLIC_BASE_URL`，日志直接显示完整地址；不设置也能使用。`0.1.2` 及更早版本使用下面的命令获取。

## 之后再次查看

容器页面打开“终端”，选择“新建终端／执行命令”，启动命令填 `/bin/sh`，保留默认 `app` 用户。连接后只需执行这一条：

```bash
pdf2zh-admin url show
```

如果是在 NAS 系统终端／SSH，使用这一条：

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

### 可选：只看令牌或生成完整地址

容器内部终端以默认 `app` 用户（UID `10001`）执行：

```bash
pdf2zh-admin url show
pdf2zh-admin token show
pdf2zh-admin url show --base-url http://192.168.1.10:8890
pdf2zh-admin url show --base-url https://pdf.example.com
```

在服务器终端执行时，添加 `docker exec zotero-pdf2zh-next` 前缀。未配置地址时，`url show` 输出路径；`--base-url` 临时选择地址。`PUBLIC_BASE_URL` 仅是可选显示偏好，支持 HTTP(S) 地址及端口，不含路径、令牌或查询参数，不绑定网关域名。

## 重置

等待正在翻译的任务完成。在容器终端执行以下命令，生成并显示新的安全入口：

```bash
pdf2zh-admin token reset
```

如果是在 NAS 系统终端／SSH，使用：

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin token reset
```

无需重启容器，命令显示新路径或地址。之后更新 Zotero 地址，旧令牌对新请求立即失效；已经授权的请求和流式响应可以完成。也可使用 `--base-url https://pdf.example.com` 显示指定域名的完整地址。

容器内部重置使用 `app` 用户。图形化终端若固定为 root，改用上面的服务器终端命令，避免写出服务用户不可读的文件。权限问题需先修复，重置不能修复挂载权限。

## 存储与日志

首次启动自动生成令牌并保存到 `/app/gateway/state/auth.json`。普通重启、容器重建和升级读取原文件，保留 `auth` 存储即可保持地址不变。

文件损坏、格式非法或无法读写时拒绝服务，不静默生成替代凭据。查看命令只读，重置通过文件锁与原子替换更新文件。

启动日志会包含安全入口，导出日志给他人前遮蔽令牌。重置后，旧日志仍保留旧入口；以查看命令输出的当前值为准。管理员主动执行查看或重置时，凭据也显示在终端。

## 使用边界

- 完整地址属于访问凭据，所有持有者共享业务数据与配置，未提供多用户隔离。
- 公网使用 HTTPS；关闭或脱敏带令牌的访问日志，关闭业务缓存。
- 插件可能在诊断日志或连接弹窗中显示地址，分享材料前遮蔽令牌。
- 令牌不随 IP 变化失效，由管理员通过重置撤销。
- 查看与重置仅通过服务器／容器终端提供，没有公网管理接口。
- 对外提供网关 `8890`，内部上游 `127.0.0.1:8891` 不发布到宿主机。

网络与挂载配置见 [部署指南](docs/DEPLOYMENT.md)。
