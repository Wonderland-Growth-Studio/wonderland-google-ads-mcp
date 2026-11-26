"""Wonderland's icon for this server: the W on the Google Ads blue tile.

One of a family: each Wonderland MCP server has its own colour and badge, so
they are told apart in Claude's connector list. Served without auth, because a
client draws the connector before it holds any credential.
"""

from importlib import resources

from mcp import types
from starlette.requests import Request
from starlette.responses import Response

ICON_PATH = "/brand/icon-512.png"

FILES = {
    "/favicon.ico": ("favicon.ico", "image/x-icon"),
    ICON_PATH: ("icon-512.png", "image/png"),
    "/brand/icon-192.png": ("icon-192.png", "image/png"),
    "/apple-touch-icon.png": ("icon-180.png", "image/png"),
}


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
