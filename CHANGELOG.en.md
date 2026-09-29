# Changelog

[简体中文](CHANGELOG.md) | **English**

## Unreleased

- Provide paired Chinese and English pages for all documentation.
- Consolidate deployment into Synology / fnOS graphical deployment and Docker Compose, each with online and offline paths.
- Publish version tags only going forward; remove commit tags and latest promotion.

## 0.1.2 - 2026-09-29

### Fixes

- Restore managed templates for empty host-folder mounts while preserving active configuration.
- Make PUBLIC_BASE_URL optional, with one reusable token path for LAN and public access and no domain binding.
- Add --base-url to URL display and reset commands for a chosen HTTP(S) address.
- Distinguish token-directory permission errors from invalid token content.

### Checks

- Five core checks cover empty folders, preserved settings, unset domains and multiple displayed addresses.
- Container checks cover named-volume persistence and startup with four empty host folders and no domain variable.

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

### Checks

- Four core checks cover authentication, forwarding, admin commands, persistence and errors.
- Real translation and Zotero attachment import require deployment acceptance; CI does not call paid APIs.
