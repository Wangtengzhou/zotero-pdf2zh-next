# Zotero PDF2zh Next

[简体中文](README.md) | **English**

[![Build](https://github.com/Wangtengzhou/zotero-pdf2zh-next/actions/workflows/ci.yml/badge.svg)](https://github.com/Wangtengzhou/zotero-pdf2zh-next/actions/workflows/ci.yml)
[![Docker Hub](https://img.shields.io/badge/Docker_Hub-wangtengzhou%2Fzotero--pdf2zh--next-2496ED?logo=docker)](https://hub.docker.com/r/wangtengzhou/zotero-pdf2zh-next)

A server-hosted [PDFMathTranslate Next](https://github.com/PDFMathTranslate/PDFMathTranslate-next) backend for the [Zotero PDF2zh](https://github.com/guaguastandup/zotero-pdf2zh) plugin.

This independently maintained container packages the original Zotero PDF2zh server and official Next engine with persistent storage and token authentication. It is not affiliated with the upstream projects or NightWatcher314's similarly named project.

## Features

- Linux x86_64 Docker deployment for Synology, fnOS and other NAS devices or servers.
- One token-based address for LAN and public access, independent of client IP changes.
- Automatic token generation, terminal retrieval and live reset; tokens persist across upgrades.
- Persistent configuration, PDFs, fonts and model caches; empty configuration folders initialize automatically.
- Non-root service user, pinned upstream versions and dependencies, and no runtime auto-updates.
- Automated versioned Docker Hub images and offline archives in GitHub Releases.

## Current Versions

| Component | Version |
| --- | --- |
| Container image | `0.1.2` |
| Zotero PDF2zh server | `4.1.7` |
| PDFMathTranslate Next | `2.9.0` |
| BabelDOC | `0.6.2` |
| Platform | `linux/amd64` |

See [versions.json](versions.json) for pinned versions and checksums, and the [changelog](CHANGELOG.en.md) for changes.

## Deployment

Two deployment methods are documented:

1. [Synology / fnOS graphical deployment](docs/DEPLOYMENT.en.md#method-1-synology--fnos-graphical-deployment): configure the image, ports and folders in your NAS container manager, with optional offline import.
2. [Docker Compose with one command block](docs/DEPLOYMENT.en.md#method-2-docker-compose): paste the block to create volumes, pull the image and start the service, without manual folder mapping.

Image: `wangtengzhou/zotero-pdf2zh-next:0.1.2`. Docker Hub publishes version tags only, with no `sha-…` or `latest` tags.

Downloads: [Docker Hub](https://hub.docker.com/r/wangtengzhou/zotero-pdf2zh-next) · [GitHub offline images](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases). GitHub's **Source code** archives are not Docker images.

## Connect Zotero

In the NAS container console, run as the default `app` user:

```bash
pdf2zh-admin url show
```

By default, this prints `/access/<token>`. Append the path to a LAN address or Lucky domain, enter the complete URL in the plugin's **Python Server IP**, select **pdf2zh_next**, and configure your translation provider, model and API key.

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

No domain is required in the container configuration. Multiple proxy domains can use the same token. `PUBLIC_BASE_URL` is an optional display preference only.

## Scope

Designed for personal or trusted small-group use. Token holders share configuration and files; there is no multi-user isolation. Use HTTPS for public access and redact tokens and API keys from logs and diagnostics.

Upstream task history is held in memory and cleared on restart; persisted PDFs remain. Browser progress-panel path adaptation is not provided. CI checks startup, authentication, CLI commands, persistence and empty-folder initialization. Confirm actual PDF translation and attachment import in your deployment environment.

## Documentation

- [Deployment guide](docs/DEPLOYMENT.en.md)
- [Access and token management](PUBLIC_ACCESS.en.md)
- [Architecture](docs/ARCHITECTURE.en.md)
- [Development and releases](CONTRIBUTING.en.md)
- [Changelog](CHANGELOG.en.md)
- [Issues](https://github.com/Wangtengzhou/zotero-pdf2zh-next/issues)

Every documentation page has a Chinese counterpart and language switch links.

## License

Original project code is licensed under the [MIT License](LICENSE). Bundled upstream components retain AGPL-3.0 and other licenses; see [third-party notices](THIRD_PARTY_NOTICES.en.md). Original license texts are preserved.
