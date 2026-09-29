# Deployment Guide

[简体中文](DEPLOYMENT.md) | **English**

Use an Intel / AMD NAS or Linux server with Docker installed, and note its LAN IP. The current image is `0.1.3`, for `linux/amd64` only.

**Choose one of the two methods below.** For an existing installation, go to [upgrades and maintenance](OPERATIONS.en.md).

| Method | Best for | Storage |
| --- | --- | --- |
| [Synology / fnOS graphical deployment](#method-1-synology--fnos-graphical-deployment) | Configuring the container in a NAS interface | Four host folders; one permission setup step |
| [Docker Compose](#method-2-docker-compose) | Pasting commands in the NAS terminal | Four Docker-managed volumes; no manual mappings |

Connect over the LAN first. Add Lucky at the end if public access is needed. Neither method requires a domain environment variable.

## Method 1: Synology / fnOS Graphical Deployment

### 1. Download or Import the Image

Open **Container Manager** on Synology or **Docker** on fnOS. Search for and download:

```text
wangtengzhou/zotero-pdf2zh-next:0.1.3
```

**If Docker Hub is slow:** download `zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz` from the [0.1.3 Release](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases/tag/v0.1.3), upload it to the NAS, and choose **Import** on the image page.

If only `.tar` is accepted, decompress the gzip file once without extracting the tar contents. GitHub's **Source code** downloads are not container images.

### 2. Prepare Folders and Permissions

In your NAS Docker folder, create a project folder containing four subfolders: `auth`, `config`, `translated`, and `cache`.

Expand your platform below. **The left side is a NAS folder; the right side is a container path. Change only the left side to match your storage.**

<details>
<summary>Synology: folder mappings and permission commands</summary>

Example using the Docker shared folder on volume 1:

| NAS folder | Container path | Access |
| --- | --- | --- |
| `/volume1/docker/zotero-pdf2zh-next/auth` | `/app/gateway/state` | Read/write |
| `/volume1/docker/zotero-pdf2zh-next/config` | `/app/server/config` | Read/write |
| `/volume1/docker/zotero-pdf2zh-next/translated` | `/app/server/translated` | Read/write |
| `/volume1/docker/zotero-pdf2zh-next/cache` | `/home/app/.cache` | Read/write |

Run these four lines in the NAS system terminal or SSH. If your folder differs, change only the first line:

```bash
PDF2ZH_STORAGE=/volume1/docker/zotero-pdf2zh-next
sudo mkdir -p "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chown -R 10001:10001 "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chmod 700 "$PDF2ZH_STORAGE/auth"
```

</details>

<details>
<summary>fnOS: folder mappings and permission commands</summary>

Example full paths are shown below. Find your actual paths in the file manager's folder properties:

| NAS folder | Container path | Access |
| --- | --- | --- |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/auth` | `/app/gateway/state` | Read/write |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/config` | `/app/server/config` | Read/write |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/translated` | `/app/server/translated` | Read/write |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/cache` | `/home/app/.cache` | Read/write |

Run these four lines in the NAS system terminal or SSH. If your folder differs, change only the first line:

```bash
PDF2ZH_STORAGE=/vol1/1000/Docker/Zotero-PDF2zh-Next
sudo mkdir -p "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chown -R 10001:10001 "$PDF2ZH_STORAGE/auth" "$PDF2ZH_STORAGE/config" "$PDF2ZH_STORAGE/translated" "$PDF2ZH_STORAGE/cache"
sudo chmod 700 "$PDF2ZH_STORAGE/auth"
```

</details>

This lets the container user, ID `10001`, read and write its files. Apply it only to the four dedicated folders, never the NAS share root. If no NAS terminal is available, enable SSH and connect from your computer using `ssh username@NAS-LAN-IP`. Share ACLs must also permit access by this user.

### 3. Create the Container

Select the downloaded or imported image and enter:

| Setting | Value |
| --- | --- |
| Container name | `zotero-pdf2zh-next` |
| Network | bridge |
| Port | Host `8890` → container `8890`, TCP |
| Bind address, if shown | `0.0.0.0` |
| Restart policy | Automatic restart / `unless-stopped` |
| User and startup command | Keep defaults |
| Privileged mode | Disabled |

Add **four rows** on the storage/folder-mapping page, following your platform table. Set all rows to read/write. Do not mount the entire `/app` or `/app/server`.

**No additional environment variables or domain are required.** Disable forced pulling when using an imported local image.

### 4. Start and Retrieve Your Entry

Start the container, open its log and wait for:

```text
服务已就绪 / Service ready
安全入口 / Access entry: /access/YOUR-FULL-TOKEN
```

Copy the complete `/access/…` path and continue to [Connect Zotero](#connect-zotero).

If the log is unavailable, open the container terminal, select “New terminal / Execute command”, enter `/bin/sh`, keep the default `app` user and run `pdf2zh-admin url show`. See [access management](../PUBLIC_ACCESS.en.md) for retrieval and reset commands.

## Method 2: Docker Compose

### Online Installation

Paste the entire block into the **NAS/server terminal**, not the container console. Docker Compose v2 is required. Enter your NAS login password if prompted.

It creates `~/zotero-pdf2zh-next`, writes the configuration and starts the service. Four persistent volumes are created automatically; **no manual folders or mappings are needed**. The first image download is approximately 843 MB.

```bash
(
set -e
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ -e compose.yaml ] || [ -e .env ]; then
  echo '已有部署文件，请使用维护指南 / Existing deployment: see the maintenance guide.'
  exit 1
fi
sudo docker compose version
cat > compose.yaml <<'YAML'
services:
  pdf2zh:
    image: ${PDF2ZH_IMAGE:-wangtengzhou/zotero-pdf2zh-next:0.1.3}
    platform: linux/amd64
    container_name: zotero-pdf2zh-next
    restart: unless-stopped
    ports:
      - "${BIND_ADDRESS:-127.0.0.1}:${HOST_PORT:-8890}:8890"
    environment:
      PUBLIC_BASE_URL: ${PUBLIC_BASE_URL:-}
      MAX_UPLOAD_MB: ${MAX_UPLOAD_MB:-100}
      UPSTREAM_TIMEOUT_SECONDS: ${UPSTREAM_TIMEOUT_SECONDS:-3600}
      TZ: ${TZ:-Asia/Shanghai}
    volumes:
      - auth:/app/gateway/state
      - config:/app/server/config
      - translated:/app/server/translated
      - cache:/home/app/.cache
    stop_grace_period: 30s
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

volumes:
  auth:
  config:
  translated:
  cache:
YAML
printf '%s\n' 'PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.3' 'BIND_ADDRESS=0.0.0.0' > .env
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
)
```

When `/access/…` appears, continue to [Connect Zotero](#connect-zotero). The command stops if deployment files already exist, protecting existing settings. See [maintenance](OPERATIONS.en.md#resume-an-interrupted-installation) to resume an interrupted installation.

<details>
<summary>Docker Hub download failed: use the offline image</summary>

1. Download `zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz` from the [0.1.3 Release](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases/tag/v0.1.3) and upload it to the NAS.
2. In the NAS terminal, type `cd ` followed by the full path of the folder containing the image, then press Enter.
3. Paste the block below. It can also resume a first installation interrupted by a failed image pull:

```bash
(
set -e
sudo docker load --input zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ ! -f compose.yaml ]; then
cat > compose.yaml <<'YAML'
services:
  pdf2zh:
    image: ${PDF2ZH_IMAGE:-wangtengzhou/zotero-pdf2zh-next:0.1.3}
    platform: linux/amd64
    container_name: zotero-pdf2zh-next
    restart: unless-stopped
    ports:
      - "${BIND_ADDRESS:-127.0.0.1}:${HOST_PORT:-8890}:8890"
    environment:
      PUBLIC_BASE_URL: ${PUBLIC_BASE_URL:-}
      MAX_UPLOAD_MB: ${MAX_UPLOAD_MB:-100}
      UPSTREAM_TIMEOUT_SECONDS: ${UPSTREAM_TIMEOUT_SECONDS:-3600}
      TZ: ${TZ:-Asia/Shanghai}
    volumes:
      - auth:/app/gateway/state
      - config:/app/server/config
      - translated:/app/server/translated
      - cache:/home/app/.cache
    stop_grace_period: 30s
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

volumes:
  auth:
  config:
  translated:
  cache:
YAML
fi
if [ ! -f .env ]; then
  printf '%s\n' 'PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.3' 'BIND_ADDRESS=0.0.0.0' > .env
fi
sudo docker compose up -d --pull never --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
)
```

These installation steps need no network connection after the image is uploaded. Actual translation still needs access to your provider. To update an existing installation on another version, follow the [upgrade steps](OPERATIONS.en.md#upgrade-the-image).

</details>

## Connect Zotero

For a NAS at `192.168.1.10` with log entry `/access/YOUR-FULL-TOKEN`:

| Plugin setting | Value |
| --- | --- |
| Python Server IP | `http://192.168.1.10:8890/access/YOUR-FULL-TOKEN` |
| Translation engine | `pdf2zh_next` |
| Translation service | **Select** your configured LLM channel |
| Model, API URL and key | Enter your provider's values |

Use your own IP and token, without a trailing `/` or `/health`. Saving a channel in the configuration manager does not select it for translation.

Test the connection, then translate a short PDF and confirm the attachment is returned. See [connection checks](OPERATIONS.en.md#connection-checks) for browser health-check URLs.

## Optional: Lucky HTTPS Proxy

First confirm LAN translation works, then add a proxy rule using your domain and certificate:

| Setting | Value |
| --- | --- |
| Frontend | Your domain, HTTPS |
| Backend: native Lucky on the same host | `http://127.0.0.1:8890` |
| Backend: Lucky in a container or on another device | `http://NAS-LAN-IP:8890` |
| Path rewriting and additional login | Disabled |

Change Zotero's address to `https://YOUR-DOMAIN/access/YOUR-FULL-TOKEN`. Multiple domains can share one token; no container variable change is needed.

Preserve paths, query parameters and SSE streaming. Match the gateway upload limit (100 MB request body by default) and allow a 3600-second timeout. Disable response caching and redact tokens in access logs. Expose HTTPS publicly rather than forwarding port `8890` directly.

---

Next steps: [Access management](../PUBLIC_ACCESS.en.md) · [Upgrades, cache and troubleshooting](OPERATIONS.en.md)
