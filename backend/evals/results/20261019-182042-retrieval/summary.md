### Retrieval eval: 25 paraphrased questions over 124 chunks from 21 documents

| Method | Hit@1 | Hit@3 | Hit@4 (what the copilot sees) | MRR@10 | p50 latency |
|---|---|---|---|---|---|
| bm25 | 52% | 64% | 76% | 0.62 | 0 ms |
| dense | 52% | 80% | 80% | 0.65 | 4 ms |
| hybrid | 60% | 80% | 80% | 0.69 | 4 ms |

Relevance gate (offline router): accepts 100% of on-topic questions, rejects 100% of 5 off-topic ones.