# 系统架构

**简体中文** | [English](ARCHITECTURE.en.md)

## 请求路径

```text
Zotero PDF2zh -> LAN / HTTPS proxy -> :8890 gateway
             -> 127.0.0.1:8891 upstream server -> Next / BabelDOC
```

认证网关和上游服务端运行在同一容器，由 `scripts/supervise.py` 管理。任一子进程退出则容器结束，Docker 按重启策略恢复。健康检查使用当前令牌访问上游健康接口。

每次启动首次通过认证健康检查后打印当前安全入口。`/_gateway/live` 无需认证，只报告网关存活；完整健康状态通过 `/access/<令牌>/health` 获取。

## 网关与认证

`gateway/app.py` 使用 Starlette 与 httpx。读取请求体及访问上游前验证令牌，支持查询参数、流式响应、SSE、上游错误转发，并限制体积与超时。

上游地址固定在回环接口，过滤逐跳头、认证头及转发头，不自动重试翻译 POST。拒绝编码分隔符、反斜线及路径穿越。内网与公网使用同一认证逻辑，域名不参与验证。

`gateway/tokens.py` 使用密码学随机数、恒定时间比较、文件锁及原子更新。每次请求读取凭据，重置对新请求立即生效。令牌目录权限 `700`，文件权限 `600`。

## 上游与初始化

构建时下载固定 Release 的 `server.zip`，核对 SHA-256 与版本，原版源码保留在 `/app/server`。Python 依赖及基础镜像固定版本与校验值，构建时 warmup 资源。启动包装器禁用上游更新和通知请求。

空宿主机缓存目录会遮住预下载资源；Docker 新建命名卷则会复制镜像目录内容。后续启动使用挂载中校验有效的缓存。

模板保存在挂载目录外的 `/app/defaults/config`。启动前恢复托管 `.example` 文件，再调用上游迁移，保留已有正式配置，支持空宿主机文件夹与命名卷。

## 存储

| 路径 | 内容 |
| --- | --- |
| `/app/gateway/state` | 令牌 |
| `/app/server/config` | 配置 |
| `/app/server/translated` | PDF |
| `/home/app/.cache` | 资源缓存 |

进程使用 UID/GID `10001:10001`。任务及历史记录保存在上游内存，重启清空；卷中的数据保留。没有多用户隔离。

## 发布

GitHub Actions 构建 Linux amd64 镜像，完成核心和真实容器检查后，只发布版本号标签。OCI 标签保留源码提交信息，镜像 digest 用于内部核对，不生成提交号或 `latest` 标签。

离线流程按同一 digest 拉取镜像，使用 `docker save` 和 gzip 导出，验证 `docker load` 后上传 GitHub Release，附带校验值、部署文件与体积报告。详情见 [开发与发布](../CONTRIBUTING.md)。
