# Deployment Guide

[简体中文](DEPLOYMENT.md) | **English**

## Requirements and Storage

Linux x86_64 / amd64 is supported; arm64 images are not available. Use HTTP for trusted LAN access and an HTTPS proxy such as Lucky for public access. No domain is required to start the container.

The service runs as UID/GID `10001:10001`. Persist these four locations:

| Container path | Example folder / volume | Contents |
| --- | --- | --- |
| `/app/gateway/state` | `auth` | Access token |
| `/app/server/config` | `config` | Translation settings and any saved API keys |
| `/app/server/translated` | `translated` | PDF files |
| `/home/app/.cache` | `cache` | Fonts, models and resource caches |

Allow time and disk space for the first download or import. Wait for the container to become `healthy` before connecting.

## Method 1: Synology / fnOS Graphical Deployment

### 1. Obtain the Image

Open **Container Manager** on Synology (Docker on older DSM versions), or the Docker application on fnOS. Menu names vary by version.

Online: search for `wangtengzhou/zotero-pdf2zh-next` in the image registry, select `0.1.2`, and download it.

Offline:

1. Download `zotero-pdf2zh-next-0.1.2-linux-amd64.tar.gz` from [GitHub Releases](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases).
2. Upload it to your NAS and select **Import / Import from file** on the image page.
3. If the dialog accepts only `.tar`, decompress the gzip file once to obtain `.tar`. Do not extract the files inside the tar archive.
4. Confirm the local image is named `wangtengzhou/zotero-pdf2zh-next:0.1.2` and disable forced pulling when creating the container.

GitHub's automatically generated **Source code** archives are not images. Compare downloaded files with the release's `SHA256SUMS` if needed.

### 2. Prepare Four Folders

Create `auth`, `config`, `translated` and `cache` inside a dedicated project directory. Example roots:

- Synology: `/volume1/docker/zotero-pdf2zh-next`
- fnOS: `/vol1/1000/Docker/Zotero-PDF2zh-Next`

**UID/GID `10001:10001` must be able to read and write all four folders.** NAS-created folders often belong to another user. Fix ownership before starting the container. Run this in the NAS terminal, changing `PDF2ZH_STORAGE` to your actual dedicated directory first:

```bash
PDF2ZH_STORAGE=/vol1/1000/Docker/Zotero-PDF2zh-Next
sudo mkdir -p "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chown -R 10001:10001 "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chmod 700 "$PDF2ZH_STORAGE/auth"
```

Apply this only to the four dedicated folders, not a NAS share root. Existing files also need the correct ownership; ACL-controlled shares must permit access by the service user.

### 3. Create the Container

Select the local image and create a container with these settings:

| Setting | Value |
| --- | --- |
| Image | `wangtengzhou/zotero-pdf2zh-next:0.1.2` |
| Container name | `zotero-pdf2zh-next` |
| Network | Default bridge |
| Port | Host `8890` to container `8890`, TCP |
| Bind address | LAN access: LAN IP or `0.0.0.0`; native Lucky on the same host: `127.0.0.1` |
| Restart policy | Automatic restart / `unless-stopped` |
| User and startup command | Keep image defaults |
| Privileged mode | Disabled |

Mount the four host folders at the corresponding container paths in the storage table, all read-write. Do not mount over `/app` or the entire `/app/server`, and do not publish the internal port `8891`.

Environment variables can use their defaults. `PUBLIC_BASE_URL` does not need to be added:

| Variable | Default | Purpose |
| --- | --- | --- |
| `MAX_UPLOAD_MB` | `100` | Request body limit, including Base64 expansion |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` | Upstream timeout in seconds |
| `TZ` | `Asia/Shanghai` | Time zone |
| `PUBLIC_BASE_URL` | Empty, optional | URL display preference for admin commands; no domain binding |

Configuration templates are restored automatically; existing active settings are passed to upstream migration. An empty cache folder hides preloaded image resources, which may need to be downloaded again during translation.

### 4. Retrieve the Address

Start the container and check its health and logs. Open the console with `/bin/sh`, using the default `app` user (UID `10001`):

```bash
pdf2zh-admin url show
```

Append the printed `/access/<token>` path to your NAS address or proxy domain:

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

## Method 2: Docker Compose

Use Docker Compose v2 and obtain the project:

```bash
git clone https://github.com/Wangtengzhou/zotero-pdf2zh-next.git
cd zotero-pdf2zh-next
cp .env.example .env
```

Example `.env`:

```dotenv
PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.2
BIND_ADDRESS=127.0.0.1
HOST_PORT=8890
PUBLIC_BASE_URL=
MAX_UPLOAD_MB=100
UPSTREAM_TIMEOUT_SECONDS=3600
TZ=Asia/Shanghai
```

The default loopback binding suits native Lucky on the same host. For LAN access, set `BIND_ADDRESS` to the server's LAN IP or `0.0.0.0`. Leave the domain unset if desired.

Start online:

```bash
docker compose pull
docker compose up -d
docker compose ps
docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

Compose uses four named volumes, initialized by Docker with image resources and permissions. Keep the Compose project name unchanged. No host folders are required. If you replace the volumes with host-folder mounts, prepare their permissions as described in the graphical deployment section.

### Offline Compose Import

Download the image, `compose.yaml`, `env.example` and optional checksum files from the release, then upload them to one directory:

```bash
docker load --input zotero-pdf2zh-next-0.1.2-linux-amd64.tar.gz
cp env.example .env
docker compose up -d --pull never
docker compose ps
```

Use the version tag `:0.1.2` and do not run `docker compose pull`. The domain can remain unset; adjust port binding if needed. If all release assets are downloaded, verify them first with `sha256sum -c SHA256SUMS`.

## Lucky and Zotero

Native Lucky on the same host proxies its HTTPS domain to `http://127.0.0.1:8890`, preserving the full path and query string. Disable additional login redirects and business-response caching. Match upload limits to `MAX_UPLOAD_MB` and timeouts to `UPSTREAM_TIMEOUT_SECONDS`; preserve SSE streaming and disable or redact access logs containing tokens.

If Lucky runs in a container, its loopback address does not reach the PDF2zh container. Connect both to a controlled shared Docker network and use `http://pdf2zh:8890` (the Compose service name), or use a reachable host LAN address. Configure the shared network persistently for both containers.

Multiple proxy domains can use the same token without changing the container. Enter the complete token URL in the Zotero plugin's **Python Server IP**, without a trailing slash. Select **pdf2zh_next** and configure the translation provider, model and API key separately. Check upload, progress, download and attachment import with a short PDF.

## Tokens and Upgrades

Run in the container console:

```bash
pdf2zh-admin url show
pdf2zh-admin url show --base-url https://pdf.example.com
pdf2zh-admin token show
pdf2zh-admin token reset
```

Use the default `app` user. If the graphical console forces root, run `docker exec zotero-pdf2zh-next pdf2zh-admin token reset` from the NAS terminal to avoid creating token files unreadable by the service user. See [token management](../PUBLIC_ACCESS.en.md).

Before upgrading, let translations finish and back up all four storage locations. In the graphical manager, import or download the new version and update the original container while retaining all mounts. With Compose, change the version in `.env`, pull and start again; use `--pull never` after offline import.

To roll back, select the old version and restore its configuration backup if the format changed. Restarting clears in-memory task history but preserves PDFs. Do not run `docker compose down -v` or select an option that deletes volumes.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Token directory is unwritable | Check read-write mounts and UID 10001 access to folders and existing files; fix permissions before changing the token |
| `0.1.0` reports missing configuration and templates | Use `0.1.2`, which restores templates automatically |
| Lucky returns 502 | Check the backend address and health; container loopback points to that container itself |
| Large PDF upload fails | Check gateway and proxy limits; Base64 increases size by roughly one third |
| Translation fails or times out | Check provider credentials, model, network and timeouts; redact credentials before sharing logs |
| Image is about 843 MB | It includes translation dependencies, Linux libraries, fonts and models; see the release's `IMAGE_INFO.txt` |

If the container exits, inspect mounts from the NAS terminal without exposing the token:

```bash
docker inspect zotero-pdf2zh-next --format 'User={{.Config.User}}{{range .Mounts}}{{println}}{{.Source}} -> {{.Destination}} RW={{.RW}}{{end}}'
docker logs --since=1m zotero-pdf2zh-next
```
