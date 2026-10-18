"""Orchestrates a risk run: probabilities → paths → simulation, with caching and provenance."""
from __future__ import annotations

import copy
import hashlib
import json
from functools import lru_cache

import numpy as np

from . import feeds
from .model import Model, edge_basis, edge_probabilities, enumerate_paths, load_model
from .montecarlo import simulate
from .settings import DATA_DIR

_MODEL: Model | None = None


def model() -> Model:
    global _MODEL
    if _MODEL is None:
        _MODEL = load_model(DATA_DIR)
    return _MODEL


def merged_assumptions(overrides: dict | None) -> dict:
    a = copy.deepcopy(model().assumptions)
    for section, values in (overrides or {}).items():
        if section in a and isinstance(values, dict):
            a[section].update(values)
    return a


def entry_tef(m: Model, assumptions: dict, overrides: dict | None) -> tuple[dict[str, float], dict]:
    tef = {e: float(m.nodes[e]["tef"]) for e in m.entries}
    for e, v in (overrides or {}).items():
        if e in tef:
            tef[e] = float(v)
    soc = feeds.soc_signal()
    mult = 1.0
    if assumptions["soc_multiplier"]["enabled"] and soc["alerts_in_window"] >= 5:
        mult = float(assumptions["soc_multiplier"]["max"])
        tef["internet"] *= mult
    return tef, {**soc, "multiplier_applied": mult}


def _key(*parts) -> str:
    return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()


@lru_cache(maxsize=256)
def _run_cached(key: str, controls: tuple, assumptions_json: str, tef_json: str, kev_state: str) -> dict:
    m = model()
    a = json.loads(assumptions_json)
    tef = json.loads(tef_json)
    kev = feeds.kev_set()
    paths = enumerate_paths(m, int(a["simulation"]["max_hops"]))
    p = edge_probabilities(m, kev, list(controls), a)
    res = simulate(m, paths, p, tef, a, list(controls))
    for k, path in enumerate(paths):
        path["eal"] = float(res["path_attribution"][k])
        path["success_rate"] = float(res["path_success_rate"][k])
        prob = 1.0
        for eid in path["edges"]:
            prob *= float(p[m.edge_index[eid]])
        path["probability_per_attempt"] = prob
    res["paths"] = paths
    res["edge_p"] = {e["id"]: float(p[i]) for i, e in enumerate(m.edges)}
    res["edge_basis"] = edge_basis(m, kev, a)
    res["input_hash"] = key
    return res


def run(controls_on: list[str] | None = None, assumption_overrides: dict | None = None,
        tef_overrides: dict | None = None) -> dict:
    m = model()
    controls = tuple(sorted(c for c in (controls_on or []) if c in m.controls))
    a = merged_assumptions(assumption_overrides)
    tef, soc = entry_tef(m, a, tef_overrides)
    kev_state = feeds.kev_state()
    key = _key(controls, a, tef, kev_state)
    res = _run_cached(key, controls, json.dumps(a, sort_keys=True), json.dumps(tef, sort_keys=True), kev_state)
    out = {k: v for k, v in res.items() if k not in ("annual", "path_attribution", "path_success_rate")}
    out["controls_on"] = list(controls)
    out["assumptions"] = a
    out["tef"] = tef
    out["soc"] = soc
    out["kev_state"] = kev_state
    out["_annual"] = res["annual"]
    return out


def public(run_result: dict) -> dict:
    return {k: v for k, v in run_result.items() if not k.startswith("_")}


def diff_paths(before: dict, after: dict, eps: float = 1e-9) -> dict:
    """Removed = probability fell to zero; new = absent before; remaining = still live."""
    b = {tuple(p["edges"]): p for p in before["paths"] if p["probability_per_attempt"] > eps}
    a = {tuple(p["edges"]): p for p in after["paths"] if p["probability_per_attempt"] > eps}
    return {
        "removed": [b[k]["id"] for k in b if k not in a],
        "remaining": [a[k]["id"] for k in a if k in b],
        "new": [a[k]["id"] for k in a if k not in b],
    }


def choke_points(r: dict, top: int = 5) -> list[dict]:
    m = model()
    ranked = sorted(r["edge_attribution"].items(), key=lambda kv: -kv[1])[:top]
    by_id = {e["id"]: e for e in m.edges}
    return [{"edge": eid, "text": by_id[eid]["text"], "eal_through": v,
             "controls": [c for c, cv in m.controls.items() if eid in cv.get("effects", {})]} for eid, v in ranked]


def np_float(x) -> float:
    return float(np.asarray(x))
