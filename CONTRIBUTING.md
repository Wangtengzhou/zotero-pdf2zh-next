# 开发与发布

**简体中文** | [English](CONTRIBUTING.en.md)

## 本地开发

使用 Python 3.12：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-gateway.lock
.venv/bin/python -m unittest discover -s tests -v
```

核心检查覆盖令牌持久化与重置、CLI、认证与转发、体积限制、上游错误和空配置目录初始化，不调用收费翻译 API。

## 构建与检查

```bash
docker build --platform linux/amd64 \
  --build-arg SOURCE_URL=https://github.com/Wangtengzhou/zotero-pdf2zh-next \
  -t zotero-pdf2zh-next:local .
bash scripts/smoke-test.sh zotero-pdf2zh-next:local
```

容器检查包括上游健康与版本、Next CLI、认证、热重置、命名卷持久化，以及无域名变量的四个空文件夹挂载启动。实际翻译与 Zotero 导入在部署环境确认。

## 更新依赖与文档

修改 `requirements.in` 后重新生成 Linux amd64 依赖锁：

```bash
uv pip compile requirements.in \
  --python-version 3.12 \
  --python-platform x86_64-unknown-linux-gnu \
  --generate-hashes -o requirements.lock
```

网关开发依赖使用 `requirements-gateway.in` 和 `.lock`。版本升级同步核对 `versions.json`、Dockerfile、`pyproject.toml`、容器检查中的版本断言、Compose 默认版本和更新日志。上游包变更需重新核实地址、校验值、协议及许可证。

所有说明文档采用中文主文件和 `.en.md` 英文对应文件；内容、命令和语言链接同步维护。许可证原文不改写。

## 自动发布

### 上游升级的维护流程

上游发布不会自动修改现有镜像或运行中的容器。服务端升级时更新 `versions.json` 中的服务端版本、下载地址与 SHA256；Next／BabelDOC 升级时同步修改版本记录和依赖约束，并重新生成锁文件。核对上游配置迁移和插件兼容性，更新容器版本、测试中的版本断言及双语更新日志，执行核心检查和真实容器启动检查，通过后发布新的 `vX.Y.Z` 标签。GitHub Actions 构建并上传版本镜像和离线附件；NAS 用户再更换镜像。不要覆盖已经发布的版本标签。

`Build, Check and Publish`：

- `main`、Pull Request 和手动运行执行检查，不发布镜像。
- 推送 `v*` Git 标签后，检查通过才发布同一受测镜像。
- 标签匹配 `versions.json` 的容器版本，已有版本禁止覆盖，修复使用新版本号。
- Docker Hub 只发布 `:<版本>`，不生成 `sha-…` 或 `latest`。
- 源码提交保存在 OCI 元数据；digest 用于验证与离线导出，不作为额外标签。
- 随后发布 GitHub Release 离线镜像、校验值、部署文件与体积明细。
- 每个新版本必须同时填写中英文更新日志；发布前检查两份版本记录，Release 自动汇总中文、英文及双语离线部署说明。

配置公开 Docker Hub 仓库和以下 GitHub 设置：

| 类型 | 名称 | 内容 |
| --- | --- | --- |
| Actions Secret | `DOCKERHUB_USERNAME` | 小写 Docker Hub 用户名 |
| Actions Secret | `DOCKERHUB_TOKEN` | 专用写入令牌 |
| Actions Variable，可选 | `DOCKERHUB_IMAGE` | 默认 `wangtengzhou/zotero-pdf2zh-next` |

Pull Request 不使用发布凭据。

## 补充离线附件

手动运行 `Publish Offline Image`，输入已有 Git 标签和对应的 `sha256:` 镜像摘要。流程验证版本、源码提交和平台，导出并实际导入检查后上传，不重建或更改版本镜像。

使用内置 GitHub 令牌的 `contents: write` 权限。同名附件不自动覆盖，失败重试前检查 Release 状态。大文件存放在 Release 中，不提交到 Git 历史。

## 反馈

[GitHub Issues](https://github.com/Wangtengzhou/zotero-pdf2zh-next/issues) 请附镜像版本、平台、部署方式、Zotero／插件版本、复现步骤和日志。先遮蔽令牌、完整带令牌地址、API 密钥及敏感 PDF 信息。
