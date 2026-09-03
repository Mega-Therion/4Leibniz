"""WebSocket build stream for the Calculemus dashboard.

The transport uses the maintained `websockets` implementation; the Lean process
remains the source of truth and every event is line-oriented and replayable.
"""
from __future__ import annotations
import asyncio, json, os
from pathlib import Path
from websockets.asyncio.server import serve

ROOT = Path(__file__).resolve().parent

async def stream_build(websocket):
    process = await asyncio.create_subprocess_exec(
        "lake", "build", cwd=ROOT, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    assert process.stdout is not None
    async for raw in process.stdout:
        await websocket.send(json.dumps({"event": "log", "line": raw.decode(errors="replace").rstrip()}))
    code = await process.wait()
    await websocket.send(json.dumps({"event": "complete", "ok": code == 0, "returncode": code}))

async def handler(websocket):
    try:
        message = json.loads(await websocket.recv())
        if message.get("action") == "build":
            await stream_build(websocket)
        else:
            await websocket.send(json.dumps({"event": "error", "message": "Unknown action"}))
    except Exception as exc:
        await websocket.send(json.dumps({"event": "error", "message": str(exc)}))

async def run():
    async with serve(handler, "127.0.0.1", 8765):
        await asyncio.Future()

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
