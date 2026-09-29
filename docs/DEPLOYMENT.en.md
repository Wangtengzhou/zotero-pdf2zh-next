# Deployment Guide

[简体中文](DEPLOYMENT.md) | **English**

## Requirements and Storage

**Choose one method; do not create the container twice.** Method 1 walks through the NAS interface. Method 2 lets you paste one command block to create storage and start the service. Install and start Docker first, and note your NAS LAN IP, for example `192.168.1.10`. Connect over the LAN before adding public access. Existing installations should use the upgrade instructions below.

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

Online: search for `wangtengzhou/zotero-pdf2zh-next` in the image registry, select `0.1.3`, and download it.

Offline:

1. Download `zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz` from [GitHub Releases](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases).
2. Upload it to your NAS and select **Import / Import from file** on the image page.
3. If the dialog accepts only `.tar`, decompress the gzip file once to obtain `.tar`. Do not extract the files inside the tar archive.
4. Confirm the local image is named `wangtengzhou/zotero-pdf2zh-next:0.1.3` and disable forced pulling when creating the container.

GitHub's automatically generated **Source code** archives are not images. Compare downloaded files with the release's `SHA256SUMS` if needed.

### 2. Prepare Four Folders

In the NAS file manager, open your Docker folder, create a project folder, and create `auth`, `config`, `translated` and `cache` inside it. When creating the container, add four storage mappings. **Select the NAS folder on the left; enter the container path exactly on the right.**

**Synology** (Docker shared folder on volume 1):

| NAS folder — left side | Container path — right side | Access |
| --- | --- | --- |
| `/volume1/docker/zotero-pdf2zh-next/auth` | `/app/gateway/state` | Read/write |
| `/volume1/docker/zotero-pdf2zh-next/config` | `/app/server/config` | Read/write |
| `/volume1/docker/zotero-pdf2zh-next/translated` | `/app/server/translated` | Read/write |
| `/volume1/docker/zotero-pdf2zh-next/cache` | `/home/app/.cache` | Read/write |

**fnOS** (example Docker folder):

| NAS folder — left side | Container path — right side | Access |
| --- | --- | --- |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/auth` | `/app/gateway/state` | Read/write |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/config` | `/app/server/config` | Read/write |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/translated` | `/app/server/translated` | Read/write |
| `/vol1/1000/Docker/Zotero-PDF2zh-Next/cache` | `/home/app/.cache` | Read/write |

Your NAS paths may differ by volume and account. Find the full path in folder properties or use the folder picker. **Only change the left side; keep the right side exactly as shown.**

**Set permissions once before starting.** The container writes as user/group `10001:10001`; NAS-created folders usually belong to another user. This graphical method therefore still requires one terminal operation. Choose Method 2 to avoid managing folder permissions yourself.

Open the NAS system terminal. If unavailable, enable SSH in NAS settings and run `ssh your-nas-user@your-nas-ip` from your computer. Run the following on the **NAS**, not inside the container. For Synology, replace the first line with `PDF2ZH_STORAGE=/volume1/docker/zotero-pdf2zh-next`. For fnOS, use the line below. If your actual folder differs, change only the path after `=`. Paste all four lines:

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
| Image | `wangtengzhou/zotero-pdf2zh-next:0.1.3` |
| Container name | `zotero-pdf2zh-next` |
| Network | Default bridge |
| Port | Host `8890` to container `8890`, TCP |
| Bind address, if shown | `0.0.0.0` for LAN access |
| Restart policy | Automatic restart / `unless-stopped` |
| User and startup command | Keep image defaults |
| Privileged mode | Disabled |

On the storage page, click **Add** four times and fill in the Synology or fnOS mapping table above. Set all four rows to read/write. Do not mount over `/app` or the entire `/app/server`, and do not publish port `8891`.

**Do not add environment variables; keep the defaults. No reverse proxy domain is needed.** The following table is only for later customization:

| Variable | Default | Purpose |
| --- | --- | --- |
| `MAX_UPLOAD_MB` | `100` | Request body limit, including Base64 expansion |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` | Upstream timeout in seconds |
| `TZ` | `Asia/Shanghai` | Time zone |
| `PUBLIC_BASE_URL` | Empty, optional | URL display preference for admin commands; no domain binding |

Configuration templates are restored automatically; existing active settings are passed to upstream migration. An empty cache folder hides preloaded image resources, which may need to be downloaded again during translation.

### 4. Retrieve the Address

Starting with `0.1.3`, successful startup prints “安全入口 / Access entry” in the container log. Copy the `/access/…` path from that line. Each restart prints it again. After resetting a token, use the command to retrieve the current entry rather than copying an older log entry. See [access management](../PUBLIC_ACCESS.en.md).

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

### 1. Paste One Block to Install and Start

Run this in the **NAS/server terminal**, not your computer's local shell or the container console. Docker Compose v2 is required. On Synology/fnOS, install and start the Docker application first. This is for a new installation; use the upgrade instructions if the container already exists.

**Paste the entire block without changing domains, paths or variables.** It creates `zotero-pdf2zh-next` in your login user's home directory, writes the deployment file, pulls the image, creates four persistent volumes and starts the service. Wait for the approximately 843 MB download. If asked for a password, enter your NAS login password; hidden password input is normal.

```bash
(
set -e
mkdir -p "$HOME/zotero-pdf2zh-next"
cd "$HOME/zotero-pdf2zh-next"
if [ -e compose.yaml ] || [ -e .env ]; then
  echo '已有部署文件，请使用升级步骤 / Existing deployment: use upgrade instructions.'
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
      - "${BIND_ADDRESS:-0.0.0.0}:8890:8890"
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

When the final command prints `/access/…`, continue below. If `--wait` is unsupported, update Docker Compose v2. If startup times out or exits, run `sudo docker logs --tail 80 zotero-pdf2zh-next` in the NAS terminal.

**No manual folder mapping is required.** Docker manages four persistent volumes that survive container replacement. Deployment files are in `~/zotero-pdf2zh-next`. Keep that folder name and do not delete the volumes.

### 2. Enter the Address in Zotero

Append the complete `/access/…` output to `http://YOUR-NAS-IP:8890`. Enter that URL in **Python Server IP**, select **pdf2zh_next**, and configure your provider, model and API key. See the example below.

### Offline Compose Import

If Docker Hub downloads fail, use this alternative. Download `zotero-pdf2zh-next-0.1.3-linux-amd64.tar.gz` from the [0.1.3 release](https://github.com/Wangtengzhou/zotero-pdf2zh-next/releases/tag/v0.1.3) and upload it to a NAS folder. In the NAS terminal, type `cd ` followed by that folder's full path and press Enter. Then run:

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
      - "${BIND_ADDRESS:-0.0.0.0}:8890:8890"
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

This also resumes an online installation that failed while pulling the image. Once the image archive is uploaded, these steps need no network connection: the commands generate the deployment file directly. Actual translation still needs access to your chosen provider and may download missing cached resources.

## Lucky and Zotero

### Connect Zotero: Confirm LAN Access First

If the NAS IP is `192.168.1.10` and the command prints `/access/abc123`, enter `http://192.168.1.10:8890/access/abc123` in **Python Server IP**. Replace `abc123` with your full real token. Do not add a trailing slash. Select **pdf2zh_next**, configure your provider, model and API key, then translate a short PDF and confirm the translated attachment appears. Opening the bare server address in a browser is not a deployment check.

### Public Access: Fill in Lucky

With a working domain and HTTPS certificate, create or edit a reverse proxy rule:

| Setting | Value |
| --- | --- |
| Frontend domain | Your domain, e.g. `pdf.example.com` |
| Frontend protocol | HTTPS with that domain's certificate |
| Backend: native Lucky on the same server | `http://127.0.0.1:8890` |
| Backend: Lucky in a container or on another device | `http://YOUR-NAS-IP:8890`, e.g. `http://192.168.1.10:8890` |
| Path rewriting | Disabled; preserve the full original path |
| Additional login | Disabled; the token URL provides authentication |

Save the rule, then enter `https://YOUR-DOMAIN/access/YOUR-FULL-TOKEN` in Zotero. Multiple domains can share one token without changing container variables. Expose the HTTPS proxy publicly; do not forward port `8890` directly from your router to the internet.

Native Lucky on the same host proxies its HTTPS domain to `http://127.0.0.1:8890`, preserving the full path and query string. Disable additional login redirects and business-response caching. Match upload limits to `MAX_UPLOAD_MB` and timeouts to `UPSTREAM_TIMEOUT_SECONDS`; preserve SSE streaming and disable or redact access logs containing tokens.

If Lucky runs in a container, its loopback address does not reach the PDF2zh container. Connect both to a controlled shared Docker network and use `http://pdf2zh:8890` (the Compose service name), or use a reachable host LAN address. Configure the shared network persistently for both containers.

Multiple proxy domains can use the same token without changing the container. Enter the complete token URL in the Zotero plugin's **Python Server IP**, without a trailing slash. Select **pdf2zh_next** and configure the translation provider, model and API key separately. Check upload, progress, download and attachment import with a short PDF.

## Tokens and Upgrades

### Restarts and Cache

Retain the same `cache` folder or volume to reuse downloaded models and fonts that pass validation. Ordinary restarts do not clear it. Keep that mount when replacing the image too. New versions may require different resources; missing or damaged files must be downloaded again. Cached resources do not remove the need for network access to your LLM provider.

### Retrieve or Reset the Entry

Run in the container console:

```bash
pdf2zh-admin url show
pdf2zh-admin url show --base-url https://pdf.example.com
pdf2zh-admin token show
pdf2zh-admin token reset
```

Use the default `app` user. If the graphical console forces root, run `docker exec zotero-pdf2zh-next pdf2zh-admin token reset` from the NAS terminal to avoid creating token files unreadable by the service user. See [token management](../PUBLIC_ACCESS.en.md).

### Upgrade the Image and Keep Your Data

In the fnOS interface: stop the old container, pull or import the new image, reset the old container, then start it. During reset, confirm the target image version and retain the ports, environment variables and all four folder mappings. Do not delete the host folders. If the image tag still shows the old version, change it first; restarting alone does not switch versions.

The upstream PDF2zh server, PDFMathTranslate Next and this container have separate version numbers. When upstream publishes an update, this project's maintainer updates the pinned versions and dependencies, checks compatibility, and publishes a new image through GitHub Actions. There is currently no scheduled workflow that automatically follows upstream releases.

NAS users update this project's image. Do not run `pip install -U`, `git pull` or upstream self-update commands inside the container: those changes bypass compatibility checks and do not survive container recreation.

1. Finish active translations and back up `auth`, `config`, `translated` and `cache`.
2. Check this project's Release for the new image version and changes. In the graphical manager, download/import the new image and use the original container's update/recreate function. Select the new version, retain the port and all four mappings, and do not select any delete-data option.
3. Wait for healthy status, test the existing entry and translate a short PDF. Keeping the `auth` mount preserves the token; Lucky needs no reconfiguration.
4. Compose users can follow the commands below. If installed elsewhere, replace the first line with the original directory containing `compose.yaml`. Keep the original Compose project and volumes.

If installed with this guide's Compose commands, open `~/zotero-pdf2zh-next/.env` in a text editor, replace `0.1.3` at the end of the first line with the desired published version, and save. Run on the NAS:

```bash
cd "$HOME/zotero-pdf2zh-next"
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
```

To resume a first online installation after fixing a network failure, run the same three lines without changing the version. For offline upgrades, import the new image first, then replace the two Docker commands with `sudo docker compose up -d --pull never --wait --wait-timeout 180`.

To roll back, select the old version and restore its configuration backup if the format changed. Restarting clears in-memory task history but preserves PDFs. Do not run `docker compose down -v` or select an option that deletes volumes.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Token directory is unwritable | Check read-write mounts and UID 10001 access to folders and existing files; fix permissions before changing the token |
| `0.1.0` reports missing configuration and templates | Use `0.1.3`, which restores templates automatically |
| Lucky returns 502 | Check the backend address and health; container loopback points to that container itself |
| Large PDF upload fails | Check gateway and proxy limits; Base64 increases size by roughly one third |
| Translation fails or times out | Check provider credentials, model, network and timeouts; redact credentials before sharing logs |
| Image is about 843 MB | It includes translation dependencies, Linux libraries, fonts and models; see the release's `IMAGE_INFO.txt` |

If the container exits, inspect mounts from the NAS terminal without exposing the token:

```bash
docker inspect zotero-pdf2zh-next --format 'User={{.Config.User}}{{range .Mounts}}{{println}}{{.Source}} -> {{.Destination}} RW={{.RW}}{{end}}'
docker logs --since=1m zotero-pdf2zh-next
```
