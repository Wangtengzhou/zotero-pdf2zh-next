# 第三方声明

**简体中文** | [English](THIRD_PARTY_NOTICES.en.md)

本镜像组合原版 Zotero PDF2zh 服务端、官方 PDFMathTranslate Next 与认证网关，不是 NightWatcher314 的分支版本。

| 组件 | 版本 | 源码 | 许可证 |
| --- | --- | --- | --- |
| Zotero PDF2zh 服务端 | 4.1.7 | [上游源码](https://github.com/guaguastandup/zotero-pdf2zh/tree/v4.1.7) | AGPL-3.0 |
| PDFMathTranslate Next | 2.9.0 | [上游源码](https://github.com/PDFMathTranslate/PDFMathTranslate-next) | AGPL-3.0 |
| BabelDOC | 0.6.2 | [上游源码](https://github.com/funstory-ai/BabelDOC) | AGPL-3.0 |

服务端包使用 `versions.json` 的哈希校验，许可证保留在 `/app/server/LICENSE`。Python 包的元数据与声明随依赖安装保留。BabelDOC warmup 下载官方字体与模型资源，其上游授权声明仍然适用。

原版服务端源码不改写。`scripts/run_upstream.py` 在内存中禁用启动通知请求，并在调用服务端前恢复托管配置模板；更新通过更换镜像完成。

封装源码应保持可从 OCI 标签 `org.opencontainers.image.source` 指定的仓库和 `org.opencontainers.image.revision` 指定的提交获得。本仓库提供构建文件、完整依赖锁、上游来源与封装源码。发布自有镜像时，将 `SOURCE_URL` 设置为实际仓库。

自有认证网关及构建文件使用仓库的 [MIT License](LICENSE)，上游保留各自 AGPL 授权。完整 AGPL 文本见 [LICENSES/AGPL-3.0.txt](LICENSES/AGPL-3.0.txt)。封装文件的 MIT 授权不替代组合分发中的上游许可证或源码提供义务。许可证原文保持不变。
