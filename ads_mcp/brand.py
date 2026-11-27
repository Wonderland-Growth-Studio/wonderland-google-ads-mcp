"""Wonderland's icon for this server: the W on the Google Ads blue tile.

One of a family: each Wonderland MCP server has its own colour and badge, so
they are told apart in Claude's connector list. Served without auth, because a
client draws the connector before it holds any credential.
"""

from importlib import resources

from mcp import types
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

ICON_PATH = "/brand/icon-512.png"

FILES = {
    "/favicon.ico": ("favicon.ico", "image/x-icon"),
    ICON_PATH: ("icon-512.png", "image/png"),
    "/brand/icon-192.png": ("icon-192.png", "image/png"),
    "/apple-touch-icon.png": ("icon-180.png", "image/png"),
}


# The page at "/". Claude shows a custom connector with the favicon Google has indexed for
# its URL, not the serverInfo icon; with no page here Google falls back to the parent
# domain's favicon, and every Wonderland connector looks the same. This page gives Google a
# <link rel="icon"> to index for this host.
HOME_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wonderland Google Ads · Wonderland</title>
<meta name="description" content="Wonderland's Google Ads MCP server for Claude.">
<link rel="icon" type="image/png" sizes="512x512" href="/brand/icon-512.png">
<link rel="icon" type="image/png" sizes="192x192" href="/brand/icon-192.png">
<link rel="shortcut icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:32rem;margin:15vh auto;padding:0 1rem;color:#1a1a1a}img{width:64px;height:64px;border-radius:14px}</style>
</head>
<body>
<img src="/brand/icon-512.png" alt="">
<h1>Wonderland Google Ads</h1>
<p>A Wonderland MCP server. Add it in Claude as a custom connector at <code>/mcp</code>.</p>
</body>
</html>
"""


def read(name: str) -> bytes:
    return resources.files("ads_mcp").joinpath("brand", name).read_bytes()


def server_icons(base_url: str) -> list[types.Icon]:
    """The serverInfo icons entry. Absolute: clients resolve it outside any page."""
    return [
        types.Icon(
            src=f"{base_url.rstrip('/')}{ICON_PATH}",
            mime_type="image/png",
            sizes=["512x512"],
        )
    ]


def register(server) -> None:
    """Adds the public icon routes to a FastMCP server. Files are read once."""
    for path, (name, media_type) in FILES.items():
        body = read(name)

        async def serve(_: Request, body=body, media_type=media_type) -> Response:
            return Response(
                body,
                media_type=media_type,
                headers={"Cache-Control": "public, max-age=86400"},
            )

        server.custom_route(path, methods=["GET", "HEAD"])(serve)

    async def home(_: Request) -> Response:
        return HTMLResponse(HOME_HTML, headers={"Cache-Control": "public, max-age=3600"})

    server.custom_route("/", methods=["GET", "HEAD"])(home)
