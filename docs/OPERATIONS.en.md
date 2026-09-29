# Upgrades and Maintenance

[简体中文](OPERATIONS.md) | **English**

For initial setup, see [deployment](DEPLOYMENT.en.md). For token retrieval and reset, see [access management](../PUBLIC_ACCESS.en.md). Run all commands on this page in the **NAS/server terminal**.

## Upgrade the Image

The upstream server, Next engine and this container have separate version numbers. Upstream updates are reviewed for compatibility before a new image is released; running containers do not update automatically. Do not run `pip install -U` or upstream self-update commands inside the container.

### Before Updating

Finish active translations and back up the four storage locations: token `auth`, settings `config`, PDFs `translated`, and resources `cache`.

For graphical deployments, stop the container and copy the four folders. Compose stores data in Docker volumes: **copying compose.yaml and .env alone does not back up your data**. Also save the volumes using your NAS or Docker volume backup process.

### fnOS / Synology

1. Stop the old container and download or import the target image.
2. In fnOS, use **Reset**; in Synology, use the corresponding update/recreate operation. Confirm the target image tag and retain the ports, environment variables and four mappings.
3. Start the container, wait for healthy status, test the existing Zotero address and translate a short PDF.

If the interface cannot change image versions, rename the stopped old container, create a container with its original name from the new image, and map the same four folders. Do not run both containers together.

**Keeping `auth` preserves the token; Lucky needs no changes.** Do not select delete-data options. Restarting alone does not switch images.

### Docker Compose

Open `.env` in the original deployment directory and change the version in `PDF2ZH_IMAGE=`, for example:

```dotenv
PDF2ZH_IMAGE=wangtengzhou/zotero-pdf2zh-next:0.1.3
```

Save and run the following, adjusting the first line if installed elsewhere:

```bash
cd "$HOME/zotero-pdf2zh-next"
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
```

For offline updates, first import the target image with `sudo docker load --input image-file.tar.gz`, then run from the original deployment directory:

```bash
sudo docker compose up -d --pull never --wait --wait-timeout 180
```

Keep the original Compose project name and volumes. Do not run `docker compose down -v`.

### Verify the Version or Roll Back

Check the image tag in container details. The `version` returned by `/health` is the **upstream server version**: image `0.1.3` correctly returns `4.1.7`.

If compatibility issues arise, switch back to the older image. Restore the previous configuration backup too if the new version migrated its format. Restarts clear in-memory tasks but retain saved PDFs.

## Cache and First Translation

The image includes preloaded resources. Docker copies them into newly created named volumes. Binding an empty NAS `cache` folder hides them, so the first translation may download models and fonts again.

Keep the same `cache` mount to reuse valid resources across restarts and image replacements. Different resources required by a new version, or missing/damaged files, need downloading. LLM translation still requires network access.

## Resume an Interrupted Installation

If the command block created deployment files but the image pull failed, restore network access and run:

```bash
cd "$HOME/zotero-pdf2zh-next"
sudo docker compose pull
sudo docker compose up -d --wait --wait-timeout 180
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

If pulling still fails, use the [offline deployment steps](DEPLOYMENT.en.md#method-2-docker-compose). Update Docker Compose v2 if `--wait` is unsupported. If a container name conflicts, inspect the existing installation rather than creating a duplicate.

## Connection Checks

Replace the IP and token below with your values. Use **HTTP on port 8890** over the LAN. The logged `localhost:8891` address is internal to the container.

| Browser URL | Expected result |
| --- | --- |
| `http://NAS-LAN-IP:8890/_gateway/live` | `{"status":"ok"}` confirms the gateway is reachable |
| `http://NAS-LAN-IP:8890/access/FULL-TOKEN/health` | `status: ok` confirms authentication and upstream health |

Bare `/health` returns 401 because it has no token. Sending HTTPS to the HTTP port may produce `Invalid HTTP request`. Zotero's server URL ends at the token, without `/health`.

| Symptom | Check first |
| --- | --- |
| LAN connection refused or timed out | Running container, port 8890 mapping and NAS firewall; binding only 127.0.0.1 prevents access from other devices |
| Lucky returns 502 | Backend address and container health; loopback inside Lucky's container refers to itself |
| Token state is unwritable | Read/write mappings and UID 10001 access to folders and existing files; fix permissions before changing the token |
| 0.1.0 reports missing configuration/templates | Upgrade to 0.1.2 or later |
| Large PDF upload fails | Proxy/gateway body limits; Base64 increases size by about one third |
| Connection works but translation is slow or fails | Selected LLM channel, model, resource downloads, timeouts and rate limits; a connection check does not validate the translation API |

## View and Export Logs

View recent output:

```bash
sudo docker logs --tail 100 zotero-pdf2zh-next
```

Save the last two hours to a file in the current directory:

```bash
sudo docker logs --since 2h --timestamps zotero-pdf2zh-next > pdf2zh-container.log 2>&1
```

**Starting with 0.1.3, startup logs contain the access entry.** Redact the token after `/access/`, API keys and sensitive filenames before sharing. Repeated progress-bar updates can produce many log lines without duplicate tasks.

## Optional Environment Variables

For graphical deployments, add variables in container settings. For Compose, edit `.env` and apply with `docker compose up -d`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `PUBLIC_BASE_URL` | Empty | Full URL display preference for logs/admin commands; does not restrict proxy domains |
| `MAX_UPLOAD_MB` | `100` | Request body limit, including Base64 expansion |
| `UPSTREAM_TIMEOUT_SECONDS` | `3600` | Gateway timeout for upstream requests, distinct from the LLM provider timeout |
| `TZ` | `Asia/Shanghai` | Time zone |
| `HOST_PORT` | `8890` | Compose host port |
| `BIND_ADDRESS` | See below | Compose host listening address |

The deployment command block writes `BIND_ADDRESS=0.0.0.0` for LAN access. Repository and Release `env.example` files default to `127.0.0.1`; change it to the NAS LAN IP or `0.0.0.0` for LAN access. Keep loopback if only native Lucky on the same host needs access.
