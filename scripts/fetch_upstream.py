import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    versions = json.loads((root / "versions.json").read_text())
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else root
    with urllib.request.urlopen(versions["server_url"], timeout=120) as response:
        bundle = response.read()
    if hashlib.sha256(bundle).hexdigest() != versions["server_sha256"]:
        raise ValueError("Upstream server archive checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        for name in archive.namelist():
            if not name.startswith("server/") or ".." in Path(name).parts:
                raise ValueError("Unexpected upstream archive path")
        archive.extractall(destination)
    source = (destination / "server/server.py").read_text()
    if f'__version__ = "{versions["server"]}"' not in source:
        raise ValueError("Upstream server version mismatch")
    url = f'https://raw.githubusercontent.com/guaguastandup/zotero-pdf2zh/v{versions["server"]}/LICENSE'
    with urllib.request.urlopen(url, timeout=60) as response:
        (destination / "server/LICENSE").write_bytes(response.read())
    print(f'Verified upstream server {versions["server"]}')


if __name__ == "__main__":
    main()
