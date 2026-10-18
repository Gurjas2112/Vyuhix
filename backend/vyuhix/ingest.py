"""Evidence ingest: deterministic parsers for known tool formats, a scan-target allowlist,
and a prompt-injection guard on every free-text field.

Level 1 replays the recorded lab outputs in data/demo/<org>/evidence. Level 2 runs the same
tools live against the Docker lab, through the same allowlist.
"""
from __future__ import annotations

import csv
import hashlib
import ipaddress
import json
import re
import time

from defusedxml import ElementTree as ET

from . import store
from .settings import DATA_DIR

EVID = DATA_DIR / "evidence"
INJECTION = re.compile(
    r"(ignore (all |any )?(previous|prior) instructions|disregard (the )?(system|above)|you are now|"
    r"mark (every|all) finding|system prompt|act as)", re.I)


class TargetRefused(Exception):
    pass


def allowlist() -> list[ipaddress.IPv4Network]:
    org = json.loads((DATA_DIR / "org.json").read_text(encoding="utf-8"))
    return [ipaddress.ip_network(c) for c in org["lab_cidrs"]]


def assert_allowed(target: str) -> None:
    try:
        net = ipaddress.ip_network(target, strict=False)
    except ValueError:
        raise TargetRefused(f"'{target}' is not an IP address or CIDR. Hostnames are resolved and approved separately.")
    if not any(net.subnet_of(a) for a in allowlist() if a.version == net.version):
        raise TargetRefused(f"{target} is outside the authorised lab ranges; nothing was sent.")


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _guard(text: str, source: str, findings: list, guard_events: list) -> str:
    if text and INJECTION.search(text):
        guard_events.append({"type": "injection_suspected", "source": source, "detail": {"text": text[:200]}})
        return "[quarantined: instruction-like text treated as data]"
    return text


def parse_nmap(name: str, findings: list, guards: list) -> None:
    root = ET.parse(EVID / name).getroot()
    for host in root.iter("host"):
        ip = host.find("address").get("addr")
        for port in host.iter("port"):
            svc = port.find("service")
            extra = _guard(svc.get("extrainfo", ""), f"{name}:{ip}:{port.get('portid')}", findings, guards)
            findings.append({
                "id": f"nmap:{ip}:{port.get('portid')}", "tool": "nmap", "asset_ip": ip, "severity": "info",
                "title": f"{svc.get('product', svc.get('name'))} {svc.get('version', '')}".strip() + f" on {port.get('portid')}/tcp",
                "detail": extra, "file": name,
            })


def parse_nuclei(findings: list, guards: list) -> None:
    for line in (EVID / "nuclei.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        findings.append({
            "id": f"nuclei:{r['template-id']}", "tool": "nuclei", "asset_ip": r["ip"],
            "severity": r["info"]["severity"], "title": _guard(r["info"]["name"], "nuclei", findings, guards),
            "detail": r["matched-at"], "file": "nuclei.jsonl",
        })


def parse_trivy(findings: list, guards: list) -> None:
    doc = json.loads((EVID / "trivy_bastion.json").read_text(encoding="utf-8"))
    for res in doc["Results"]:
        for v in res.get("Vulnerabilities", []):
            findings.append({
                "id": f"trivy:bastion:{v['VulnerabilityID']}", "tool": "trivy", "asset_ip": "172.30.0.11",
                "severity": v["Severity"].lower(), "title": f"{v['VulnerabilityID']} in {v['PkgName']} {v['InstalledVersion']}",
                "detail": f"Fixed in {v['FixedVersion']}. " + _guard(v.get("Title", ""), "trivy", findings, guards),
                "file": "trivy_bastion.json",
            })


def parse_gitleaks(findings: list, guards: list) -> None:
    for r in json.loads((EVID / "gitleaks.json").read_text(encoding="utf-8")):
        if "****" not in r["Secret"]:
            raise ValueError("unmasked secret in evidence; refusing to store it")
        findings.append({
            "id": f"gitleaks:{r['Fingerprint']}", "tool": "gitleaks", "asset_ip": None, "severity": "high",
            "title": f"{r['Description']} in {r['File']}:{r['StartLine']}", "detail": r["Secret"], "file": "gitleaks.json",
        })


def parse_grants(findings: list) -> None:
    with open(EVID / "pg_grants.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            stale = int(r["role_last_login_days"]) > 90
            findings.append({
                "id": f"pg:{r['grantee']}:{r['table_name']}:{r['privilege_type']}", "tool": "postgres", "asset_ip": "172.30.1.30",
                "severity": "medium" if stale else "info",
                "title": f"{r['grantee']} has {r['privilege_type']} on {r['table_name']}",
                "detail": f"role last used {r['role_last_login_days']} days ago" + (" (stale)" if stale else ""),
                "file": "pg_grants.csv",
            })


def parse_misc(findings: list) -> None:
    idp = json.loads((EVID / "identity_export.json").read_text(encoding="utf-8"))
    findings.append({"id": "idp:vpn-mfa-disabled", "tool": "idp", "asset_ip": None, "severity": "high",
                     "title": f"MFA not enforced for {idp['vpn']['users']} VPN users", "detail": "identity_export.json",
                     "file": "identity_export.json"})
    rk = json.loads((EVID / "redis_keys.json").read_text(encoding="utf-8"))
    for fnd in rk["findings"]:
        findings.append({"id": f"redis:key:{fnd['fingerprint']}", "tool": "redis", "asset_ip": rk["host"], "severity": "high",
                         "title": f"Redis key {fnd['key']} contains {fnd['contains']}", "detail": "redis_keys.json",
                         "file": "redis_keys.json"})


def parse_suricata(findings: list) -> None:
    n = 0
    sigs: dict[str, int] = {}
    for line in (EVID / "suricata_eve.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            ev = json.loads(line)
            if ev.get("event_type") == "alert":
                n += 1
                sigs[ev["alert"]["signature"]] = sigs.get(ev["alert"]["signature"], 0) + 1
    findings.append({"id": "suricata:edge-alerts", "tool": "suricata", "asset_ip": "172.30.0.10", "severity": "medium",
                     "title": f"{n} IDS alerts against edge in the last 7 days",
                     "detail": "; ".join(f"{k} ×{v}" for k, v in sigs.items()), "file": "suricata_eve.jsonl"})


STEPS = [
    ("Nmap · external view", lambda f, g: parse_nmap("nmap_external.xml", f, g)),
    ("Nmap · internal view", lambda f, g: parse_nmap("nmap_internal.xml", f, g)),
    ("Nuclei templates", parse_nuclei),
    ("Trivy image scan", parse_trivy),
    ("Gitleaks secrets", parse_gitleaks),
    ("Postgres grants", lambda f, g: parse_grants(f)),
    ("Identity and cache exports", lambda f, g: parse_misc(f)),
    ("Suricata IDS alerts", lambda f, g: parse_suricata(f)),
]


def run_scan(actor: str, targets: list[str]) -> dict:
    for t in targets:
        try:
            assert_allowed(t)
        except TargetRefused as e:
            store.audit(actor, "scan_refused", t, {"reason": str(e)})
            store.insert("guardrail_events", type="scan_refused", source=t, detail={"reason": str(e)})
            store.insert("jobs", kind="scan", status="refused", actor=actor, detail={"target": t, "reason": str(e)})
            raise
    job = store.insert("jobs", kind="scan", status="running", actor=actor, detail={"targets": targets})
    findings: list[dict] = []
    guards: list[dict] = []
    steps = []
    for label, fn in STEPS:
        t0 = time.perf_counter()
        before = len(findings)
        fn(findings, guards)
        steps.append({"step": label, "records": len(findings) - before, "ms": round((time.perf_counter() - t0) * 1000, 1)})
    files = sorted({f["file"] for f in findings})
    hashes = {name: _sha(EVID / name) for name in files}
    for g in guards:
        store.insert("guardrail_events", type=g["type"], source=g["source"], detail=g["detail"])
    detail = {"targets": targets, "steps": steps, "findings": len(findings), "guardrail_events": len(guards), "sha256": hashes}
    store.update_job(job, "done", detail)
    store.audit(actor, "scan_completed", ",".join(targets), {"job": job, "findings": len(findings)})
    store.set_state("last_scan", json.dumps({"job": job, "at": store.now(), "findings": findings, "steps": steps,
                                             "guardrails": guards, "sha256": hashes}))
    return {"job": job, "steps": steps, "findings": findings, "guardrails": guards, "sha256": hashes}


def last_scan() -> dict | None:
    raw = store.get_state("last_scan", "")
    return json.loads(raw) if raw else None
