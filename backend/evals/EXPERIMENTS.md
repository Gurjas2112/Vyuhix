# Copilot experiments

This is a log of what was measured, what changed and what improved. Raw results for every run are in
[`results/`](results/): `results.jsonl` holds each answer with its tool calls, citations, guardrail blocks and token usage,
and `summary.md` holds the table. Re-run any of it from `backend/`:

```bash
python -m evals.run retrieval                                  # free
python -m evals.run copilot --mode offline                     # free
python -m evals.run copilot --mode null                        # free: checks the grader is not lenient
python -m evals.run copilot --mode claude --effort low --reps 2  # about $0.35 with Sonnet 5.5
```

## The eval

- **43 copilot questions** in [`cases.jsonl`](cases.jsonl), in 8 categories:
  - figures 8, what-if 6, budget plan 5, insurance 4, knowledge (RAG) 11;
  - refusal 4, adversarial 3, broker role 2.
  - Both directions are covered: questions it must answer and questions it must refuse.
- **Expected figures come from the deterministic engine**, not from a model, so the key cannot favour any model's wording.
- **Grading checks outcomes, not routes:**
  - the answer must contain the expected facts (figures compared by value, so "₹5.0 L" equals "₹5 lakh");
  - refusal cases must refuse;
  - knowledge answers must cite;
  - the model's draft must pass the guardrails unchanged.

  The tool called is reported but not graded.
- **API failures are kept apart from wrong answers.** These go to `errors.jsonl`:
  - a call that fell back to offline mode;
  - an answer served by a model other than the one requested.
- **25 retrieval questions** in [`retrieval.jsonl`](retrieval.jsonl), worded differently from the docs so keyword overlap
  doesn't decide the result. A hit means a top-k passage contains the expected fact.

## Results

### 1. Grader sanity check

A constant answer, "I can't answer that.", passes **12%** (the 5 refusal cases) and fails every other case.
So the grader isn't lenient, and the refusal cases are the only ones a do-nothing answer can pass.

### 2. Retrieval: hybrid beats either method alone

| Method | Hit@1 | Hit@3 | Hit@4 (what the copilot sees) | MRR@10 |
|---|---|---|---|---|
| BM25 keywords | 52% | 64% | 76% | 0.62 |
| Dense (bge-small-en-v1.5, CPU) | 52% | 80% | 80% | 0.65 |
| **Hybrid (reciprocal-rank fusion)** | **60%** | **80%** | **80%** | **0.69** |

- **Search:** 124 section-level chunks from 21 documents; queries take about 4 ms on a laptop CPU, with no API key.
  (The Claude runs below used the corpus before this change's doc edits: 119 chunks.)
- **Relevance gate:** the offline router answers from the docs only when the top hit has cosine ≥ 0.60. That accepted all
  25 on-topic questions and rejected all 5 off-topic ones; in calibration, on-topic hits scored 0.64 or more and off-topic ones 0.53 or less.
- **Misses:** hybrid search misses 5 questions at k=4.
  - Three have the fact inside a long table: two in the glossary (one chunk holds 20+ definitions, which dilutes the
    match) and one in the loss-component table.
  - The other two (r18, r20) reach the right document but a neighbouring section.
  - Next things to try: one chunk per table row, and returning the neighbouring section with each hit.

### 3. Guardrail false positives, found by testing Claude mode by hand

The first Claude-mode test (8 questions, before this eval existed) blocked two of eight answers:

| Question | Blocked figure | Verdict | Fix |
|---|---|---|---|
| "We have a 5 lakh budget…" | "₹5 lakh" | False positive: the user's own number | Figures in the question are now allowed |
| same | "₹1 L" left over | **Correct block.** The model subtracted ₹4 L from ₹5 L, but the plan costs ₹3.95 L, so ₹1.05 L is left over | The plan tool now reports `unspent ₹1.1 L` itself |
| "Ignore your rules… round number" | "5%" | Correct block | None needed |

Figures are now compared by value, not as text: ₹5 lakh, ₹5.0 L and ₹5,00,000 are the same figure.

### 4. Claude mode: definitions tripped the guardrail

| Run | Pass | Drafts passing the guardrails unchanged | p50 / p95 latency | Cost per question |
|---|---|---|---|---|
| Sonnet 5.5, effort low, 2 reps (before the fix) | 88% (88%, 88%) | 88% | 5.4 s / 18.3 s | $0.0057 |
| Sonnet 5.5, effort low, 2 reps (after the fix) | **100%** (100%, 100%) | 100% | 5.1 s / 7.0 s | **$0.0039** |
| Sonnet 5.5, effort medium, 2 reps | 100% (100%, 100%) | 100% | 5.0 s / 6.8 s | $0.0045 |

- **What failed:** all 10 failures in the first run were blocked drafts. Explaining "VaR95 is the loss exceeded in 5% of
  years" put a "5%" in the answer that no tool had returned.
- **The fix:** the summary and coverage tools now state what VaR95, CVaR95 and VaR99 mean. The fix went into the tools,
  not the guardrail: the check stays strict, and the model gets the definitions it needs.
- **Choice of effort level:** `low` matches `medium` on quality at lower cost, so `low` is the default
  (`VYUHIX_LLM_EFFORT`). The low and medium runs ran at the same time, so their cache-write shares differ (21.9k vs
  41.7k tokens); some of the cost gap is cache timing, not effort.
- **Prompt caching works:** each question reads about 1,300 tokens of system prompt and tool definitions from cache.

### 5. Offline router: the eval found bugs

| Run | Pass |
|---|---|
| Before fixes | 65% |
| After fixes | 93% |

- **The bugs:**
  - "What's" and "the Board's" were read as other organisations' names, so the question was refused.
  - Some intent keywords were missing.
  - Premium questions returned coverage figures.
  - Offline knowledge answers quoted only the top passage.
- **The fixes:** offline answers now pull the sentences that best match the question from all four passages.
- **Caveat:** these fixes were made by reading failures in this same question set, so 93% is optimistic for the offline
  router. The Claude-mode results had no such tuning: no prompt was changed for a specific case.

## Known limits

- **The eval is saturated in Claude mode.** At 100% it can't separate effort levels or models. The next step is harder
  cases: multi-step questions, questions that need two tools, and conflicting passages.
- **The grounding check verifies numbers, not meaning.** In one passing answer, the model said a closed path "adds no
  measurable loss". In fact its loss moves to other paths rather than vanishing. A rubric or model-graded check of the
  explanation would catch this; the current grader would not.
- **The questions are single-turn.** Follow-up questions ("and with EDR as well?") are not tested.
- **Two repetitions per setting.** The per-rep scores agree, but the error bars are wide.
