# 实施方案

设计日期：2026-09-29。

## 1. 目标与范围

在用户服务器运行单个容器，支持原版 Zotero PDF2zh 插件提交 PDF、显示进度、取回中文及双语 PDF、导入附件。

本仓库维护容器封装、版本清单、部署配置和 GitHub Actions。服务端使用 guaguastandup/zotero-pdf2zh，翻译引擎使用官方 pdf2zh-next。首版仅提供 Next 引擎。

容器运行时直接调用引擎，不挂载宿主机 docker.sock。首版面向个人使用；批量请求先按单任务串行验收，多用户并发需要另行验证配置隔离和文件冲突。

## 2. 已核实事实与候选版本

2026-09-29 读取上游 GitHub Release、对应 tag 源码和 PyPI 元数据：

| 项目 | 候选值 | 状态 |
| --- | --- | --- |
| 原版服务端 | v4.1.7 | 当前非预发布 Release，已核实 |
| server.zip SHA-256 | 118c7f37844ebeb67f7c9f018421ef1ab72e25e42ee7fd5b83a11c731d4b666b | GitHub Release 元数据提供；实现时下载并复核 |
| pdf2zh-next | 2.9.0 | PyPI 当前版本，已核实 |
| Next 的 Python 要求 | >=3.10,<3.14 | 已核实 |
| Next 的 BabelDOC 要求 | >=0.6.2,<0.7.0 | 已核实；具体版本在依赖锁定时确定 |
| Python | 3.12 | 设计选择；以真实构建验证为准 |
| 首发架构 | linux/amd64 | 用户提供 Linux x86，按常见 x86_64 解释；实施时用 uname -m 核实 |

服务端 v4.1.7 默认监听 127.0.0.1；修订方案保留上游回环监听，仅鉴权网关监听容器 0.0.0.0:8890。
源码提供 /health、/translate、/events、/translatedFile 等端点，配置目录是 /app/server/config，输出目录是 /app/server/translated。
--check_update=False 关闭源码更新检查，但启动通知获取仍在该条件之外；实现时需检查网络超时对启动的影响。

上述组合是候选基线，尚未通过镜像构建或翻译联调。用户说明插件为最新版，按原版 v4.1.7 准备；联调前核对实际来源和版本号。

## 3. 运行架构

```text
本机 Zotero 原插件
  -> 公网 HTTPS 独立域名
  -> Lucky HTTPS 反代，保留路径
  -> 容器鉴权网关:8890，验证 URL 路径令牌
  -> 容器内部回环地址:8891
  -> 容器内原版服务端
  -> pdf2zh_next CLI / BabelDOC
  -> 翻译服务商 API 或用户已有模型服务
  -> PDF 输出文件
  -> 原插件通过 HTTP 下载并导入附件
```

用户要求便捷公网访问，使用 Lucky 提供 HTTPS 反代。8890 为网关端口，根据 Lucky 部署位置使用回环地址、受控容器网络或受限制内网地址；上游端口不直接暴露。
公网方案详见 PUBLIC_ACCESS.md。用户一次配置 https://域名/access/<随机令牌>，网关逐次自动验证，不要求手动认证 IP，换网仍可使用。
已核查 v4.1.7 的上传、轮询与附件下载调用没有发送 Authorization 头，不能把 BasicAuth 或浏览器登录 Cookie 的兼容性当作已验证事实。
已核查 v4.1.7 的连接检查、上传、轮询和附件下载保留 URL 前缀；实际兼容性待联调。网关精确验证可撤销的高熵随机令牌，不依赖可猜隐藏路径。

首版沿用上游进程模型，单服务进程运行。不能直接启用多个 WSGI worker，否则内存任务状态和进度可能不一致。

## 4. 构建与版本固定

采用 Python 3.12 Debian slim 基础镜像，在镜像内安装服务端依赖、pdf2zh-next 及所需系统库。
参考官方 Next Dockerfile 的系统库和 BabelDOC warmup，避免依赖可变的官方 latest 镜像。基础镜像在首个通过验证的版本中固定 digest。

构建步骤：

1. 从指定 Release 下载 server.zip，并验证 SHA-256。
2. 检查解压后的 server/server.py 与预期版本一致。
3. 安装针对目标架构生成的完整依赖锁文件；不仅固定 Next 的直接版本。
4. 预热 BabelDOC 字体与模型资源，核对缓存路径、许可证和容器用户权限。
5. 设置非 root 用户及可写目录，启动时禁用虚拟环境管理和源码自动更新。
6. 添加内部网关存活检查，用临时测试令牌检查受保护的 /health，确认上游和依赖可用。

计划启动参数：

```text
python /app/server/server.py --host=127.0.0.1 --port=8891 --enable_venv=False --check_update=False
```

实际参数与启动工作目录在镜像测试后固化。若上游通知请求造成启动阻塞，只添加有记录、可复核的最小补丁。
容器内不执行 pip upgrade 或服务端自更新；更新通过重建镜像完成。

## 5. 数据与配置

| 路径 | 用途 | 处理方式 |
| --- | --- | --- |
| /app/server/config | 服务端配置、翻译 API 配置 | 持久化；可能含密钥，排除 Git 与镜像构建上下文 |
| /app/server/translated | 上传 PDF、输出 PDF | 持久化；用户显式清理 |
| /app/gateway/state | 入口令牌 auth.json | 持久化，服务账户私有权限；首次自动生成，重启和升级保留 |
| BabelDOC 资源缓存 | 字体、模型等 | 构建时预热；实际路径核实后决定卷挂载 |
| 任务与历史 | 内存状态 | 已核查 task_manager.py，重启清空；PDF 文件独立持久化 |

API Key 沿用原插件配置流程，不写入 Dockerfile、Actions 或公共仓库。部署文档说明卷目录权限和备份方式。
挂载空配置目录后，必须验证上游配置模板初始化正常。
入口凭据只以持久化文件为准，不同时用环境变量保存第二份令牌。PUBLIC_BASE_URL 配置公网域名，用于管理命令输出完整插件地址。
提供 pdf2zh-admin token show、url show、token reset，服务器 docker exec 或容器终端可调用。reset 原子写入并对新请求即时生效，无需重启容器；旧在途请求可完成。
启动日志显示查看命令，不打印令牌。完整管理行为及失败边界见 PUBLIC_ACCESS.md。

## 6. GitHub Actions 与 Docker Hub

实现采用 ci.yml 合并验证与按 tag 发布，受测镜像直接推送；promote.yml 独立推广 digest：

### CI 验证

- pull_request、主分支 push、手动触发。
- 检查 Dockerfile、Compose 和 workflow；构建镜像但不发布。
- 启动容器，检查 /health、版本及输出目录。
- 不使用翻译服务密钥，不在来自 fork 的 PR 中开放发布凭据。

### 发布

- 首次联调后，以 v 开头的本仓库版本 tag 自动触发，例如 v0.1.0。
- 使用 Docker Hub 专用访问令牌；GitHub Secrets 为 DOCKERHUB_USERNAME、DOCKERHUB_TOKEN。
- GitHub Variable DOCKERHUB_IMAGE 保存完整仓库名：wangtengzhou/zotero-pdf2zh-next。用户提供用户名 Wangtengzhou，镜像路径按 Docker 命名要求使用小写，首次配置时核对账户。
- 先构建并通过容器启动测试，再上传同一待发布构建产物；不能用另一次可变构建替代受测镜像。
- 首版只发布目标架构；固定 Actions commit，使用最小权限与发布并发控制。
- 发布明确的版本 tag 和 Git commit tag，写入 OCI 源码、版本、许可证及上游版本标签，输出镜像 digest。
- latest 通过手动推广已验收版本的同一 digest 更新，避免把仅启动成功的版本当作已完成插件验收。
- 重复发布同一版本必须阻止覆盖或显式报错；修复使用新版本号。

注意：GitHub Actions 可以自动打包发布，但实际 Zotero 附件导入是首发及兼容性升级时的人工验收项目。
首次启用 tag 自动发布需要用户确认；之后约定的版本发布由既定流程执行。

## 7. 计划文件

```text
Dockerfile
compose.yaml
.env.example
.dockerignore
.gitignore
versions.json
requirements.in
requirements.lock
scripts/supervise.py
scripts/run_upstream.py
scripts/smoke-test.sh
gateway/
gateway/admin.py
tests/test_core.py
.github/workflows/ci.yml
.github/workflows/promote.yml
README.md
IMPLEMENTATION_PLAN.md
PUBLIC_ACCESS.md
THIRD_PARTY_NOTICES.md
```

实现时核对服务端、Next、BabelDOC 及资产的许可证，保留要求的声明，并记录对应源码下载位置与补丁。
沿用用户已初始化仓库的 MIT LICENSE，独立保留上游 AGPL 文本与声明，不覆盖上游组件授权。

## 8. 验收与回滚

首发验收：

- 镜像构建成功；Next 版本与依赖锁一致。
- 容器健康且从另一台设备可访问，返回服务端 v4.1.7。
- 用自有或可合法使用的小 PDF 完成一次真实翻译。
- Zotero 显示进度、下载中文及双语 PDF、自动导入附件，并能打开结果。
- 中文文件名正常；无共享本地目录时仍可通过 HTTP 导入。
- 单次失败后服务可继续处理任务；不宣称已支持取消或并发隔离，除非验证通过。
- 重启容器后配置和 PDF 保留，缓存与历史行为有明确记录。
- 非 root 容器能写挂载目录；无需 docker.sock。
- 从 Docker Hub 拉取发布 digest，在服务器完成同一验收。
- 无令牌、错误或已撤销令牌不能访问全部业务端点；一次配置有效令牌后插件全部请求可用，换 IP 无需认证。
- 通过 Lucky 完成大文件提交、长时间翻译及进度流验证，确认超时和缓冲设置。
- 确认上游端口无法绕过网关访问，令牌轮换与撤销有效，日志不泄漏凭据。
- 验证终端查看/重置、首次自动生成、重建保留、损坏拒绝及写入失败保留原凭据。

回滚：停止提交新任务，等待运行任务完成；备份 config 和输出目录；将 Compose 改回旧 digest 并重建容器。
如上游更改配置格式，恢复配套配置备份；保留新生成 PDF，避免用旧备份覆盖输出。
不使用 docker compose down -v，不删除旧镜像版本。

## 9. 实施顺序与工作量

1. 确认插件版本、服务器架构与网络入口，预计 0.5 小时。
2. 实现版本清单、Dockerfile、依赖锁及 Compose，预计 2-4 小时。
3. 构建与服务器/Zotero 联调，预计 2-4 小时，具体取决于资源下载和上游兼容性。
4. 实现并检查 CI、发布、latest 推广，预计 1-2 小时。
5. 整理部署、升级、回滚及许可证说明，预计 1-2 小时。

容器封装约 1-2 个工作日，鉴权网关另增加半天到一天。普通升级约 30-60 分钟；遇到接口或依赖变化需额外排查。

当前完成：鉴权与令牌管理、4 个核心测试、上游包校验、完整 Linux 依赖锁、Dockerfile/Compose、Actions/推广流程与部署说明；Actionlint、Ruff 和 YAML 语法检查通过。
2026-09-29 已推送到 GitHub，并通过首次云端镜像构建和容器启动检查（Actions run 36513219727）。提交作者及提交者按用户最新指示使用 Wangtengzhou，保留 Agent: Codex。
2026-09-29 已配置 Docker Hub Secrets，并通过 v0.1.0 发布流程（Actions run 36514321090）：核心测试、真实容器检查与镜像推送全部成功。公开镜像 wangtengzhou/zotero-pdf2zh-next:0.1.0，digest 为 sha256:44d27f56df09beca3e8ff9f288b1dc91d0fe7f876e3abfea9807b19baaecaeaf。
当前未完成：服务器部署、Zotero 翻译联调；完成实际验收后再推广 latest。

## 10. 已确认、待核实信息与执行边界

- 用户已确认：Linux x86、最新版插件、GitHub 仓库名 zotero-pdf2zh-next、Docker Hub 用户名 wangtengzhou（小写）。
- 服务器 uname -m，以及 Docker / Compose 是否可用。
- 已安装插件的实际来源、版本号和 Zotero 版本。
- 已确认公网 HTTPS + 同服务器 Lucky 反代、路径令牌自动鉴权；待确认 Lucky 版本、原生/容器运行方式和公网域名。
- GitHub 仓库：https://github.com/Wangtengzhou/zotero-pdf2zh-next，main 分支，保留原 MIT LICENSE。Docker Hub 账户及公开目标仓库已通过实际发布验证。
- 用于真实翻译验收的服务商配置和样本 PDF。

可以先本地实现与检查。创建本地提交遵守项目身份与 Agent: Codex 正文规则，不修改持久 Git 配置。
推送远程仓库前必须询问用户，并按项目规则说明身份名称确认；保留已有提交身份，不改写历史。
部署到现有服务器及首次镜像发布在具体文件、测试结果和目标明确后执行。

## 11. 核查来源

- https://api.github.com/repos/guaguastandup/zotero-pdf2zh/releases/latest
- https://github.com/guaguastandup/zotero-pdf2zh/releases/tag/v4.1.7
- https://github.com/guaguastandup/zotero-pdf2zh/blob/v4.1.7/server/server.py
- https://github.com/guaguastandup/zotero-pdf2zh/blob/main/docker2/Dockerfile
- https://pypi.org/pypi/pdf2zh-next/json
- https://github.com/PDFMathTranslate/PDFMathTranslate-next/blob/main/Dockerfile
- https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images
- https://github.com/guaguastandup/zotero-pdf2zh/blob/v4.1.7/plugin/src/modules/pdf2zhHelper.ts
- https://lucky666.cn/docs/modules/web/
- https://lucky666.cn/docs/modules/ipfilter/
