"""Maps control areas to frameworks. Status comes from the same evidence as the insurance view."""
from __future__ import annotations

from . import insurance

AREAS = [
    {"area": "Vulnerability management", "key": "patch_kev",
     "map": {"ISO 27001:2022": "A.8.8", "NIST CSF 2.0": "ID.RA-01, PR.PS-02", "CIS v8.1": "7", "CERT-In 2022": "Advisory response", "RBI ITGRCA 2023": "Patch and vulnerability management", "DPDP Rules 2025": "Reasonable security safeguards"}},
    {"area": "Multi-factor authentication", "key": "mfa",
     "map": {"ISO 27001:2022": "A.8.5", "NIST CSF 2.0": "PR.AA-03", "CIS v8.1": "6.3–6.5", "CERT-In 2022": "—", "RBI ITGRCA 2023": "Access control", "DPDP Rules 2025": "Access control"}},
    {"area": "Least privilege and secrets", "key": "pam",
     "map": {"ISO 27001:2022": "A.5.15, A.5.17, A.8.2", "NIST CSF 2.0": "PR.AA-01, PR.AA-05", "CIS v8.1": "5, 6", "CERT-In 2022": "—", "RBI ITGRCA 2023": "Privileged access", "DPDP Rules 2025": "Access control"}},
    {"area": "Endpoint detection and monitoring", "key": "edr",
     "map": {"ISO 27001:2022": "A.8.7, A.8.16", "NIST CSF 2.0": "DE.CM-01, DE.CM-09", "CIS v8.1": "10, 13", "CERT-In 2022": "Log retention 180 days", "RBI ITGRCA 2023": "Security operations", "DPDP Rules 2025": "Logging and monitoring (1-year logs)"}},
    {"area": "Backup and recovery", "key": "backups",
     "map": {"ISO 27001:2022": "A.8.13", "NIST CSF 2.0": "PR.DS-11, RC.RP-03", "CIS v8.1": "11", "CERT-In 2022": "—", "RBI ITGRCA 2023": "Business continuity", "DPDP Rules 2025": "Backups and continuity"}},
    {"area": "Email security", "key": "email",
     "map": {"ISO 27001:2022": "A.5.14", "NIST CSF 2.0": "PR.PS-01", "CIS v8.1": "9", "CERT-In 2022": "—", "RBI ITGRCA 2023": "—", "DPDP Rules 2025": "—"}},
    {"area": "Incident response and reporting", "key": "ir_plan",
     "map": {"ISO 27001:2022": "A.5.24–A.5.26", "NIST CSF 2.0": "RS.MA-01, RS.CO-02", "CIS v8.1": "17", "CERT-In 2022": "6-hour reporting", "RBI ITGRCA 2023": "Incident management", "DPDP Rules 2025": "Breach intimation (72-hour report)"}},
]
FRAMEWORKS = ["ISO 27001:2022", "NIST CSF 2.0", "CIS v8.1", "CERT-In 2022", "RBI ITGRCA 2023", "DPDP Rules 2025"]


def matrix(controls_on: list[str] | None = None) -> dict:
    st = {s["key"]: s for s in insurance.control_status(controls_on or [])}
    rows = [{"area": a["area"], "status": st[a["key"]]["status"], "note": st[a["key"]]["note"],
             "evidence": st[a["key"]]["evidence"], "map": a["map"]} for a in AREAS]
    return {"frameworks": FRAMEWORKS, "rows": rows,
            "note": "Mappings are indicative and for discussion; confirm clause applicability with your auditor."}
