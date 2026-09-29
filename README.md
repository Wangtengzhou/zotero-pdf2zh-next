# Zotero PDF2zh Next 容器封装

使用原版 Zotero PDF2zh 服务端与官方 PDFMathTranslate Next，提供 Linux amd64 容器与 GitHub Actions 自动发布。与 NightWatcher314 同名项目无关联。

当前：4 个核心测试、云端镜像构建及容器启动检查通过，Docker Hub 已发布 0.1.0。真实 Zotero 翻译联调尚未完成，暂不推广 latest。

## 版本与入口

服务端 4.1.7、pdf2zh-next 2.9.0、BabelDOC 0.6.2，首版容器版本 0.1.0，架构 linux/amd64。
完整依赖及哈希见 requirements.lock，源码校验值与基础镜像 digest 见 versions.json。

```text
Zotero -> Lucky HTTPS -> 8890 鉴权网关 -> 127.0.0.1:8891 原服务端 -> Next
```

只需在 Zotero 配置一次带随机令牌的地址，之后自动鉴权，换 IP 无需登录。首次启动自动生成令牌并持久化，普通重启和升级沿用原值。
镜像以非 root 用户运行，不挂载 docker.sock，不在容器内自动升级源码或安装包。

## 部署

在服务器获取本仓库的 compose.yaml 与 .env.example，使用已发布镜像：

```bash
cp .env.example .env
docker compose pull
```

编辑 .env，PUBLIC_BASE_URL 填实际 HTTPS 域名，PDF2ZH_IMAGE 默认使用 wangtengzhou/zotero-pdf2zh-next:0.1.0。也可使用以下 digest 固定镜像：

```text
wangtengzhou/zotero-pdf2zh-next@sha256:44d27f56df09beca3e8ff9f288b1dc91d0fe7f876e3abfea9807b19baaecaeaf
```

```bash
docker compose up -d
docker compose ps
docker compose logs --tail=50
```

如需本地构建，执行以下命令，并把 .env 的 PDF2ZH_IMAGE 改为 zotero-pdf2zh-next:local。首次构建会下载字体、模型及 Python 包。

```bash
docker build --platform linux/amd64 \
  --build-arg SOURCE_URL=https://github.com/Wangtengzhou/zotero-pdf2zh-next \
  -t zotero-pdf2zh-next:local .
```

### Lucky 同服务器反代

独立域名配置有效 HTTPS 证书，整站反代到网关并保留路径，不启用登录跳转、BasicAuth 或 IP 自动认证。
同机原生 Lucky 可使用默认 127.0.0.1:8890。若 Lucky 也在容器里，接入受控共享 Docker 网络并通过服务名访问；Lucky 容器的 127.0.0.1 不是宿主机。
关闭或脱敏包含完整 URL 的访问日志，不缓存业务请求；上传大小、长任务超时和 SSE 流式转发与网关设置匹配。内部 8891 不发布到宿主机。

### 获取与重置地址

```bash
# 获取可直接填入 Zotero 的完整地址
docker exec zotero-pdf2zh-next pdf2zh-admin url show

# 只查看当前令牌
docker exec zotero-pdf2zh-next pdf2zh-admin token show

# 重置并显示新地址，无需重启容器
docker exec zotero-pdf2zh-next pdf2zh-admin token reset
```

容器终端可直接运行 pdf2zh-admin。把完整地址填入原插件的 Python Server IP，末尾不加斜线，引擎选择 pdf2zh_next。
reset 后旧令牌对新请求立即失效，需更新 Zotero 地址；已授权的在途请求可以完成。启动日志只提示查看命令。
完整 URL 属于凭据；原插件可能在诊断日志或连接检查弹窗中显示它，分享材料时遮蔽。

## Actions 与 Docker Hub

仓库：https://github.com/Wangtengzhou/zotero-pdf2zh-next

首次配置：

- Docker Hub 创建公开仓库 wangtengzhou/zotero-pdf2zh-next。
- GitHub Actions Secrets：DOCKERHUB_USERNAME、DOCKERHUB_TOKEN。使用专用 Docker Hub 写入令牌。
- 可选 Variable DOCKERHUB_IMAGE，默认 wangtengzhou/zotero-pdf2zh-next。

Build, Check and Publish：

- main、PR、手动运行：核心测试、构建与容器启动检查，不发布。
- 推送 v0.1.0 等 tag：检查后推送同一个镜像，生成 0.1.0 和 sha-<提交号> 标签。
- tag 必须匹配 versions.json 的 container 字段；已存在的公开版本阻止重复发布。
- Actions 输出镜像 digest。首次发布后，在 Zotero 实测 PDF 上传、进度、下载及附件导入。

验收后手动运行 Promote Tested Digest to Latest，填写 sha256 digest，只推广原镜像，不重新构建。服务器可以直接使用 digest 固定部署版本。

## 数据、升级与回滚

Compose 命名卷 auth、config、translated、cache 分别保存令牌、服务配置、PDF 与资源缓存。config 可能含翻译 API 密钥，auth 含入口凭据，备份按秘密处理。
上游任务与历史记录保存在内存，重启后清空；已生成的 PDF 仍保留在 translated 卷。
不要执行 docker compose down -v；删除 auth 卷会使下次启动生成新令牌。

升级前等待现有任务完成并备份卷数据，修改 .env 的 PDF2ZH_IMAGE 为新版本或 digest：

```bash
docker compose pull
docker compose up -d
```

回滚改回旧 digest 并执行同样命令。配置格式有变化时恢复配套配置备份，保留新生成 PDF。

## 本地维护与检查

Python 3.12 环境：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-gateway.lock
.venv/bin/python -m unittest discover -s tests -v
```

Linux Docker 环境可运行 bash scripts/smoke-test.sh IMAGE，检查启动、版本、鉴权、CLI 重置和持久化，不调用收费翻译 API。
更新 requirements.in 后，用 uv pip compile requirements.in --python-version 3.12 --python-platform x86_64-unknown-linux-gnu --generate-hashes -o requirements.lock 重新生成依赖锁。
版本升级同时核对 versions.json、Dockerfile 版本标签和断言、pyproject.toml、smoke-test.sh 的版本断言。

首版面向个人使用，不宣称多用户数据隔离或并发配置安全。浏览器进度面板的路径适配暂不提供。

设计：[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)、[PUBLIC_ACCESS.md](PUBLIC_ACCESS.md)。授权：[LICENSE](LICENSE)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
