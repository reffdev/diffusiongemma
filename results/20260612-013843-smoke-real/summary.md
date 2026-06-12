# Agreement summary

Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, implied speedup (accepted tokens / weight passes), and the commit-entropy vs disagreement correlation. Derived from blocks.jsonl.

| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |
|---|---|---|---|---|---|---|---|---|
| code | 2 | 512 | 0.9121 | 1.5000 | 1.5000 | 2.7000 | n/a | n/a |
| ALL | 2 | 512 | 0.9121 | 1.5000 | 1.5000 | 2.7000 | n/a | n/a |

## Accepted-prefix-length histograms

### code
```
   0: # (1)
   3: # (1)
```

## Decision gates (per the plan)

- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks
- p 0.7–0.9  → viable with reduced block size / light distillation
- p < 0.7  → Phase 2 becomes a distillation project first
