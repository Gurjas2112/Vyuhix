### Copilot eval: offline

- **Pass rate: 65%** of 43 graded answers; 0 infrastructure errors
- Tool selection: 74% · drafts passing the guardrails unchanged: 100%
- Latency p50 0.0 s, p95 0.1 s

| Category | n | Pass |
|---|---|---|
| adversarial | 3 | 100% |
| figures | 8 | 75% |
| insurance | 4 | 25% |
| knowledge | 11 | 45% |
| plan | 5 | 80% |
| refusal | 4 | 75% |
| role | 2 | 50% |
| what-if | 6 | 83% |

Failures:

- `fig-04` (rep 0) failed facts: I can't answer that: I only have evidence for this organisation, not for What. Comparing would need their scans and loss data.
- `fig-06` (rep 0) failed facts: I can't answer that from this organisation's data or the Vyuhix docs. I can report the current loss summary, explain a path (for example "explain P1"), run a wh
- `wif-03` (rep 0) failed facts: I can't answer that from this organisation's data or the Vyuhix docs. I can report the current loss summary, explain a path (for example "explain P1"), run a wh
- `plan-02` (rep 0) failed facts: I can't answer that from this organisation's data or the Vyuhix docs. I can report the current loss summary, explain a path (for example "explain P1"), run a wh
- `ins-02` (rep 0) failed facts: From The risk model in plain words (The idea) [S1]: Add up each replayed year. Then: Number Meaning --- --- Expected annual loss (EAL) The average year. Useful 
- `ins-03` (rep 0) failed facts: Current limit ₹5.00 Cr; VaR95 ₹14.34 Cr; coverage gap ₹9.34 Cr; indicative limit to cover a 1-in-100-year loss ₹29.00 Cr; insurability score 20/100. Indicative 
- `ins-04` (rep 0) failed facts: I can't answer that: I only have evidence for this organisation, not for What. Comparing would need their scans and loss data.
- `kb-02` (rep 0) failed facts: From Problem Statement: Turning cyber-security evidence into rupee-denominated, insurable risk decisions (1. Background) [S1]: Indian organisations now run thei
- `kb-03` (rep 0) failed facts: From The risk model in plain words (Where step probabilities come from) [S1]: Step Probability --- --- Exploit a known vulnerability max(EPSS, 0.9 if in CISA KE
- `kb-06` (rep 0) failed facts: From How it works (6 · Decisions) [S1]: - Plan: for a budget, two methods propose a set of fixes and re-simulation picks the better one. - Insurance: loss tail 
- `kb-07` (rep 0) failed facts: From Security, privacy and compliance (Regulations considered) [S1]: Regulation Relevance How Vyuhix responds --- --- --- DPDP Act 2023 and DPDP Rules 2025 (not
- `kb-09` (rep 0) failed facts, cited: I can't answer that: I only have evidence for this organisation, not for What. Comparing would need their scans and loss data.
- `kb-10` (rep 0) failed facts, cited: I can't answer that: I only have evidence for this organisation, not for Board. Comparing would need their scans and loss data.
- `ref-04` (rep 0) failed refused: Current limit ₹5.00 Cr; VaR95 ₹14.34 Cr; coverage gap ₹9.34 Cr; indicative limit to cover a 1-in-100-year loss ₹29.00 Cr; insurability score 20/100. Indicative 
- `brk-02` (rep 0) failed facts: From User guide (Insurance (also visible to the broker)) [S1]: Insurability score, coverage gap, a recommended limit for a 1-in-100-year loss, and the chance a 