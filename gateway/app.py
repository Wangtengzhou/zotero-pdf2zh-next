import asyncio
import os
import re
import secrets
from contextlib import asynccontextmanager

import httpx
from starlette.applications import Starlette
from starlette.requests import ClientDisconnect, Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from gateway import tokens

HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
               "te", "trailer", "transfer-encoding", "upgrade"}


def filtered_headers(headers):
    blocked = HOP_HEADERS | {part.strip().lower() for part in headers.get("connection", "").split(",")}
    return {key: value for key, value in headers.items() if key.lower() not in blocked}


def error(status, message):
    return JSONResponse({"status": "error", "message": message}, status_code=status,
                        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})


def create_app(directory=None, transport=None):
    directory = directory or tokens.state_dir()
    max_body = int(os.environ.get("MAX_UPLOAD_MB", "100")) * 1024 * 1024
    if max_body <= 0:
        raise ValueError("MAX_UPLOAD_MB must be positive")

    @asynccontextmanager
    async def lifespan(app):
        tokens.initialize(directory)
        timeout = httpx.Timeout(float(os.environ.get("UPSTREAM_TIMEOUT_SECONDS", "3600")), connect=10)
        async with httpx.AsyncClient(transport=transport, timeout=timeout, trust_env=False,
                                    follow_redirects=False) as client:
            app.state.client = client
            yield

    async def live(request):
        return JSONResponse({"status": "ok"}, headers={"Cache-Control": "no-store"})

    async def proxy(request: Request):
        raw_path = request.scope.get("raw_path", b"").split(b"?", 1)[0]
        parts = raw_path.split(b"/", 3)
        if len(parts) != 4 or parts[1] != b"access" or not re.fullmatch(rb"[A-Za-z0-9_-]{43}", parts[2]):
            return error(401, "Unauthorized")
        try:
            token = await asyncio.to_thread(tokens.current, directory)
        except (OSError, ValueError, KeyError):
            return error(503, "Authentication unavailable")
        if not secrets.compare_digest(parts[2], token.encode("ascii")):
            return error(401, "Unauthorized")

        decoded = request.url.path.split("/", 3)[-1]
        if (not parts[3] or "\\" in decoded
                or any(segment in ("", ".", "..") for segment in decoded.split("/"))):
            return error(400, "Invalid API path")
        if re.search(rb"%(?:2f|5c)", parts[3], re.IGNORECASE):
            return error(400, "Invalid API path")

        try:
            if int(request.headers.get("content-length", "0")) > max_body:
                return error(413, "Upload too large")
        except ValueError:
            return error(400, "Invalid content length")
        body = bytearray()
        try:
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > max_body:
                    return error(413, "Upload too large")
        except ClientDisconnect:
            return error(400, "Client disconnected")

        raw_target = b"/" + parts[3]
        if request.scope.get("query_string"):
            raw_target += b"?" + request.scope["query_string"]
        target = httpx.URL("http://127.0.0.1:8891").copy_with(raw_path=raw_target)
        headers = filtered_headers(request.headers)
        for key in ("host", "authorization", "cookie", "forwarded", "x-forwarded-for", "x-forwarded-host", "x-forwarded-proto"):
            headers.pop(key, None)
        headers["accept-encoding"] = "identity"
        # Never retry a translation submission after an uncertain upstream result.
        try:
            outgoing = request.app.state.client.build_request(request.method, target, headers=headers, content=bytes(body))
            upstream = await request.app.state.client.send(outgoing, stream=True)
        except httpx.TimeoutException:
            return error(504, "Upstream timeout; check task status before submitting again")
        except httpx.HTTPError:
            return error(502, "Upstream unavailable")

        response_headers = filtered_headers(upstream.headers)
        response_headers.update({"cache-control": "no-store", "referrer-policy": "no-referrer",
                                 "x-content-type-options": "nosniff"})
        if upstream.is_redirect:
            await upstream.aclose()
            return error(502, "Unexpected upstream redirect")
        async def stream():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            finally:
                await upstream.aclose()

        return StreamingResponse(stream(), status_code=upstream.status_code, headers=response_headers)

    return Starlette(lifespan=lifespan, routes=[
        Route("/_gateway/live", live, methods=["GET"]),
        Route("/{path:path}", proxy, methods=["GET", "POST", "HEAD", "PUT", "PATCH", "DELETE", "OPTIONS"]),
    ])


app = create_app()
