# Changelog

## 0.1.2 - 2026-09-29

### Fixes

- Initialize managed configuration templates for empty host-folder mounts while preserving active user configuration.
- Make PUBLIC_BASE_URL optional. Use a reusable token path for both LAN and public access, with no domain binding.
- Add --base-url to URL display and token reset commands to generate a full HTTP(S) URL for any chosen address without recreating the container.
- Improve token storage diagnostics to distinguish mount permission failures from invalid token content.

### Validation

- Five focused core tests include empty-config initialization, active-config preservation, and URL display with no configured domain or multiple addresses.
- Container checks cover both named-volume persistence and startup with four empty host-folder mounts without a domain environment variable.

## 0.1.1 - 2026-09-29

Publication canceled before uploading images; the fixes are included in 0.1.2.

### Fixes

- Restore managed configuration templates from an image directory outside the config mount before starting the upstream server. Empty host-folder mounts now initialize correctly, while active user configuration is preserved for upstream migration.
- Distinguish token storage permission errors from invalid token content in startup diagnostics, including the service UID/GID and mount repair guidance.

### Validation

- Add a focused regression check for empty configuration directories and preservation of existing active configuration.
- Check real container startup with all four storage paths mounted as empty host folders, in addition to named-volume token persistence.

## 0.1.0 - 2026-09-29

### Features

- Package the original Zotero PDF2zh server 4.1.7 with official PDFMathTranslate Next 2.9.0 and BabelDOC 0.6.2 for Linux amd64.
- Add automatic authentication through a persistent random token in the server URL, compatible with Lucky HTTPS reverse proxy.
- Provide terminal commands to view the token, display the Zotero URL, and reset credentials without restarting the container.
- Persist configuration, PDFs, token state, and translation resource caches.
- Build and check images with GitHub Actions, publish version tags to Docker Hub, and promote accepted digests to latest without rebuilding.

### Validation

- Four focused core tests cover token persistence, CLI management, authentication, forwarding, upload limits, and upstream error responses.
- Real Zotero translation and attachment import require deployment acceptance; CI does not call a paid translation API.
