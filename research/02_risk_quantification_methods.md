# 02 · Risk quantification methods

## FAIR as the backbone

The Open FAIR model decomposes risk into **loss event frequency** (how often a threat acts and succeeds)
and **loss magnitude** (what each event costs, split into primary and secondary losses). It is the most
widely used quantitative framework in cyber risk. Vyuhix follows its structure:

- frequency = entry attempts (Poisson) × path success (from edge probabilities);
- magnitude = incident response + notification + downtime + ransom + regulatory + fraud, each a PERT range.

## Monte Carlo over distributions

Point estimates hide the tail that insurance is about. Simulating many years gives the whole loss
distribution: mean (EAL), quantiles (VaR95, VaR99), tail mean (CVaR95) and the exceedance curve.
Cyentia's IRIS studies publish incident frequency and loss percentiles by organisation size and sector.
They are the natural public source for priors, and in production would be replaced by calibration on
claims and incident data.

## Why sample edges, not paths

Two paths that share an edge are **not independent**: if the shared step is blocked, both fail. Sampling
each edge once per attempt, and evaluating all paths on those samples, captures that dependence for free.
Independent path sampling would overstate the chance of loss whenever paths overlap, which in real
networks they almost always do.

## Common random numbers

When comparing "with control" and "without", using the same random draws makes the difference
reflect the control, not the noise. Vyuhix draws in an order that does not depend on the active
controls, which is why every control's effect is monotone in the tests.

## Optimisation

Choosing controls under a budget is a knapsack-like integer program. The exact objective (simulated EAL)
is non-linear because controls interact through shared paths. Vyuhix solves a linear **path-coverage
surrogate** with an integer program, runs a **simulation-verified greedy** search in parallel, and keeps
whichever plan re-simulates better. On the demo catalogue, tests confirm the result is within 5% of brute
force over every subset.

## Related work on AI-era risk and insurance

- arXiv 2512.08864 builds quantitative cyber-risk models mapped to MITRE ATT&CK, estimating parameters
  with Delphi studies and Monte Carlo, to measure how AI shifts attacker capability.
- arXiv 2606.16465 proposes **trace-based underwriting** for autonomous AI agents: per-trace risk scores
  feed claim probabilities and premiums, and pre-loss controls reduce tail risk. Vyuhix's roadmap uses
  this idea to treat deployed AI agents as insurable assets.

## Sources

- The Open Group, Open FAIR body of knowledge: https://www.opengroup.org/certifications/openfair
- Cyentia Institute, *Information Risk Insights Study 2025*: https://www.cyentia.com/iris2025/
- arXiv 2512.08864: https://arxiv.org/abs/2512.08864v1
- arXiv 2606.16465: https://arxiv.org/pdf/2606.16465
- PuLP: https://coin-or.github.io/pulp/ · HiGHS: https://highs.dev
