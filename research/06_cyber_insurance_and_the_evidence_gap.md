# 06 · Cyber insurance and the evidence gap

## How cyber cover is commonly underwritten

Proposal forms ask a recurring set of control questions: MFA on remote and privileged access, EDR,
offline or immutable backups, patching of known-exploited vulnerabilities, email authentication,
privileged access management and an incident response plan. Answers are typically **self-declared**.

## The gap

- Declared controls are not evidence. A "yes" to MFA says nothing about the VPN users without it.
- Limits are often chosen without reference to the organisation's own tail loss.
- Security improvements rarely flow back into the insurance conversation in a measurable way.

Investors in the Indian market have described this missing link between live security telemetry and
underwriting as the core opportunity for insurance-plus-security platforms (see Bessemer's note on
Mitigata). Mitigata's public product set (an AI-powered SOC, a risk-measurement engine, a security
co-pilot and an IRDAI-regulated broking business) sits exactly at this junction.

## What Vyuhix contributes

| Gap | Vyuhix output |
|---|---|
| Declared vs real | Each insurer control is **evidenced / planned / declared / absent**, with the evidence ID |
| Limit vs tail | Coverage gap at VaR95; recommended limit for a 1-in-100-year loss; a draggable limit on the curve |
| Security ↔ insurance | "Show with plan" re-scores insurability and recomputes the gap after the chosen fixes |
| Claims | A readiness checklist for CERT-In and DPDP clocks |

It deliberately does **not** produce premiums: pricing belongs to insurers and their actuaries.

## Sources

- Bessemer Venture Partners, *Securing India's digital economy with Mitigata*: https://www.bvp.com/news/securing-indias-digital-economy-with-mitigata
- Inc42, *Cyber Risk And Insurance Startup Mitigata Raises $15 Mn* (Jun 2026): https://inc42.com/buzz/cyber-risk-and-insurance-startup-mitigata-raises-15-mn/
- Mitigata: https://mitigata.com/
- arXiv 2606.16465 (trace-based underwriting of AI agents): https://arxiv.org/pdf/2606.16465
