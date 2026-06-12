# Agreement summary

Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, implied speedup (accepted tokens / weight passes), and the commit-entropy vs disagreement correlation. Derived from blocks.jsonl.

| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |
|---|---|---|---|---|---|---|---|---|
| chat | 18 | 4608 | 0.6039 | 5.5556 | 5.0000 | 11.0000 | n/a | n/a |
| code | 16 | 4096 | 0.6709 | 10.0000 | 6.5000 | 20.0000 | n/a | n/a |
| prose | 14 | 3584 | 0.4568 | 2.6429 | 1.0000 | 3.0000 | n/a | n/a |
| structured | 8 | 2048 | 0.1719 | 35.1250 | 35.0000 | 62.9000 | n/a | n/a |
| ALL | 56 | 14336 | 0.5246 | 10.3214 | 4.5000 | 28.5000 | n/a | n/a |

## Accepted-prefix-length histograms

### chat
```
   0: ## (2)
   1: ### (3)
   2: # (1)
   3: # (1)
   5: ### (3)
   6: # (1)
   7: # (1)
   8: # (1)
  11: #### (4)
  12: # (1)
```
### code
```
   0: ### (3)
   3: # (1)
   4: ## (2)
   5: # (1)
   6: # (1)
   7: # (1)
   9: # (1)
  10: # (1)
  12: # (1)
  17: # (1)
  20: ## (2)
  43: # (1)
```
### prose
```
   0: #### (4)
   1: ##### (5)
   2: ## (2)
   3: ## (2)
  22: # (1)
```
### structured
```
   0: # (1)
   1: # (1)
  23: # (1)
  34: # (1)
  36: # (1)
  56: # (1)
  59: # (1)
  72: # (1)
```

## Decision gates (per the plan)

- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks
- p 0.7–0.9  → viable with reduced block size / light distillation
- p < 0.7  → Phase 2 becomes a distillation project first
