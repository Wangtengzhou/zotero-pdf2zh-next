# Third-Party Notices

This container combines the original Zotero PDF2zh server and official PDFMathTranslate Next engine with an authentication proxy. It is not the NightWatcher314 fork.

| Component | Version | Source | License |
| --- | --- | --- | --- |
| Zotero PDF2zh server | 4.1.7 | https://github.com/guaguastandup/zotero-pdf2zh/tree/v4.1.7 | AGPL-3.0 |
| PDFMathTranslate Next | 2.9.0 | https://github.com/PDFMathTranslate/PDFMathTranslate-next | AGPL-3.0 |
| BabelDOC | 0.6.2 | https://github.com/funstory-ai/BabelDOC | AGPL-3.0 |

The server archive is verified against the hash in versions.json. Its license is retained at /app/server/LICENSE. Python distribution metadata and notices remain installed alongside dependencies. BabelDOC downloads its official font and model assets during warmup; their upstream notices remain applicable.

The upstream server source is unchanged. scripts/run_upstream.py disables startup notice fetching in memory so the container starts without contacting the upstream notice servers. Updates are performed by replacing images.

Source for this wrapper must remain available at the repository indicated by the image's org.opencontainers.image.source label, at the indicated revision. This repository includes the build recipe, complete dependency lock, upstream source locations, and wrapper source. Set SOURCE_URL to the actual repository when publishing your own image.

The original authentication wrapper and build files retain the repository owner's MIT license; see LICENSE. Upstream components retain their AGPL licenses; the full AGPL text is included in LICENSES/AGPL-3.0.txt. MIT licensing of these wrapper files does not replace upstream licensing or source availability obligations for the combined distribution.
