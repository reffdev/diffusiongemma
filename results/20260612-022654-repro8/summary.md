# Agreement summary

Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, implied speedup (accepted tokens / weight passes), and the commit-entropy vs disagreement correlation. Derived from blocks.jsonl.

| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |
|---|---|---|---|---|---|---|---|---|
| code | 22 | 5632 | 0.6729 | 10.2727 | 7.5000 | 20.0000 | n/a | n/a |
| ALL | 22 | 5632 | 0.6729 | 10.2727 | 7.5000 | 20.0000 | n/a | n/a |

## Accepted-prefix-length histograms

### code
```
   0: #### (4)
   1: # (1)
   3: # (1)
   4: ## (2)
   5: # (1)
   6: # (1)
   7: # (1)
   8: # (1)
   9: ## (2)
  10: # (1)
  12: # (1)
  13: # (1)
  17: # (1)
  20: ## (2)
  35: # (1)
  43: # (1)
```

## Decision gates (per the plan)

- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks
- p 0.7–0.9  → viable with reduced block size / light distillation
- p < 0.7  → Phase 2 becomes a distillation project first
