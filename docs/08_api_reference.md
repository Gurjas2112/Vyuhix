# API reference

Base URL `http://localhost:8000/api`. Interactive docs are at `http://localhost:8000/docs` (OpenAPI).
Every route except login, signup and health needs `Authorization: Bearer <token>`. Request bodies
reject unknown fields (422).

## Auth

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/auth/login` | `{email, password}` | `{token, user}`; 401 wrong credentials, 429 after 5 failures |
| POST | `/auth/signup` | `{email, name, password}` | `{token, user}` (role `analyst`) |
| GET | `/me` | — | JWT claims |

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login -H 'content-type: application/json' \
  -d '{"email":"ananya@acme.demo","password":"Demo@12345"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
```

## Risk

| Method | Path | Roles | Body | Returns |
|---|---|---|---|---|
| GET | `/org` | all | — | org profile, controls, assumptions, feed status, copilot mode |
| GET | `/graph` | org roles | — | nodes, edges |
| POST | `/run` | org roles, broker | `{controls?: [id], assumptions?: {section: {...}}, tef?: {entry: n}}` | summary, LEC, paths with ₹, edge probabilities and basis, components, diff vs baseline, choke points, edge info. Brokers get summary + LEC only |
| POST | `/plan` | org roles | `{budget_inr}` | chosen controls, cost, EAL before/after (re-simulated), VaR95, ROSI, path diff |
| GET | `/frontier` | org roles | — | budget → EAL points (monotone) |
| POST | `/insurance` | org roles, broker | `{limit_inr?, controls?}` | score, gap, recommended limit, statuses, proposal answers, claims readiness, LEC, disclaimer |
| GET | `/compliance` | org roles | — | framework matrix |
| GET | `/report` | org roles | — | board report data |
| GET | `/alerts` | all | — | latest drift alerts |

```bash
curl -s -X POST localhost:8000/api/run -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d '{"controls":["patch_edge_httpd"]}' | python -m json.tool | head -30
```

## Evidence

| Method | Path | Roles | Body | Returns |
|---|---|---|---|---|
| GET | `/evidence` | org admin, analyst | — | last scan, allowlist |
| POST | `/scan` | org admin, analyst | `{targets: [ip or cidr]}` | steps, findings, guardrail events, SHA-256 per file; 403 if any target is outside the allowlist |

## Copilot

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/copilot` | `{question}` | `{answer, mode, grounded, latency_ms, tools[], evidence[], citations[], blocked, usage}`. `citations` lists the docs passages the answer cites; `blocked` lists figures or citations the guardrails rejected; `usage` holds token counts in Claude mode. Brokers can use only the coverage and docs-search tools |

## Admin (platform admin)

| Method | Path | Returns |
|---|---|---|
| GET | `/admin/overview` | users, jobs, feeds, copilot usage, open guardrails, alerts, audit size |
| GET | `/admin/guardrails` | events |
| GET | `/admin/audit` | last 200 entries |
| POST | `/admin/audit/verify` | `{ok, rows, head}` or `{ok:false, first_broken_id}` |
| POST | `/admin/feeds/simulate-kev-update` | `{message, before, after}` |
| POST | `/admin/feeds/reset` | `{state}` |

## Health

`GET /health` → `{ok, kev}` (no auth).
