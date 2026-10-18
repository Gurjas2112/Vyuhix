# Demo script: five minutes

One person drives and one narrates. Every number on screen comes from the run, not from this script.
Before you start: delete `data/runtime/` for a fresh database, start the API and open the login page.

| Time | Screen | Say |
|---|---|---|
| 0:00 | Login | "Boards hear cyber risk as a colour. Insurers price it from a questionnaire. Vyuhix turns evidence into rupees and shows its working." Click **Ananya · CISO**. |
| 0:20 | Overview | "Acme is a fictional lender. Expected loss ₹3 crore a year; a bad year, 1 in 20, is ₹14 crore, almost three times their ₹5 crore policy." |
| 0:45 | Evidence → Try scan 8.8.8.8 → Run lab scan | "We only scan what we own; anything else is refused before a packet leaves. Eight real tool formats in. And this Redis banner tries to instruct our AI. It is quarantined as data." |
| 1:25 | Attack paths | "Seventeen findings, one route that matters most: a KEV-listed Apache flaw, a readable `.env`, a database password, two lakh customer records. Four hops, in plain English." Tick **Patch Apache** and **Rotate secret**: "Paths cut, loss falls, live." |
| 2:05 | Header → EAL (Trace this rupee) → expand P2 | "Click any rupee. Here's where it comes from, down to the scanner line and the EPSS value." |
| 2:35 | Plan | "Five lakh rupees. Two methods propose a plan, and the simulator picks the winner: 94% less expected loss for ₹4 lakh. The curve shows where spending stops paying off." |
| 3:05 | Insurance → drag the limit | "That's the coverage gap. This is the conversation a broker wants to have, backed by evidence instead of tick-boxes. And we never quote premiums." |
| 3:35 | Copilot → "What if we enforce MFA on admins?" → "What is HDFC's cyber risk?" | "Every number is from the engine; an invented figure would be blocked. Questions it can't answer from evidence are refused." |
| 4:10 | Sign out → Divya → Feeds → Load simulated KEV update | "Tomorrow a new CVE is added to the known-exploited list. Risk re-prices: plus 39%, with the reason." Then **Audit log → Verify chain**. |
| 4:40 | Board report | "One page for the board. Insure, detect, defend, recover, measured in rupees." |

## Questions to rehearse

| Question | Answer |
|---|---|
| "Isn't EPSS the wrong probability?" | It's a 30-day in-the-wild prior. We combine it with KEV, exposure and controls, label it as an assumption, and the structure doesn't depend on it. |
| "Where do the rupee ranges come from?" | Editable PERT ranges anchored to IBM's 2025 India average breach cost and public loss studies; DPDP penalties are date-aware. Acme's own revenue drives downtime. |
| "What stops the AI hallucinating?" | It never computes. Tools return numbers, and a grounding check rejects any figure no tool produced. |
| "Is the scan real?" | The tool outputs are in real formats and the CVEs are real; level 1 replays them. Level 2 runs the same parsers live against a Docker lab. |
| "Would this scale?" | The engine is per-organisation and cached by input hash; runs are about 10 ms. Production adds a job queue and per-tenant storage. |
| "Why can't the optimiser hit zero?" | The residual entry models what scans can't see. Claiming zero risk would be dishonest. |
