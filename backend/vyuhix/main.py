"""Vyuhix API (level-1 proof of concept)."""
from __future__ import annotations

import json
import threading
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from . import auth, compliance, copilot, engine, feeds, ingest, insurance, optimise, rag, store
from .auth import ORG_ALL, ORG_READ, ORG_WRITE, require
from .money import inr
from .settings import ANTHROPIC_API_KEY, CORS_ORIGINS, FRONTEND_DIST

@asynccontextmanager
async def lifespan(_app):
    store.init()
    auth.seed_users()
    engine.run()                                   # warm the cache
    threading.Thread(target=rag.index, daemon=True).start()   # build the docs index without blocking startup
    if not store.scalar("select count(*) from audit_log"):
        store.audit("system", "startup", detail={"version": "0.1.0"})
    yield


app = FastAPI(title="Vyuhix API", version="0.1.0", lifespan=lifespan,
              description="Cyber risk in rupees: attack paths, loss simulation, budget plans and insurance view.")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    t0 = time.perf_counter()
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Server-Timing"] = f"app;dur={(time.perf_counter() - t0) * 1000:.1f}"
    return resp


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoginIn(Strict):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class SignupIn(LoginIn):
    name: str = Field(max_length=80)


class RunIn(Strict):
    controls: list[str] = Field(default_factory=list, max_length=20)
    assumptions: dict = Field(default_factory=dict)
    tef: dict[str, float] = Field(default_factory=dict)


class PlanIn(Strict):
    budget_inr: float = Field(ge=0, le=1e9)


class InsuranceIn(Strict):
    limit_inr: float | None = Field(default=None, ge=0, le=1e11)
    controls: list[str] = Field(default_factory=list, max_length=20)


class ScanIn(Strict):
    targets: list[str] = Field(min_length=1, max_length=10)


class AskIn(Strict):
    question: str = Field(min_length=2, max_length=500)


# ── auth ─────────────────────────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
def login(body: LoginIn, request: Request):
    return auth.login(body.email.strip().lower(), body.password, request.client.host if request.client else "?")


@app.post("/api/auth/signup")
def signup(body: SignupIn):
    return auth.signup(body.email, body.name, body.password)


@app.get("/api/me")
def me(user: dict = Depends(auth.current)):
    return user


# ── organisation and risk ────────────────────────────────────────────────────────────────
@app.get("/api/org")
def org(user: dict = Depends(require(*ORG_ALL, "platform_admin"))):
    m = engine.model()
    return {"org": m.org, "controls": list(m.controls.values()), "assumptions": m.assumptions,
            "feeds": feeds.status(), "llm_mode": "claude" if ANTHROPIC_API_KEY else "offline"}


@app.get("/api/graph")
def graph(user: dict = Depends(require(*ORG_READ))):
    m = engine.model()
    return {"nodes": list(m.nodes.values()), "edges": m.edges}


def _validate_controls(controls: list[str]) -> None:
    unknown = set(controls) - set(engine.model().controls)
    if unknown:
        raise HTTPException(422, f"Unknown controls: {', '.join(sorted(unknown))}")


@app.post("/api/run")
def run(body: RunIn, user: dict = Depends(require(*ORG_ALL))):
    _validate_controls(body.controls)
    r = engine.run(body.controls, body.assumptions, body.tef)
    base = engine.run([], body.assumptions, body.tef)
    out = engine.public(r)
    out["baseline_summary"] = base["summary"]
    out["diff"] = engine.diff_paths(base, r)
    out["choke_points"] = engine.choke_points(base)
    out["edge_info"] = {e["id"]: {k: e.get(k) for k in ("src", "dst", "type", "text", "technique", "evidence", "cve")}
                        for e in engine.model().edges}
    if user["role"] == "broker":                       # brokers see quantiles, not attack paths
        out = {k: out[k] for k in ("summary", "baseline_summary", "lec", "kev_state", "soc")}
    return out


@app.get("/api/frontier")
def frontier(user: dict = Depends(require(*ORG_READ))):
    return {"points": optimise.frontier()}


@app.post("/api/plan")
def plan(body: PlanIn, user: dict = Depends(require(*ORG_READ))):
    p = optimise.plan(body.budget_inr)
    store.audit(user["sub"], "plan_computed", detail={"budget": body.budget_inr, "chosen": p["chosen"]})
    return p


@app.post("/api/insurance")
def insurance_view(body: InsuranceIn, user: dict = Depends(require(*ORG_ALL))):
    _validate_controls(body.controls)
    return insurance.view(body.limit_inr, body.controls)


@app.get("/api/compliance")
def compliance_view(user: dict = Depends(require(*ORG_READ))):
    return compliance.matrix()


@app.get("/api/evidence")
def evidence(user: dict = Depends(require(*ORG_WRITE))):
    return {"last_scan": ingest.last_scan(), "allowlist": [str(n) for n in ingest.allowlist()]}


@app.post("/api/scan")
def scan(body: ScanIn, user: dict = Depends(require(*ORG_WRITE))):
    try:
        return ingest.run_scan(user["sub"], body.targets)
    except ingest.TargetRefused as e:
        raise HTTPException(403, str(e))


@app.post("/api/copilot")
def ask(body: AskIn, user: dict = Depends(require(*ORG_ALL))):
    if user["role"] == "broker" and not any(w in body.question.lower() for w in ("insur", "cover", "limit", "policy", "gap")):
        return {"answer": "Broker access is limited to the insurance view. Ask about coverage, limits or the gap.",
                "mode": "policy", "grounded": True, "latency_ms": 0, "tools": [], "evidence": []}
    return copilot.ask(body.question, user["sub"], user["role"])


@app.get("/api/report")
def report(user: dict = Depends(require(*ORG_READ))):
    r = engine.run()
    p = optimise.plan(1500000)
    v = insurance.view()
    store.audit(user["sub"], "report_exported")
    return {"org": engine.model().org, "summary": r["summary"], "top_paths": sorted(r["paths"], key=lambda x: -x["eal"])[:3],
            "plan": p, "insurance": {k: v[k] for k in ("current_limit_inr", "var95", "coverage_gap_inr", "recommended_limit_inr",
                                                         "insurability_score", "disclaimer")},
            "assumptions_note": engine.model().assumptions["_label"], "generated_at": store.now()}


# ── admin console ────────────────────────────────────────────────────────────────────────
ADMIN = require("platform_admin")


@app.get("/api/admin/overview")
def admin_overview(user: dict = Depends(ADMIN)):
    calls = store.rows("select mode, count(*) n, avg(latency_ms) avg_ms, sum(grounded) grounded from copilot_calls group by mode")
    return {
        "users": store.rows("select email, name, role, org_id, created_at from users order by id"),
        "jobs": store.rows("select * from jobs order by id desc limit 20"),
        "feeds": feeds.status(),
        "copilot": calls,
        "guardrails_open": store.scalar("select count(*) from guardrail_events where status='open'"),
        "alerts": store.rows("select * from alerts order by id desc limit 10"),
        "audit_rows": store.scalar("select count(*) from audit_log"),
        "llm_mode": "claude" if ANTHROPIC_API_KEY else "offline",
        "knowledge": rag.status(),
    }


@app.get("/api/admin/guardrails")
def admin_guardrails(user: dict = Depends(ADMIN)):
    return store.rows("select * from guardrail_events order by id desc limit 100")


@app.get("/api/admin/audit")
def admin_audit(user: dict = Depends(ADMIN)):
    return store.rows("select * from audit_log order by id desc limit 200")


@app.post("/api/admin/audit/verify")
def admin_verify(user: dict = Depends(ADMIN)):
    res = store.verify_audit()
    store.audit(user["sub"], "audit_verified", detail=res)
    return res


@app.post("/api/admin/feeds/simulate-kev-update")
def simulate_kev(user: dict = Depends(ADMIN)):
    before = engine.run()["summary"]
    store.set_state("kev", "simulated")
    after = engine.run()["summary"]
    delta = after["eal"] - before["eal"]
    msg = (f"EAL {'+' if delta >= 0 else ''}{inr(delta)} ({delta / max(before['eal'], 1) * 100:+.0f}%): CVE-2024-6387 appears in the "
           f"SIMULATED KEV update and affects internet-facing bastion.")
    store.insert("alerts", severity="high", message=msg, detail={"before": before["eal"], "after": after["eal"], "simulated": True})
    store.audit(user["sub"], "feed_simulated_update", "kev", {"before": before["eal"], "after": after["eal"]})
    return {"message": msg, "before": before, "after": after}


@app.post("/api/admin/feeds/reset")
def reset_kev(user: dict = Depends(ADMIN)):
    store.set_state("kev", "snapshot")
    store.audit(user["sub"], "feed_reset", "kev")
    return {"state": "snapshot"}


@app.get("/api/alerts")
def alerts(user: dict = Depends(require(*ORG_ALL, "platform_admin"))):
    return store.rows("select * from alerts order by id desc limit 5")


@app.get("/api/health")
def health():
    return {"ok": True, "kev": feeds.kev_state()}


# ── frontend (built SPA) ─────────────────────────────────────────────────────────────────
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        if path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        f = FRONTEND_DIST / path
        return FileResponse(f if path and f.is_file() else FRONTEND_DIST / "index.html")


def _json(o) -> str:
    return json.dumps(o, default=str)
