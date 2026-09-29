# Changelog

[简体中文](CHANGELOG.md) | **English**

## 0.1.3 - 2026-09-29

- Print the current access entry once per startup after the authenticated health check succeeds; document retrieval, reset, cache reuse and image upgrades.
- Add complete Synology/fnOS folder mapping tables and copy-and-run online/offline Compose installation blocks.
- Require Chinese and English changelog entries before new releases and generate bilingual Release notes.
- Provide paired Chinese and English pages for all documentation.
- Publish version tags only going forward; remove commit tags and latest promotion.

## 0.1.2 - 2026-09-29

### Fixes

- Restore managed templates for empty host-folder mounts while preserving active configuration.
- Make PUBLIC_BASE_URL optional, with one reusable token path for LAN and public access and no domain binding.
- Add --base-url to URL display and reset commands for a chosen HTTP(S) address.
- Distinguish token-directory permission errors from invalid token content.


## 0.1.1 - 2026-09-29

Publication was canceled before image upload; the fixes are included in 0.1.2.

- Fix template initialization with empty configuration mounts.
- Improve token-storage diagnostics and add initialization checks.

## 0.1.0 - 2026-09-29

### Features

- Package original server 4.1.7, Next 2.9.0 and BabelDOC 0.6.2 for Linux amd64.
- Add persistent random-token authentication compatible with Lucky HTTPS proxies.
- Provide URL and token retrieval plus live token reset.
- Persist configuration, PDFs, tokens and resource caches.
- Build, check and publish images with GitHub Actions. The initial policy included version and commit tags with separate latest promotion, later replaced by version tags only.
