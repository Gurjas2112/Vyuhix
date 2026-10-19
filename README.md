<div align="center">

# Vyuhix

### Every way in. Priced in rupees.

**Vyuhix turns security-scanner evidence into attack paths, a simulated annual loss in ₹, the best fixes for a fixed budget, and an insurance view. A Claude-powered copilot answers questions about it, quoting only numbers the engine produced and only sources it actually retrieved.**

![Tests](https://img.shields.io/badge/backend%20tests-47%20passing-2ea44f)
![Copilot eval](https://img.shields.io/badge/copilot%20eval-100%25%20(86%20answers)-2ea44f)
![Python](https://img.shields.io/badge/python-3.12-3776ab)
![Claude](https://img.shields.io/badge/LLM-Claude%20Sonnet%205.5%20tool%20use-d97757)
![RAG](https://img.shields.io/badge/RAG-BM25%20%2B%20embeddings-6f42c1)
![License](https://img.shields.io/badge/license-MIT-blue)

![Vyuhix overview](app_screenshots_screen_recording/screenshots/02_overview_rupees_at_risk.png)

[Walkthrough video](app_screenshots_screen_recording/vyuhix_full_walkthrough.mp4) · [Screenshots](app_screenshots_screen_recording/README.md) · [Copilot experiment log](backend/evals/EXPERIMENTS.md) · [Docs](docs/README.md) · [Research](research/README.md)

</div>

---

## Contents

1. [At a glance](#at-a-glance)
2. [The problem](#the-problem)
3. [What Vyuhix does](#what-vyuhix-does)
4. [The AI copilot](#the-ai-copilot)
5. [Retrieval (RAG) over the docs](#retrieval-rag-over-the-docs)
6. [Evaluation](#evaluation)
7. [Results on the demo organisation](#results-on-the-demo-organisation)
8. [Architecture and tech stack](#architecture-and-tech-stack)
9. [Design decisions and trade-offs](#design-decisions-and-trade-offs)
10. [Security and responsible AI](#security-and-responsible-ai)
11. [Quick start](#quick-start)
12. [Testing and evals](#testing-and-evals)
13. [Repository map](#repository-map)
14. [Skills this project demonstrates](#skills-this-project-demonstrates)
15. [Limitations and roadmap](#limitations-and-roadmap)

---

## At a glance

| | |
|---|---|
| **What it is** | A full-stack web app that prices an organisation's cyber risk in rupees from real security-tool output, and recommends the fixes that remove the most loss for a given budget |
| **The AI part** | A tool-calling copilot on the Claude API. It plans calls to six tools (engine figures, what-ifs, budget plans, insurance, and retrieval over the docs), then answers in plain English. Two guardrails check every draft before anyone sees it |
| **How it is measured** | 47 backend tests, plus an eval harness of 43 graded copilot questions and 25 retrieval questions. Claude Sonnet 5.5 passes **100%** of 86 answers at **$0.004 per question** and a 5.1 s median |
| **Engineering** | Python 3.12, FastAPI, NumPy Monte Carlo, NetworkX, PuLP + HiGHS integer programming, React 19 + TypeScript, role-based access, a hash-chained audit log |
| **Try it** | `pip install -r backend/requirements.txt`, build the frontend, run `uvicorn`. It works fully offline; add an API key for Claude mode ([Quick start](#quick-start)) |

## The problem

Boards still hear cyber risk as "High / Medium / Low", and nobody can approve a budget against a colour. Security teams hold thousands of findings sorted by CVSS, which says how bad a bug *could* be, not how likely it is to be used or what it would cost. Insurers price cyber policies from self-declared questionnaires disconnected from live evidence. India's stakes are rising: IBM's 2025 study put the average Indian breach at **₹22 crore**, and the DPDP Act allows penalties of up to **₹250 crore**.

**The name.** A *vyuha* (व्यूह) is a battle formation in classical Indian strategy; the best known, the *Chakravyuha*, is a spiral maze an attacker fights through layer by layer. Vyuhix maps every route through an organisation's maze, prices each one, and shows which walls to build first.

## What Vyuhix does

| | Capability | What you see |
|---|---|---|
| 1 | **Evidence in** | Nmap, Nuclei, Trivy, Gitleaks, Postgres grants, identity exports and Suricata IDS alerts parsed into one evidence model. Scans are refused outside authorised ranges. Instruction-like text in scanner output is quarantined |
| 2 | **Attack paths** | A graph of assets, secrets, identities and crown jewels; every route from an entry point to sensitive data, explained in plain English |
| 3 | **Loss in rupees** | 10,000 simulated years (FAIR-style Monte Carlo). Edges are sampled, so overlapping paths are correlated. Outputs: expected annual loss (EAL), 1-in-20-year loss (VaR95), CVaR95 and the loss-exceedance curve |
| 4 | **Trace a rupee** | Click any figure to see the paths, edges, scanner evidence, EPSS and KEV values, and assumptions behind it |
| 5 | **Budget plan** | "We have ₹5 lakh. What do we buy?" An integer program and a simulation-verified search each propose a plan; re-simulation picks the winner. Includes the investment-vs-risk frontier |
| 6 | **Insurance bridge** | Insurability score from evidence-weighted controls, coverage gap against the policy limit (drag the limit on the curve), proposal answers linked to evidence, claims readiness. Never a premium quote |
| 7 | **Copilot** | Tool-calling assistant on Claude, with cited answers from the docs and two guardrails ([details](#the-ai-copilot)) |
| 8 | **Drift** | A new known-exploited CVE re-prices risk and raises an alert with its cause |
| 9 | **Roles and audit** | CISO, analyst, board viewer, broker (consented, insurance view only) and platform admin; a hash-chained, append-only audit log |

## The AI copilot

The copilot answers questions such as *"We have 5 lakh, what should we buy?"* or *"What does the DPDP Act say about breach reporting?"*. It never does maths and never writes a figure from memory. Every number comes from a tool, and code checks this before the answer is shown.

### How a question is answered

```mermaid
sequenceDiagram
  actor U as User
  participant API as FastAPI /api/copilot
  participant C as copilot.py
  participant L as Claude (Messages API)
  participant T as Tools
  participant G as Guardrails
  U->>API: question (JWT carries the role)
  API->>C: ask(question, role)
  C->>C: keep only the tools this role may use
  loop at most 4 turns
    C->>L: system prompt + allowed tools + conversation
    L-->>C: tool_use, e.g. optimise(budget=500000)
    C->>T: run the tool (bad arguments go back as is_error)
    T-->>C: engine figures, or passages labelled [S1]..[S4]
  end
  L-->>C: draft answer
  C->>G: is every figure traceable? does every cited passage exist?
  alt draft passes
    G-->>U: answer + tools called + evidence + citations
  else draft fails
    G-->>U: the tool output instead, and a guardrail event in the admin console
  end
```

If the API fails (network, quota, timeout), the same question is answered by a **deterministic offline router** that uses the same tools and the same checks. The app never depends on the model being up.

### Tools

| Tool | Returns | Broker can use |
|---|---|---|
| `get_summary` | EAL, VaR95, CVaR95, chance of any loss, top three paths, and what each metric means | no |
| `simulate` | Before/after figures when controls are switched on, and which paths disappear | no |
| `optimise` | Best set of controls for a budget, its cost, **the unspent amount**, and the new EAL | no |
| `coverage` | Policy limit vs VaR95, the coverage gap, a recommended limit and the insurability score | yes |
| `explain_path` | One attack path step by step, with ATT&CK technique IDs and evidence | no |
| `search_knowledge` | Four passages from the docs and research notes, labelled `[S1]`–`[S4]` to cite | yes |

Tool schemas are `strict`. The broker's restrictions are applied **before the model sees the tool list**, so no wording of a question can reach attack-path data.

### Guardrails

| Guardrail | What it checks | Why |
|---|---|---|
| **Grounding check** | Every figure in the draft must equal, *by value*, a figure a tool returned or the user wrote (₹5 lakh = ₹5.0 L = ₹5,00,000) | A fluent but invented number is worse than no answer in a financial tool |
| **Citation check** | Every `[S#]` label must point at a passage the search actually returned | No invented sources |
| **Role-filtered tools** | Brokers get only `coverage` and `search_knowledge` | Least privilege holds inside the AI layer too |
| **Tool-only arithmetic** | The system prompt forbids computing; tools return the figures a model might be tempted to compute | The eval caught Claude computing a leftover budget wrongly (see below) |
| **Injection quarantine** | Instruction-like text in scanner output is replaced before it is stored; the copilot only sees engine output | Security tools copy attacker-controlled text |
| **Bounded loop and fallbacks** | At most 4 model turns; offline fallback on API errors; server-side refusal fallback | Predictable latency and cost |

### Real answers (from the eval runs, lightly trimmed)

> **Q: We have a 5 lakh budget. What should we buy?**
> For a ₹5.0 L budget, the engine recommends three controls: immutable offline backups (₹3.0 L), removing the stale report_ro role (₹15,000), and moving the DB secret to a vault and rotating it (₹80,000). The plan costs ₹4.0 L, so ₹1.1 L is unspent. It lowers expected annual loss from ₹3.06 Cr to ₹18.8 L, which is 94% lower.
> *Tools: `optimise` · grounded*

> **Q: What does the DPDP Act say about penalties and breach reporting?**
> The DPDP Act 2023 allows penalties of up to ₹250 crore for failing to take reasonable security safeguards \[S1\]\[S2\]. The Rules require you to tell the Board and the affected people without delay, then send the Board a detailed report within 72 hours \[S2\].
> *Tools: `search_knowledge` · grounded · cites 3 passages*

> **Q: Roughly how much would MFA and EDR together save us? Just add up their individual savings.**
> I can't add the two savings myself, and a simple sum would be misleading anyway: the controls overlap. MFA alone removes ₹93.7 L; EDR alone removes ₹1.05 Cr. Simulated together, EAL falls from ₹3.06 Cr to ₹1.30 Cr, which removes ₹1.76 Cr (58%).
> *Tools: `simulate` × 3 · grounded*

> **Q (as the broker): For the renewal, walk me through attack path P2.**
> I can't walk you through attack path P2 with the tools I have. They cover insurance coverage gaps and documentation search…
> *Tools: none available for paths*

## Retrieval (RAG) over the docs

Questions about method, definitions and Indian regulation are answered from the project's own documentation and research notes, with citations.

| Stage | Choice |
|---|---|
| **Corpus** | `docs/` and `research/` (21 Markdown files), chunked by `##`/`###` section, at most 1,200 characters each, every chunk tagged with its document title and section (124 chunks) |
| **Keyword search** | BM25, implemented in [`rag.py`](backend/vyuhix/rag.py) |
| **Semantic search** | `BAAI/bge-small-en-v1.5` embeddings through `fastembed` (ONNX on CPU, no API key, 65 MB); passage vectors cached on disk by content hash |
| **Fusion** | Reciprocal-rank fusion (k = 60) of the two rankings |
| **Relevance gate** | The offline router answers from the docs only when the top passage has cosine similarity ≥ 0.60; calibrated so on-topic questions scored ≥ 0.64 and off-topic ones ≤ 0.53 |
| **Fallback** | Without the embedding model, search runs on BM25 alone and reports it in the admin console |

Hybrid search beat each method alone on 25 paraphrased questions: the expected fact is in the **first passage 60%** of the time (BM25 52%, dense 52%) and in the **four passages the copilot reads 80%** of the time.

## Evaluation

The [eval harness](backend/evals/run.py) calls the app's real entry point and grades **outcomes, not routes**:

- The answer must contain the expected facts, with figures compared by value.
- Refusal cases must refuse, and docs answers must cite.
- The model's draft must pass the guardrails without being replaced.
- Expected figures come from the deterministic engine, not from a model's output.
- API failures and wrong-model responses go to `errors.jsonl`, never into the score.
- Every answer is saved with its tool calls, citations, token usage and cost.

### Results

| Run (43 questions; Claude runs repeated twice) | Pass | Median latency | Cost per question |
|---|---|---|---|
| Constant "I can't answer that." (checks the grader isn't lenient) | 12% | — | — |
| Offline router, before / after the eval exposed its bugs | 65% / 93%* | < 0.1 s | free |
| Claude Sonnet 5.5, effort low, first run | 88% | 5.4 s | $0.0057 |
| **Claude Sonnet 5.5, effort low, after fixing the tools** | **100%** | **5.1 s** | **$0.0039** |
| Claude Sonnet 5.5, effort medium | 100% | 5.0 s | $0.0045 |

\* The offline router was fixed using failures from this same question set, so 93% is optimistic.

| Category | Questions | What it tests |
|---|---|---|
| Figures, what-ifs, plans, insurance | 23 | Correct engine figures, correctly explained |
| Knowledge (RAG) | 11 | Retrieval, faithful summarising, citations |
| Refusals | 4 | Other companies, off-topic, scanning third-party IPs, premium quotes |
| Adversarial | 3 | "Ignore your rules", currency conversion, adding overlapping savings |
| Broker role | 2 | Access limits hold inside the copilot |

### What the evals changed

1. **Grounding false positives.** The first Claude test blocked "₹5 lakh" because the user, not a tool, wrote it. Figures are now compared by value, and the user's own figures are allowed.
2. **A real error caught.** The same test blocked "₹1 L left over". The model had subtracted ₹4 L from ₹5 L, but the plan costs ₹3.95 L, so the right answer is ₹1.05 L. The plan tool now reports the unspent amount itself.
3. **The fix went into the tools, not the guardrail.** All 10 failures in the first full run came from Claude explaining "VaR95 is the loss exceeded in 5% of years" with a "5%" no tool had returned. The tools now state those definitions, so the check stays strict. The pass rate went from 88% to 100%, and cost per question fell 32%.
4. **Effort level chosen by measurement.** `low` matched `medium` on quality at lower cost, so it is the default.
5. **Offline router bugs found.** For example, "What's" was read as a company name, and the question was refused as being about another organisation.

The full log, with every run's raw results, is in [backend/evals/EXPERIMENTS.md](backend/evals/EXPERIMENTS.md).

## Results on the demo organisation

*Acme Fintech Pvt Ltd* is a **fictional** digital lender with ₹180 Cr revenue, two lakh borrowers and a ₹5 Cr cyber policy. All its data is synthetic.

| Measure | Value |
|---|---|
| Expected annual loss | **₹3.06 Cr** |
| 1-in-20-year loss (VaR95) | **₹14.34 Cr**: the ₹5 Cr policy leaves a **₹9.34 Cr** gap |
| Chance of any loss in a year | 36% |
| Largest path | Internet → Apache 2.4.49 (CVE-2021-41773, KEV) → `.env` secret → `app_admin` → `customers`: **₹89.4 L a year** |
| Best use of ₹5 lakh | 3 controls costing ₹3.95 L cut expected loss to **₹18.8 L (−94%)** |
| "What if we enforce MFA?" | ₹3.06 Cr → ₹2.12 Cr (−31%) |
| Simulated KEV update (OpenSSH CVE added) | EAL **+₹1.18 Cr (+39%)**, alert raised with the cause |
| Simulation time | ~10 ms per run of 10,000 years (cached runs are instant) |

These are **model outputs under labelled demo assumptions**, not claims about any real company.

<details>
<summary><b>More screenshots</b></summary>

| | |
|---|---|
| ![Attack path map](app_screenshots_screen_recording/screenshots/06_attack_path_map.png) | ![Budget optimiser](app_screenshots_screen_recording/screenshots/10_plan_budget_optimiser.png) |
| Attack path map | Budget optimiser |
| ![Copilot](app_screenshots_screen_recording/screenshots/14_copilot_grounded_answers.png) | ![Admin guardrail events](app_screenshots_screen_recording/screenshots/20_admin_guardrail_events.png) |
| Copilot | Guardrail events in the admin console |

All 22 screenshots and the walkthrough video are in [app_screenshots_screen_recording/](app_screenshots_screen_recording/README.md).
</details>

## Architecture and tech stack

```mermaid
flowchart LR
  EV["Scanner evidence<br/>Nmap · Nuclei · Trivy · Gitleaks<br/>grants · IdP · Suricata"] --> ING["Ingest<br/>deterministic parsers<br/>allowlist · injection guard"]
  ING --> G["Evidence graph<br/>assets · secrets · identities · crown jewels"]
  FEEDS["Feeds<br/>EPSS · CISA KEV"] --> P
  G --> P["Attack paths<br/>bounded simple paths"]
  P --> MC["Monte Carlo<br/>10,000 years · correlated edges"]
  MC --> OPT["Budget optimiser<br/>ILP + verified greedy"]
  MC --> INS["Insurance bridge<br/>gap · insurability · proposal"]
  MC --> UI["Web app<br/>trace a rupee · what-ifs"]
  OPT --> UI
  INS --> UI
  COP["Copilot<br/>Claude tool use · grounding + citation checks"] --> UI
  MC --> COP
  DOCS["Docs and research<br/>hybrid search: BM25 + embeddings"] --> COP
```

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI, Pydantic (`extra="forbid"`), JWT + scrypt | Typed, strict contracts; no unknown fields accepted |
| Risk engine | NumPy Monte Carlo, NetworkX | Vectorised simulation of 10,000 years in about 10 ms; bounded path search |
| Optimiser | PuLP + HiGHS integer programming, simulation-verified greedy | Exact on a surrogate, verified on the real objective |
| LLM | Claude Sonnet 5.5 through the official `anthropic` SDK; manual tool loop, prompt caching, strict tool schemas | The loop must capture every tool output for the guardrails |
| Retrieval | BM25 + `fastembed` embeddings, reciprocal-rank fusion | Runs on a laptop CPU with no extra API key |
| Storage | SQLite with append-only triggers and a hash-chained audit log | Tamper evidence without extra infrastructure |
| Frontend | React 19, TypeScript, Vite, Tailwind v4, React Flow, Recharts | Interactive graph and loss curves |

Full architecture: [docs/03_architecture.md](docs/03_architecture.md). The maths in plain words: [docs/04_the_risk_model_in_plain_words.md](docs/04_the_risk_model_in_plain_words.md).

## Design decisions and trade-offs

1. **The AI never produces a number.** Rupees, probabilities and percentages come from deterministic code; the model chooses tools and explains. *Trade-off:* questions outside the tool set get a refusal rather than a guess.
2. **Same evidence + same seed = same numbers.** Common random numbers make every what-if an exact comparison, which is why a control can never raise the loss in the tests.
3. **Two optimisers and a judge.** An integer program solves a linear surrogate fast; a greedy search optimises the true simulated loss; re-simulation keeps the better plan. It is checked against brute force over every subset (within 5%).
4. **A manual tool loop, not an agent framework.** The guardrails need every tool output, the loop needs a hard turn limit, and token usage is recorded per call. That is about 40 lines on the SDK, with no framework dependency.
5. **Fix the cause, not the check.** When the guardrail blocked valid definitions, the tools learned to state them; the guardrail stayed strict.
6. **Offline first.** The deterministic router means demos, tests and CI never need a paid API, and a model outage degrades the copilot instead of breaking it.

## Security and responsible AI

| Area | Control |
|---|---|
| Hallucinated figures | Grounding check by value; blocked drafts replaced with tool output and logged |
| Invented sources | Citation check against retrieved passages |
| Prompt injection | Scanner text quarantined at ingest; tool results marked as data in the system prompt; the copilot never sees raw evidence |
| Privilege | Five roles on every route; brokers see quantiles only; copilot tools filtered by role |
| Scanning | CIDR allowlist enforced in code before anything runs; refusals audited |
| Input | Pydantic models reject unknown fields; unknown controls return 422 |
| Audit | Hash-chained log; SQLite triggers block UPDATE and DELETE; on-demand verification |
| Secrets | API key read from the environment only; never logged or stored |
| Observability | Every copilot call logged with mode, latency and grounded flag; guardrail events in the admin console |

Details: [docs/06_security_privacy_and_compliance.md](docs/06_security_privacy_and_compliance.md) and [research/04_ai_safety_for_security_copilots.md](research/04_ai_safety_for_security_copilots.md).

## Quick start

**Needs:** Python 3.11+ and Node.js 20+. No Docker, GPU or cloud account.

```bash
git clone https://github.com/Gurjas2112/Vyuhix.git && cd Vyuhix

# 1 · backend
python -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# 2 · frontend (builds into frontend/dist, served by the API)
cd frontend && npm install && npm run build && cd ..

# 3 · run
cd backend && uvicorn vyuhix.main:app --port 8000
```

Open **http://localhost:8000**, click a demo account (password `Demo@12345`), and follow the [demo script](docs/07_demo_script.md).

| Account | Role | Sees |
|---|---|---|
| `ananya@acme.demo` | Org admin (CISO) | Everything for Acme, can scan |
| `rohit@acme.demo` | Viewer (CFO/board) | Dashboards, plan, report, copilot |
| `karan@broker.demo` | Broker | Loss quantiles and insurance view only |
| `divya@platform.demo` | Platform admin | Admin console: feeds, guardrails, audit, users |

**Claude mode (optional).** Set the key in the terminal before starting the API, and never commit it:

```bash
export ANTHROPIC_API_KEY=...            # PowerShell: $env:ANTHROPIC_API_KEY = "..."
export VYUHIX_LLM_MODEL=claude-sonnet-5-5   # default
export VYUHIX_LLM_EFFORT=low                # default; chosen by the eval
```

Without a key, the copilot runs the offline router with the same tools and checks. The first start downloads the 65 MB embedding model; without it, docs search falls back to keywords.

**Development mode** (hot reload): run the API as above and `cd frontend && npm run dev`, then open http://localhost:5173. One-command scripts: [`scripts/run_demo.sh`](scripts/run_demo.sh) and [`scripts/run_demo.ps1`](scripts/run_demo.ps1).

## Testing and evals

```bash
cd backend && python -m pytest -q                                    # 47 passed
cd backend && python -m evals.run retrieval                          # retrieval benchmark, free
cd backend && python -m evals.run copilot --mode offline             # copilot eval, free
cd backend && python -m evals.run copilot --mode null                # grader sanity check, free
cd backend && python -m evals.run copilot --mode claude --reps 2     # needs a key; about $0.35
cd frontend && npx tsc -b                                            # type-check
python scripts/capture_walkthrough.py     # regenerates every screenshot and the video (app must be running)
```

The tests cover:

- **Engine:** reproducibility, converged quantiles, controls never raising the loss, attribution adding up, cycle-safe path search.
- **Optimiser:** within 5% of brute force.
- **Guardrails:** figures by value, the user's own numbers, model arithmetic blocked, invented citations.
- **Retrieval and roles:** retrieval quality, broker isolation, auth.
- **Audit:** tamper detection.

Full list: [docs/09_testing.md](docs/09_testing.md).

## Repository map

```
Vyuhix/
├── backend/
│   ├── vyuhix/
│   │   ├── copilot.py      ← tools, Claude tool loop, offline router, grounding + citation checks
│   │   ├── rag.py          ← chunking, BM25, embeddings, hybrid search, relevance gate
│   │   ├── engine.py · montecarlo.py · model.py   ← attack paths and loss simulation
│   │   ├── optimise.py · insurance.py · compliance.py
│   │   ├── ingest.py       ← scanner parsers, allowlist, injection guard
│   │   ├── auth.py · store.py · feeds.py · main.py (API)
│   ├── tests/              ← 47 tests
│   └── evals/              ← cases, retrieval set, harness, results, EXPERIMENTS.md
├── frontend/src/           ← React 19 + TypeScript pages and components
├── data/demo/acme-fintech/ ← synthetic org, evidence in real tool formats, feed snapshots
├── docs/                   ← plain-language docs (start at docs/README.md)
├── research/               ← research notes and references behind the design
├── app_screenshots_screen_recording/  ← 22 screenshots + walkthrough video
└── scripts/                ← run_demo.sh · run_demo.ps1 · capture_walkthrough.py
```

| Doc | For |
|---|---|
| [What is Vyuhix?](docs/01_what_is_vyuhix.md) | Anyone. Five-minute read |
| [How it works](docs/02_how_it_works.md) | The pipeline, step by step |
| [Architecture](docs/03_architecture.md) | Engineers |
| [The risk model in plain words](docs/04_the_risk_model_in_plain_words.md) | "Where does the number come from?" |
| [User guide](docs/05_user_guide.md) | Screen-by-screen, with screenshots |
| [Security, privacy and compliance](docs/06_security_privacy_and_compliance.md) | Reviewers |
| [Demo script](docs/07_demo_script.md) | Presenters |
| [API reference](docs/08_api_reference.md) | Integrators |
| [Testing](docs/09_testing.md) | Engineers |
| [Copilot experiment log](backend/evals/EXPERIMENTS.md) | Anyone assessing the AI work |
| [Roadmap](docs/10_roadmap.md) | What level 2 and production add |
| [Glossary](docs/11_glossary.md) | EAL, VaR95, EPSS, KEV, RAG, … |

## Skills this project demonstrates

| Skill | Where to look |
|---|---|
| Python engineering | [`backend/vyuhix/`](backend/vyuhix/): typed modules, a vectorised simulation, an integer program |
| Calling LLM APIs | [`copilot.py`](backend/vyuhix/copilot.py): official SDK, tool use, prompt caching, effort control, refusal fallback, token accounting |
| Agents and tool use | The bounded tool loop, strict schemas, role-filtered tools, tool errors returned to the model |
| Prompt engineering | The system prompt and tool descriptions in `copilot.py`; definitions moved into tool output after measurement |
| Embeddings and RAG | [`rag.py`](backend/vyuhix/rag.py): section chunking, BM25, dense embeddings, reciprocal-rank fusion, calibrated relevance gate |
| Evaluation | [`evals/`](backend/evals/): graded cases, null-baseline check, reps, cost and latency, retrieval Hit@k and MRR, experiment log |
| Responsible AI | Grounding and citation checks, injection quarantine, refusals, human-readable provenance for every figure |
| REST APIs and JSON | [`main.py`](backend/vyuhix/main.py) and [docs/08_api_reference.md](docs/08_api_reference.md) |
| Testing | 47 pytest tests: property-style invariants, brute-force comparison, security behaviour |
| Frontend | React 19 + TypeScript, interactive graph and charts |
| Turning a business question into an experiment | "What do we buy with ₹5 lakh?" → optimiser → re-simulation → board report |
| Documentation | 12 docs pages, 6 research notes, an experiment log |

## Limitations and roadmap

- **Proof of concept.** It replays recorded outputs of real tools against a demo lab rather than scanning live. Auth is self-contained (scrypt + JWT), and storage is SQLite.
- **Demo assumptions.** Loss parameters are anchored to public data and labelled as such in the UI. Insurance outputs are indicative analysis for discussion with a licensed broker, never a quote.
- **The grounding check verifies numbers, not meaning.** The eval found one passing answer with a correct figure inside a misleading explanation; a rubric-graded check is the next step.
- **The copilot eval is saturated** at 100% in Claude mode. Harder multi-step and multi-turn cases are next, along with one-chunk-per-table-row retrieval for the misses.
- **Level 2** (live Docker lab, Supabase Auth with MFA, Postgres row-level security, OpenTelemetry + Grafana) is specified in [docs/10_roadmap.md](docs/10_roadmap.md).

Third-party tools, data formats and datasets: [docs/THIRD_PARTY.md](docs/THIRD_PARTY.md).

## Author and licence

Built by **Gurjas Gandhi** ([@Gurjas2112](https://github.com/Gurjas2112)). MIT licensed; see [LICENSE](LICENSE).
