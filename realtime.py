"""WebSocket build stream for the Calculemus dashboard.

The transport uses the maintained `websockets` implementation; the Lean process
remains the source of truth and every event is line-oriented and replayable.

## Why this file is guarded the way it is (finding F-01)

`POST /api/build` was locked behind a bearer token AND disabled by default,
because it spawns `lake build`. This module offered the SAME capability with
neither control: any client that could open the socket could send
`{"action": "build"}` and start an unbounded Lean build.

The bind to 127.0.0.1 is not the boundary it looks like. Browsers do not apply
the same-origin policy to WebSocket connections the way they do to `fetch`: a
page on any origin the operator happens to visit can open
`ws://127.0.0.1:8765` and send messages to it. That is cross-site WebSocket
hijacking, and localhost-only binding does nothing against it.

So this module now enforces the same three controls as the HTTP route, plus one
the HTTP route does not need:

1. `LEIBNIZ_ENABLE_BUILD_ENDPOINT=1` -- off by default, same flag as /api/build.
2. A bearer token, same `LEIBNIZ_API_TOKEN`. No token configured = refuse.
3. An Origin allow-list, which is the actual defence against CSWSH.
4. A concurrency cap, so a permitted caller cannot start unbounded builds.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from websockets.asyncio.server import serve

ROOT = Path(__file__).resolve().parent

API_TOKEN = os.environ.get("LEIBNIZ_API_TOKEN")
ENABLE_BUILD_ENDPOINT = os.environ.get("LEIBNIZ_ENABLE_BUILD_ENDPOINT") == "1"

# Browsers always send Origin on a WebSocket handshake. Non-browser clients may
# omit it, which is allowed here -- the bearer token is what authenticates them.
# A PRESENT but unlisted Origin is a browser on a page we do not trust, and is
# the CSWSH case, so it is rejected.
ALLOWED_ORIGINS = frozenset(
    o.strip() for o in os.environ.get(
        "LEIBNIZ_WS_ALLOWED_ORIGINS",
        "http://localhost:5000,http://127.0.0.1:5000",
    ).split(",") if o.strip()
)

MAX_CONCURRENT_BUILDS = int(os.environ.get("LEIBNIZ_WS_MAX_BUILDS", "1"))
_build_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BUILDS)


def _origin_permitted(origin: str | None) -> bool:
    if origin is None:
        return True
    return origin in ALLOWED_ORIGINS


def _token_valid(supplied: object) -> bool:
    if API_TOKEN is None:
        return False
    if not isinstance(supplied, str):
        return False
    import hmac
    return hmac.compare_digest(supplied, API_TOKEN)


async def _deny(websocket, message: str, code: str) -> None:
    await websocket.send(json.dumps({"event": "error", "code": code, "message": message}))


async def stream_build(websocket):
    async with _build_semaphore:
        process = await asyncio.create_subprocess_exec(
            "lake", "build", cwd=ROOT,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        assert process.stdout is not None
        async for raw in process.stdout:
            await websocket.send(json.dumps(
                {"event": "log", "line": raw.decode(errors="replace").rstrip()}))
        code = await process.wait()
        await websocket.send(json.dumps({"event": "complete", "ok": code == 0, "returncode": code}))


async def handler(websocket):
    try:
        origin = websocket.request.headers.get("Origin") if hasattr(websocket, "request") else None
        if not _origin_permitted(origin):
            await _deny(websocket, f"origin not permitted: {origin}", "forbidden_origin")
            return

        message = json.loads(await websocket.recv())
        action = message.get("action")

        if action != "build":
            await _deny(websocket, "Unknown action", "unknown_action")
            return

        if not ENABLE_BUILD_ENDPOINT:
            await _deny(
                websocket,
                "build streaming is disabled; set LEIBNIZ_ENABLE_BUILD_ENDPOINT=1 for local dev only",
                "disabled",
            )
            return

        if API_TOKEN is None:
            await _deny(
                websocket,
                "server has no LEIBNIZ_API_TOKEN configured; build streaming is disabled",
                "no_token_configured",
            )
            return

        if not _token_valid(message.get("token")):
            await _deny(websocket, "unauthorized", "unauthorized")
            return

        await stream_build(websocket)
    except Exception as exc:
        await websocket.send(json.dumps({"event": "error", "message": str(exc)}))


async def run():
    async with serve(handler, "127.0.0.1", 8765):
        await asyncio.Future()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
