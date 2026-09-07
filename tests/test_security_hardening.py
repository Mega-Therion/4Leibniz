"""Negative tests for the Phase 1 release-hardening pass (2026-09-07 assessment).

Covers: unauthorized access to mutation routes (B-01), the disabled-by-default
build and keypair endpoints (B-02, B-03), malformed ZK proof rejection and
per-request isolation (B-04), replay-guard persistence (B-05), and the
request-size limit (B-12).
"""
import importlib, json, os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from conftest import AUTH_HEADERS

import api
from security import ReplayGuard, generate_keypair, sign_proposal, verify_fresh_proposal


class UnauthorizedAccessTests(unittest.TestCase):
    """B-01: mutation/dangerous routes must refuse an unauthenticated caller."""

    def setUp(self):
        self.client = api.app.test_client()

    def test_governance_evaluate_rejects_missing_token(self):
        response = self.client.post("/api/governance/evaluate", json={})
        self.assertEqual(response.status_code, 401)

    def test_peers_admit_rejects_missing_token(self):
        response = self.client.post("/api/peers/admit", json={})
        self.assertEqual(response.status_code, 401)

    def test_shards_atomic_commit_rejects_missing_token(self):
        response = self.client.post("/api/shards/atomic-commit", json={})
        self.assertEqual(response.status_code, 401)

    def test_zk_verify_rejects_missing_token(self):
        response = self.client.post("/api/zk/verify", json={"proof": {}, "public_signals": []})
        self.assertEqual(response.status_code, 401)

    def test_wrong_token_is_rejected(self):
        response = self.client.post("/api/governance/evaluate", json={},
                                     headers={"Authorization": "Bearer not-the-token"})
        self.assertEqual(response.status_code, 401)

    def test_correct_token_passes_the_gate(self):
        # Passes auth, then fails on the empty payload -- proves the 401 above
        # was the auth check, not an unrelated validation error.
        response = self.client.post("/api/governance/evaluate", json={}, headers=AUTH_HEADERS)
        self.assertNotEqual(response.status_code, 401)

    def test_read_only_routes_stay_public(self):
        # Phase 1's ask is "no unauthenticated mutation or process-spawning
        # endpoint" -- stateless read/compute routes should not regress into
        # requiring a token.
        for path in ("/api/metadata", "/api/modules", "/api/theorems", "/api/zk/status"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)


class NoTokenConfiguredTests(unittest.TestCase):
    """Secure-by-default: with LEIBNIZ_API_TOKEN unset, protected routes refuse everything."""

    def setUp(self):
        self._saved = os.environ.pop("LEIBNIZ_API_TOKEN", None)
        importlib.reload(api)
        self.client = api.app.test_client()

    def tearDown(self):
        if self._saved is not None:
            os.environ["LEIBNIZ_API_TOKEN"] = self._saved
        importlib.reload(api)

    def test_protected_route_returns_503_with_no_token_configured(self):
        response = self.client.post("/api/governance/evaluate", json={},
                                     headers={"Authorization": "Bearer anything"})
        self.assertEqual(response.status_code, 503)


class DangerousRoutesDisabledByDefaultTests(unittest.TestCase):
    """B-02, B-03: build execution and key generation are opt-in, not default-on."""

    def setUp(self):
        self.client = api.app.test_client()

    def test_build_endpoint_disabled_by_default(self):
        response = self.client.post("/api/build", headers=AUTH_HEADERS)
        self.assertEqual(response.status_code, 404)

    def test_keypair_endpoint_disabled_by_default(self):
        response = self.client.post("/api/security/keypair", headers=AUTH_HEADERS)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("private_key", response.get_json())


class ZkVerifyHardeningTests(unittest.TestCase):
    """B-04: malformed input is rejected before any subprocess or disk write."""

    def setUp(self):
        self.client = api.app.test_client()

    def test_malformed_proof_shape_is_rejected(self):
        response = self.client.post(
            "/api/zk/verify",
            json={"proof": {"not": "a groth16 proof"}, "public_signals": []},
            headers=AUTH_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertFalse(body["verified"])
        self.assertEqual(body["status"], "malformed")

    def test_oversized_public_signals_is_rejected(self):
        proof = {"pi_a": [], "pi_b": [], "pi_c": [], "protocol": "groth16"}
        response = self.client.post(
            "/api/zk/verify",
            json={"proof": proof, "public_signals": ["1"] * 1000},
            headers=AUTH_HEADERS,
        )
        body = response.get_json()
        self.assertFalse(body["verified"])
        self.assertEqual(body["status"], "malformed")


class ReplayGuardPersistenceTests(unittest.TestCase):
    """B-05: an on-disk ReplayGuard remembers a consumed nonce across instances."""

    def test_sqlite_backed_guard_survives_reinstantiation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "replay.sqlite3")
            private, _ = generate_keypair()
            proposal = sign_proposal("n1", {"claim": "C"}, private, timestamp=1000, nonce="fixed")

            guard_a = ReplayGuard(max_age_seconds=300, db_path=db_path)
            self.assertTrue(verify_fresh_proposal(proposal, guard_a, now=1000))

            # A fresh instance pointed at the same file must still see the
            # nonce as spent -- this is the behavior an in-memory dict cannot
            # offer across a process restart.
            guard_b = ReplayGuard(max_age_seconds=300, db_path=db_path)
            self.assertFalse(verify_fresh_proposal(proposal, guard_b, now=1000))

    def test_in_memory_default_is_unchanged(self):
        private, _ = generate_keypair()
        proposal = sign_proposal("n1", {"claim": "C"}, private, timestamp=1000, nonce="fixed")
        guard = ReplayGuard(max_age_seconds=300)
        self.assertTrue(verify_fresh_proposal(proposal, guard, now=1000))
        self.assertFalse(verify_fresh_proposal(proposal, guard, now=1000))


class RequestSizeLimitTests(unittest.TestCase):
    """B-12: the API enforces a body-size ceiling instead of accepting arbitrary JSON."""

    def setUp(self):
        self.client = api.app.test_client()

    def test_oversized_body_is_rejected(self):
        oversized = json.dumps({"text": "x" * 2_000_000})
        response = self.client.post(
            "/api/compile", data=oversized, content_type="application/json",
        )
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
