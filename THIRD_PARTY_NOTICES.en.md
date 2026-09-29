# Third-Party Notices

[简体中文](THIRD_PARTY_NOTICES.md) | **English**

This image combines the original Zotero PDF2zh server, official PDFMathTranslate Next and an authentication gateway. It is not the NightWatcher314 fork.

| Component | Version | Source | License |
| --- | --- | --- | --- |
| Zotero PDF2zh server | 4.1.7 | [Upstream source](https://github.com/guaguastandup/zotero-pdf2zh/tree/v4.1.7) | AGPL-3.0 |
| PDFMathTranslate Next | 2.9.0 | [Upstream source](https://github.com/PDFMathTranslate/PDFMathTranslate-next) | AGPL-3.0 |
| BabelDOC | 0.6.2 | [Upstream source](https://github.com/funstory-ai/BabelDOC) | AGPL-3.0 |

The server archive is checked against the hash in `versions.json`, and its license remains at `/app/server/LICENSE`. Python distribution metadata and notices stay installed with dependencies. BabelDOC warmup downloads official fonts and models; their upstream notices remain applicable.

The original server source is unchanged. `scripts/run_upstream.py` disables startup notices in memory and restores managed configuration templates before invoking the server. Updates are performed by replacing images.

Wrapper sources must remain available at the repository and revision identified by `org.opencontainers.image.source` and `org.opencontainers.image.revision`. This repository contains the build recipe, complete dependency locks, upstream source locations and wrapper sources. Set `SOURCE_URL` to the actual repository when publishing your own image.

Original authentication and build files use the repository's [MIT License](LICENSE). Upstream components retain their AGPL licenses; the full text is in [LICENSES/AGPL-3.0.txt](LICENSES/AGPL-3.0.txt). MIT licensing of wrapper files does not replace upstream licensing or source-availability obligations for the combined distribution. Original license texts are preserved.
