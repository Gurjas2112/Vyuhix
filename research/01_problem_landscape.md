# 01 · The problem landscape

## Findings

- **Breach costs in India are at a record high.** IBM's *Cost of a Data Breach 2025* reported an Indian
  average of **₹22 crore** (INR 220 million) per breach, the highest it had recorded for India.
- **Penalties are rising.** The DPDP Act 2023 allows penalties of up to **₹250 crore** for failing to take
  reasonable security safeguards. The DPDP Rules 2025 (notified 13 November 2025) bring substantive
  obligations and the Data Protection Board's penalty powers into force on **13 May 2027**.
- **Reporting clocks are short.** CERT-In's 2022 directions require cyber incidents to be reported within
  **6 hours**. The DPDP Rules require Board intimation without delay and a detailed report within
  **72 hours**.
- **Communication fails at the top.** Risk is still commonly expressed as qualitative ratings, which do not
  support investment decisions or insurance limits.
- **AI is widening the attack surface.** Recent work quantifies how AI capability raises attacker
  effectiveness across ATT&CK-mapped attack steps (arXiv 2512.08864).

## Implications for the design

1. Express risk in **rupees** with a distribution, not a colour.
2. Make the **India-specific** loss components (DPDP penalties, reporting obligations) explicit and **date-aware**.
3. Tie risk to **decisions**: what to fix, and how much insurance to buy.
4. Make every number **traceable**, because boards, insurers and regulators will ask.

## Sources

- IBM India newsroom, *India Records Highest Average Cost of a Data Breach* (7 Aug 2025): https://in.newsroom.ibm.com/2025-08-07-India-Records-Highest-Average-Cost-of-a-Data-Breach-IBM
- AZB & Partners, DPDP framework commencement (Nov 2025): https://www.azbpartners.com/bank/update-indias-digital-personal-data-protection-framework-comes-into-effect/
- *Toward Quantitative Modeling of Cybersecurity Risks*, arXiv 2512.08864: https://arxiv.org/abs/2512.08864v1
