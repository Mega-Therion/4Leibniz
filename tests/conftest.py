"""Test-only auth token, set before `api` is imported anywhere.

`api.API_TOKEN` is read from the environment at module import time, so this
must run before any test module does `from api import app`. pytest loads
conftest.py ahead of test collection in the same directory, which gives us
that ordering for free.
"""
import os

os.environ.setdefault("LEIBNIZ_API_TOKEN", "test-only-token-do-not-use-in-production")

AUTH_HEADERS = {"Authorization": f"Bearer {os.environ['LEIBNIZ_API_TOKEN']}"}
