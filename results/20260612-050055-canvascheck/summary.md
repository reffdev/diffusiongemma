# Agreement summary

Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, implied speedup (accepted tokens / weight passes), and the commit-entropy vs disagreement correlation. Derived from blocks.jsonl.

| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |
|---|---|---|---|---|---|---|---|---|
| code | 8 | 128 | 0.8125 | 5.3750 | 4.0000 | 11.8000 | 0.1604 | n/a |
| ALL | 8 | 128 | 0.8125 | 5.3750 | 4.0000 | 11.8000 | 0.1604 | n/a |

## Accepted-prefix-length histograms

### code
```
   0: ## (2)
   1: # (1)
   2: # (1)
   6: # (1)
   8: # (1)
  10: # (1)
  16: # (1)
```

## Decision gates (per the plan)

- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks
- p 0.7–0.9  → viable with reduced block size / light distillation
- p < 0.7  → Phase 2 becomes a distillation project first
