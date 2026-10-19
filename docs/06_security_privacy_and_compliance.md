# Security, privacy and compliance

A product that stores an organisation's attack paths is itself a target. This page covers how Vyuhix
protects itself (level 1 as built, level 2 as designed) and what it helps its users comply with.

## How the prototype protects itself (level 1, built and tested)

| Area | Measure |
|---|---|
| **Authentication** | scrypt password hashes (n=2¹⁴, r=8, p=1) with per-user salt; constant-time comparison; HS256 JWT, 8-hour expiry; secret from env or generated per install |
| **Password policy** | 10–128 characters with upper, lower, digit and symbol |
| **Brute force** | 5 failed logins per IP+email in 5 minutes → 429, audited |
| **Authorisation** | Five roles enforced on every route; brokers get quantiles only; admin routes are admin-only |
| **Input validation** | Pydantic models with `extra="forbid"`, length and range limits; unknown control IDs → 422 |
| **Untrusted files** | Scanner XML parsed only with `defusedxml` (XXE-safe); unmasked secrets refused at parse time |
| **Prompt injection** | Instruction-like text in scanner output quarantined and logged; the copilot only ever sees engine output |
| **AI output** | Numeric grounding check by value; citation check on docs answers; brokers get only the coverage and docs tools inside the copilot; a model or network failure falls back to the deterministic router |
| **Scanning** | CIDR allowlist checked before anything runs; refusals audited and raised as guardrail events |
| **Audit** | Hash-chained log with SQLite triggers that block UPDATE and DELETE; on-demand chain verification |
| **Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy` |
| **Data** | Synthetic only. No real personal data anywhere in the repository |

## Level 2 (designed, not in this prototype)

Supabase Auth (email confirmation, TOTP MFA required for admins and brokers, Cloudflare Turnstile,
ES256 tokens verified against JWKS); Postgres row-level security enforced even for the API's own
queries; consent-scoped, expiring broker grants; AES-256-GCM encryption of raw evidence; hosting in an
Indian region; OpenTelemetry with Grafana dashboards and alerts; a `local_only` AI mode so no evidence
leaves the machine.

## Regulations considered

| Regulation | Relevance | How Vyuhix responds |
|---|---|---|
| **DPDP Act 2023 and DPDP Rules 2025** (notified 13 Nov 2025; substantive duties from 13 May 2027) | Penalty exposure in the loss model; safeguards and breach intimation for users; Vyuhix itself holds account data | Date-aware regulatory loss; compliance mapping; minimal account data; claims checklist with Board intimation and a 72-hour report |
| **CERT-In Directions (Apr 2022)** | 6-hour incident reporting; 180-day log retention | Claims-readiness checklist; compliance mapping; retention design in level 2 |
| **IT Act 2000** (unauthorised access) | Scanning systems you do not own is an offence | Code-enforced allowlist |
| **Insurance regulation** | Software must not look like an unlicensed insurance offer | No premiums; disclaimer on every insurance output; broker access by client consent |
| **RBI IT governance directions (2023), SEBI CSCRF (2024)** | Apply to regulated clients | Mapped in the compliance matrix |
| **ISO 27001:2022, NIST CSF 2.0, CIS v8.1** | Common control frameworks | Mapped in the compliance matrix |

Mappings are indicative and meant for discussion; confirm applicability with an auditor.

## Responsible use

Vyuhix analyses evidence about systems you are authorised to assess. The demo lab and data are
fictional. Do not point any scanner at systems without written permission.
