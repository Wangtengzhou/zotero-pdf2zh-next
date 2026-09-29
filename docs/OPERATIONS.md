# 升级与维护

**简体中文** | [English](OPERATIONS.en.md)

首次安装见 [部署指南](DEPLOYMENT.md)，查看或更换令牌见 [安全入口管理](../PUBLIC_ACCESS.md)。本页命令均在 **NAS／服务器终端**执行。

## 升级镜像

上游服务端、Next 引擎和本项目镜像有各自的版本号。上游更新后，本项目先核对兼容性，再发布新镜像；现有容器不会自动升级。不要在容器中执行 `pip install -U` 或上游自更新命令。

### 更新前

等待翻译结束，备份令牌 `auth`、配置 `config`、PDF `translated`、缓存 `cache` 四个存储位置。

图形化部署可停止容器后复制这四个文件夹。Compose 数据在 Docker 卷中，**只复制 compose.yaml 和 .env 不等于备份数据**，还需用 NAS 或 Docker 的卷备份方式保存数据卷。

### 飞牛／群晖

1. 停止旧容器，下载或导入目标版本镜像。
2. 飞牛使用“重置”；群晖使用对应的更新／重新创建操作。确认镜像标签是目标版本，保留原端口、环境变量和四组映射。
3. 启动后等待健康状态正常，用原地址测试 Zotero 连接，再翻译一篇短 PDF。

若界面不能修改镜像版本，可将停止的旧容器改名，用新镜像创建原名称的容器，并映射回原来的四个文件夹。不要同时启动两个容器。

**保留 `auth` 时令牌不变，Lucky 无需修改。** 不要勾选删除数据。仅重启旧容器不会切换镜像。

### Docker Compose

打开原部署目录的 `.env`，将 `PDF2ZH_IMAGE=` 后的版本改为目标版本，例如：

```dotenv
PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.3
```

保存后执行；若安装目录不同，修改第一行：

```bash
cd "$HOME/zotero-pdf2zh-next"
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
```

离线更新时，先用 `sudo docker load --input 镜像文件.tar.gz` 导入目标镜像，再在原部署目录执行：

```bash
sudo docker compose up -d --pull never --wait --wait-timeout 180
```

保持原 Compose 项目名称和数据卷。不要执行 `docker compose down -v`。

### 确认版本与回滚

在容器详情中确认镜像标签。`/health` 中的 `version` 是**上游服务端版本**：镜像 `0.1.3` 返回 `4.1.7` 是正常的。

出现兼容问题时可切回旧镜像；若新版迁移了配置格式，还需恢复升级前的配置备份。重启会清空内存任务记录，已保存的 PDF 不受影响。

## 缓存与首次翻译

镜像包含预下载资源。Docker 新建命名卷时会复制这些资源；绑定一个空 NAS `cache` 文件夹则会遮住它们，第一次翻译可能重新下载模型和字体。

保留同一个 `cache` 挂载后，普通重启和换镜像都能复用有效缓存。新版本需要不同资源，或文件缺失、损坏时才需补下载。LLM 翻译仍需要网络。

## 安装中断后继续

若一段式安装已生成配置，但拉取镜像失败，恢复网络后执行：

```bash
cd "$HOME/zotero-pdf2zh-next"
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

若仍无法拉取，使用 [部署指南中的离线步骤](DEPLOYMENT.md#方式二docker-compose)。`--wait` 不受支持时需更新 Docker Compose v2；同名容器冲突时先检查已有部署，不要重复创建。

## 连接排查

将下表的 IP 和令牌换成实际值。内网使用 **HTTP、端口 8890**；日志中的 `localhost:8891` 仅供容器内部使用。

| 浏览器访问地址 | 正常结果 |
| --- | --- |
| `http://NAS内网IP:8890/_gateway/live` | `{"status":"ok"}`，证明网关可达 |
| `http://NAS内网IP:8890/access/完整令牌/health` | `status: ok`，证明认证和上游服务正常 |

直接访问 `/health` 返回 401 是缺少令牌。HTTPS 请求发到 HTTP 端口可能产生 `Invalid HTTP request`。Zotero 的服务器地址只填到令牌，不加 `/health`。

| 现象 | 优先检查 |
| --- | --- |
| 内网连接被拒绝或超时 | 容器是否运行、8890 端口映射、NAS 防火墙；仅绑定 127.0.0.1 时其他设备无法连接 |
| Lucky 502 | 后端地址与容器健康状态；Lucky 容器内的 127.0.0.1 指向它自己 |
| 令牌状态不可写 | 四组映射是否读写、文件夹及现有文件是否允许 UID 10001 访问；先修权限，不删除令牌 |
| 0.1.0 缺少配置文件及模板 | 更新到 0.1.2 或更新版本 |
| 大 PDF 上传失败 | 反代与网关体积限制；Base64 编码后体积约增加 1/3 |
| 连接成功但翻译慢或失败 | 当前选中的 LLM 渠道、模型、资源下载、请求超时和限流；连接成功不代表翻译 API 正常 |

## 查看与导出日志

查看最近输出：

```bash
sudo docker logs --tail 100 zotero-pdf2zh-next
```

在当前目录保存近两小时的日志，无需复制整个窗口：

```bash
sudo docker logs --since 2h --timestamps zotero-pdf2zh-next > pdf2zh-container.log 2>&1
```

**0.1.3 起，启动日志含安全入口。** 分享前遮蔽 `/access/` 后的令牌、API 密钥及敏感文件名。进度条重复刷新可能产生大量日志，不代表重复提交了任务。

## 可选环境变量

图形化部署在容器设置中添加；Compose 在 `.env` 中修改并执行 `docker compose up -d` 应用。

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `PUBLIC_BASE_URL` | 空 | 日志及管理命令显示完整 URL 的偏好，不限制反代域名 |
| `MAX_UPLOAD_MB` | `100` | 请求体上限，包含 Base64 编码体积 |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` | 网关等待上游请求的超时，不是 LLM 服务商的请求超时 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `HOST_PORT` | `8890` | Compose 宿主机端口 |
| `BIND_ADDRESS` | 见下文 | Compose 宿主机监听地址 |

部署指南的一段式命令写入 `BIND_ADDRESS=0.0.0.0`，支持内网访问。直接使用仓库或 Release 的 `env.example` 时，默认是 `127.0.0.1`；若需内网访问，改为 NAS 内网 IP 或 `0.0.0.0`。仅由同机原生 Lucky 转发时可保留回环地址。
