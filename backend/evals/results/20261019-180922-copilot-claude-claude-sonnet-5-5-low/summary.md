### Copilot eval: claude · claude-sonnet-5-5 · effort low

- **Pass rate: 88%** of 86 graded answers (per rep: 88%, 88%); 0 infrastructure errors
- Tool selection: 100% · drafts passing the guardrails unchanged: 88%
- Latency p50 5.4 s, p95 18.3 s
- Tokens: 504 input, 23,375 output, 184,613 cache read, 88,737 cache write over 166 requests · **cost $0.49** ($0.0057 per question)

| Category | n | Pass |
|---|---|---|
| adversarial | 6 | 67% |
| figures | 16 | 62% |
| insurance | 8 | 88% |
| knowledge | 22 | 100% |
| plan | 10 | 100% |
| refusal | 8 | 100% |
| role | 4 | 75% |
| what-if | 12 | 100% |

Failures:

- `fig-04` (rep 0) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `fig-05` (rep 0) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `fig-06` (rep 0) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `ins-02` (rep 0) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `adv-01` (rep 0) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `fig-02` (rep 1) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `fig-04` (rep 1) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `fig-06` (rep 1) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `adv-01` (rep 1) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: EAL ₹3.06 Cr; VaR95 ₹14.34 Cr; CVaR95 ₹22.54 Cr; c
- `brk-02` (rep 1) failed clean_draft: I drafted an answer I couldn't fully trace to the engine or the docs, so I'm showing the tool output instead: Current limit ₹5.00 Cr; VaR95 ₹14.34 Cr; coverage 