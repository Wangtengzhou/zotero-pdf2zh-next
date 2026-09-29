import json
import os
import re
import sys
import urllib.error
import urllib.request


def request(path, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = json.dumps(data).encode() if data is not None else None
    with urllib.request.urlopen(urllib.request.Request(
        "https://hub.docker.com" + path, data=payload, headers=headers, method=method,
    ), timeout=30) as response:
        body = response.read()
        return json.loads(body) if body else None


def main():
    image = os.environ["DOCKERHUB_IMAGE"]
    if not re.fullmatch(r"[a-z0-9_-]+/[a-z0-9._-]+", image):
        raise ValueError("Invalid Docker Hub repository")
    path = f"/v2/repositories/{image}/tags/"
    before = request(path + "?page_size=100")
    if before.get("next"):
        raise ValueError("More than 100 tags; inspect pagination before cleanup")
    versions = {item["name"]: item["digest"] for item in before["results"]
                if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", item["name"])}
    aliases = [item for item in before["results"] if re.fullmatch(r"sha-[0-9a-f]{40}", item["name"])]
    for item in aliases:
        if item["digest"] not in versions.values():
            raise ValueError("SHA tag has no matching version tag; refusing deletion")
    if aliases:
        token = request("/v2/auth/token", method="POST", data={
            "identifier": os.environ["DOCKERHUB_USERNAME"],
            "secret": os.environ["DOCKERHUB_TOKEN"],
        })["access_token"]
        for item in aliases:
            # Delete the tag reference through Hub, never the shared registry manifest.
            request(path + item["name"] + "/", method="DELETE", token=token)
            print(f"Removed {image}:{item['name']}")
    after = request(path + "?page_size=100")
    remaining = {item["name"]: item["digest"] for item in after["results"]}
    if any(remaining.get(name) != digest for name, digest in versions.items()):
        raise ValueError("Version tag verification failed")
    if any(name.startswith("sha-") for name in remaining):
        raise ValueError("SHA tags still present")
    print("Version tags preserved: " + ", ".join(sorted(versions)))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        print(f"Docker Hub request failed: HTTP {error.code}. Tag removal requires delete permission.", file=sys.stderr)
        sys.exit(1)
