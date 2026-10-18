# The risk model in plain words

> "Where does ₹3.06 crore come from?" This page answers that, without equations first and with them after.

## The idea

Imagine replaying the next year 10,000 times.

- In each replay, attackers make a few **attempts** at each way in. On average that is 0.25 serious
  internet attempts a year, 0.5 successful phishes and 0.04 attempts by routes nobody can see. When the
  intrusion-detection system has seen probing in the last week, the internet figure doubles.
- For every attempt, each step an attacker could take **succeeds or fails**, like flipping a weighted coin.
  The weight is the step's probability. Because each step is flipped once per attempt, two routes that
  share a step succeed or fail together.
- If any route from that entry reaches a **crown jewel** (customer data, the loan ledger), the year
  takes a **loss**, made of six parts:

| Part | Demo range (low · likely · high) |
|---|---|
| Incident response and forensics | ₹50 L · ₹1.5 Cr · ₹5 Cr |
| Customer notification | ₹20 · ₹60 · ₹150 per record × 2,00,000 records |
| Downtime | 4 · 24 · 120 hours × revenue per hour |
| Ransom / extortion | 20% chance × ₹50 L · ₹2 Cr · ₹10 Cr |
| Regulatory (DPDP, forward-looking) | 10% chance × ₹50 L · ₹5 Cr · ₹50 Cr, capped at ₹250 Cr |
| Fraud (ledger only) | ₹20 L · ₹1.5 Cr · ₹8 Cr |

Add up each replayed year. Then:

| Number | Meaning |
|---|---|
| **Expected annual loss (EAL)** | The average year. Useful for budgeting |
| **P50** | The median year. Often ₹0, because most years nothing happens |
| **VaR95 (1-in-20-year loss)** | 19 years in 20 are better than this; useful for insurance limits |
| **CVaR95** | The average of the worst 1-in-20 years: how bad "bad" is |
| **VaR99 (1-in-100-year loss)** | Used for the recommended policy limit |
| **Chance of any loss** | Share of replayed years with any loss at all |

## Where step probabilities come from

| Step | Probability |
|---|---|
| Exploit a known vulnerability | max(EPSS, 0.9 if in CISA KEV and internet-facing) × exposure (1.0 internet, 0.3 internal) |
| Read a secret, use a stolen password, use a privilege | From the evidence (e.g. 1.0 for a database grant that exists; 0.35 for discovering a shared volume) |
| After a control | × the control's factor (patch → 0; MFA → 0.1; EDR → 0.6) |

**On EPSS.** EPSS estimates the probability of exploitation activity in the wild within 30 days. Vyuhix
uses it as a **prior** for "this step works", combined with KEV, exposure and controls. That is a
modelling choice; it is stated on screen and every value is editable.

## Who gets the blame: attribution

When an attempt reaches a crown jewel through several routes at once, that loss is split equally among
those routes. Summed over all years, each path's share is its **₹ per year**, and the shares add up
exactly to the EAL. That is what the "Trace this rupee" drawer shows.

## The maths, briefly

- Attempts per entry per year ~ Poisson(λ).
- Edge success per attempt ~ Bernoulli(pₑ), drawn once per edge per attempt.
- Path success = all its edges succeeded and the attempt came from its entry.
- Each loss component ~ PERT(a, m, b), sampled as a + (b − a)·Beta(1 + 4(m − a)/(b − a), 1 + 4(b − m)/(b − a)).
- Year loss = Σ over attempts and reached jewels of the sum of components.
- Standard error of EAL is reported; with 10,000 years it is about 2% on the demo.

## Choosing fixes

**Method A (fast):** an integer program that picks controls under the budget to "cover" as much
path-loss as possible, where each control covers a path by the fraction of probability it removes.
**Method B (careful):** add, one at a time, the control that removes the most *simulated* loss per rupee.
**Judge:** whichever plan has lower re-simulated EAL wins. On the budget frontier, a larger budget is never
allowed to show a worse result, because a cheaper plan is still affordable.

## Known limits

- Demo magnitudes are assumptions anchored to public data, not to an insurer's claims history.
- Edge probabilities are independent given the attempt. Attacker learning across attempts is not modelled.
- Downtime uses average revenue per hour; seasonality is ignored.
- Six hops is the path limit; longer chains exist but contribute little at these probabilities.
