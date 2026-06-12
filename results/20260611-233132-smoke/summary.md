# Agreement summary

Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, implied speedup (accepted tokens / weight passes), and the commit-entropy vs disagreement correlation. Derived from blocks.jsonl.

| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |
|---|---|---|---|---|---|---|---|---|
| code | 9 | 144 | 0.8125 | 3.0000 | 1 | 7.0000 | 0.5000 | -0.1911 |
| ALL | 9 | 144 | 0.8125 | 3.0000 | 1 | 7.0000 | 0.5000 | -0.1911 |

## Accepted-prefix-length histograms

### code
```
   1: ###### (6)
   7: ### (3)
```

## Decision gates (per the plan)

- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks
- p 0.7–0.9  → viable with reduced block size / light distillation
- p < 0.7  → Phase 2 becomes a distillation project first
