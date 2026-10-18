"""Insurance bridge: insurability evidence, coverage gap and proposal answers. It never quotes premiums."""
from __future__ import annotations

import json
import math

from . import engine, feeds
from .settings import DATA_DIR

DISCLAIMER = ("Indicative analysis for discussion with your licensed insurance broker. "
              "Not an offer of insurance and not a premium quote.")

INSURER_CONTROLS = [
    ("mfa", "MFA on remote access and admin accounts", 25),
    ("patch_kev", "Known-exploited (KEV) vulnerabilities patched on internet-facing assets", 20),
    ("edr", "Endpoint detection and response on servers", 15),
    ("backups", "Immutable or offline backups, tested", 15),
    ("pam", "Least privilege for privileged and service accounts", 10),
    ("email", "Email authentication (SPF, DMARC enforcement)", 10),
    ("ir_plan", "Incident response plan with CERT-In 6-hour reporting", 5),
]


def control_status(controls_on: list[str]) -> list[dict]:
    m = engine.model()
    idp = json.loads((DATA_DIR / "evidence" / "identity_export.json").read_text(encoding="utf-8"))
    kev = feeds.kev_set()
    unpatched_kev = [e["cve"] for e in m.edges if e["type"] == "exploits" and e["cve"] in kev
                     and m.nodes[e["dst"]].get("internet_facing")]
    planned = {m.controls[c].get("insurer") for c in controls_on} - {"patch_kev"}
    if unpatched_kev and all(_patched(c, controls_on) for c in unpatched_kev):
        planned.add("patch_kev")          # only when every internet-facing KEV item is fixed
    base = {
        "mfa": ("absent", "idp:vpn-mfa-disabled", "MFA is not enforced for VPN or admin users"),
        "patch_kev": (("absent", "nuclei:CVE-2021-41773", f"Unpatched KEV on internet-facing assets: {', '.join(unpatched_kev)}")
                      if unpatched_kev else ("evidenced", "feeds:kev", "No KEV vulnerabilities on internet-facing assets")),
        "edr": ("absent", "idp:declared_controls", "No EDR reported"),
        "backups": ("declared", "idp:declared_controls", "Backups declared, not evidenced"),
        "pam": ("absent", "pg:app_admin:customers:SELECT", "Service role app_admin can bulk-read customers"),
        "email": ("evidenced", "idp:email", f"DMARC {idp['email']['dmarc']}, SPF {idp['email']['spf']}"),
        "ir_plan": ("declared", "idp:declared_controls", "IR plan declared, not evidenced"),
    }
    out = []
    for key, label, weight in INSURER_CONTROLS:
        status, ev, note = base[key]
        if key in planned and status != "evidenced":
            status, note = "planned", note + " → fixed by the selected plan"
        out.append({"key": key, "label": label, "weight": weight, "status": status, "evidence": ev, "note": note})
    return out


def _patched(cve: str, controls_on: list[str]) -> bool:
    return (cve == "CVE-2021-41773" and "patch_edge_httpd" in controls_on) or \
           (cve == "CVE-2024-6387" and "patch_bastion_openssh" in controls_on)


def score(statuses: list[dict]) -> int:
    credit = {"evidenced": 1.0, "planned": 1.0, "declared": 0.5, "absent": 0.0}
    return round(sum(s["weight"] * credit[s["status"]] for s in statuses))


def view(limit_inr: float | None = None, controls_on: list[str] | None = None) -> dict:
    m = engine.model()
    controls_on = controls_on or []
    r = engine.run(controls_on)
    s = r["summary"]
    limit = float(limit_inr if limit_inr is not None else m.org["current_policy"]["limit_inr"])
    statuses = control_status(controls_on)
    recommended = max(5e6, math.ceil(s["var99"] / 5e6) * 5e6)   # covers a 1-in-100-year loss
    proposal = [
        {"q": "Is MFA enforced for all remote access?", "a": _yn(statuses, "mfa"), "evidence": "idp:vpn-mfa-disabled"},
        {"q": "Are known-exploited vulnerabilities patched within 14 days?", "a": _yn(statuses, "patch_kev"), "evidence": "nuclei:CVE-2021-41773"},
        {"q": "Is EDR deployed on all servers?", "a": _yn(statuses, "edr"), "evidence": "idp:declared_controls"},
        {"q": "Are backups immutable or offline, and tested?", "a": _yn(statuses, "backups"), "evidence": "idp:declared_controls"},
        {"q": "How many personal-data records are held?", "a": "2,00,000 borrower records", "evidence": "org.json"},
        {"q": "Any security incidents or IDS alerts in the last 7 days?",
         "a": f"{r['soc']['alerts_in_window']} IDS alerts against the edge server; no confirmed incident",
         "evidence": "suricata:edge-alerts"},
    ]
    return {
        "disclaimer": DISCLAIMER,
        "current_limit_inr": limit,
        "retention_inr": m.org["current_policy"]["retention_inr"],
        "var95": s["var95"], "var99": s["var99"], "cvar95": s["cvar95"], "eal": s["eal"],
        "coverage_gap_inr": max(0.0, s["var95"] - limit),
        "recommended_limit_inr": recommended,
        "p_exceed_limit": next((pt["p_exceed"] for pt in r["lec"] if pt["loss"] >= limit), 0.0),
        "insurability_score": score(statuses),
        "controls": statuses,
        "proposal_answers": proposal,
        "claims_readiness": [
            {"item": "Report notifiable cyber incidents to CERT-In within 6 hours", "status": "declared"},
            {"item": "Keep ICT logs for 180 days (CERT-In)", "status": "absent"},
            {"item": "Notify the Data Protection Board and affected people without delay; detailed report within 72 hours (DPDP Rules, from May 2027)", "status": "absent"},
            {"item": "Preserve evidence and chain of custody", "status": "declared"},
        ],
        "lec": r["lec"],
    }


def _yn(statuses: list[dict], key: str) -> str:
    s = next(x for x in statuses if x["key"] == key)["status"]
    return {"evidenced": "Yes (evidenced)", "planned": "Planned", "declared": "Yes (declared, no evidence)", "absent": "No"}[s]
