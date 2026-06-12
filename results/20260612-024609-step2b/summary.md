# Agreement summary

Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, implied speedup (accepted tokens / weight passes), and the commit-entropy vs disagreement correlation. Derived from blocks.jsonl.

| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |
|---|---|---|---|---|---|---|---|---|
| code | 105 | 26880 | 0.6787 | 8.8952 | 5 | 22.0000 | n/a | n/a |
| ALL | 105 | 26880 | 0.6787 | 8.8952 | 5 | 22.0000 | n/a | n/a |

## Accepted-prefix-length histograms

### code
```
   0: ############################ (28)
   1: ### (3)
   2: ############# (13)
   3: ## (2)
   4: ###### (6)
   5: ##### (5)
   6: ### (3)
   7: ### (3)
   8: ## (2)
   9: ##### (5)
  10: ### (3)
  11: ## (2)
  12: ## (2)
  13: ## (2)
  14: # (1)
  16: # (1)
  17: # (1)
  18: ## (2)
  19: #### (4)
  20: ### (3)
  21: # (1)
  22: #### (4)
  24: # (1)
  25: # (1)
  29: # (1)
  33: # (1)
  35: # (1)
  36: # (1)
  43: # (1)
  47: # (1)
  48: # (1)
```

## Decision gates (per the plan)

- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks
- p 0.7–0.9  → viable with reduced block size / light distillation
- p < 0.7  → Phase 2 becomes a distillation project first
