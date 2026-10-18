"""FAIR-style annual loss simulation over correlated attack paths.

Each simulated year draws a Poisson number of attempts per entry point. Each attempt samples
every edge independently, so two paths that share an edge succeed or fail together (correlation
is modelled by sampling edges, not paths). A crown jewel is reached if any path from that entry
succeeds. Draw order never depends on which controls are on, so before/after comparisons use
common random numbers and differences are exact rather than noisy.
"""
from __future__ import annotations

import numpy as np

from .model import Model


def pert(rng: np.random.Generator, lo: float, mode: float, hi: float, size) -> np.ndarray:
    if hi <= lo:
        return np.full(size, float(lo))
    a = 1 + 4 * (mode - lo) / (hi - lo)
    b = 1 + 4 * (hi - mode) / (hi - lo)
    return lo + rng.beta(a, b, size) * (hi - lo)


COMPONENTS = ["incident_response", "notification", "downtime", "ransom", "regulatory", "fraud"]


def sample_magnitudes(rng, m: Model, assumptions: dict, controls_on: list[str], A: int) -> np.ndarray:
    """Returns (A, J, C) rupees: attempts × crown jewels × loss components."""
    jewels = m.jewels
    out = np.zeros((A, len(jewels), len(COMPONENTS)))
    rev_per_hour = m.org["annual_revenue_inr"] / 8760.0
    down_mult, ransom_mult = 1.0, 1.0
    for cid in controls_on:
        mag = m.controls[cid].get("magnitude", {})
        down_mult *= mag.get("downtime", 1.0)
        ransom_mult *= mag.get("ransom", 1.0)
    reg = assumptions["regulatory"]
    for j, jid in enumerate(jewels):
        prof = assumptions["profiles"][m.nodes[jid]["profile"]]
        records = m.nodes[jid].get("records", 0)
        # draws happen in a fixed order for every profile so streams stay aligned
        ir = pert(rng, *prof["ir_inr"], A)
        per_rec = pert(rng, *prof.get("per_record_inr", [0, 0, 0]), A)
        hours = pert(rng, *prof["downtime_hours"], A)
        ransom_hit = rng.random(A) < prof["ransom_prob"]
        ransom = pert(rng, *prof["ransom_inr"], A)
        reg_hit = rng.random(A) < reg["dpdp_enforce_prob"]
        regulatory = pert(rng, *prof.get("regulatory_inr", [0, 0, 0]), A)
        fraud = pert(rng, *prof.get("fraud_inr", [0, 0, 0]), A)
        out[:, j, 0] = ir
        out[:, j, 1] = per_rec * records
        out[:, j, 2] = hours * rev_per_hour * down_mult
        out[:, j, 3] = ransom_hit * ransom * ransom_mult
        out[:, j, 4] = (reg_hit * np.minimum(regulatory, reg["dpdp_cap_inr"])) if reg["dpdp_enabled"] else 0.0
        out[:, j, 5] = fraud
    return out


def simulate(m: Model, paths: list[dict], edge_p: np.ndarray, entry_tef: dict[str, float],
             assumptions: dict, controls_on: list[str]) -> dict:
    sim = assumptions["simulation"]
    n_years, seed = int(sim["n_years"]), int(sim["seed"])
    rng = np.random.default_rng(seed)
    entries, jewels = m.entries, m.jewels
    tef = np.array([entry_tef[e] for e in entries])

    attempts = rng.poisson(tef, size=(n_years, len(entries)))
    y, e = np.nonzero(attempts)
    reps = attempts[y, e]
    year_of, entry_of = np.repeat(y, reps), np.repeat(e, reps)
    A = year_of.size

    edge_up = rng.random((A, edge_p.size)) < edge_p
    mags = sample_magnitudes(rng, m, assumptions, controls_on, A)          # (A, J, C)
    jewel_loss = mags.sum(axis=2)                                          # (A, J)

    P = len(paths)
    ok = np.zeros((A, P), dtype=bool)
    for k, p in enumerate(paths):
        idx = [m.edge_index[eid] for eid in p["edges"]]
        ok[:, k] = edge_up[:, idx].all(axis=1) & (entry_of == entries.index(p["entry"]))

    reached = np.zeros((A, len(jewels)), dtype=bool)
    path_attr = np.zeros(P)
    comp_by_jewel = np.zeros((len(jewels), len(COMPONENTS)))
    for j, jid in enumerate(jewels):
        ks = [k for k, p in enumerate(paths) if p["jewel"] == jid]
        if not ks:
            continue
        okj = ok[:, ks]
        reached[:, j] = okj.any(axis=1)
        count = np.maximum(okj.sum(axis=1), 1)
        for col, k in enumerate(ks):
            path_attr[k] = (jewel_loss[:, j] * okj[:, col] / count).sum() / n_years
        comp_by_jewel[j] = (mags[:, j, :] * reached[:, j:j + 1]).sum(axis=0) / n_years

    event_loss = (jewel_loss * reached).sum(axis=1)
    annual = np.bincount(year_of, weights=event_loss, minlength=n_years)

    edge_attr = {ed["id"]: 0.0 for ed in m.edges}
    for k, p in enumerate(paths):
        for eid in p["edges"]:
            edge_attr[eid] += path_attr[k]

    var95 = float(np.quantile(annual, 0.95))
    tail = annual[annual >= var95]
    se = float(annual.std(ddof=1) / np.sqrt(n_years) / max(annual.mean(), 1.0))
    summary = {
        "eal": float(annual.mean()),
        "p50": float(np.median(annual)),
        "p90": float(np.quantile(annual, 0.90)),
        "var95": var95,
        "var99": float(np.quantile(annual, 0.99)),
        "cvar95": float(tail.mean()) if tail.size else var95,
        "p_any_loss": float((annual > 0).mean()),
        "rel_std_error": se,
        "attempts_simulated": int(A),
    }
    return {
        "annual": annual,
        "summary": summary,
        "lec": loss_exceedance(annual),
        "path_attribution": path_attr,
        "edge_attribution": edge_attr,
        "components": {jid: dict(zip(COMPONENTS, map(float, comp_by_jewel[j]))) for j, jid in enumerate(jewels)},
        "path_success_rate": ok.mean(axis=0) if A else np.zeros(P),
    }


def loss_exceedance(annual: np.ndarray, points: int = 60) -> list[dict]:
    hi = max(float(annual.max()), 1e6)
    xs = np.unique(np.concatenate([[0.0], np.geomspace(1e5, hi, points)]))
    s = np.sort(annual)
    n = s.size
    return [{"loss": float(x), "p_exceed": float(1 - np.searchsorted(s, x, side="right") / n)} for x in xs]
