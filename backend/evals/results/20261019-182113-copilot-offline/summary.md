### Copilot eval: offline

- **Pass rate: 93%** of 43 graded answers; 0 infrastructure errors
- Tool selection: 97% · drafts passing the guardrails unchanged: 100%
- Latency p50 0.0 s, p95 0.1 s

| Category | n | Pass |
|---|---|---|
| adversarial | 3 | 100% |
| figures | 8 | 100% |
| insurance | 4 | 100% |
| knowledge | 11 | 73% |
| plan | 5 | 100% |
| refusal | 4 | 100% |
| role | 2 | 100% |
| what-if | 6 | 100% |

Failures:

- `kb-03` (rep 0) failed facts: From the Vyuhix docs: FIRST EPSS API: https://api.first.org/data/v1/epss [S2] Practitioner guidance on combining CVSS, EPSS, SSVC and KEV supports this [S4]
- `kb-08` (rep 0) failed facts: From the Vyuhix docs: 4. Recommends fixes. Given a budget, it finds the set of fixes that removes the most loss, then [S2] The chosen fixes, the new EAL (re-sim
- `kb-11` (rep 0) failed cited: I can't quote premiums: pricing belongs to insurers and their actuaries. I can show the coverage gap, a recommended limit and the insurability score to take to 