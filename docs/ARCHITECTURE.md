# 系统架构

## 请求路径

```text
Zotero PDF2zh 插件
  -> Lucky / HTTPS 反向代理
  -> :8890 Starlette 认证网关
  -> 127.0.0.1:8891 原版 Zotero PDF2zh 服务端
  -> PDFMathTranslate Next / BabelDOC
```

认证网关和上游服务端运行在同一容器中，由 `scripts/supervise.py` 管理。任一子进程退出时容器结束，Docker 根据重启策略恢复服务。容器健康检查使用当前令牌访问上游健康接口。

## 网关

`gateway/app.py` 使用 Starlette 与 httpx 转发请求。令牌在读取请求体与访问上游之前验证，所有业务接口使用同一认证规则。

网关支持流式响应、SSE、查询参数与上游错误转发，限制请求体大小和请求超时。上游目标固定为容器回环地址；过滤逐跳头、认证头与转发头，不自动重试翻译 POST。路径校验拒绝编码分隔符、反斜线及路径穿越。

`gateway/tokens.py` 使用密码学随机数生成 URL 安全令牌，按独立路径段进行恒定时间比较。每次请求读取凭据，重置后新请求立即使用新值。令牌目录权限为 `700`，文件权限为 `600`。

## 上游与依赖

构建时从固定 Zotero PDF2zh Release 下载 `server.zip`，验证 `versions.json` 中的 SHA-256，并检查服务端版本。原版源码保留在 `/app/server`。

PDFMathTranslate Next 与 BabelDOC 使用固定 Python 依赖锁安装。基础镜像固定 digest，构建时执行资源 warmup。启动包装器禁用上游自动更新与启动通知请求，运行时使用镜像中的依赖。

## 存储

| 容器路径 | 用途 |
| --- | --- |
| `/app/gateway/state` | 访问令牌 |
| `/app/server/config` | 上游翻译配置 |
| `/app/server/translated` | PDF 输出 |
| `/home/app/.cache` | 资源缓存 |

进程使用 UID/GID `10001:10001`。任务及历史记录由上游保存在内存中，重启后清空；卷中的配置和文件保留。服务不提供多用户隔离。

## 镜像发布

GitHub Actions 构建一个 Linux amd64 镜像，通过核心测试与真实容器检查后，将该镜像发布为版本标签及 Git 提交追溯标签。两者指向相同内容。

独立推广流程接受已发布镜像的 digest，在人工完成实际 Zotero 验收后创建 `latest` 标签，不重新构建。发布操作和本地开发流程见 [CONTRIBUTING.md](../CONTRIBUTING.md)。
