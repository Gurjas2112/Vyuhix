# Screenshots and screen recording

**Full walkthrough video:** [vyuhix_full_walkthrough.mp4](vyuhix_full_walkthrough.mp4). One continuous take through every role and screen, with step captions.

Everything below was captured automatically from the running app by
[`scripts/capture_walkthrough.py`](../scripts/capture_walkthrough.py), so it can be regenerated at any time:

```bash
cd backend && uvicorn vyuhix.main:app --port 8000      # in one terminal
python scripts/capture_walkthrough.py                   # in another (pip install playwright; python -m playwright install chromium)
```

## System flow

### 1 · Sign in
| | |
|---|---|
| ![](screenshots/01_login_and_demo_accounts.png) | **01 Login.** Sign in or create an account; one-click demo accounts for each role. |

### 2 · The CISO's view
| | |
|---|---|
| ![](screenshots/02_overview_rupees_at_risk.png) | **02 Overview.** EAL, 1-in-20-year loss, CVaR95, chance of loss; loss curve vs policy limit; best use of ₹5 lakh; top paths; live signals. |
| ![](screenshots/03_trace_a_rupee_provenance.png) | **03 Trace a rupee.** Paths ranked by ₹; each step's probability basis (EPSS, KEV, exposure) and evidence IDs. |

### 3 · Evidence in
| | |
|---|---|
| ![](screenshots/04_evidence_scan_pipeline_and_guardrail.png) | **04 Scan pipeline.** Eight parser steps; a target outside the lab is refused; a planted prompt injection is quarantined. |
| ![](screenshots/05_evidence_findings_table.png) | **05 Findings.** Severity, tool, asset and stable evidence IDs. |

### 4 · Paths and what-ifs
| | |
|---|---|
| ![](screenshots/06_attack_path_map.png) | **06 Attack-path map.** Entries → assets → secrets → identities → crown jewels, with step probabilities. |
| ![](screenshots/07_attack_path_what_if_controls.png) | **07 What-if.** Patching Apache and rotating the secret cuts paths; EAL updates live; choke points. |

### 5 · Loss, plan, insurance, compliance
| | |
|---|---|
| ![](screenshots/08_loss_curve_and_assumptions.png) | **08 Loss.** Exceedance curve, components, editable assumptions. |
| ![](screenshots/09_loss_assumption_changed_live.png) | **09 Assumption changed.** Re-simulated in milliseconds. |
| ![](screenshots/10_plan_budget_optimiser.png) | **10 Plan.** Budget slider, chosen controls, frontier. |
| ![](screenshots/11_insurance_coverage_gap.png) | **11 Insurance.** Insurability score, coverage gap, recommended limit, evidence-linked controls. |
| ![](screenshots/12_insurance_with_plan_and_new_limit.png) | **12 With plan + new limit.** How fixes and a higher limit change the picture. |
| ![](screenshots/13_compliance_framework_matrix.png) | **13 Compliance.** ISO 27001, NIST CSF 2.0, CIS, CERT-In, RBI, DPDP. |

### 6 · Copilot and board report
| | |
|---|---|
| ![](screenshots/14_copilot_grounded_answers.png) | **14 Copilot.** Grounded answers with tools and evidence; a refusal for another organisation. |
| ![](screenshots/15_board_report.png) | **15 Board report.** One printable page. |

### 7 · Broker (consented, insurance-only)
| | |
|---|---|
| ![](screenshots/16_broker_shared_summary.png) | **16 Broker summary.** Quantiles only, no attack paths. |
| ![](screenshots/17_broker_insurance_view.png) | **17 Broker insurance view.** |

### 8 · Platform admin
| | |
|---|---|
| ![](screenshots/18_admin_console_overview.png) | **18 Admin overview.** Users, guardrail events, copilot usage, jobs. |
| ![](screenshots/19_admin_feeds_kev_drift.png) | **19 Feeds.** Loading the *simulated* KEV update re-prices risk. |
| ![](screenshots/20_admin_guardrail_events.png) | **20 Guardrails.** Quarantined injection and refused scan. |
| ![](screenshots/21_admin_audit_chain_verified.png) | **21 Audit.** Hash chain verified. |

### 9 · Continuous re-pricing
| | |
|---|---|
| ![](screenshots/22_overview_after_drift_alert.png) | **22 Drift alert.** The CISO sees the higher EAL and the reason. |
