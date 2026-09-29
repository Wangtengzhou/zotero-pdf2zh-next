# Docker 部署指南

## 环境要求

- Linux x86_64 / amd64 主机；当前镜像不提供 arm64 版本。
- Docker Engine；Compose 部署使用 Docker Compose v2。
- Zotero 与 Zotero PDF2zh 插件，后端固定为服务端 4.1.7。
- HTTPS 域名与反向代理，例如 Lucky。
- 翻译服务商所需的模型、API 地址及密钥，在 Zotero 插件中配置。

下面各部署方式选择一种即可。首次拉取镜像包含 Python 依赖、字体及模型资源，需要预留下载与启动时间。容器健康状态变为 `healthy` 后，再连接 Zotero。

## 方式一：Docker Compose

获取项目文件：

```bash
git clone https://github.com/Wangtengzhou/zotero-pdf2zh-next.git
cd zotero-pdf2zh-next
cp .env.example .env
```

编辑 `.env`，至少修改公网域名：

```dotenv
PUBLIC_BASE_URL=https://pdf.example.com
PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.1
BIND_ADDRESS=127.0.0.1
HOST_PORT=8890
MAX_UPLOAD_MB=100
UPSTREAM_TIMEOUT_SECONDS=3600
TZ=Asia/Shanghai
```

启动并获取客户端地址：

```bash
docker compose pull
docker compose up -d
docker compose ps
docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

Compose 自动创建四个命名卷并设置自动重启策略。命名卷带有 Compose 项目前缀；升级时保持项目目录或项目名称一致。

## 方式二：docker run

不使用 Compose 时，可直接创建容器。替换下方的 HTTPS 域名：

```bash
docker run -d \
  --name zotero-pdf2zh-next \
  --platform linux/amd64 \
  --restart unless-stopped \
  --stop-timeout 30 \
  --security-opt no-new-privileges:true \
  --cap-drop ALL \
  -p 127.0.0.1:8890:8890 \
  -e PUBLIC_BASE_URL=https://pdf.example.com \
  -e MAX_UPLOAD_MB=100 \
  -e UPSTREAM_TIMEOUT_SECONDS=3600 \
  -e TZ=Asia/Shanghai \
  -v pdf2zh-auth:/app/gateway/state \
  -v pdf2zh-config:/app/server/config \
  -v pdf2zh-translated:/app/server/translated \
  -v pdf2zh-cache:/home/app/.cache \
  wangtengzhou/zotero-pdf2zh-next:0.1.1
```

查看状态与地址：

```bash
docker inspect --format '{{.State.Health.Status}}' zotero-pdf2zh-next
docker logs --tail=50 zotero-pdf2zh-next
docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

## 方式三：Portainer 图形化部署

以下适用于 Portainer 管理的 Docker Standalone 环境。

1. 进入目标 Docker 环境，打开 **Stacks → Add stack**。
2. 填写 Stack 名称，例如 `pdf2zh`，选择 **Web editor**。
3. 将本项目 [compose.yaml](../compose.yaml) 的完整内容粘贴到编辑器。
4. 在 **Environment variables** 添加 `PUBLIC_BASE_URL`，值为实际 HTTPS 域名，例如 `https://pdf.example.com`。也可以上传编辑好的 `.env` 文件。其他变量采用 Compose 默认值。
5. 点击 **Deploy the stack**，等待镜像下载与容器启动。
6. 进入 **Containers → zotero-pdf2zh-next**，检查健康状态和日志。
7. 打开容器的 **Console**，选择 `/bin/sh`，用户使用镜像默认的 `app`（UID `10001`），连接后运行：

```bash
pdf2zh-admin url show
```

复制输出地址到 Zotero 插件。需要重置时，在同一终端运行 `pdf2zh-admin token reset`。

更新时进入原 Stack 的编辑页面，修改 `PDF2ZH_IMAGE` 或镜像版本，重新部署并拉取镜像。保持 Stack 名称与卷配置一致，避免创建一套新的空卷。

界面选项可参考 [Portainer Stack 部署文档](https://docs.portainer.io/user/docker/stacks/add)。

## 离线部署：GitHub Release

Docker Hub 下载受限时，可在电脑上从 [GitHub Releases](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases) 下载镜像并上传到 NAS。

### 下载文件

选择所需版本，下载以下附件：

| 文件 | 用途 |
| --- | --- |
| `zotero-pdf2zh-next-0.1.1-linux-amd64.tar.gz` | 完整 Docker 镜像，版本号随发布变化 |
| `SHA256SUMS` | 下载文件校验值 |
| `compose.yaml` | 容器编排配置 |
| `env.example` | 环境变量模板 |
| `IMAGE_INFO.txt` | 源镜像 digest、源码提交与体积明细 |

GitHub 自动提供的 **Source code (zip / tar.gz)** 是源码包，不能导入为 Docker 镜像。

### NAS 图形化导入

1. 将镜像压缩包上传到 NAS。
2. 打开容器管理器的 **镜像 → 导入 / 从文件导入**，选择该文件。
3. 如果界面仅接受 `.tar`，先在电脑或 NAS 解压 `.tar.gz` 得到 `.tar` 再导入。不要解开 `.tar` 内部的镜像文件。
4. 导入后，确认本地镜像名称为 `wangtengzhou/zotero-pdf2zh-next:0.1.1`。
5. 从该本地镜像创建容器，按本指南的图形化参数配置环境变量、端口与持久化卷；关闭强制拉取镜像选项。

### 终端导入

上传附件到同一目录后，可先核对校验值，再加载镜像：

```bash
sha256sum -c SHA256SUMS
docker load --input zotero-pdf2zh-next-0.1.1-linux-amd64.tar.gz
docker image ls wangtengzhou/zotero-pdf2zh-next
cp env.example .env
```

编辑 `.env`，填写 `PUBLIC_BASE_URL` 后启动：

```bash
docker compose up -d --pull never
docker compose ps
docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

离线部署不执行 `docker compose pull`。如果只下载了镜像，可以跳过校验其他附件的命令，直接对镜像文件执行 `sha256sum` 并与 `SHA256SUMS` 的对应行比对。

镜像压缩包包含运行环境及预下载资源；翻译时仍需要访问所选翻译服务商。未预下载或被空缓存挂载遮住的资源也可能需要网络下载。

### 镜像大小

本地源码目录与镜像的内容不同：镜像包含基础 Linux / Python 环境、完整翻译依赖、系统库和预下载的模型字体。网关开发虚拟环境只安装少量开发依赖，不等同于翻译引擎的运行环境。

Docker Hub 显示压缩镜像层的总大小，`docker image ls` 通常显示解压后的镜像大小，Release 的 `.tar.gz` 是整个 Docker 导出包重新压缩后的大小，因此这三个数字可能不同。各版本的实际目录与镜像层大小见 `IMAGE_INFO.txt`。

## 方式四：NAS / 容器管理器图形化部署

适用于飞牛、群晖 Container Manager 等提供镜像、容器、卷与环境变量设置的管理器。不同版本的菜单名称可能不同。

如果管理器支持 **Compose / 项目 / 编排**，优先导入 [compose.yaml](../compose.yaml)，并添加 `PUBLIC_BASE_URL` 环境变量；不支持变量输入时，将 YAML 中的 `${PUBLIC_BASE_URL:?Set PUBLIC_BASE_URL in .env}` 替换为实际 HTTPS 域名。

手动创建单个容器时，按以下配置填写：

| 项目 | 值 |
| --- | --- |
| 镜像 | `wangtengzhou/zotero-pdf2zh-next:0.1.1` |
| 容器名称 | `zotero-pdf2zh-next` |
| 网络 | 默认 bridge |
| 宿主机 IP / 端口 | `127.0.0.1` / `8890`，适用于同机原生 Lucky |
| 容器端口 / 协议 | `8890` / TCP |
| 自动重启 | `unless-stopped`，或管理器提供的自动重启选项 |
| 启动命令 / 用户 | 保留镜像默认值 |
| 特权模式 | 关闭 |
| `PUBLIC_BASE_URL` | 实际 HTTPS 域名，例如 `https://pdf.example.com` |
| `MAX_UPLOAD_MB` | `100` |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` |
| `TZ` | `Asia/Shanghai` |

创建四个命名卷，并将它们挂载到以下容器路径：

| 卷名示例 | 容器路径 | 内容 |
| --- | --- | --- |
| `pdf2zh-auth` | `/app/gateway/state` | 访问令牌 |
| `pdf2zh-config` | `/app/server/config` | 翻译配置及可能保存的 API 密钥 |
| `pdf2zh-translated` | `/app/server/translated` | PDF 文件 |
| `pdf2zh-cache` | `/home/app/.cache` | 字体、模型等资源缓存 |

创建后，在容器详情页查看日志和健康状态。打开 **终端 / Console**，选择 `/bin/sh`，用户使用镜像默认的 `app`（UID `10001`），运行 `pdf2zh-admin url show` 获取地址。升级或重建容器时重新挂载原有卷。

如果管理器的终端固定为 root，使用服务器上的 `docker exec zotero-pdf2zh-next pdf2zh-admin token reset` 重置令牌；不要在 root 终端直接重置，以免生成服务用户无法读取的凭据文件。

### 宿主机文件夹挂载

如果管理器只支持选择宿主机文件夹，可以为上表四个路径分别创建文件夹并设为读写挂载。镜像进程使用 UID/GID `10001:10001`，文件夹必须允许该用户读写；令牌文件夹权限设为 `700`。例如，先在服务器终端执行：

```bash
sudo mkdir -p /srv/pdf2zh/auth /srv/pdf2zh/config /srv/pdf2zh/translated /srv/pdf2zh/cache
sudo chown 10001:10001 /srv/pdf2zh/auth /srv/pdf2zh/config /srv/pdf2zh/translated /srv/pdf2zh/cache
sudo chmod 700 /srv/pdf2zh/auth
```

然后把这四个宿主机目录分别映射到对应容器路径。空缓存目录会遮住镜像内预下载的资源，翻译引擎可能需要重新下载；希望复用镜像缓存时使用命名卷。已有卷迁移到文件夹挂载时需先复制数据；不要直接切换到空目录，否则令牌和配置会改变。

从 `0.1.1` 起，配置模板保存在镜像的独立目录，启动时自动写入配置挂载目录。首次使用空配置文件夹会生成正式配置；后续启动保留已有正式配置并执行上游迁移。

### 管理器无法指定绑定 IP

部分图形化界面只允许填写端口，实际会绑定所有网卡。此时使用 Compose 明确设置 `127.0.0.1:8890:8890`；或绑定服务器内网地址并通过 Docker 感知的防火墙规则限制来源。路由器只转发反代的 HTTPS 端口，不转发 `8890` 或 `8891`；有公网 IPv6 的主机也需限制入站访问。

## Lucky 反向代理

### Lucky 原生运行在同一台服务器

| 配置 | 值 |
| --- | --- |
| 公网入口 | `https://pdf.example.com`，有效 HTTPS 证书 |
| 后端地址 | `http://127.0.0.1:8890` |
| 转发路径 | 保留完整请求路径与查询参数 |
| 认证 | 使用本项目的地址令牌，关闭额外登录跳转 |
| 缓存 | 关闭业务请求及 PDF 缓存 |
| 超时 | 与 `UPSTREAM_TIMEOUT_SECONDS` 匹配，例如 3600 秒 |
| 上传限制 | 至少与 `MAX_UPLOAD_MB` 匹配 |
| 流式响应 | 保留 SSE，关闭会延迟进度流的响应缓冲 |
| 访问日志 | 关闭或遮蔽 `/access/<令牌>` 中的凭据 |

### Lucky 也运行在容器中

Lucky 容器内的 `127.0.0.1` 指向 Lucky 自己。可让两个容器接入同一受控 Docker 网络，后端改为 `http://pdf2zh:8890`。例如先创建共享网络：

```bash
docker network create pdf2zh-proxy
```

在 PDF2zh 的 Compose 中为服务添加网络，并在顶层声明外部网络：

```yaml
services:
  pdf2zh:
    # 保留 compose.yaml 中其他配置
    networks:
      - proxy

networks:
  proxy:
    external: true
    name: pdf2zh-proxy
```

同样在 Lucky 的持久化容器配置中接入 `pdf2zh-proxy`。共享网络模式不需要向宿主机发布 PDF2zh 端口，可以移除 PDF2zh 的 `ports` 配置。不要发布内部上游端口 `8891`。

## Zotero 配置

1. 在容器终端运行 `pdf2zh-admin url show`，获得 `https://pdf.example.com/access/<令牌>`。
2. 在 Zotero PDF2zh 插件设置中，将完整地址填入 **Python Server IP**，末尾不要添加斜线。
3. 将翻译引擎设为 **pdf2zh_next**。
4. 按翻译服务商要求设置 API 地址、模型与密钥。入口令牌和翻译 API 密钥是两种不同凭据。
5. 检查连接，再用一篇短 PDF 确认上传、进度、下载及附件导入。

完整令牌管理说明见 [公网访问与令牌管理](../PUBLIC_ACCESS.md)。

## 配置参考

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PUBLIC_BASE_URL` | 必填 | HTTPS 域名及可选端口；不含 `/access`、令牌、查询参数 |
| `PDF2ZH_IMAGE` | `wangtengzhou/zotero-pdf2zh-next:0.1.1` | Compose 使用的镜像版本或 digest |
| `BIND_ADDRESS` | `127.0.0.1` | Compose 发布端口时使用的宿主机地址 |
| `HOST_PORT` | `8890` | Compose 的宿主机端口 |
| `MAX_UPLOAD_MB` | `100` | 网关请求体大小上限；PDF Base64 编码后约增加 1/3 |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` | 网关上游请求超时 |
| `TZ` | `Asia/Shanghai` | 容器时区 |

`PDF2ZH_IMAGE`、`BIND_ADDRESS` 与 `HOST_PORT` 是 Compose 配置变量；使用单容器图形化部署时，在镜像及端口页面设置对应值。

## 升级与回滚

等待翻译任务结束，备份四个持久化卷，尤其是令牌、配置与 PDF。修改 `.env` 的 `PDF2ZH_IMAGE` 为目标版本，执行：

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Portainer / NAS 使用原 Stack 或原容器的更新功能，拉取目标版本并保留所有挂载。`docker run` 部署停止并移除旧容器后，用原命令、原卷名及新镜像重新创建。

回滚时将镜像改回旧版本或 digest；若上游配置格式变化，同时恢复对应的配置备份。容器重启会清空上游内存中的任务记录，已有 PDF 文件保留。

不要执行 `docker compose down -v` 或勾选管理器的“同时删除卷”，除非需要删除全部持久化数据。

## 常见问题

| 现象 | 检查方法 |
| --- | --- |
| 容器无法启动 / `unhealthy` | 查看容器日志，检查挂载权限、令牌文件和上游启动错误 |
| 命令无法读取或写入令牌 | 检查 `/app/gateway/state` 是否可写；文件夹挂载需允许 UID 10001 访问 |
| 提示 `PUBLIC_BASE_URL` 无效 | 使用完整 HTTPS 域名，不包含 `/access` 或令牌 |
| Lucky 返回 502 | 检查后端地址；容器模式不能用 Lucky 自己的回环地址访问其他容器 |
| 连接检查被拒绝 | 从终端重新获取完整地址，检查令牌、路径保留及额外认证设置 |
| 大 PDF 上传失败 | 同时检查 Lucky 上传限制和 `MAX_UPLOAD_MB`，计入 Base64 体积 |
| 翻译失败 / 超时 | 检查服务商密钥、模型、网络及反代超时；提交反馈前遮蔽密钥与令牌 |

### 启动时提示 Invalid or unwritable token state

该错误发生在令牌初始化阶段，尚未启动反向代理后端。`0.1.0` 的日志将挂载权限错误和令牌格式错误合并显示；先检查挂载，不要立即删除令牌文件。

在服务器终端执行下面的只读命令，确认路径、读写标志和容器用户：

```bash
docker inspect zotero-pdf2zh-next --format 'User={{.Config.User}}{{range .Mounts}}{{println}}{{.Source}} -> {{.Destination}} RW={{.RW}}{{end}}'
```

宿主机文件夹挂载必须满足：`RW=true`、服务用户 UID/GID `10001:10001` 可以读写目录，以及已有的 `auth.json` 和 `.lock` 文件。仅修改目录权限不会修复曾由 root 创建的文件权限。

首次部署使用本指南示例的 `/srv/pdf2zh` 专用目录时，可先停止容器，修复目录及已有文件的所有权，再启动：

```bash
docker stop zotero-pdf2zh-next
sudo chown -R 10001:10001 /srv/pdf2zh/auth /srv/pdf2zh/config /srv/pdf2zh/translated /srv/pdf2zh/cache
sudo chmod 700 /srv/pdf2zh/auth
docker start zotero-pdf2zh-next
docker logs --tail=50 zotero-pdf2zh-next
```

实际映射使用其他路径时，将这四个目录替换为 `docker inspect` 中对应的专用目录；不要对 NAS 共享根目录或系统目录递归修改所有权。若 NAS 使用 ACL 或远程共享，需让 ACL 也允许 UID 10001 访问；若 `RW=false`，先将挂载改为读写。

只有确认权限正确后仍出现令牌格式错误时，才从备份恢复 `auth.json` 或显式重置令牌。容器已经退出时无法使用 `docker exec`，需通过保留原挂载的一次性容器执行恢复操作。

### 启动时提示缺少配置文件及模板

`0.1.0` 使用空宿主机文件夹挂载 `/app/server/config` 时，镜像内的模板会被遮住，导致上游启动失败。升级到 `0.1.1` 可自动恢复模板；保留原有挂载目录及权限。

需要继续使用 `0.1.0` 时，可从一个不带挂载的临时容器复制模板。将目标路径替换为实际的配置目录：

```bash
docker stop zotero-pdf2zh-next
docker create --name pdf2zh-template-source wangtengzhou/zotero-pdf2zh-next:0.1.0
docker cp pdf2zh-template-source:/app/server/config/. /srv/pdf2zh/config/
docker rm pdf2zh-template-source
sudo chown -R 10001:10001 /srv/pdf2zh/config
docker start zotero-pdf2zh-next
```

此操作从原镜像恢复 `.example` 模板，不删除令牌或翻译文件。

端口和数据卷的行为参见 [Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/) 与 [Docker 数据卷](https://docs.docker.com/engine/storage/volumes/)。
