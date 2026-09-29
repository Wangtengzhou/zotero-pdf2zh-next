# Access and Token Management

[简体中文](PUBLIC_ACCESS.md) | **English**

An access entry combines a server address with a token path. LAN access, public access and multiple proxy domains can use the same `/access/<token>` path, without client IP restrictions or browser login.

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

## First Retrieval

Starting with `0.1.3`, successful startup health checks produce this log line:

```text
安全入口 / Access entry: /access/YOUR-FULL-TOKEN
```

Append the copied path to your NAS address or proxy domain and enter it in Zotero's **Python Server IP**. Do not append `/health` or a trailing `/` to the plugin address.

Every restart prints the current entry and retains the token. On `0.1.2` and earlier, use the commands below.

## Retrieve It Again

Open the container terminal, select “New terminal / Execute command”, enter `/bin/sh`, keep the default `app` user and run:

```bash
pdf2zh-admin url show
```

From the **NAS system terminal / SSH**, use instead:

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

<details>
<summary>Optional: display a full URL or only the token</summary>

Run in the container console, replacing example addresses with your own:

```bash
pdf2zh-admin url show --base-url http://192.168.1.10:8890
pdf2zh-admin url show --base-url https://pdf.example.com
pdf2zh-admin token show
```

`--base-url` affects only that command's output. Optional `PUBLIC_BASE_URL` sets a persistent display preference; it is not required and does not bind proxy domains. Use an HTTP(S) origin and optional port, without paths, credentials or query parameters.

</details>

## Replace the Token

Let active translations finish. In the **container console**, run:

```bash
pdf2zh-admin token reset
```

From the **NAS system terminal / SSH**, use:

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin token reset
```

The new entry appears and takes effect immediately, without restarting. Replace the old path in Zotero. The old token cannot start new requests; previously authorized requests can finish.

Use the default `app` user in the container console. If the interface forces root, use the NAS command above to avoid creating token files unreadable by the service.

## Storage and Sharing

- The token is stored in `/app/gateway/state/auth.json`. Keep the `auth` mount during upgrades and recreation to retain the entry.
- Old logs may retain an obsolete entry after a reset. The show command returns the current value.
- **The full entry is a credential.** Redact tokens before sharing logs or screenshots. All holders share configuration and files; there is no multi-user isolation.
- Use HTTPS publicly, preserve paths and queries through the proxy, and disable or redact token-bearing access logs.
- Repair damaged files or permissions first. The service does not silently replace credentials, and reset cannot fix mount permissions.
- Administration is available through the container/server terminal only, with no public token-management endpoint.

Related: [Deployment](docs/DEPLOYMENT.en.md) · [Upgrades and troubleshooting](docs/OPERATIONS.en.md)
