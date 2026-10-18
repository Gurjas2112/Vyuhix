"""Feed state: KEV snapshot (or the clearly labelled simulated update) and the SOC signal."""
from __future__ import annotations

import datetime as dt
import json

from . import store
from .settings import DATA_DIR

FEEDS = DATA_DIR / "feeds"


def kev_state() -> str:
    return store.get_state("kev", "snapshot")


def kev_doc() -> dict:
    name = "kev_update_simulated.json" if kev_state() == "simulated" else "kev_snapshot.json"
    return json.loads((FEEDS / name).read_text(encoding="utf-8"))


def kev_set() -> set[str]:
    return {v["cveID"] for v in kev_doc()["vulnerabilities"]}


def epss_doc() -> dict:
    return json.loads((FEEDS / "epss_snapshot.json").read_text(encoding="utf-8"))


def soc_signal(window_days: int = 7) -> dict:
    alerts = []
    for line in (DATA_DIR / "evidence" / "suricata_eve.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            ev = json.loads(line)
            if ev.get("event_type") == "alert":
                alerts.append(ev)
    if not alerts:
        return {"alerts_in_window": 0, "window_days": window_days, "latest": None, "target": None}
    ts = [dt.datetime.strptime(a["timestamp"][:19], "%Y-%m-%dT%H:%M:%S") for a in alerts]
    latest = max(ts)
    in_window = [a for a, t in zip(alerts, ts) if (latest - t).days < window_days]
    return {
        "alerts_in_window": len(in_window),
        "window_days": window_days,
        "latest": latest.isoformat(),
        "target": "edge (172.30.0.10)",
        "top_signature": max({a["alert"]["signature"] for a in in_window},
                             key=lambda s: sum(a["alert"]["signature"] == s for a in in_window)),
    }


def status() -> dict:
    k, e = kev_doc(), epss_doc()
    return {
        "kev": {"state": kev_state(), "version": k["catalogVersion"], "count": k["count"],
                "simulated": bool(k.get("simulated")), "title": k["title"]},
        "epss": {"score_date": e["score_date"], "count": len(e["data"]), "title": e["title"]},
        "soc": soc_signal(),
    }
