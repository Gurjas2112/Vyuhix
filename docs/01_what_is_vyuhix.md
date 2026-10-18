# What is Vyuhix?

## In one sentence

Vyuhix looks at what security scanners found inside a company, works out every way an attacker could
chain those weaknesses together to reach important data, and tells you, in rupees, how much that is
likely to cost, what to fix first, and whether the company's cyber insurance is enough.

## Why it is needed

Picture three people in a meeting:

- **The security head** has a spreadsheet of 5,000 vulnerabilities sorted by a "severity score". The
  score says how bad a bug *could* be, not how likely it is to be used or what it would cost.
- **The finance head** is asked to approve ₹15 lakh for security. Her question is simple: *"What do we
  get for it?"* Nobody can answer in rupees.
- **The insurance broker** is asked for a cyber policy. The insurer prices it from a questionnaire the
  company fills in about itself, without seeing any real evidence.

Each of them is looking at a different, incomplete picture. Vyuhix gives all three the **same number,
backed by the same evidence**.

## What it does, step by step

1. **Reads evidence.** Outputs from standard security tools (port scans, vulnerability checks, secret
   scanners, database permissions, intrusion alerts) are turned into one clean list of findings.
2. **Connects the dots.** Findings become a map. For example: *the web server has a known flaw → through
   it, an attacker can read a settings file → the file contains a database password → that password can
   read every customer record.* Each chain is an **attack path**.
3. **Puts a price on it.** Vyuhix plays out 10,000 possible years. In each year attackers try, sometimes
   succeed, and when they do, there are costs: investigation, notifying customers, downtime, ransom,
   regulatory penalties. Averaging those years gives the **expected annual loss**; the bad years give
   the **1-in-20-year loss**.
4. **Recommends fixes.** Given a budget, it finds the set of fixes that removes the most loss, then
   re-checks the answer by simulating again.
5. **Speaks insurance.** It compares the 1-in-20-year loss with the policy limit, shows the gap, and
   answers common insurer questions with links to evidence.
6. **Answers questions.** A copilot answers things like *"What if we turn on MFA?"*. It is not allowed
   to make up numbers: every figure must come from the engine, or the answer is blocked.

## What makes it different

- **It prices paths, not single bugs.** A "medium" bug on a route to customer data matters more than a
  "critical" bug on an isolated test machine.
- **Every rupee is traceable.** Click any figure to see exactly which paths, findings and assumptions
  produced it.
- **It is honest about uncertainty.** Assumptions are visible and editable, and a "residual" entry admits
  that scans never see everything.
- **The AI is boxed in.** It explains; it never calculates.

## Who uses it

| Person | What they get |
|---|---|
| Security head (CISO) | The routes that matter, what to fix first, proof for the board |
| Finance head / board | Three numbers and one chart; the best use of a given budget |
| Insurance broker | An evidence-backed view of insurability and the coverage gap, only with the client's permission |
| Platform operations | Health of data feeds, AI guardrail events, a tamper-evident audit log |

## What this repository is

A **working proof of concept** using a **fictional company** ("Acme Fintech Pvt Ltd") and **synthetic
data** in the formats real tools produce. It runs on a laptop with no cloud accounts. See the
[roadmap](10_roadmap.md) for what comes next.
