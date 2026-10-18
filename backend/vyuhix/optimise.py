"""Budget optimiser: integer program on a path-coverage surrogate, verified by re-simulation."""
from __future__ import annotations

import math

import pulp

from . import engine


def _efficiency(baseline: dict) -> dict[tuple[str, str], float]:
    m = engine.model()
    eff: dict[tuple[str, str], float] = {}
    for c, cv in m.controls.items():
        for p in baseline["paths"]:
            keep = 1.0
            for eid in p["edges"]:
                keep *= cv.get("effects", {}).get(eid, 1.0)
            reduction = 1.0 - keep
            mag = cv.get("magnitude")
            if mag:
                comp = baseline["components"][p["jewel"]]
                total = sum(comp.values()) or 1.0
                reduction = max(reduction, ((1 - mag.get("downtime", 1)) * comp["downtime"]
                                            + (1 - mag.get("ransom", 1)) * comp["ransom"]) / total)
            if reduction > 0:
                eff[(c, p["id"])] = reduction
    return eff


def choose(baseline: dict, budget: float) -> list[str]:
    m = engine.model()
    loss = {p["id"]: p["eal"] for p in baseline["paths"]}
    eff = _efficiency(baseline)
    prob = pulp.LpProblem("vyuhix_plan", pulp.LpMaximize)
    x = {c: prob.add_variable(f"x_{c}", cat="Binary") for c in m.controls}
    y = {p: prob.add_variable(f"y_{p}", 0, 1) for p in loss}
    # small cost penalty breaks ties toward cheaper plans
    prob += pulp.lpSum(loss[p] * y[p] for p in loss) - 1e-6 * pulp.lpSum(m.controls[c]["cost_inr"] * x[c] for c in x)
    for p in loss:
        prob += y[p] <= pulp.lpSum(eff.get((c, p), 0.0) * x[c] for c in m.controls)
    prob += pulp.lpSum(m.controls[c]["cost_inr"] * x[c] for c in m.controls) <= budget
    prob.solve(pulp.HiGHS(msg=False, timeLimit=10))
    return sorted(c for c in m.controls if (x[c].value() or 0) > 0.5)


def greedy(budget: float, assumption_overrides: dict | None = None) -> list[str]:
    """Simulation-verified greedy: add the control with the most simulated EAL removed per rupee."""
    m = engine.model()
    chosen: list[str] = []
    spent = 0.0
    eal = engine.run([], assumption_overrides)["summary"]["eal"]
    while True:
        best, best_ratio, best_eal = None, 0.0, eal
        for c, cv in m.controls.items():
            if c in chosen or spent + cv["cost_inr"] > budget:
                continue
            e = engine.run(chosen + [c], assumption_overrides)["summary"]["eal"]
            ratio = (eal - e) / max(cv["cost_inr"], 1)
            if e < eal and ratio > best_ratio:
                best, best_ratio, best_eal = c, ratio, e
        if best is None:
            return sorted(chosen)
        chosen.append(best)
        spent += m.controls[best]["cost_inr"]
        eal = best_eal


def best_plan(budget: float, assumption_overrides: dict | None = None) -> list[str]:
    """The surrogate integer program and the greedy search each propose a plan; simulation picks the winner."""
    base = engine.run([], assumption_overrides)
    candidates = {tuple(choose(base, budget)), tuple(greedy(budget, assumption_overrides))}
    return list(min(candidates, key=lambda c: (engine.run(list(c), assumption_overrides)["summary"]["eal"], len(c))))


def plan(budget: float, assumption_overrides: dict | None = None) -> dict:
    m = engine.model()
    base = engine.run([], assumption_overrides)
    chosen = best_plan(budget, assumption_overrides)
    after = engine.run(chosen, assumption_overrides)
    cost = sum(m.controls[c]["cost_inr"] for c in chosen)
    removed = base["summary"]["eal"] - after["summary"]["eal"]
    per_control = []
    for c in chosen:
        solo = engine.run([c], assumption_overrides)
        per_control.append({
            "id": c, "label": m.controls[c]["label"], "cost_inr": m.controls[c]["cost_inr"],
            "eal_removed_alone": base["summary"]["eal"] - solo["summary"]["eal"],
        })
    for pc in per_control:
        pc["rupees_removed_per_rupee"] = pc["eal_removed_alone"] / max(pc["cost_inr"], 1)
    return {
        "budget_inr": budget, "chosen": chosen, "controls": per_control, "cost_inr": cost,
        "eal_before": base["summary"]["eal"], "eal_after": after["summary"]["eal"],
        "var95_before": base["summary"]["var95"], "var95_after": after["summary"]["var95"],
        "eal_removed": removed, "reduction_pct": removed / max(base["summary"]["eal"], 1.0),
        "rosi": (removed - cost) / max(cost, 1) if cost else None,
        "paths": engine.diff_paths(base, after),
        "method": "Integer program on a path-coverage surrogate (PuLP + HiGHS) and a simulation-verified greedy search each propose a plan; the one with lower re-simulated EAL wins.",
    }


def frontier(steps: int = 12, assumption_overrides: dict | None = None) -> list[dict]:
    m = engine.model()
    total = sum(c["cost_inr"] for c in m.controls.values())
    budgets = sorted({0, *[round(total * (i / steps) ** 2, -3) for i in range(1, steps + 1)], 1500000})
    out: list[dict] = []
    best: tuple[float, list[str]] | None = None
    for b in budgets:
        chosen = best_plan(b, assumption_overrides)
        eal = engine.run(chosen, assumption_overrides)["summary"]["eal"]
        if best is not None and best[0] <= eal:          # a cheaper plan stays affordable: never get worse
            eal, chosen = best
        best = (eal, chosen)
        out.append({"budget_inr": b, "eal_after": eal, "chosen": chosen,
                    "cost_inr": sum(m.controls[c]["cost_inr"] for c in chosen)})
    return out


def round_up(x: float, step: float) -> float:
    return math.ceil(x / step) * step
