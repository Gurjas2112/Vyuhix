# User guide

Sign in at `http://localhost:8000` with one of the demo accounts (password `Demo@12345`), or create an
account; new accounts join the demo organisation as analysts.

![Login](../app_screenshots_screen_recording/screenshots/01_login_and_demo_accounts.png)

## The header, on every page

**Expected annual loss** and **1-in-20-year loss** are buttons: click either to open **Trace this
rupee**. The KEV chip shows which known-exploited catalogue is in use (orange when a simulated update is
loaded). **Copilot** opens the assistant panel.

## Overview

The four headline numbers, the loss curve against the policy limit (dashed line), the best use of
₹5 lakh, the paths that contribute most, and live signals.

![Overview](../app_screenshots_screen_recording/screenshots/02_overview_rupees_at_risk.png)

## Trace this rupee

Paths ranked by rupees. Expand one to see each step's probability and why (EPSS, KEV, internet-facing,
floor), the evidence IDs behind it, what the loss is made of, and the assumptions.

![Trace](../app_screenshots_screen_recording/screenshots/03_trace_a_rupee_provenance.png)

## Evidence (org admin, analyst)

**Run lab scan** plays the eight-step pipeline. Try a target outside the lab (8.8.8.8 is pre-filled): it
is refused and audited. The orange box shows the quarantined prompt-injection text from the Redis banner.

![Evidence](../app_screenshots_screen_recording/screenshots/04_evidence_scan_pipeline_and_guardrail.png)

## Attack paths

The map runs left to right from entries to crown jewels. Edge labels are per-attempt success
probabilities. Select a path to highlight it. Tick fixes under **What if we fix…** to see paths cut and
the new EAL. **Choke points** are the steps most loss flows through.

![Paths](../app_screenshots_screen_recording/screenshots/07_attack_path_what_if_controls.png)

## Loss

The loss-exceedance curve, what the loss is made of, and the **assumptions panel**. Move a slider and
everything re-simulates in milliseconds.

![Loss](../app_screenshots_screen_recording/screenshots/08_loss_curve_and_assumptions.png)

## Plan

Drag the budget. The chosen fixes, the new EAL (re-simulated) and the frontier showing where extra spend
stops paying off.

![Plan](../app_screenshots_screen_recording/screenshots/10_plan_budget_optimiser.png)

## Insurance (also visible to the broker)

Insurability score, coverage gap, a recommended limit for a 1-in-100-year loss, and the chance a year
exceeds the limit. Drag the limit; tick "Show with the ₹5 lakh plan applied" to see how fixes change the
picture. Proposal answers link to evidence. This is indicative analysis only, not a quote.

![Insurance](../app_screenshots_screen_recording/screenshots/11_insurance_coverage_gap.png)

## Compliance

The same evidence mapped to ISO 27001:2022, NIST CSF 2.0, CIS v8.1, CERT-In, RBI IT governance and the
DPDP Rules.

![Compliance](../app_screenshots_screen_recording/screenshots/13_compliance_framework_matrix.png)

## Copilot

Try the suggestion chips. Each answer shows whether it is **grounded**, the mode (offline or Claude), the
tools called and the evidence used. Questions about other organisations are refused.

![Copilot](../app_screenshots_screen_recording/screenshots/14_copilot_grounded_answers.png)

## Board report

One printable page: three numbers, top paths, plan and insurance. Use **Print or save as PDF**.

![Report](../app_screenshots_screen_recording/screenshots/15_board_report.png)

## Broker view

The broker sees loss quantiles and the insurance view, but not attack paths or raw evidence.

![Broker](../app_screenshots_screen_recording/screenshots/17_broker_insurance_view.png)

## Admin console (platform admin)

Overview, **Feeds** (load or reset the *simulated* KEV update to demonstrate drift), **Guardrails**
(quarantined text, refused scans, blocked figures), **Audit log** (verify the hash chain) and **Users**.

![Admin](../app_screenshots_screen_recording/screenshots/19_admin_feeds_kev_drift.png)
