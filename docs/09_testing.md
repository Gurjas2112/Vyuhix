# Testing

```bash
cd backend && python -m pytest -q      # 38 passed
cd frontend && npx tsc -b              # type-check
```

## What the 38 tests prove

| Area | Test | Why it matters |
|---|---|---|
| Reproducibility | same input ⇒ identical summary | Underwriting and audit need repeatable numbers |
| Statistics | P50 ≤ VaR95 ≤ CVaR95; relative standard error < 3% | The simulation is converged and coherent |
| Monotonicity | each of the 10 controls never raises EAL (10 tests) | Common random numbers make what-ifs exact |
| Attribution | path shares add up to EAL | "Trace this rupee" is complete |
| Paths | the hero path has the expected node order; cycles terminate | Correct and safe graph search |
| Validation | malformed model rejected, naming the bad node | Never invents data |
| Optimiser | plan ≤ budget; reported EAL equals re-simulation; within 5% of brute force over every subset at ₹3 L; frontier never worsens | The plan is real, not a surrogate artefact |
| Allowlist | 5 outside targets refused; lab targets allowed | Authorised scanning only |
| Injection | the Redis banner is quarantined and never stored as text | Untrusted text stays data |
| Grounding | invented figures rejected; tool figures, percentages and single digits accepted | The AI cannot make up numbers |
| Refusal | other organisations' questions refused | No fabricated comparisons |
| Formatting | Indian grouping, crore and lakh | The UI and the copilot agree |
| Auth | 401 without a token; wrong password; signup policy | Basic access control |
| Roles | broker sees quantiles only; viewer cannot scan; admin-only routes | Least privilege |
| Input | unknown fields and unknown controls → 422 | Strict contracts |
| Drift | simulated KEV raises EAL; reset restores | Continuous re-pricing works |
| Audit | a forged row is detected and its ID reported | Tamper evidence |

## End-to-end

`scripts/capture_walkthrough.py` drives every role through every page in a real Chromium browser and
fails if any step breaks. Its output is the screenshot set and the walkthrough video.
