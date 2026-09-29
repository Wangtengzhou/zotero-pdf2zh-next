# 部署指南

**简体中文** | [English](DEPLOYMENT.en.md)

## 开始前

准备一台 Intel / AMD 处理器的 NAS 或 Linux 服务器，安装并打开 Docker。先记下 NAS 的内网 IP（例如 `192.168.1.10`）。本指南先完成内网连接，最后再配置公网反代。

**下面两种方式选一种即可，不要重复创建容器。** 想在页面中逐项填写，选方式一；可以使用 NAS 终端，推荐方式二，复制一整段命令即可创建并启动服务，无需手工映射文件夹。已经部署过的用户直接看文末升级说明。

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

在 NAS 文件管理器中打开 Docker 文件夹，新建项目文件夹，再在里面新建 `auth`、`config`、`translated`、`cache` 四个子文件夹。后面创建容器时，需要添加四行“存储空间／文件夹映射”，**每行的左侧选 NAS 上的文件夹，右侧原样填写容器路径**：

**群晖填写表**（Docker 共享文件夹位于存储空间 1）：

| NAS 文件夹（左侧） | 容器路径（右侧，原样复制） | 权限 |
| --- | --- | --- |
| `/volume1/docker/zotero-pdf2zh-next/auth` | `/app/gateway/state` | 读写 |
| `/volume1/docker/zotero-pdf2zh-next/config` | `/app/server/config` | 读写 |
| `/volume1/docker/zotero-pdf2zh-next/translated` | `/app/server/translated` | 读写 |
| `/volume1/docker/zotero-pdf2zh-next/cache` | `/home/app/.cache` | 读写 |

**飞牛填写表**（以本文的 Docker 文件夹为例）：

| NAS 文件夹（左侧） | 容器路径（右侧，原样复制） | 权限 |
| --- | --- | --- |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/auth` | `/app/gateway/state` | 读写 |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/config` | `/app/server/config` | 读写 |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/translated` | `/app/server/translated` | 读写 |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/cache` | `/home/app/.cache` | 读写 |

左侧路径随存储空间和用户名变化：在文件管理器的文件夹属性中查看实际完整路径，或直接用选择按钮选中对应文件夹。**只改左侧，右侧四个路径不能改。**

**启动前还需做一次权限设置，否则容器可能报错退出。** 当前镜像使用编号为 `10001` 的用户读写文件，NAS 新建文件夹通常不属于该用户，因此本方式仍需要一次终端操作。想省去这一步，请使用方式二。

打开 NAS 系统终端；没有终端入口时，在 NAS 设置中启用 SSH，然后在电脑终端输入 `ssh 你的NAS用户名@你的NAS内网IP` 登录。以下命令在 **NAS 的终端**执行，不是在容器终端执行。群晖第一行用 `PDF2ZH_STORAGE=/volume1/docker/zotero-pdf2zh-next`；飞牛可直接使用下方第一行。如果刚才选择的实际目录不同，只替换第一行等号后面的路径。完整复制这四行：

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
| 绑定地址（如果页面有此项） | 填 `0.0.0.0`，便于内网连接 |
| 重启策略 | 自动重启／`unless-stopped` |
| 用户、启动命令 | 保留镜像默认值 |
| 特权模式 | 关闭 |

在“存储空间／文件夹映射”页面点击“添加”四次，按照上面的群晖表或飞牛表逐行填写，勾选读写。确认一共四行后保存。不要挂载到 `/app` 或整个 `/app/server`，也不要发布内部端口 `8891`。

**环境变量页面不用新增任何项目，直接保留默认值。无需填写反代域名。** 以下仅供以后调整时参考：

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

命令会输出一段以 `/access/` 开头的文字，完整复制下来。假设 NAS 内网 IP 是 `192.168.1.10`，把这段文字接到 `http://192.168.1.10:8890` 后面。下面的 `<token>` 必须替换为命令输出的真实令牌，不能原样填写：

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

## 方式二：Docker Compose

### 1. 复制命令，自动创建并启动

在 **NAS／服务器终端**执行（不是电脑本机终端或容器终端）。需要 Docker Compose v2；群晖／飞牛先安装并启动 Docker 应用。此命令用于首次部署，已有同名容器请看升级说明。

**完整复制下面一段即可，无需修改域名、目录或环境变量。** 它会在当前登录用户的个人目录下创建 `zotero-pdf2zh-next` 文件夹，写好部署文件、拉取镜像、自动创建四个数据卷并启动。首次下载约 843 MB，请等待完成。提示密码时输入 NAS 登录密码，输入时不显示字符属于正常现象。

```bash
(
set -e
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ -e compose.yaml ] || [ -e .env ]; then
  echo '已有部署文件，请使用升级步骤 / Existing deployment: use upgrade instructions.'
  exit 1
fi
sudo docker compose version
cat > compose.yaml <<'YAML'
services:
  pdf2zh:
    image: ${PDF2ZH_IMAGE:-wangtengzhou/zotero-pdf2zh-next:0.1.2}
    platform: linux/amd64
    container_name: zotero-pdf2zh-next
    restart: unless-stopped
    ports:
      - "${BIND_ADDRESS:-0.0.0.0}:8890:8890"
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
printf '%s\n' 'PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.2' 'BIND_ADDRESS=0.0.0.0' > .env
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
)
```

最后看到 `/access/` 开头的令牌路径，就可以进行下一步。若提示不支持 `--wait`，升级 Docker Compose v2；若提示超时或退出，在 NAS 终端执行 `sudo docker logs --tail 80 zotero-pdf2zh-next` 查看原因。

**这里不需要再配置文件夹映射。** 四个数据存储位置由 Docker 自动创建并管理，重建容器后仍保留。部署文件位于 `~/zotero-pdf2zh-next`；不要改文件夹名称或删除 Docker 数据卷。

### 2. 填入 Zotero

复制最后输出的整个 `/access/…` 路径，接到 `http://你的NAS内网IP:8890` 后，在 Zotero 插件的 **Python Server IP** 中填写该完整地址。引擎选择 **pdf2zh_next**，填写翻译服务商的模型和 API 密钥。具体例子见下方“连接 Zotero”。

### Compose 离线导入

如果 Docker Hub 下载失败，使用这个替代步骤。打开 [0.1.2 下载页](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases/tag/v0.1.2)，下载 `zotero-pdf2zh-next-0.1.2-linux-amd64.tar.gz`，上传到 NAS 文件管理器可见的目录。在 NAS 终端输入 `cd `（后面有一个空格），再填入该目录完整路径，回车进入，然后执行：

```bash
(
set -e
sudo docker load --input zotero-pdf2zh-next-0.1.2-linux-amd64.tar.gz
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ ! -f compose.yaml ]; then
cat > compose.yaml <<'YAML'
services:
  pdf2zh:
    image: ${PDF2ZH_IMAGE:-wangtengzhou/zotero-pdf2zh-next:0.1.2}
    platform: linux/amd64
    container_name: zotero-pdf2zh-next
    restart: unless-stopped
    ports:
      - "${BIND_ADDRESS:-0.0.0.0}:8890:8890"
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
  printf '%s\n' 'PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.2' 'BIND_ADDRESS=0.0.0.0' > .env
fi
sudo docker compose up -d --pull never --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
)
```

这段命令也适用于上面的在线安装在拉取镜像时失败后继续安装。镜像提前上传后，以上步骤无需联网：部署文件直接由命令生成。之后的实际翻译仍需连接所选翻译服务，空缓存所需资源也可能需要下载。

## Lucky 与 Zotero

### 连接 Zotero：先确认内网能用

假设 NAS IP 为 `192.168.1.10`，命令输出 `/access/abc123`，则 **Python Server IP** 填 `http://192.168.1.10:8890/access/abc123`。`abc123` 只是示例，用你自己的完整令牌替换，末尾不加 `/`。

引擎选择 **pdf2zh_next**，再填写翻译服务商、模型和 API 密钥。选一篇较短的 PDF 进行翻译，确认能返回译文附件。不要用浏览器打开服务根地址是否显示网页来判断是否部署成功。

### 公网访问：在 Lucky 中照表填写

已有可用域名和 HTTPS 证书时，在 Lucky 新建或编辑反向代理规则：

| 项目 | 填写内容 |
| --- | --- |
| 前端域名 | 你的域名，例如 `pdf.example.com` |
| 前端协议 | HTTPS，选择该域名证书 |
| 后端地址（Lucky 与服务在同一台机器原生运行） | `http://127.0.0.1:8890` |
| 后端地址（Lucky 运行在容器或另一台设备） | `http://你的NAS内网IP:8890`，例如 `http://192.168.1.10:8890` |
| 路径重写 | 不启用，保留原始完整路径 |
| 额外登录认证 | 不启用；令牌地址已提供认证 |

保存后，将 Zotero 中的地址改为 `https://你的域名/access/你的完整令牌`。多个域名可使用同一个令牌，不需要修改容器环境变量。公网只开放反代的 HTTPS 入口，不要在路由器中将 `8890` 直接转发到公网。

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

按本文 Compose 命令安装的用户，用文本编辑器打开 `~/zotero-pdf2zh-next/.env`，把第一行末尾的 `0.1.2` 改成要升级到的已发布版本，保存后在 NAS 终端执行：

```bash
cd "$HOME/zotero-pdf2zh-next"
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
```

首次在线安装因网络问题中断，修复网络后也可执行上面三行继续安装，无需修改版本。离线升级时先导入新镜像，再将上面两个 Docker 命令换为 `sudo docker compose up -d --pull never --wait --wait-timeout 180`。

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
