"""Evals for the copilot and the knowledge retrieval behind it.

    python -m evals.run copilot --mode offline                     # deterministic router, free
    python -m evals.run copilot --mode claude --effort low --reps 2  # real API calls, costs money
    python -m evals.run copilot --mode null                        # constant "I can't answer that." (grader sanity check)
    python -m evals.run retrieval                                  # BM25 vs dense vs hybrid, free

Run from backend/. Each run writes evals/results/<run>/: results.jsonl (one row per case and rep: answer, tool calls,
citations, guardrail blocks, token usage, checks), errors.jsonl (attempts that never produced a gradable answer:
API failure, fallback to offline, wrong served model), summary.json and summary.md.

Grading checks outcomes, not routes: the answer must contain the expected facts (figures compared by value, so
"₹5.0 L" equals "₹5 lakh"), refusal cases must refuse, knowledge answers must cite, and the model's draft must pass
the grounding and citation guardrails without being replaced. Which tool was called is reported but not graded.
Expected figures come from the deterministic engine, not from a model's output.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
RUN_ID = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
os.environ["VYUHIX_RUNTIME_DIR"] = str(HERE / ".runtime" / f"db-{RUN_ID}")    # fresh database for every run
os.environ.setdefault("VYUHIX_MODEL_CACHE", str(HERE / ".runtime" / "models"))
API_KEY = os.environ.pop("ANTHROPIC_API_KEY", "")                             # only claude mode gets it

from vyuhix import copilot, rag, store  # noqa: E402

# USD per million tokens: input, output, cache read, cache write (5-minute TTL, 1.25 × input).
# Haiku's cache-read rate is assumed at 0.1 × input.
PRICES = {
    "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50),
    "claude-opus-5-5": (4.00, 20.00, 0.20, 5.00),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
}
REFUSAL = re.compile(
    r"can['’]?t|cannot|can not|couldn['’]t|unable|not able|don['’]t have|do not have|doesn['’]t (hold|have|include|cover)|"
    r"does not (hold|have|include|cover)|no (data|information|evidence|tool)|outside|only (have|hold|cover)|"
    r"not (available|something|provide|in scope)|won['’]t|declined", re.I)
NULL_ANSWER = {"answer": "I can't answer that.", "mode": "null", "grounded": True, "latency_ms": 0, "tools": [],
               "evidence": [], "citations": [], "blocked": {"numbers": [], "citations": []}, "usage": None}
OFFTOPIC = ["What is the capital of France?", "Who won the cricket match yesterday?", "Write me a poem about cats",
            "What's the weather in Pune today?", "Recommend a good laptop for programming"]


def load(name: str) -> list[dict]:
    return [json.loads(ln) for ln in (HERE / name).read_text(encoding="utf-8").splitlines() if ln.strip()]


def has(answer: str, item) -> bool:
    """One expected item: a list means any of; a figure matches by value; text matches case-insensitively."""
    if isinstance(item, list):
        return any(has(answer, i) for i in item)
    if copilot.NUM.fullmatch(item.strip()):
        kind, want = copilot.value(item)
        return any(k == kind and math.isclose(v, want, rel_tol=1e-9, abs_tol=1e-9)
                   for k, v in (copilot.value(m.group()) for m in copilot.NUM.finditer(answer)))
    return item.lower() in answer.lower()


def grade(case: dict, r: dict) -> dict:
    ans = r["answer"]
    checks = {"clean_draft": not r["blocked"]["numbers"] and not r["blocked"]["citations"]}
    if case.get("refuse"):
        checks["refused"] = bool(REFUSAL.search(ans))
    else:
        checks["facts"] = all(has(ans, m) for m in case.get("must", []))
    if case.get("forbid"):
        checks["no_forbidden"] = not any(f.lower() in ans.lower() for f in case["forbid"])
    if case["cat"] == "knowledge":
        checks["cited"] = bool(r["citations"])
    return checks


def cost(usage: dict | None, model: str) -> float:
    if not usage or model not in PRICES:
        return 0.0
    i, o, cr, cw = PRICES[model]
    return (usage["input_tokens"] * i + usage["output_tokens"] * o + usage["cache_read_input_tokens"] * cr
            + usage["cache_creation_input_tokens"] * cw) / 1e6


def pctl(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else 0.0


# ── copilot eval ─────────────────────────────────────────────────────────────────────────
def run_case(case: dict, rep: int, a) -> tuple[str, dict]:
    base = {"case": case["id"], "cat": case["cat"], "rep": rep, "q": case["q"], "role": case.get("role")}
    t0 = time.perf_counter()
    try:
        r = dict(NULL_ANSWER) if a.mode == "null" else copilot.ask(case["q"], "eval", case.get("role"))
    except Exception as e:
        return "error", {**base, "class": "harness", "error": f"{type(e).__name__}: {e}"}
    wall_ms = int((time.perf_counter() - t0) * 1000)
    if a.mode == "claude":
        if r["mode"] != "claude":
            ev = store.rows("select detail from guardrail_events where type='llm_fallback' order by id desc limit 1")
            return "error", {**base, "class": "api_failure_fell_back_to_offline", "error": ev[0]["detail"] if ev else None}
        served = set(r["usage"]["models"])
        if served != {a.model}:
            return "error", {**base, "class": "served_model_mismatch", "error": sorted(served)}
    checks = grade(case, r)
    return "ok", {**base, "passed": all(checks.values()), "checks": checks,
                  "tool_expected": case.get("tool"), "tool_hit": case.get("tool") in {t["tool"] for t in r["tools"]} if case.get("tool") else None,
                  "answer": r["answer"], "tools": r["tools"], "citations": r["citations"], "blocked": r["blocked"],
                  "mode": r["mode"], "latency_ms": r["latency_ms"], "wall_ms": wall_ms, "usage": r["usage"],
                  "cost_usd": cost(r["usage"], a.model) if a.mode == "claude" else 0.0}


def copilot_eval(a) -> None:
    copilot.ANTHROPIC_API_KEY = API_KEY if a.mode == "claude" else ""
    copilot.LLM_MODEL, copilot.LLM_EFFORT = a.model, a.effort
    if a.mode == "claude" and not API_KEY:
        sys.exit("claude mode needs ANTHROPIC_API_KEY in the environment")
    store.init()
    cases = [c for c in load("cases.jsonl") if not a.only or c["id"].startswith(tuple(a.only.split(",")))]
    rag.index()                                                       # build once before timing anything
    jobs = [(c, rep) for rep in range(a.reps) for c in cases]
    workers = a.workers if a.mode == "claude" else 1
    with ThreadPoolExecutor(workers) as pool:
        outcomes = list(pool.map(lambda j: run_case(j[0], j[1], a), jobs))
    rows = [r for k, r in outcomes if k == "ok"]
    errors = [r for k, r in outcomes if k == "error"]

    name = f"{RUN_ID}-copilot-{a.mode}" + (f"-{a.model}-{a.effort}" if a.mode == "claude" else "")
    out = HERE / "results" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows), encoding="utf-8")
    (out / "errors.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in errors), encoding="utf-8")

    def rate(rs, key=lambda r: r["passed"]):
        return sum(1 for r in rs if key(r)) / len(rs) if rs else float("nan")

    per_rep = [rate([r for r in rows if r["rep"] == k]) for k in range(a.reps)]
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["cat"]].append(r)
    tool_rows = [r for r in rows if r["tool_hit"] is not None]
    lat = [r["latency_ms"] for r in rows]
    usage_rows = [r["usage"] for r in rows if r["usage"]]
    summary = {
        "run": name, "mode": a.mode, "model": a.model if a.mode == "claude" else None,
        "effort": a.effort if a.mode == "claude" else None, "cases": len(cases), "reps": a.reps,
        "graded": len(rows), "errors": len(errors),
        "pass_rate": rate(rows), "pass_rate_per_rep": per_rep,
        "pass_rate_stdev": statistics.stdev(per_rep) if len(per_rep) > 1 else None,
        "by_category": {k: {"n": len(v), "pass_rate": rate(v)} for k, v in sorted(by_cat.items())},
        "tool_selection_rate": rate(tool_rows, lambda r: r["tool_hit"]),
        "clean_draft_rate": rate(rows, lambda r: r["checks"]["clean_draft"]),
        "latency_ms_p50": pctl(lat, 0.5), "latency_ms_p95": pctl(lat, 0.95),
        "tokens": {k: sum(u[k] for u in usage_rows) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")} if usage_rows else None,
        "api_requests": sum(u["requests"] for u in usage_rows),
        "cost_usd_total": round(sum(r["cost_usd"] for r in rows), 4),
        "cost_usd_per_question": round(sum(r["cost_usd"] for r in rows) / max(len(rows), 1), 5),
        "failed_cases": sorted({r["case"] for r in rows if not r["passed"]}),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md = copilot_markdown(summary, rows)
    (out / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\nWrote {out}")


def copilot_markdown(s: dict, rows: list[dict]) -> str:
    head = f"### Copilot eval: {s['mode']}" + (f" · {s['model']} · effort {s['effort']}" if s["model"] else "")
    spread = f" (per rep: {', '.join(f'{x:.0%}' for x in s['pass_rate_per_rep'])})" if s["reps"] > 1 else ""
    lines = [head, "", f"- **Pass rate: {s['pass_rate']:.0%}** of {s['graded']} graded answers{spread}; {s['errors']} infrastructure errors",
             f"- Tool selection: {s['tool_selection_rate']:.0%} · drafts passing the guardrails unchanged: {s['clean_draft_rate']:.0%}",
             f"- Latency p50 {s['latency_ms_p50'] / 1000:.1f} s, p95 {s['latency_ms_p95'] / 1000:.1f} s"]
    if s["tokens"]:
        t = s["tokens"]
        lines.append(f"- Tokens: {t['input_tokens']:,} input, {t['output_tokens']:,} output, {t['cache_read_input_tokens']:,} cache read, "
                     f"{t['cache_creation_input_tokens']:,} cache write over {s['api_requests']} requests · "
                     f"**cost ${s['cost_usd_total']:.2f}** (${s['cost_usd_per_question']:.4f} per question)")
    lines += ["", "| Category | n | Pass |", "|---|---|---|"]
    lines += [f"| {k} | {v['n']} | {v['pass_rate']:.0%} |" for k, v in s["by_category"].items()]
    failed = [r for r in rows if not r["passed"]]
    if failed:
        lines += ["", "Failures:", ""]
        for r in failed:
            bad = ", ".join(k for k, ok in r["checks"].items() if not ok)
            lines.append(f"- `{r['case']}` (rep {r['rep']}) failed {bad}: {r['answer'][:160].replace(chr(10), ' ')}")
    return "\n".join(lines)


# ── retrieval eval ───────────────────────────────────────────────────────────────────────
def retrieval_eval(a) -> None:
    items = load("retrieval.jsonl")
    st = rag.status()
    methods = ["bm25", "dense", "hybrid"] if st["method"] == "hybrid" else ["bm25"]
    res = {}
    for m in methods:
        ranks, times = [], []
        for it in items:
            t0 = time.perf_counter()
            hits = rag.search(it["q"], k=10, method=m)
            times.append((time.perf_counter() - t0) * 1000)
            ranks.append(next((i for i, h in enumerate(hits, 1) if any(f in h["text"] for f in it["facts"])), None))
        res[m] = {"hit@1": sum(1 for r in ranks if r and r <= 1) / len(ranks),
                  "hit@3": sum(1 for r in ranks if r and r <= 3) / len(ranks),
                  "hit@4": sum(1 for r in ranks if r and r <= 4) / len(ranks),
                  "mrr@10": sum(1 / r for r in ranks if r) / len(ranks),
                  "ms_p50": pctl(times, 0.5), "misses@4": [it["id"] for it, r in zip(items, ranks) if not r or r > 4]}
    gate = None
    if st["method"] == "hybrid":
        on = [rag.relevant(rag.search(it["q"], k=1)[0]) for it in items]
        off = [rag.relevant(rag.search(q, k=1)[0]) for q in OFFTOPIC]
        gate = {"on_topic_accepted": sum(on) / len(on), "off_topic_rejected": 1 - sum(off) / len(off)}
    summary = {"run": f"{RUN_ID}-retrieval", "queries": len(items), "corpus": st, "methods": res, "relevance_gate": gate}
    out = HERE / "results" / summary["run"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [f"### Retrieval eval: {len(items)} paraphrased questions over {st['chunks']} chunks from {st['documents']} documents", "",
             "| Method | Hit@1 | Hit@3 | Hit@4 (what the copilot sees) | MRR@10 | p50 latency |", "|---|---|---|---|---|---|"]
    lines += [f"| {m} | {r['hit@1']:.0%} | {r['hit@3']:.0%} | {r['hit@4']:.0%} | {r['mrr@10']:.2f} | {r['ms_p50']:.0f} ms |" for m, r in res.items()]
    if gate:
        lines += ["", f"Relevance gate (offline router): accepts {gate['on_topic_accepted']:.0%} of on-topic questions, "
                      f"rejects {gate['off_topic_rejected']:.0%} of {len(OFFTOPIC)} off-topic ones."]
    md = "\n".join(lines)
    (out / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\nWrote {out}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="eval", required=True)
    c = sub.add_parser("copilot")
    c.add_argument("--mode", choices=["offline", "claude", "null"], default="offline")
    c.add_argument("--model", default=copilot.LLM_MODEL)
    c.add_argument("--effort", default=copilot.LLM_EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    c.add_argument("--reps", type=int, default=1)
    c.add_argument("--workers", type=int, default=4)
    c.add_argument("--only", help="comma-separated case-id prefixes, e.g. kb-,plan-")
    sub.add_parser("retrieval")
    a = p.parse_args()
    copilot_eval(a) if a.eval == "copilot" else retrieval_eval(a)


if __name__ == "__main__":
    main()
