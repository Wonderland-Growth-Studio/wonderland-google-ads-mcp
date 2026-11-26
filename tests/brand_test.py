"""The Wonderland icon: public routes, and serverInfo pointing at the base URL."""

import importlib
import os
import unittest
from unittest import mock

from starlette.testclient import TestClient

BASE = "https://google-ads.mcp.wonderland.marketing"


class BrandTest(unittest.TestCase):
    def setUp(self):
        env = {
            "GOOGLE_ADS_MCP_OAUTH_CLIENT_ID": "test-id",
            "GOOGLE_ADS_MCP_OAUTH_CLIENT_SECRET": "test-secret",
            "GOOGLE_ADS_MCP_BASE_URL": BASE,
            "GOOGLE_ADS_MCP_JWT_SIGNING_KEY": "x" * 32,
        }
        self._env = mock.patch.dict(os.environ, env)
        self._env.start()
        import ads_mcp.coordinator as coordinator

        self.coordinator = importlib.reload(coordinator)

    def tearDown(self):
        self._env.stop()
        # Rebuild the module-level server under the original environment, so
        # tests that run after this one see the server they expect.
        importlib.reload(self.coordinator)

    def test_server_info_icon_uses_base_url(self):
        icons = self.coordinator.mcp.icons
        self.assertEqual(str(icons[0].src), f"{BASE}/brand/icon-512.png")
        self.assertEqual(icons[0].sizes, ["512x512"])

    def test_icons_served_without_auth(self):
        app = self.coordinator.mcp.http_app(transport="streamable-http")
        with TestClient(app) as c:
            for path, media in [
                ("/favicon.ico", "image/x-icon"),
                ("/brand/icon-512.png", "image/png"),
                ("/apple-touch-icon.png", "image/png"),
            ]:
                r = c.get(path)
                self.assertEqual(r.status_code, 200, path)
                self.assertEqual(r.headers["content-type"], media)
                self.assertGreater(len(r.content), 100)
            self.assertEqual(c.post("/mcp", json={}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
