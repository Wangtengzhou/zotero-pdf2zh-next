# 部署指南

**简体中文** | [English](DEPLOYMENT.en.md)

准备一台已安装 Docker 的 Intel / AMD NAS 或 Linux 服务器，记下它的内网 IP。当前镜像为 `0.1.3`，仅支持 `linux/amd64`。

**下面两种方式选一种即可。** 已经部署过，请直接看 [升级与维护](OPERATIONS.md)。

| 方式 | 适合谁 | 数据保存方式 |
| --- | --- | --- |
| [群晖／飞牛图形化部署](#方式一群晖飞牛图形化部署) | 希望在页面中配置容器 | 自己选择四个 NAS 文件夹；需设置一次权限 |
| [Docker Compose](#方式二docker-compose) | 可以在 NAS 终端粘贴命令 | Docker 自动创建四个数据卷，无需手工映射 |

先完成内网连接；有公网需求，再配置文末的 Lucky 反代。两种方式都不要求填写域名环境变量。

## 方式一：群晖／飞牛图形化部署

### 1. 下载或导入镜像

群晖打开 **Container Manager**，飞牛打开 **Docker**。在镜像仓库搜索并下载：

```text
wangtengzhou/zotero-pdf2zh-next:0.1.3
```

**Docker Hub 下载慢时：** 从 [0.1.3 Release](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases/tag/v0.1.3) 下载 `zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz`，上传到 NAS，在镜像页面选择“导入”。

若导入窗口只接受 `.tar`，先解压一层，不要解开 tar 内部文件。GitHub 的 **Source code** 下载项不是容器镜像。

### 2. 准备文件夹和权限

在 NAS 的 Docker 文件夹中，新建项目文件夹，再在里面新建 `auth`、`config`、`translated`、`cache` 四个子文件夹。

展开对应平台，按表准备。**左侧是 NAS 文件夹，右侧是容器路径；只有左侧可以按实际位置修改。**

<details>
<summary>群晖：目录映射与权限命令</summary>

以 Docker 共享文件夹位于存储空间 1 为例：

| NAS 文件夹 | 容器路径 | 权限 |
| --- | --- | --- |
| `/volume1/docker/zotero-pdf2zh-next/auth` | `/app/gateway/state` | 读写 |
| `/volume1/docker/zotero-pdf2zh-next/config` | `/app/server/config` | 读写 |
| `/volume1/docker/zotero-pdf2zh-next/translated` | `/app/server/translated` | 读写 |
| `/volume1/docker/zotero-pdf2zh-next/cache` | `/home/app/.cache` | 读写 |

在 NAS 系统终端／SSH 中执行下面四行。目录与上表不同时，只修改第一行：

```bash
PDF2ZH_STORAGE=/volume1/docker/zotero-pdf2zh-next
sudo mkdir -p "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chown -R 10001:10001 "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chmod 700 "$PDF2ZH_STORAGE/auth"
```

</details>

<details>
<summary>飞牛：目录映射与权限命令</summary>

以下是示例完整路径。实际位置可在文件管理器的文件夹属性中查看：

| NAS 文件夹 | 容器路径 | 权限 |
| --- | --- | --- |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/auth` | `/app/gateway/state` | 读写 |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/config` | `/app/server/config` | 读写 |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/translated` | `/app/server/translated` | 读写 |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/cache` | `/home/app/.cache` | 读写 |

在 NAS 系统终端／SSH 中执行下面四行。目录与上表不同时，只修改第一行：

```bash
PDF2ZH_STORAGE=/vol1/1000/Docker/Zotero-PDF2zh-Next
sudo mkdir -p "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chown -R 10001:10001 "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chmod 700 "$PDF2ZH_STORAGE/auth"
```

</details>

这一步让容器用户（编号 `10001`）能读写文件。仅处理项目的四个专用文件夹，不要对 NAS 共享根目录执行。如果 NAS 没有终端入口，可启用 SSH，再从电脑终端用 `ssh 用户名@NAS内网IP` 登录。共享目录的 ACL 也需允许该用户访问。

### 3. 创建容器

选择刚下载或导入的镜像，按下表填写：

| 项目 | 填写内容 |
| --- | --- |
| 容器名称 | `zotero-pdf2zh-next` |
| 网络 | bridge |
| 端口 | 宿主机 `8890` → 容器 `8890`，TCP |
| 绑定地址（如有） | `0.0.0.0` |
| 重启策略 | 自动重启／`unless-stopped` |
| 用户、启动命令 | 保留默认值 |
| 特权模式 | 关闭 |

在“存储空间／文件夹映射”中添加 **四行**，照平台表格填写，全部设为读写。不要挂载整个 `/app` 或 `/app/server`。

**环境变量无需新增，域名无需填写。** 导入本地镜像时，关闭强制拉取。

### 4. 启动并获取安全入口

启动后，打开容器日志，等待出现：

```text
服务已就绪 / Service ready
安全入口 / Access entry: /access/你的完整令牌
```

复制 `/access/` 开头的整段路径，继续下面的 [连接 Zotero](#连接-zotero)。

找不到日志时，可在容器终端选择“新建终端／执行命令”，填 `/bin/sh`，保留默认 `app` 用户，再执行 `pdf2zh-admin url show`。查看及更换令牌的完整步骤见 [安全入口管理](../PUBLIC_ACCESS.md)。

## 方式二：Docker Compose

### 在线安装

在 **NAS／服务器终端**粘贴整段命令，不是在容器终端执行。需要 Docker Compose v2；提示密码时输入 NAS 登录密码。

命令会创建 `~/zotero-pdf2zh-next`、写入配置并启动服务。四个数据卷自动创建，**无需准备文件夹或设置映射**。首次镜像下载约 843 MB。

```bash
(
set -e
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ -e compose.yaml ] || [ -e .env ]; then
  echo '已有部署文件，请使用维护指南 / Existing deployment: see the maintenance guide.'
  exit 1
fi
sudo docker compose version
cat > compose.yaml <<'YAML'
services:
  pdf2zh:
    image: ${PDF2ZH_IMAGE:-wangtengzhou/zotero-pdf2zh-next:0.1.3}
    platform: linux/amd64
    container_name: zotero-pdf2zh-next
    restart: unless-stopped
    ports:
      - "${BIND_ADDRESS:-127.0.0.1}:${HOST_PORT:-8890}:8890"
    environment:
      PUBLIC_BASE_URL: ${PUBLIC_BASE_URL:-}
      MAX_UPLOAD_MB: ${MAX_UPLOAD_MB:-100}
      UPSTREAM_TIMEOUT_SECONDS: ${UPSTREAM_TIMEOUT_SECONDS:-3600}
      TZ: ${TZ:-Asia/Shanghai}
    volumes:
      - auth:/app/gateway/state
      - config:/app/server/config
      - translated:/app/server/translated
      - cache:/home/app/.cache
    stop_grace_period: 30s
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

volumes:
  auth:
  config:
  translated:
  cache:
YAML
printf '%s\n' 'PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.3' 'BIND_ADDRESS=0.0.0.0' > .env
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
)
```

最后输出 `/access/…` 即可继续 [连接 Zotero](#连接-zotero)。已有部署文件时命令会停止，避免覆盖配置；安装中断的恢复方法见 [维护指南](OPERATIONS.md#安装中断后继续)。

<details>
<summary>Docker Hub 下载失败：改用离线镜像</summary>

1. 从 [0.1.3 Release](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases/tag/v0.1.3) 下载 `zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz`，上传到 NAS。
2. 在 NAS 终端输入 `cd `，接上存放镜像文件的文件夹完整路径，再回车。
3. 复制下面整段命令。它也可以接着完成因拉取失败而中断的首次安装：

```bash
(
set -e
sudo docker load --input zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ ! -f compose.yaml ]; then
cat > compose.yaml <<'YAML'
services:
  pdf2zh:
    image: ${PDF2ZH_IMAGE:-wangtengzhou/zotero-pdf2zh-next:0.1.3}
    platform: linux/amd64
    container_name: zotero-pdf2zh-next
    restart: unless-stopped
    ports:
      - "${BIND_ADDRESS:-127.0.0.1}:${HOST_PORT:-8890}:8890"
    environment:
      PUBLIC_BASE_URL: ${PUBLIC_BASE_URL:-}
      MAX_UPLOAD_MB: ${MAX_UPLOAD_MB:-100}
      UPSTREAM_TIMEOUT_SECONDS: ${UPSTREAM_TIMEOUT_SECONDS:-3600}
      TZ: ${TZ:-Asia/Shanghai}
    volumes:
      - auth:/app/gateway/state
      - config:/app/server/config
      - translated:/app/server/translated
      - cache:/home/app/.cache
    stop_grace_period: 30s
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

volumes:
  auth:
  config:
  translated:
  cache:
YAML
fi
if [ ! -f .env ]; then
  printf '%s\n' 'PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.3' 'BIND_ADDRESS=0.0.0.0' > .env
fi
sudo docker compose up -d --pull never --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
)
```

镜像上传后，上述安装步骤无需联网；实际翻译仍需访问翻译服务商。已有其他版本的部署请按 [升级步骤](OPERATIONS.md#升级镜像) 操作。

</details>

## 连接 Zotero

假设 NAS IP 为 `192.168.1.10`，日志中的路径是 `/access/你的完整令牌`：

| 插件设置 | 填写内容 |
| --- | --- |
| Python Server IP | `http://192.168.1.10:8890/access/你的完整令牌` |
| 翻译引擎 | `pdf2zh_next` |
| 翻译服务 | **选中**已配置的 LLM 渠道 |
| 模型、API 地址和密钥 | 按该渠道填写 |

IP 和令牌换成自己的值，末尾不加 `/` 或 `/health`。仅在配置管理中保存渠道还不够，翻译前必须选中它。

先测试连接，再翻译一篇短 PDF，确认译文附件正常返回。浏览器健康检查的正确地址见 [连接排查](OPERATIONS.md#连接排查)。

## 可选：Lucky 公网反代

先确认内网翻译正常，再用已有域名和证书添加反代规则：

| 项目 | 填写内容 |
| --- | --- |
| 前端 | 你的域名，HTTPS |
| 后端：Lucky 同机原生运行 | `http://127.0.0.1:8890` |
| 后端：Lucky 在容器或其他设备 | `http://NAS内网IP:8890` |
| 路径重写、额外登录 | 不启用 |

保存后，把 Zotero 地址改成 `https://你的域名/access/你的完整令牌`。多个域名可以复用同一令牌，容器环境变量不需要修改。

反代保留路径、查询参数和 SSE 流式响应；上传上限与网关一致（默认 100 MB 请求体），超时可设 3600 秒。关闭业务缓存，访问日志隐藏令牌。公网开放 HTTPS 入口，不要直接转发 `8890` 端口。

---

后续操作：[安全入口管理](../PUBLIC_ACCESS.md) · [升级、缓存与排错](OPERATIONS.md)
