# Demo data: Acme Fintech Pvt Ltd (fictional)

Everything in this folder is **synthetic demo data** for a fictional digital lender.
The files mimic the *output formats* of real tools (Nmap XML, Nuclei JSONL, Trivy JSON,
Gitleaks JSON, Suricata EVE JSON, a Postgres grants export) so the ingest pipeline is
exercised exactly as it would be on real scans. Feed values (EPSS, KEV) are a frozen demo
snapshot; refresh them from the live APIs before using Vyuhix on anything real.

`feeds/kev_update_simulated.json` is a **simulated** future KEV update used only to
demonstrate drift detection. It is labelled as a simulation everywhere it appears.
