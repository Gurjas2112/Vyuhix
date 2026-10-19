# Glossary

| Term | Meaning |
|---|---|
| **Attack path** | A chain of steps from an entry point to a crown jewel, e.g. exploit a web server → read a password file → log in to the database → read customer records |
| **ATT&CK** | MITRE's public catalogue of attacker techniques; every edge carries a technique ID such as T1190 (exploit public-facing application) |
| **Choke point** | A step that many high-loss paths pass through; fixing it removes the most loss |
| **Crown jewel** | Data or a system whose compromise causes the big losses (customer records, the loan ledger) |
| **CVaR95** | Average loss across the worst 5% of simulated years |
| **CVE** | A public identifier for a specific vulnerability, e.g. CVE-2021-41773 |
| **DPDP** | India's Digital Personal Data Protection Act 2023 and Rules 2025; substantive obligations and Board penalties from 13 May 2027, up to ₹250 crore |
| **EAL** | Expected annual loss: the average loss per year across all simulated years |
| **Edge** | One step an attacker can take, with a probability and evidence |
| **EPSS** | Exploit Prediction Scoring System (FIRST): estimated probability that a CVE is exploited in the wild in the next 30 days |
| **Evidence ID** | A stable reference to the finding that justifies an edge, e.g. `nuclei:CVE-2021-41773` |
| **FAIR** | Factor Analysis of Information Risk: loss event frequency × loss magnitude |
| **Frontier** | The curve of best achievable loss for each budget |
| **Citation check** | The rule that every `[S#]` label in a copilot answer must point at a passage the docs search returned |
| **Grounding check** | The rule that every number in a copilot answer must equal, by value, a number in that turn's tool output or in the user's question |
| **Hybrid search** | Docs retrieval that fuses keyword (BM25) and embedding rankings with reciprocal-rank fusion |
| **Insurability score** | 0–100, weighted by controls insurers ask about; evidenced counts fully, declared counts half |
| **KEV** | CISA's Known Exploited Vulnerabilities catalogue: CVEs confirmed exploited in the wild |
| **Loss-exceedance curve** | For each amount, the chance a year's loss is at least that much |
| **Monte Carlo** | Estimating outcomes by simulating many random scenarios |
| **RAG** | Retrieval-augmented generation: the copilot searches Vyuhix's docs and quotes the passages it found, with citations |
| **PERT distribution** | A range defined by low, most likely and high values |
| **Residual entry** | A deliberate allowance for routes no scan can see (insiders, zero-days) |
| **ROSI** | Return on security investment: (loss removed − cost) / cost |
| **VaR95** | 1-in-20-year loss: 95% of simulated years lose less than this |
| **VaR99** | 1-in-100-year loss; used for the recommended policy limit |
