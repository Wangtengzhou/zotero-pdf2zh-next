import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
versions = json.loads((root / "versions.json").read_text())
version = versions["container"]
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    raise SystemExit("Use a numeric container version, e.g. 0.1.0")
if os.environ.get("RELEASE_TAG") != "v" + version:
    raise SystemExit("Release tag must match versions.json")

for filename in ("CHANGELOG.md", "CHANGELOG.en.md"):
    changelog = root / filename
    match = re.search(
        rf"^## {re.escape(version)} - [^\n]+\n(.*?)(?=^## |\Z)",
        changelog.read_text() if changelog.is_file() else "",
        re.MULTILINE | re.DOTALL,
    )
    if not match or not match.group(1).strip():
        raise SystemExit(f"Add release notes for {version} to {filename}")

image = os.environ["DOCKERHUB_IMAGE"]
if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*/[a-z0-9][a-z0-9_.-]*", image):
    raise SystemExit("DOCKERHUB_IMAGE must be a lowercase Docker Hub namespace/repository")

# Query the public registry API. Errors other than a missing tag stop release.
request = urllib.request.Request(f"https://hub.docker.com/v2/repositories/{image}/tags/{version}/")
try:
    with urllib.request.urlopen(request, timeout=30):
        raise SystemExit("This version already exists on Docker Hub; increment versions.json")
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise SystemExit(f"Cannot verify Docker Hub tag availability: HTTP {error.code}") from None
print(f"Ready to publish {image}:{version}")
