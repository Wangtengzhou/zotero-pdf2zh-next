# Architecture

[简体中文](ARCHITECTURE.md) | **English**

## Request Path

```text
Zotero PDF2zh -> LAN / HTTPS proxy -> :8890 gateway
             -> 127.0.0.1:8891 upstream server -> Next / BabelDOC
```

The gateway and upstream server run in one container, managed by `scripts/supervise.py`. If either child exits, the container stops and Docker applies its restart policy. Health checks authenticate with the current token and reach the upstream health endpoint.

## Gateway and Authentication

`gateway/app.py` uses Starlette and httpx. Tokens are checked before reading request bodies or contacting upstream. The proxy handles query strings, streaming, SSE and upstream errors, with body-size and timeout limits.

The upstream destination is fixed to loopback. Hop-by-hop, authentication and forwarded headers are filtered. Translation POST requests are not retried automatically. Encoded separators, backslashes and traversal paths are rejected. LAN and public access use the same authentication; domains are not part of validation.

`gateway/tokens.py` uses cryptographic randomness, constant-time comparison, file locking and atomic replacement. Credentials are read per request, so resets apply immediately to new requests. Directory permissions are `700`; token file permissions are `600`.

## Upstream and Initialization

The build downloads a pinned release's `server.zip` and checks its SHA-256 and version. Original server sources remain in `/app/server`. Python dependencies and the base image are pinned and verified, with resource warmup during the build. The startup wrapper disables upstream updates and notice requests.

Templates live outside mounted storage at `/app/defaults/config`. Startup restores managed `.example` files, then calls upstream migration while preserving active user settings. This supports both empty host folders and named volumes.

## Storage

| Path | Contents |
| --- | --- |
| `/app/gateway/state` | Token |
| `/app/server/config` | Configuration |
| `/app/server/translated` | PDFs |
| `/home/app/.cache` | Resource cache |

Processes run as UID/GID `10001:10001`. Upstream keeps tasks and history in memory, cleared on restart; persisted data remains. There is no multi-user isolation.

## Releases

GitHub Actions builds a Linux amd64 image and runs core and real-container checks before publishing a version tag only. OCI labels retain the source revision; digests are used for internal verification. No commit-based or `latest` tags are created.

The offline workflow pulls the same digest, exports with `docker save` and gzip, verifies `docker load`, and uploads GitHub Release assets with checksums, deployment files and size information. See [development and releases](../CONTRIBUTING.en.md).
