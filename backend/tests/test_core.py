import itertools
import json
import os
import tempfile

import pytest

os.environ.setdefault("VYUHIX_RUNTIME_DIR", tempfile.mkdtemp(prefix="rf-test-"))

from fastapi.testclient import TestClient  # noqa: E402

from vyuhix import copilot, engine, ingest, optimise, store  # noqa: E402
from vyuhix.main import app  # noqa: E402
from vyuhix.model import ModelError, validate  # noqa: E402
from vyuhix.money import group_indian, inr  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def token(c, email):
    return {"Authorization": "Bearer " + c.post("/api/auth/login", json={"email": email, "password": "Demo@12345"}).json()["token"]}


# ── engine ───────────────────────────────────────────────────────────────────────────────
def test_same_input_same_numbers():
    engine._run_cached.cache_clear()
    a = engine.run()["summary"]
    engine._run_cached.cache_clear()
    b = engine.run()["summary"]
    assert a == b


def test_quantiles_ordered_and_converged():
    s = engine.run()["summary"]
    assert s["p50"] <= s["var95"] <= s["cvar95"]
    assert s["rel_std_error"] < 0.03


@pytest.mark.parametrize("control", list(engine.model().controls))
def test_a_control_never_increases_expected_loss(control):
    assert engine.run([control])["summary"]["eal"] <= engine.run()["summary"]["eal"] * 1.0001


def test_attribution_adds_up():
    r = engine.run()
    assert abs(sum(p["eal"] for p in r["paths"]) - r["summary"]["eal"]) / r["summary"]["eal"] < 1e-6


def test_hero_path_is_found_in_order():
    p = next(p for p in engine.run()["paths"] if p["edges"] == ["e1", "e2", "e3", "e4"])
    assert p["nodes"] == ["internet", "edge", "db_secret", "app_admin", "customers"]


def test_cycles_terminate():
    m = engine.model()
    from vyuhix.model import enumerate_paths
    m.edges.append({"id": "loop", "src": "app_admin", "dst": "app", "type": "reaches", "p": 1.0,
                    "technique": "T0", "evidence": [], "text": "loop back"})
    try:
        assert enumerate_paths(m, 6)
    finally:
        m.edges.pop()


def test_malformed_model_is_rejected_not_repaired():
    with pytest.raises(ModelError, match="unknown node 'ghost'"):
        validate({"a": {}}, [{"id": "x", "src": "a", "dst": "ghost", "type": "reaches", "p": 1}], {})


# ── optimiser ────────────────────────────────────────────────────────────────────────────
def test_plan_respects_budget_and_is_verified():
    p = optimise.plan(300000)
    assert p["cost_inr"] <= 300000
    assert abs(p["eal_after"] - engine.run(p["chosen"])["summary"]["eal"]) < 1


def test_plan_close_to_brute_force():
    m = engine.model()
    budget = 300000
    ids = list(m.controls)
    best = min(engine.run(list(s))["summary"]["eal"]
               for r in range(len(ids) + 1) for s in itertools.combinations(ids, r)
               if sum(m.controls[c]["cost_inr"] for c in s) <= budget)
    assert optimise.plan(budget)["eal_after"] <= best * 1.05


def test_frontier_never_gets_worse():
    pts = optimise.frontier()
    assert all(b["eal_after"] <= a["eal_after"] + 1 for a, b in zip(pts, pts[1:]))


# ── ingest and guardrails ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("target", ["8.8.8.8", "127.0.0.1", "172.30.2.5", "10.0.0.0/8", "example.com"])
def test_scan_refuses_targets_outside_the_lab(target):
    with pytest.raises(ingest.TargetRefused):
        ingest.assert_allowed(target)


def test_lab_targets_allowed():
    ingest.assert_allowed("172.30.0.10")
    ingest.assert_allowed("172.30.1.0/24")


def test_prompt_injection_in_banner_is_quarantined():
    out = ingest.run_scan("test", ["172.30.1.0/24"])
    assert any(g["type"] == "injection_suspected" for g in out["guardrails"])
    assert all("IGNORE PREVIOUS" not in (f["detail"] or "") for f in out["findings"])


def test_grounding_rejects_invented_numbers():
    assert copilot.ungrounded("EAL is ₹4.20 Cr", ["EAL ₹3.06 Cr"]) == ["₹4.20 Cr"]
    assert copilot.ungrounded("EAL is ₹3.06 Cr, step 2", ["EAL ₹3.06 Cr"]) == []
    assert copilot.ungrounded("cut 31% of risk", ["removes ₹93.7 L, 31%"]) == []


def test_copilot_refuses_other_organisations():
    assert "can't answer" in copilot.offline("What is HDFC's cyber risk?")[0]


# ── money formatting ─────────────────────────────────────────────────────────────────────
def test_indian_grouping():
    assert group_indian(200000) == "2,00,000"
    assert group_indian(12345678) == "1,23,45,678"
    assert inr(30600000) == "₹3.06 Cr" and inr(937000) == "₹9.4 L" and inr(95000) == "₹95,000"


# ── API: auth, roles, audit ──────────────────────────────────────────────────────────────
def test_login_required(client):
    assert client.post("/api/run", json={}).status_code == 401


def test_wrong_password(client):
    assert client.post("/api/auth/login", json={"email": "ananya@acme.demo", "password": "nope"}).status_code == 401


def test_signup_password_policy(client):
    r = client.post("/api/auth/signup", json={"email": "new@acme.demo", "name": "New", "password": "short"})
    assert r.status_code == 422


def test_broker_sees_quantiles_not_paths(client):
    h = token(client, "karan@broker.demo")
    assert client.get("/api/graph", headers=h).status_code == 403
    assert set(client.post("/api/run", json={}, headers=h).json()) == {"summary", "baseline_summary", "lec", "kev_state", "soc"}


def test_viewer_cannot_scan(client):
    h = token(client, "rohit@acme.demo")
    assert client.post("/api/scan", json={"targets": ["172.30.0.10"]}, headers=h).status_code == 403


def test_admin_only_routes(client):
    assert client.get("/api/admin/overview", headers=token(client, "ananya@acme.demo")).status_code == 403
    assert client.get("/api/admin/overview", headers=token(client, "divya@platform.demo")).status_code == 200


def test_unknown_fields_rejected(client):
    h = token(client, "ananya@acme.demo")
    assert client.post("/api/run", json={"controls": [], "sql": "drop table"}, headers=h).status_code == 422
    assert client.post("/api/run", json={"controls": ["not_a_control"]}, headers=h).status_code == 422


def test_kev_drift_raises_eal_and_resets(client):
    h = token(client, "divya@platform.demo")
    r = client.post("/api/admin/feeds/simulate-kev-update", headers=h).json()
    assert r["after"]["eal"] > r["before"]["eal"] and "SIMULATED" in r["message"]
    client.post("/api/admin/feeds/reset", headers=h)
    assert store.get_state("kev", "") == "snapshot"


def test_audit_chain_detects_tampering(client):
    h = token(client, "divya@platform.demo")
    assert client.post("/api/admin/audit/verify", headers=h).json()["ok"]
    with store.raw() as c:
        c.execute("drop trigger audit_no_update")
        c.execute("update audit_log set detail=? where id=(select min(id) from audit_log)", (json.dumps({"forged": True}),))
    res = store.verify_audit()
    assert not res["ok"] and res["first_broken_id"] >= 1
