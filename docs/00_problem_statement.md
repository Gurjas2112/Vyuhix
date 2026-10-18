# Problem Statement: Turning cyber-security evidence into rupee-denominated, insurable risk decisions

**Theme:** AI & Cybersecurity · **Track:** Innovative Solution for AI & Cybersecurity
**Team:** Runtime Renegades (Gurjas Gandhi, Sumedh Khedekar) · **Solution:** Vyuhix

## 1. Background

Indian organisations now run their business on digital infrastructure: cloud applications, internet-facing services, remote access, third-party integrations and large stores of customer data. The cost of a breach has risen with it. IBM's 2025 study put the average Indian data breach at a record **₹22 crore**. Under the DPDP Act 2023, failing to take reasonable security safeguards can cost up to **₹250 crore**, and those penalties can be enforced from **13 May 2027** under the DPDP Rules 2025. CERT-In requires incidents to be reported within **6 hours**.

Organisations already collect a lot of security evidence: vulnerability scans, cloud and identity configurations, secret-scanning results, database permissions and SOC alerts. Cyber insurance is becoming a standard part of risk management. Yet the people who must act on cyber risk still lack one shared, trustworthy answer to a simple question: **"How much could this cost us, why, and what should we do about it?"**

## 2. The problem

Cyber risk is measured in the wrong units, scored one finding at a time, and kept separate from the financial and insurance decisions it should drive.

1. **Risk is reported in colours, not money.** Boards and CFOs see "High / Medium / Low" heatmaps. They cannot approve a budget, set an insurance limit or compare cyber risk with other business risks using a colour.
2. **Findings are scored in isolation.** Security teams get thousands of findings ranked by CVSS severity, which describes how bad a flaw *could* be, not how likely it is to be used or what it would cost. Real attacks chain several weaknesses. For example: an exposed web flaw → a readable configuration file → a database password → bulk access to customer records. A "medium" finding on such a chain matters more than a "critical" one on an isolated machine, and per-finding scoring cannot show this.
3. **Spending is not optimised.** With a fixed budget, teams cannot show which combination of fixes removes the most expected loss per rupee, so money follows intuition, vendor pressure or the longest list.
4. **Insurance is disconnected from evidence.** Cyber policies are typically priced from self-declared questionnaires. Policy limits are rarely compared with the organisation's own tail loss, and security improvements rarely flow back into the insurance conversation in a measurable way.
5. **Risk goes stale silently.** When a vulnerability starts being exploited in the wild (for example, it is added to CISA's Known Exploited Vulnerabilities list), an organisation's risk changes overnight. Periodic, manual assessments miss this.
6. **AI assistants add a new risk.** Language-model copilots in security tools can produce fluent but invented figures. Security tools also copy attacker-controlled text (service banners, file contents) into their output, which can be used to manipulate a model (prompt injection). In a financial decision, an untraceable number is worse than none.

## 3. Who is affected

| Stakeholder | Question they cannot answer today |
|---|---|
| CISO / security team | Which attack paths matter most, and what do we fix first? |
| CFO / board | What is our exposure in rupees, and what does a given budget buy? |
| Insurance broker / underwriter | Is this organisation's evidence good enough, and is the policy limit adequate? |
| Compliance / risk officer | Are we meeting DPDP, CERT-In, RBI and ISO 27001 expectations, and where is the gap? |
| Security platform operators | Are our data feeds current, and is the AI behaving safely? |

## 4. Why existing approaches fall short

- **Vulnerability scanners and dashboards** list and rank findings, but do not connect them into paths or translate them into money.
- **Attack-path tools** show routes, but rarely put a price on them or link them to budget and insurance decisions.
- **Risk-quantification spreadsheets and point estimates** are manual and periodic. They hide uncertainty and cannot be traced back to evidence.
- **Questionnaire-based underwriting** relies on self-declaration rather than verified controls.
- **AI copilots without guardrails** can hallucinate figures and are exposed to prompt injection through security data.

## 5. Objective

Build an AI-assisted platform that:

1. **Ingests real security evidence** from standard tool formats (port and service scans, vulnerability checks, image and configuration scans, secret scans, database grants, identity exports, IDS alerts) into one validated model, scanning only authorised targets.
2. **Discovers multi-step attack paths** from entry points (internet, phished users, unmodelled routes) to crown-jewel data, and explains each in plain language.
3. **Quantifies risk in rupees, with uncertainty**: expected annual loss, 1-in-20-year loss (VaR95), tail loss (CVaR95) and a loss-exceedance curve. Likelihood comes from exploit-prediction (EPSS) and known-exploitation (KEV) signals, exposure and controls. Losses are India-specific: incident response, notification, downtime, ransom, DPDP penalties and fraud.
4. **Makes every figure traceable** to the paths, steps, evidence, feed values and assumptions behind it.
5. **Recommends the best set of fixes for a given budget**, verified by re-simulation, and shows where extra spending stops paying off.
6. **Bridges security to insurance**: an evidence-weighted insurability score, the coverage gap against the current policy limit, a suggested limit, and proposal answers linked to evidence. Never a premium quote.
7. **Re-prices continuously** when threat intelligence changes, with an alert that explains the cause.
8. **Provides a safe AI copilot** for what-if questions that can only quote figures produced by the engine. Untraceable numbers are blocked and prompt-injection attempts are quarantined.
9. **Protects itself**: role-based access for CISO, analyst, board viewer, consented broker and platform admin; a tamper-evident audit log; and an admin view of feeds, jobs and AI guardrail events.

## 6. Scope and constraints

- **In scope:** evidence ingestion, the attack-path graph, Monte Carlo loss simulation, budget optimisation, the insurance and compliance views, the copilot, roles, audit and admin observability.
- **Out of scope:** replacing a SOC or SIEM, live attack execution, and setting insurance premiums. Pricing remains the insurer's decision.
- **Constraints:**
  - Only systems the organisation owns or is authorised to assess may be scanned.
  - No real personal data is used in the demo.
  - Results must be reproducible (same evidence and seed give the same numbers).
  - All modelling assumptions must be visible and editable.
  - Regulatory references to DPDP, CERT-In, RBI and ISO 27001 must be accurate and date-aware.

## 7. Success criteria

| Criterion | Measure |
|---|---|
| Decision-ready output | Exposure expressed in ₹ (EAL, VaR95, CVaR95) with the drivers of the loss identified |
| Traceability | Any displayed figure can be traced to evidence, feed values and assumptions |
| Correct modelling | Overlapping paths are correlated; adding a control never increases expected loss; results are reproducible |
| Actionability | A budget plan that is verified by simulation and close to the best possible plan |
| Insurance relevance | The coverage gap and evidence-backed control status are visible to a consented broker |
| AI safety | Zero untraceable figures shown; injected instructions in scanner data quarantined |
| Security of the platform | Scans outside the authorised range refused; least-privilege roles; tamper detection |
| Usability | A board member understands the three headline numbers and the recommended plan in under a minute |

## 8. Expected impact

- **CISOs** get a prioritised, evidence-backed fix list.
- **Boards** get a rupee figure they can budget against.
- **Brokers and insurers** get verified evidence instead of self-declared answers.
- **Organisations** see their DPDP and CERT-In readiness alongside their financial exposure.

For a cyber-resilience provider that spans security operations, compliance and insurance broking, this closes the loop between **Detect and Defend** and **Insure and Recover**.

## Sources

- IBM, *India Records Highest Average Cost of a Data Breach* (2025): https://in.newsroom.ibm.com/2025-08-07-India-Records-Highest-Average-Cost-of-a-Data-Breach-IBM
- AZB & Partners, DPDP Rules 2025 commencement: https://www.azbpartners.com/bank/update-indias-digital-personal-data-protection-framework-comes-into-effect/
- CERT-In: https://www.cert-in.org.in/
- CISA Known Exploited Vulnerabilities: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- FIRST EPSS: https://www.first.org/epss/
