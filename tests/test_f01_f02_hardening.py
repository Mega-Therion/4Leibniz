"""Regression tests for F-01 (WebSocket build bypass) and F-02 (paid AI route).

Both findings are from docs/BLOCKER_STATUS_VERIFIED_2026-09-08.md.
"""
from __future__ import annotations

import asyncio
import importlib
import json
import os

import pytest


# ── F-02: /api/ai/suggest ───────────────────────────────────────────────────

@pytest.fixture()
def client(monkeypatch):
    """Reload `api` with a known token, then reload it back afterwards.

    `importlib.reload` rebinds module-level globals -- API_TOKEN among them --
    for every later importer in the same process. Without the teardown reload
    this fixture leaked its token into tests/test_security_hardening.py, which
    then failed only when the full suite ran and passed when run alone. Test
    pollution of exactly the kind that is easy to misread as a code defect.
    """
    import api
    monkeypatch.setenv("LEIBNIZ_API_TOKEN", "test-token")
    importlib.reload(api)
    api.app.config["TESTING"] = True
    try:
        with api.app.test_client() as c:
            yield c
    finally:
        monkeypatch.undo()
        importlib.reload(api)


def test_ai_suggest_rejects_unauthenticated(client):
    """Old behaviour: public. It calls a paid completions API when a key is set.

    Unauthenticated cost exhaustion -- and it degrades to a deterministic stub
    with no key configured, which is why it looked harmless in every audit run
    without credentials.
    """
    resp = client.post("/api/ai/suggest", json={"text": "omne corpus movetur"})
    assert resp.status_code == 401


def test_ai_suggest_accepts_authenticated(client):
    resp = client.post("/api/ai/suggest", json={"text": "omne corpus movetur"},
                       headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 200


def test_ai_suggest_rejects_unlisted_model(client):
    """`model` came straight from the request body, unvalidated."""
    resp = client.post("/api/ai/suggest",
                       json={"text": "x", "model": "some-enormous-expensive-model"},
                       headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 400
    assert "allowed" in resp.get_json()


def test_ai_suggest_rejects_non_string_model(client):
    resp = client.post("/api/ai/suggest", json={"text": "x", "model": {"$ne": None}},
                       headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 400


# ── F-01: the WebSocket build path ──────────────────────────────────────────

class FakeRequest:
    def __init__(self, origin=None):
        self.headers = {} if origin is None else {"Origin": origin}


class FakeSocket:
    """Records what the handler sends, and never lets a build actually start."""

    def __init__(self, message, origin=None):
        self._message = json.dumps(message)
        self.request = FakeRequest(origin)
        self.sent = []

    async def recv(self):
        return self._message

    async def send(self, data):
        self.sent.append(json.loads(data))

    def codes(self):
        return [m.get("code") for m in self.sent]


def _run(handler, socket):
    asyncio.run(handler(socket))
    return socket


@pytest.fixture(autouse=True)
def _restore_realtime():
    """Reload `realtime` after each test so its module globals do not leak."""
    yield
    import realtime
    importlib.reload(realtime)


def _reload_realtime(monkeypatch, **env):
    for key in ("LEIBNIZ_API_TOKEN", "LEIBNIZ_ENABLE_BUILD_ENDPOINT", "LEIBNIZ_WS_ALLOWED_ORIGINS"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import realtime
    importlib.reload(realtime)
    return realtime


def test_ws_build_disabled_by_default(monkeypatch):
    """Old behaviour: `{"action":"build"}` spawned `lake build`, no controls."""
    rt = _reload_realtime(monkeypatch, LEIBNIZ_API_TOKEN="t")
    sock = _run(rt.handler, FakeSocket({"action": "build"}))
    assert "disabled" in sock.codes()


def test_ws_build_requires_token(monkeypatch):
    rt = _reload_realtime(monkeypatch, LEIBNIZ_API_TOKEN="t",
                          LEIBNIZ_ENABLE_BUILD_ENDPOINT="1")
    sock = _run(rt.handler, FakeSocket({"action": "build"}))
    assert "unauthorized" in sock.codes()


def test_ws_build_rejects_wrong_token(monkeypatch):
    rt = _reload_realtime(monkeypatch, LEIBNIZ_API_TOKEN="t",
                          LEIBNIZ_ENABLE_BUILD_ENDPOINT="1")
    sock = _run(rt.handler, FakeSocket({"action": "build", "token": "wrong"}))
    assert "unauthorized" in sock.codes()


def test_ws_build_refuses_when_no_token_configured(monkeypatch):
    """Secure by default: no token configured means refuse, not allow."""
    rt = _reload_realtime(monkeypatch, LEIBNIZ_ENABLE_BUILD_ENDPOINT="1")
    sock = _run(rt.handler, FakeSocket({"action": "build", "token": "anything"}))
    assert "no_token_configured" in sock.codes()


def test_ws_rejects_cross_site_origin(monkeypatch):
    """Cross-site WebSocket hijacking.

    Browsers do not apply the same-origin policy to WebSockets as they do to
    fetch, so any page the operator visits could open ws://127.0.0.1:8765. The
    localhost bind is not a boundary; the Origin check is.
    """
    rt = _reload_realtime(monkeypatch, LEIBNIZ_API_TOKEN="t",
                          LEIBNIZ_ENABLE_BUILD_ENDPOINT="1")
    sock = _run(rt.handler,
                FakeSocket({"action": "build", "token": "t"}, origin="https://evil.example"))
    assert "forbidden_origin" in sock.codes()


def test_ws_allows_configured_origin(monkeypatch):
    rt = _reload_realtime(monkeypatch, LEIBNIZ_API_TOKEN="t",
                          LEIBNIZ_ENABLE_BUILD_ENDPOINT="1",
                          LEIBNIZ_WS_ALLOWED_ORIGINS="http://localhost:5000")
    sock = _run(rt.handler,
                FakeSocket({"action": "wrong"}, origin="http://localhost:5000"))
    assert "forbidden_origin" not in sock.codes()


def test_ws_unknown_action_still_rejected(monkeypatch):
    rt = _reload_realtime(monkeypatch, LEIBNIZ_API_TOKEN="t")
    sock = _run(rt.handler, FakeSocket({"action": "definitely-not-build"}))
    assert "unknown_action" in sock.codes()
