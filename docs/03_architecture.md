# Architecture

## Components

```mermaid
flowchart TB
  subgraph Browser
    SPA["React 19 SPA<br/>React Flow · Recharts · Tailwind v4"]
  end
  subgraph API["FastAPI (Python)"]
    AUTH["auth.py<br/>scrypt · JWT · roles · throttling"]
    ROUTES["main.py<br/>REST routes · strict request models · security headers"]
    ING["ingest.py<br/>allowlist · parsers · injection guard"]
    ENG["engine.py<br/>orchestration · cache · diff · choke points"]
    MOD["model.py<br/>validation · edge probabilities · paths"]
    MC["montecarlo.py<br/>correlated simulation · attribution"]
    OPT["optimise.py<br/>ILP (PuLP + HiGHS) · verified greedy · frontier"]
    INS["insurance.py · compliance.py"]
    COP["copilot.py<br/>tools · offline router · Claude mode · grounding + citation checks"]
    RAG["rag.py<br/>docs index · BM25 + embeddings · hybrid search"]
    FEED["feeds.py<br/>KEV / EPSS snapshots · SOC signal"]
    ST["store.py<br/>SQLite · hash-chained audit"]
  end
  DATA[("data/demo/acme-fintech<br/>evidence · feeds · assumptions")]
  SPA -- "/api (JWT)" --> ROUTES
  ROUTES --> AUTH & ING & ENG & OPT & INS & COP
  COP --> RAG
  ENG --> MOD --> MC
  OPT --> ENG
  INS --> ENG
  COP --> ENG & OPT & INS
  ENG --> FEED
  ING & FEED & MOD --> DATA
  AUTH & ING & COP & ROUTES --> ST
```

## Design decisions

| Decision | Why |
|---|---|
| **Deterministic engine; AI at the edges** | Underwriters, auditors and regulators need reproducible numbers. The AI explains; it cannot change a figure |
| **Sample edges, not paths** | Paths that share a step must fail together. Sampling paths independently would overstate risk |
| **Common random numbers** | Random draws do not depend on which controls are on, so "before vs after" differences are exact rather than noise |
| **A residual entry** | Scans never see everything. Modelling the unseen keeps the optimiser from claiming zero risk |
| **ILP and greedy, verified by simulation** | The fast linear surrogate can over-credit overlapping controls. Re-simulation is the judge, and the frontier is forced to be monotone |
| **LRU cache keyed by an input hash** | Toggling a control back is instant; the same hash always gives the same answer |
| **Strict request models** (`extra="forbid"`) | Unknown fields are rejected, not ignored |
| **SQLite with an append-only audit log** | No infrastructure to install. Triggers block UPDATE and DELETE; a hash chain detects tampering anyway |
| **Built SPA served by the API** | One process, one port, works offline |

## Data model (level 1)

| Store | Content |
|---|---|
| `data/demo/<org>/*.json` | Organisation, graph, controls, assumptions (versioned in git) |
| `data/demo/<org>/evidence/` | Tool outputs (synthetic, real formats) |
| `data/demo/<org>/feeds/` | KEV and EPSS snapshots, plus the labelled simulated update |
| `data/runtime/vyuhix.db` | users · audit_log · guardrail_events · jobs · alerts · copilot_calls · state |

## Performance

A 10,000-year run of the demo graph takes about 10 ms. A budget plan with re-simulation takes 0.1–0.4 s.
The frontier takes about 0.4 s. All runs are cached by input hash.

## Level 2 architecture

Level 2 adds a live Docker lab, Supabase (Auth with TOTP MFA, Postgres with row-level security, Storage),
OpenTelemetry with Grafana, and a job worker. See [the roadmap](10_roadmap.md).
