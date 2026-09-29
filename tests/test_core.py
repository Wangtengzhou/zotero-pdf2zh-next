import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import httpx
from starlette.testclient import TestClient

from gateway import tokens
from gateway.app import create_app
from scripts.config_bootstrap import TEMPLATES, seed_config_templates


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_config_templates_on_empty_mount_preserve_active_config(self):
        defaults = self.directory / "defaults"
        target = self.directory / "mounted-config"
        defaults.mkdir()
        for name in TEMPLATES:
            (defaults / name).write_text("image defaults")
        seed_config_templates(defaults, target)
        self.assertEqual(sorted(path.name for path in target.iterdir()), sorted(TEMPLATES))
        active = target / "config.json"
        active.write_text('{"user_setting": "preserve"}')
        (target / "config.json.example").write_text("old template")
        seed_config_templates(defaults, target)
        self.assertEqual(active.read_text(), '{"user_setting": "preserve"}')
        self.assertEqual((target / "config.json.example").read_text(), "image defaults")

    def test_token_persistence_reset_and_corruption(self):
        original = tokens.initialize(self.directory)
        self.assertEqual(tokens.initialize(self.directory), original)
        replacement = tokens.reset(self.directory)
        self.assertNotEqual(original, replacement)
        self.assertEqual(tokens.current(self.directory), replacement)
        self.assertEqual((self.directory / "auth.json").stat().st_mode & 0o777, 0o600)
        (self.directory / "auth.json").write_text("broken")
        with self.assertRaises(ValueError):
            tokens.initialize(self.directory)

    def test_auth_forwarding_and_live_reset(self):
        seen = []

        def upstream(request):
            seen.append((request.method, str(request.url), request.content))
            if request.url.path == "/events":
                return httpx.Response(200, stream=httpx.ByteStream(b"data: progress\n\n"), headers={"content-type": "text/event-stream"})
            return httpx.Response(200, stream=httpx.ByteStream(b"PDF-result"), headers={"content-type": "application/pdf"})

        app = create_app(self.directory, transport=httpx.MockTransport(upstream))
        with TestClient(app) as client:
            token = tokens.current(self.directory)
            base = f"/access/{token}"
            self.assertEqual(client.get("/health").status_code, 401)
            self.assertEqual(client.get("/access/incorrect/health").status_code, 401)
            self.assertEqual(seen, [])
            result = client.post(f"{base}/translate?mode=test", json={"fileName": "paper.pdf"})
            self.assertEqual(result.content, b"PDF-result")
            self.assertEqual(seen[0][1], "http://127.0.0.1:8891/translate?mode=test")
            self.assertEqual(json.loads(seen[0][2])["fileName"], "paper.pdf")
            self.assertEqual(client.get(f"{base}/translatedFile/paper.pdf").content, b"PDF-result")
            self.assertEqual(client.get(f"{base}/events").content, b"data: progress\n\n")
            self.assertEqual(client.get(f"{base}/api%2Fconfig").status_code, 400)
            replacement = tokens.reset(self.directory)
            self.assertEqual(client.get(f"{base}/health").status_code, 401)
            self.assertEqual(client.get(f"/access/{replacement}/health").status_code, 200)

    def test_terminal_show_url_and_reset(self):
        original = tokens.initialize(self.directory)
        env = dict(os.environ, GATEWAY_STATE_DIR=str(self.directory), PUBLIC_BASE_URL="https://pdf.example.com")

        def run(*args):
            return subprocess.check_output([sys.executable, "-m", "gateway.admin", *args], env=env, text=True).strip()

        self.assertEqual(run("token", "show"), original)
        self.assertEqual(run("url", "show"), f"https://pdf.example.com/access/{original}")
        result = run("token", "reset")
        replacement = tokens.current(self.directory)
        self.assertNotEqual(original, replacement)
        self.assertIn(f"https://pdf.example.com/access/{replacement}", result)

    def test_upload_limit_and_upstream_error(self):
        os.environ["MAX_UPLOAD_MB"] = "1"
        try:
            def upstream(request):
                return httpx.Response(422, stream=httpx.ByteStream(b"invalid PDF"))

            with TestClient(create_app(self.directory, transport=httpx.MockTransport(upstream))) as client:
                base = f"/access/{tokens.current(self.directory)}"
                self.assertEqual(client.post(f"{base}/translate", content=b"x" * (1024 * 1024 + 1)).status_code, 413)
                response = client.post(f"{base}/translate", content=b"bad")
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.content, b"invalid PDF")
        finally:
            os.environ.pop("MAX_UPLOAD_MB", None)


if __name__ == "__main__":
    unittest.main()
