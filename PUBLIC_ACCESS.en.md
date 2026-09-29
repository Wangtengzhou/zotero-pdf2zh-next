# Access and Token Management

[简体中文](PUBLIC_ACCESS.md) | **English**

## Address Rules

Both LAN and public access use `/access/<token>`. The plugin appends connection-check, upload, polling and download paths to the complete address. The gateway validates each request independently of client IP or browser login.

```text
http://192.168.1.10:8890/access/<token>
https://pdf.example.com/access/<token>
```

The proxy must preserve the full path and query string. After validation, the gateway strips the token prefix and forwards to the internal server. All business endpoints are protected. Multiple domains can use the same token.

## Get Your Entry for the First Time

Starting with `0.1.3`, open the container logs and wait for “服务已就绪 / Service ready”. The next line shows:

```text
安全入口 / Access entry: /access/YOUR-FULL-TOKEN
```

Append the entire `/access/…` path to `http://YOUR-NAS-IP:8890` or `https://YOUR-PROXY-DOMAIN`. Enter the complete address in Zotero's **Python Server IP**, without `/health` or a trailing slash. Multiple domains can reuse the same path.

The entry is printed once per startup after the authenticated health check succeeds. Restarts reuse the existing token. Optional `PUBLIC_BASE_URL` makes the log show a full URL; it is not required. On `0.1.2` and earlier, use the commands below.

## Retrieve the Current Entry Later

Open the container's terminal, select “New terminal / Execute command”, enter `/bin/sh`, and keep the default `app` user. Run:

```bash
pdf2zh-admin url show
```

From the NAS system terminal or SSH, run instead:

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin url show
```

### Optional: Show Only the Token or a Full URL

Run in the container console as the default `app` user (UID `10001`):

```bash
pdf2zh-admin url show
pdf2zh-admin token show
pdf2zh-admin url show --base-url http://192.168.1.10:8890
pdf2zh-admin url show --base-url https://pdf.example.com
```

From the server terminal, prefix commands with `docker exec zotero-pdf2zh-next`. Without an address setting, `url show` prints a path. `--base-url` selects an address for that command only. `PUBLIC_BASE_URL` is an optional display preference: an HTTP(S) origin and optional port, without a path, token or query. It does not bind the gateway to a domain.

## Reset

Let active translations finish. In the container console, run this to generate and display a new entry:

```bash
pdf2zh-admin token reset
```

From the NAS system terminal or SSH, run instead:

```bash
sudo docker exec zotero-pdf2zh-next pdf2zh-admin token reset
```

No restart is required. The command displays the new path or address. Update Zotero afterward: the old token is rejected for new requests, while previously authorized requests and streams can finish. Add `--base-url https://pdf.example.com` to display a full URL for that domain.

Use `app` for resets inside the container. If the graphical console forces root, use the server-terminal command above to avoid creating files unreadable by the service user. Fix storage permissions first; resetting cannot repair mount permissions.

## Storage and Logs

First startup generates a token at `/app/gateway/state/auth.json`. Restarts, container recreation and upgrades read the existing file. Retaining `auth` storage keeps the address unchanged.

Corrupt, invalid or inaccessible files cause service failure rather than silent credential replacement. Show commands are read-only; reset uses a file lock and atomic replacement.

Startup logs contain the access entry; redact the token before sharing logs. After a reset, historical logs still contain the old entry, so use the show command for the current value. Explicit show and reset commands also print credentials in the terminal.

## Access Boundaries

- The full address is a credential. All holders share business data and configuration; there is no multi-user isolation.
- Use HTTPS publicly, disable or redact token-bearing access logs, and disable business-response caching.
- The plugin may display the address in diagnostics or connection dialogs; redact the token before sharing.
- IP changes do not revoke tokens. Administrators revoke them through reset.
- Show and reset are available only through the server or container terminal, with no public management endpoint.
- Expose gateway port `8890`; do not publish internal upstream `127.0.0.1:8891` to the host.

See the [deployment guide](docs/DEPLOYMENT.en.md) for networking and storage.
