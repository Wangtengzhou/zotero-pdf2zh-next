# 部署指南

**简体中文** | [English](DEPLOYMENT.en.md)

## 环境与存储

支持 Linux x86_64 / amd64，当前不提供 arm64 镜像。内网可直接使用 HTTP；公网使用 Lucky 等 HTTPS 反代。域名不是容器启动的必填项。

服务用户为 UID/GID `10001:10001`。需要持久化以下四个位置：

| 容器路径 | 文件夹／卷示例 | 内容 |
| --- | --- | --- |
| `/app/gateway/state` | `auth` | 访问令牌 |
| `/app/server/config` | `config` | 翻译配置及可能保存的 API 密钥 |
| `/app/server/translated` | `translated` | PDF 文件 |
| `/home/app/.cache` | `cache` | 字体、模型及资源缓存 |

首次拉取或导入镜像需要预留时间和磁盘空间。启动后等待容器健康状态变为 `healthy`。

## 方式一：群晖／飞牛图形化部署

### 1. 获取镜像

群晖打开 **Container Manager**（旧版 DSM 为 Docker）；飞牛打开 Docker 应用。不同版本的菜单名称可能不同。

在线方式：在镜像仓库搜索 `wangtengzhou/zotero-pdf2zh-next`，选择版本 `0.1.2` 并下载。

离线方式：

1. 从 [GitHub Releases](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases) 下载 `zotero-pdf2zh-next-0.1.2-linux-amd64.tar.gz`。
2. 上传到 NAS，在镜像页面选择 **导入／从文件导入**。
3. 若仅支持 `.tar`，先解压一层得到 `.tar` 再导入，不要解开 `.tar` 内部文件。
4. 确认本地镜像名称为 `wangtengzhou/zotero-pdf2zh-next:0.1.2`，创建时关闭强制拉取。

GitHub 自动生成的 **Source code** 包不能作为镜像导入。下载可与 Release 中的 `SHA256SUMS` 对照校验。

### 2. 准备四个文件夹

在专用项目目录下创建 `auth`、`config`、`translated`、`cache`。示例根目录：

- 群晖：`/volume1/docker/zotero-pdf2zh-next`
- 飞牛：`/vol1/1000/Docker/Zotero-PDF2zh-Next`

**四个文件夹必须允许 UID/GID `10001:10001` 读写。** NAS 自动创建的文件夹通常属于其他用户，需在启动前修复所有权。以下在 NAS 终端执行，先将 `PDF2ZH_STORAGE` 改为实际的专用项目目录：

```bash
PDF2ZH_STORAGE=/vol1/1000/Docker/Zotero-PDF2zh-Next
sudo mkdir -p "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chown -R 10001:10001 "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chmod 700 "$PDF2ZH_STORAGE/auth"
```

仅对这四个专用目录执行，不要修改 NAS 共享根目录。已有文件也需要正确所有权；使用 ACL 的共享目录还需允许该服务用户访问。

### 3. 创建容器

选择本地镜像，新建容器并填写：

| 项目 | 配置 |
| --- | --- |
| 镜像 | `wangtengzhou/zotero-pdf2zh-next:0.1.2` |
| 容器名称 | `zotero-pdf2zh-next` |
| 网络 | 默认 bridge |
| 端口 | 宿主机 `8890` → 容器 `8890`，TCP |
| 绑定地址 | 内网直连：内网 IP 或 `0.0.0.0`；同机原生 Lucky：`127.0.0.1` |
| 重启策略 | 自动重启／`unless-stopped` |
| 用户、启动命令 | 保留镜像默认值 |
| 特权模式 | 关闭 |

将四个宿主机文件夹分别挂载到上表的容器路径，全部设为读写。不要挂载到 `/app` 或整个 `/app/server`，也不要发布内部端口 `8891`。

环境变量可使用默认值；`PUBLIC_BASE_URL` 无需添加：

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `MAX_UPLOAD_MB` | `100` | 请求体上限，计入 Base64 编码体积 |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` | 上游请求超时，秒 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `PUBLIC_BASE_URL` | 空，可选 | 管理命令显示 URL 的偏好，不绑定域名 |

配置模板会自动补齐，已有正式配置保留并交给上游迁移。空缓存文件夹会遮住镜像内预下载的资源，翻译时可能需要重新下载。

### 4. 获取地址

启动容器，查看健康状态与日志。打开容器终端，选择 `/bin/sh`，用户为默认 `app`（UID `10001`）：

```bash
pdf2zh-admin url show
```

输出 `/access/<令牌>`，接在 NAS 地址或反代域名后即可。例如：

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

## 方式二：Docker Compose

使用 Docker Compose v2 获取项目：

```bash
git clone https://github.com/Wangtengzhou/zotero-pdf2zh-next.git
cd zotero-pdf2zh-next
cp .env.example .env
```

示例 `.env`：

```dotenv
PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.2
BIND_ADDRESS=127.0.0.1
HOST_PORT=8890
PUBLIC_BASE_URL=
MAX_UPLOAD_MB=100
UPSTREAM_TIMEOUT_SECONDS=3600
TZ=Asia/Shanghai
```

默认回环地址适用于同机原生 Lucky。内网直连将 `BIND_ADDRESS` 改为服务器内网 IP 或 `0.0.0.0`。无需填写域名。

在线启动：

```bash
docker compose pull
docker compose up -d
docker compose ps
docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

Compose 使用四个命名卷，Docker 自动初始化卷内的权限与镜像资源。保持 Compose 项目名称一致；不需要手动创建宿主机文件夹。若自行改为文件夹挂载，按图形化部署章节准备权限。

### Compose 离线导入

从 Release 下载镜像、`compose.yaml`、`env.example` 和可选校验文件，上传到同一目录：

```bash
docker load --input zotero-pdf2zh-next-0.1.2-linux-amd64.tar.gz
cp env.example .env
docker compose up -d --pull never
docker compose ps
```

使用版本标签 `:0.1.2`，不执行 `docker compose pull`。域名变量可留空，按需要修改端口绑定。下载全部 Release 附件时，可先执行 `sha256sum -c SHA256SUMS`。

## Lucky 与 Zotero

同机原生 Lucky 将 HTTPS 域名反代到 `http://127.0.0.1:8890`，保留完整路径与查询参数。关闭额外登录跳转和业务缓存；上传限制与 `MAX_UPLOAD_MB` 匹配，超时与 `UPSTREAM_TIMEOUT_SECONDS` 匹配，保留 SSE 流式响应，并关闭或脱敏带令牌的访问日志。

Lucky 若在容器中运行，其回环地址不指向 PDF2zh 容器。可将两者接入同一个受控 Docker 网络，通过 `http://pdf2zh:8890`（Compose 服务名）访问后端，或使用可达的宿主机内网地址。共享网络需在两者持久化配置中设置。

多个反代域名可同时使用同一令牌，无需修改容器。将完整令牌地址填入 Zotero 插件的 **Python Server IP**，末尾不加斜线；引擎选 **pdf2zh_next**，另行配置翻译服务商、模型和 API 密钥。用一篇短 PDF 确认上传、进度、下载及附件导入。

## 令牌与升级

容器终端中执行：

```bash
pdf2zh-admin url show
pdf2zh-admin url show --base-url https://pdf.example.com
pdf2zh-admin token show
pdf2zh-admin token reset
```

使用默认 `app` 用户。若图形终端固定为 root，在 NAS 终端使用 `docker exec zotero-pdf2zh-next pdf2zh-admin token reset`，避免 root 创建服务用户无法读取的令牌文件。详情见 [令牌管理](../PUBLIC_ACCESS.md)。

升级前等待翻译结束，备份四个持久化位置。图形化管理器导入／下载新版本，在原容器的更新功能中更换镜像，保留所有挂载；Compose 修改 `.env` 的版本后重新拉取并启动，离线导入后使用 `--pull never`。

回滚选择旧版本，并在配置格式变化时恢复对应备份。重启清空内存任务记录，已有 PDF 保留。不要执行 `docker compose down -v` 或勾选“同时删除卷”。

## 常见问题

| 现象 | 处理 |
| --- | --- |
| 令牌目录不可写 | 检查读写挂载、UID 10001 的目录及已有文件权限；先修权限，不删除令牌 |
| `0.1.0` 提示缺少配置文件及模板 | 使用 `0.1.2`，它会自动恢复模板 |
| Lucky 502 | 检查后端地址与健康状态；容器中的 `127.0.0.1` 指向容器自己 |
| 大 PDF 上传失败 | 检查反代与网关限制，Base64 编码后体积约增加 1/3 |
| 翻译失败或超时 | 检查服务商密钥、模型、网络及超时；反馈日志前遮蔽凭据 |
| 镜像约 843 MB | 包含完整 Python 翻译依赖、Linux 系统库、字体与模型；明细见 Release 的 `IMAGE_INFO.txt` |

容器退出时，可在 NAS 终端检查挂载，不会输出令牌：

```bash
docker inspect zotero-pdf2zh-next --format 'User={{.Config.User}}{{range .Mounts}}{{println}}{{.Source}} -> {{.Destination}} RW={{.RW}}{{end}}'
docker logs --since=1m zotero-pdf2zh-next
```
