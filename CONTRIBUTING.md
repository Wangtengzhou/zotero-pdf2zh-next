# 开发与镜像发布

## 本地开发

网关开发使用 Python 3.12：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-gateway.lock
.venv/bin/python -m unittest discover -s tests -v
```

核心测试覆盖令牌持久化及重置、终端管理、认证和转发、请求体限制及上游错误。测试不调用收费翻译 API。

## 构建镜像

```bash
docker build --platform linux/amd64 \
  --build-arg SOURCE_URL=https://github.com/Wangtengzhou/zotero-pdf2zh-next \
  -t zotero-pdf2zh-next:local .
bash scripts/smoke-test.sh zotero-pdf2zh-next:local
```

容器检查包括上游启动、版本与 Next CLI、认证、令牌重置和保留卷后的重建。部署后使用 Zotero 确认 PDF 上传、进度、下载及附件导入。

## 更新依赖

修改 `requirements.in` 后使用 uv 重新生成 Linux amd64 依赖锁：

```bash
uv pip compile requirements.in \
  --python-version 3.12 \
  --python-platform x86_64-unknown-linux-gnu \
  --generate-hashes \
  -o requirements.lock
```

网关测试依赖由 `requirements-gateway.in` 与 `requirements-gateway.lock` 管理。

版本升级时同步检查 `versions.json`、`Dockerfile` 的版本标签与断言、`pyproject.toml`、`scripts/smoke-test.sh` 及 `CHANGELOG.md`。变更上游包时重新核实下载地址、校验值、插件协议及许可证。

## GitHub Actions

### Build, Check and Publish

- `main`、Pull Request 与手动运行：核心测试、镜像构建、容器检查。
- 推送 `v*` Git 标签：完成上述检查后发布同一受测镜像。
- Git 标签必须与 `versions.json` 中的容器版本对应；已存在的公开版本阻止覆盖，修复使用新版本号。
- 发布 `:<版本>` 和 `:sha-<Git 提交号>`，并在 Actions 摘要中输出镜像 digest。
- 发布完成后调用 `Publish Offline Image`，按同一 digest 导出 Docker 镜像，在 GitHub Release 附加 `.tar.gz`、校验值、部署文件及体积明细。

在自有仓库启用发布时，配置：

| 类型 | 名称 | 内容 |
| --- | --- | --- |
| Actions Secret | `DOCKERHUB_USERNAME` | Docker Hub 用户名，按实际账号使用小写 |
| Actions Secret | `DOCKERHUB_TOKEN` | Docker Hub 专用写入令牌 |
| Actions Variable，可选 | `DOCKERHUB_IMAGE` | 目标镜像仓库；默认 `wangtengzhou/zotero-pdf2zh-next` |

目标 Docker Hub 仓库需为公开仓库，以便执行已有版本检查。发布凭据不会提供给 Pull Request 检查。

### Publish Offline Image

也可手动运行此流程，为已有版本补充离线镜像。输入现有 Git 标签（如 `v0.1.0`）以及已发布镜像的 `sha256:` digest。流程拉取该镜像，核对版本、源码提交和平台，导出并实际执行 `docker load` 校验后上传 Release 附件，不重新构建或更改原镜像。

流程使用 GitHub 内置令牌的 `contents: write` 权限，不需要额外配置发布 Secret。已存在的同名附件不自动覆盖；失败重试前检查 Release 状态。二进制镜像保存在 Release 附件中，不提交到 Git 源码历史。

### Promote Tested Digest to Latest

部署指定版本并完成实际 Zotero 翻译验收后，手动运行推广流程，输入该镜像的 `sha256:<64位十六进制摘要>`。流程将同一镜像标记为 `latest`。

## 问题反馈

通过 [GitHub Issues](https://github.com/Wangtengzhou/zotero-pdf2zh-next/issues) 提交镜像版本、平台、部署方式、Zotero / 插件版本、复现步骤及相关日志。提交前遮蔽入口令牌、完整带令牌地址、API 密钥与 PDF 私有内容。
