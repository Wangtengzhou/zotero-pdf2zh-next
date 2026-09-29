# Development and Releases

[简体中文](CONTRIBUTING.md) | **English**

## Local Development

Use Python 3.12:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-gateway.lock
.venv/bin/python -m unittest discover -s tests -v
```

Core checks cover token persistence and reset, CLI commands, authentication and forwarding, size limits, upstream errors and empty configuration initialization. They do not call paid translation APIs.

## Build and Check

```bash
docker build --platform linux/amd64 \
  --build-arg SOURCE_URL=https://github.com/Wangtengzhou/zotero-pdf2zh-next \
  -t zotero-pdf2zh-next:local .
bash scripts/smoke-test.sh zotero-pdf2zh-next:local
```

Container checks cover upstream health and versions, Next CLI, authentication, live reset, named-volume persistence, and startup with four empty host folders and no domain variable. Confirm real translation and Zotero import in your deployment environment.

## Update Dependencies and Documentation

After editing `requirements.in`, regenerate the Linux amd64 lock:

```bash
uv pip compile requirements.in \
  --python-version 3.12 \
  --python-platform x86_64-unknown-linux-gnu \
  --generate-hashes -o requirements.lock
```

Gateway development dependencies use `requirements-gateway.in` and `.lock`. For version updates, check `versions.json`, Dockerfile, `pyproject.toml`, smoke-test version assertions, Compose defaults and changelogs together. Recheck source URLs, hashes, protocols and licenses when upstream packages change.

Every documentation page has a Chinese primary file and an English `.en.md` counterpart. Keep content, commands and language links synchronized. Do not rewrite original license texts.

Keep installation and connection steps in the deployment guide, upgrades and troubleshooting in the operations guide, and token management in the access guide. Release notes describe user-facing changes, compatibility and downloads, not task progress or test counts. When editing historical releases, preserve tags and assets.

## Automated Releases

### Maintaining Upstream Updates

An upstream release does not change existing images or running containers. For server updates, update the server version, download URL and SHA256 in `versions.json`. For Next/BabelDOC updates, synchronize version records and dependency constraints and regenerate the lock file. Review configuration migrations and plugin compatibility, update the container version, version assertions and bilingual changelogs, and run core and real-container startup checks. Then publish a new `vX.Y.Z` tag. GitHub Actions builds and uploads the versioned image and offline archive; NAS users replace their image afterward. Never overwrite a published version tag.

`Build, Check and Publish`:

| Trigger | Work performed |
| --- | --- |
| Markdown or license changes only | No workflow run |
| Code pushed to `main` | Core checks |
| Pull Request or manual run | Core checks, image build and container checks; no publishing |
| `v*` tag | Full checks, image publication and offline assets |

When a commit and release tag are pushed together, only the tag run builds the image.

- A `v*` Git tag publishes the same tested image only after checks pass.
- The tag must match the container version in `versions.json`. Existing versions cannot be overwritten; fixes need a new version.
- Docker Hub publishes `:<version>` only, without `sha-…` or `latest`.
- Every new version requires both Chinese and English changelog entries. Release checks require both, and GitHub Release notes include both languages and bilingual offline instructions.
- Source revisions remain in OCI metadata. Digests are used for verification and offline export, not extra tags.
- The workflow then publishes GitHub Release offline images, checksums, deployment files and size information.

Configure a public Docker Hub repository and these GitHub settings:

| Type | Name | Value |
| --- | --- | --- |
| Actions Secret | `DOCKERHUB_USERNAME` | Lowercase Docker Hub username |
| Actions Secret | `DOCKERHUB_TOKEN` | Dedicated write token |
| Optional Actions Variable | `DOCKERHUB_IMAGE` | Defaults to `wangtengzhou/zotero-pdf2zh-next` |

Pull Requests do not use publishing credentials.

## Backfill Offline Assets

Run `Publish Offline Image` manually with an existing Git tag and its `sha256:` image digest. It verifies version, source revision and platform, exports and imports the archive, then uploads it without rebuilding or changing the versioned image.

The workflow uses the built-in GitHub token with `contents: write`. Existing asset names are not overwritten; inspect release state before retrying failures. Large files are stored as release assets, not committed to Git history.

## Feedback

In [GitHub Issues](https://github.com/Wangtengzhou/zotero-pdf2zh-next/issues), include image version, platform, deployment method, Zotero and plugin versions, reproduction steps and logs. Redact tokens, complete token-bearing URLs, API keys and sensitive PDF information first.
