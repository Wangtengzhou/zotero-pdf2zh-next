import json
import urllib.request

from gateway.tokens import current

try:
    with urllib.request.urlopen(f"http://127.0.0.1:8890/access/{current()}/health", timeout=5) as response:
        if json.load(response).get("status") != "ok":
            raise SystemExit(1)
except (OSError, ValueError, KeyError):
    raise SystemExit("Gateway/upstream health check failed") from None
