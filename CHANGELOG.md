# Changelog

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
