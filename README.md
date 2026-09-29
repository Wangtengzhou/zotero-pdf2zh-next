# Zotero PDF2zh Next

**简体中文** | [English](README.en.md)

[![Build](https://github.com/Wangtengzhou/zotero-pdf2zh-next/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Wangtengzhou/zotero-pdf2zh-next/actions/workflows/ci.yml)
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-wangtengzhou%2Fzotero--pdf2zh--next-2496ED?logo=docker)](https://hub.docker.com/r/wangtengzhou/zotero-pdf2zh-next)

为 [Zotero PDF2zh](https://github.com/guaguastandup/zotero-pdf2zh) 插件提供运行在服务器上的 [PDFMathTranslate Next](https://github.com/PDFMathTranslate/PDFMathTranslate-next) 后端。

本项目是独立维护的容器封装，使用原版 Zotero PDF2zh 服务端和官方 Next 引擎，提供持久化存储及令牌认证。

## 功能

- Linux x86_64 Docker 部署，适用于群晖、飞牛等 NAS 和普通服务器。
- 内网与公网统一使用令牌地址，更换客户端 IP 无需重新认证。
- 启动就绪后在日志显示安全入口，支持命令查看与重置；升级保留原令牌。
- 持久化翻译配置、PDF、字体与模型缓存，支持空配置文件夹初始化。
- 使用非 root 服务用户、固定上游版本和依赖，不在运行时自动升级。
- 自动发布 Docker Hub 版本镜像与 GitHub Release 离线镜像包。

## 当前版本

| 组件 | 版本 |
| --- | --- |
| 容器镜像 | `0.1.3` |
| Zotero PDF2zh 服务端 | `4.1.7` |
| PDFMathTranslate Next | `2.9.0` |
| BabelDOC | `0.6.2` |
| 平台 | `linux/amd64` |

依赖与校验值见 [versions.json](versions.json)，变更见 [更新日志](CHANGELOG.md)。

## 部署

提供两种部署方式：

1. [群晖／飞牛图形化部署](docs/DEPLOYMENT.md#方式一群晖飞牛图形化部署)：在 NAS 容器管理器中配置镜像、端口和文件夹，可导入 GitHub 离线镜像。
2. [Docker Compose 一段命令部署](docs/DEPLOYMENT.md#方式二docker-compose)：复制整段命令，自动创建数据卷、拉取镜像并启动，无需手工映射目录。

镜像地址：`wangtengzhou/zotero-pdf2zh-next:0.1.3`。Docker Hub 只发布版本号标签，不提供 `sha-…` 或 `latest` 标签。

下载入口：[Docker Hub](https://hub.docker.com/r/wangtengzhou/zotero-pdf2zh-next) · [GitHub 离线镜像](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases)。GitHub 的 **Source code** 附件是源码，不能作为镜像导入。

## 连接 Zotero

启动就绪后，从容器日志复制“安全入口 / Access entry”一行的路径。也可在容器终端以默认 `app` 用户执行：

```bash
pdf2zh-admin url show
```

将 `/access/<令牌>` 接在内网地址或 Lucky 域名后，填入插件的 **Python Server IP**。引擎选择 **pdf2zh_next**，并选中已配置模型和密钥的翻译渠道。

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

容器无需配置域名；多个反代域名可使用同一令牌。`PUBLIC_BASE_URL` 仅是可选的地址显示偏好。

## 适用范围

面向个人或受信任的小范围使用，所有持有令牌的客户端共享配置与文件，未提供多用户隔离。公网使用 HTTPS，日志及诊断材料需遮蔽令牌和 API 密钥。

上游任务记录保存在内存中，重启后清空；持久化 PDF 保留。服务供 Zotero 插件连接使用，不提供适配安全入口的浏览器进度面板。

## 文档

- [部署指南](docs/DEPLOYMENT.md)
- [访问与令牌管理](PUBLIC_ACCESS.md)
- [升级、缓存与排错](docs/OPERATIONS.md)
- [系统架构](docs/ARCHITECTURE.md)
- [开发与发布](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [问题反馈](https://github.com/Wangtengzhou/zotero-pdf2zh-next/issues)

所有说明文档均提供对应英文文件和语言切换链接。

## 许可证

本项目自有代码采用 [MIT License](LICENSE)。镜像中的上游组件保留 AGPL-3.0 等许可证，详见 [第三方声明](THIRD_PARTY_NOTICES.md)。许可证原文保持不变。
