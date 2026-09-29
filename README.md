# Zotero PDF2zh Next

[![Build](https://github.com/Wangtengzhou/zotero-pdf2zh-next/actions/workflows/ci.yml/badge.svg)](https://github.com/Wangtengzhou/zotero-pdf2zh-next/actions/workflows/ci.yml)
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-wangtengzhou%2Fzotero--pdf2zh--next-2496ED?logo=docker)](https://hub.docker.com/r/wangtengzhou/zotero-pdf2zh-next)

为 [Zotero PDF2zh](https://github.com/guaguastandup/zotero-pdf2zh) 插件提供可部署在服务器上的 PDFMathTranslate Next 后端。

本项目封装原版 Zotero PDF2zh 服务端与官方 [PDFMathTranslate Next](https://github.com/PDFMathTranslate/PDFMathTranslate-next)，提供 Docker 镜像、持久化存储和适用于 HTTPS 反向代理的访问认证。它是独立维护的容器封装项目，与上游及 NightWatcher314 的同名项目无隶属关系。

## 功能

- 在 Linux x86_64 服务器运行 Next 翻译引擎，通过 Zotero 插件提交与获取 PDF。
- 通过带访问令牌的服务器地址自动认证，客户端更换 IP 后仍可使用。
- 自动生成并持久化令牌，支持在容器终端查看地址、查看令牌和重置令牌。
- 持久化翻译配置、PDF 文件及资源缓存。
- 以非 root 用户运行，构建时固定上游版本及依赖，不在运行时自动升级。
- 使用 GitHub Actions 构建、检查并发布 Docker Hub 版本镜像。

## 版本

| 组件 | 版本 |
| --- | --- |
| 容器镜像 | `0.1.2` |
| Zotero PDF2zh 服务端 | `4.1.7` |
| PDFMathTranslate Next | `2.9.0` |
| BabelDOC | `0.6.2` |
| 平台 | `linux/amd64` |

上游版本与校验值见 [versions.json](versions.json)，发布变更见 [CHANGELOG.md](CHANGELOG.md)。

## 快速开始

需要 Linux x86_64、Docker Engine 与 Docker Compose。可直接使用内网 HTTP 地址；公网使用 HTTPS 反向代理入口。

```bash
git clone https://github.com/Wangtengzhou/zotero-pdf2zh-next.git
cd zotero-pdf2zh-next
cp .env.example .env
```

无需配置域名即可启动。同服务器原生运行 Lucky 时，保留默认的 `127.0.0.1:8890` 端口绑定；需要从局域网直连时，将 `.env` 的 `BIND_ADDRESS` 设置为服务器内网 IP 或 `0.0.0.0`。

```bash
docker compose pull
docker compose up -d
docker compose ps
docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

最后一条命令默认输出 `/access/<令牌>` 路径，将它接在服务器地址之后，例如 `http://192.168.1.10:8890/access/<令牌>` 或 `https://pdf.example.com/access/<令牌>`。Lucky 保留完整请求路径，同一令牌可以在多个反代域名下使用，无需修改容器。

将完整地址填入 Zotero PDF2zh 插件的 **Python Server IP**，引擎选择 **pdf2zh_next**，并配置翻译服务商、模型及 API 密钥。

完整说明：[Docker 部署指南](docs/DEPLOYMENT.md)，包含 Compose、`docker run`、Portainer 和 NAS 图形化部署。

Docker Hub 下载困难时，可从 [GitHub Releases](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases) 下载离线镜像，上传到 NAS 后通过镜像导入功能或 `docker load` 加载，详见 [离线部署](docs/DEPLOYMENT.md#离线部署github-release)。

## 镜像标签

镜像仓库：[wangtengzhou/zotero-pdf2zh-next](https://hub.docker.com/r/wangtengzhou/zotero-pdf2zh-next)。

| 引用方式 | 用途 |
| --- | --- |
| `:0.1.2` | 正式版本，推荐部署使用 |
| `:sha-<Git 提交号>` | 对应发布源码的追溯标签，与该版本标签指向同一个镜像 |
| `@sha256:<镜像摘要>` | 按内容固定镜像，用于精确部署及回滚 |
| `:latest` | 经过实际 Zotero 验收后手动推广的版本；当前尚未提供 |

`sha-` 标签中的值是 Git 提交号，`sha256:` 后的值是镜像内容摘要，两者含义不同。Docker Hub 会将多个标签并列显示；同一镜像的标签只是不同名称，无需分别下载。

## 管理命令

```bash
# 显示可复用的令牌路径
docker exec zotero-pdf2zh-next pdf2zh-admin url show

# 临时指定内网地址，生成完整 URL
docker exec zotero-pdf2zh-next pdf2zh-admin url show --base-url http://192.168.1.10:8890

# 查看当前令牌
docker exec zotero-pdf2zh-next pdf2zh-admin token show

# 重置令牌并显示新地址
docker exec zotero-pdf2zh-next pdf2zh-admin token reset
```

在图形化管理器的容器终端中，直接运行 `pdf2zh-admin url show` 等命令。重置无需重启容器，之后需要更新 Zotero 中的地址。普通重启及升级保留原令牌。

`PUBLIC_BASE_URL` 仅是可选的地址显示偏好，不参与认证或域名绑定。省略它时始终输出路径；`--base-url` 可以临时选择任意内网地址或反代域名。

## 适用范围

- 面向个人或受信任的小范围使用，所有持有令牌的客户端共享后端数据与配置；没有多用户数据隔离。
- 对外入口使用 HTTPS，令牌地址属于访问凭据。反向代理日志及插件诊断材料需遮蔽完整地址。
- 上游任务记录保存在内存，容器重启后清空；持久化卷中的 PDF 保留。
- 当前入口以 Zotero 插件为主要客户端，未提供浏览器进度面板的路径适配。
- CI 检查容器启动、引擎 CLI、认证和令牌持久化；端到端 PDF 翻译及 Zotero 附件导入需在部署环境确认。

## 文档

- [部署、配置与升级](docs/DEPLOYMENT.md)
- [公网访问与令牌管理](PUBLIC_ACCESS.md)
- [系统架构](docs/ARCHITECTURE.md)
- [开发与镜像发布](CONTRIBUTING.md)
- [问题反馈](https://github.com/Wangtengzhou/zotero-pdf2zh-next/issues)

## 许可证

本项目自有代码采用 [MIT License](LICENSE)。镜像包含采用 AGPL-3.0 的上游服务端及其他第三方组件，分发与部署时需同时遵守各组件许可证，详情见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
