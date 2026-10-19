# Roadmap

## Level 1: proof of concept (this repository)

Synthetic organisation; recorded tool outputs in real formats; deterministic engine; budget optimiser;
insurance and compliance views; grounded copilot (offline, or Claude with a key) with cited docs search; roles; hash-chained
audit; 47 tests; a copilot and retrieval eval harness; screenshots and a video.

## Level 2: live prototype

| Area | Addition |
|---|---|
| Live evidence | Docker Compose lab (a vulnerable Apache 2.4.49 edge, app, Postgres with synthetic PII, Redis, Suricata) with Nmap, Nuclei, Trivy and Gitleaks run live through the same allowlist |
| Feeds | Daily pulls from the FIRST EPSS API, CISA KEV, NVD 2.0 and CISA Vulnrichment, with snapshots for offline use and freshness alerts |
| Identity | Supabase Auth: email confirmation, TOTP MFA required for admins and brokers, Cloudflare Turnstile, ES256 JWT verified via JWKS |
| Data | Supabase Postgres with row-level security enforced even for the API; private evidence storage with AES-256-GCM; Indian region |
| Consent | Expiring, revocable broker grants scoped to the insurance view, visible to the client |
| Observability | OpenTelemetry → Grafana (metrics, logs, traces): API latency, job queue, feed age, LLM tokens and latency, guardrail counters |
| AI | Local open-weight model fallback via Ollama; per-organisation `local_only` mode |
| Tests | Schemathesis API fuzzing, Playwright end-to-end, promptfoo red-team suite in CI |

## Production

Cloud connectors (AWS, Azure, GCP, Microsoft 365, Active Directory attack paths, vulnerability-management
APIs, SOC alert queues); proof of asset ownership before any lookup; SSO and SCIM; per-tenant KMS keys;
calibration with real claims and incident data using Bayesian updating; treating deployed AI agents as
insurable assets; ISO 27001 and SOC 2 controls; multi-region recovery.
