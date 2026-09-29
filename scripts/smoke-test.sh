#!/usr/bin/env bash
set -euo pipefail
image="${1:?Usage: smoke-test.sh IMAGE}"
container="pdf2zh-smoke-${RANDOM}"
state="pdf2zh-smoke-auth-${RANDOM}"

cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
  docker volume rm "$state" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker run -d --name "$container" --mount "type=volume,src=$state,dst=/app/gateway/state" \
  -e PUBLIC_BASE_URL=https://pdf.example.com "$image" >/dev/null

ready=false
for ((attempt=0; attempt<60; attempt++)); do
  if docker exec "$container" python /app/scripts/healthcheck.py >/dev/null 2>&1; then
    ready=true
    break
  fi
  if [[ "$(docker inspect --format '{{.State.Running}}' "$container")" != true ]]; then
    break
  fi
  sleep 2
done
if [[ "$ready" != true ]]; then
  docker logs "$container"
  exit 1
fi

docker exec -i "$container" python - <<'PY'
import importlib.metadata as metadata
import json
import subprocess
import urllib.error
import urllib.request
from gateway import tokens

def status(path):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8890' + path, timeout=10) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, b''

original = tokens.current()
assert status('/health')[0] == 401
code, body = status('/access/' + original + '/health')
assert code == 200 and json.loads(body)['version'] == '4.1.7'
assert metadata.version('pdf2zh-next') == '2.9.0'
assert metadata.version('babeldoc') == '0.6.2'
subprocess.run(['pdf2zh_next', '--help'], check=True, stdout=subprocess.DEVNULL)
assert subprocess.check_output(['pdf2zh-admin', 'token', 'show'], text=True).strip() == original
assert subprocess.check_output(['pdf2zh-admin', 'url', 'show'], text=True).strip() == tokens.public_url(original)
subprocess.run(['pdf2zh-admin', 'token', 'reset'], check=True, stdout=subprocess.DEVNULL)
replacement = tokens.current()
assert replacement != original
assert status('/access/' + original + '/health')[0] == 401
assert status('/access/' + replacement + '/health')[0] == 200
print('Container startup, upstream version, auth, CLI and live reset passed')
PY

# Preserve the token volume while replacing the container.
docker rm -f "$container" >/dev/null
docker run --rm --mount "type=volume,src=$state,dst=/app/gateway/state" "$image" \
  python -c 'from gateway.tokens import current, initialize; assert current() == initialize(); print("Token persistence passed")'
