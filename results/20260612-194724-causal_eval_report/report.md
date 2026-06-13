# Causal-mode quality eval — comparison report

generations: results/20260612-194118-causal_eval_smoke/

## structured (automated)

- normalized exact-match causal vs Gemma 4: **1.000** (n=2)
- JSON-valid: causal 1.000 | gemma4 1.000

## code (automated; correctness is your manual read)

- Python syntax-valid: causal 1.000 | gemma4 0.500 (n=2)
- median output tokens: causal 320 | gemma4 320

## degeneracy screen (all 200 causal outputs)

2 flagged:
  - code/code-001: truncated
  - code/code-002: truncated

## per-domain degeneracy counts

domain         n  degenerate mean_rep3
structured     2           0     0.025
code           2           2     0.007

## automated bucket pointer

points to FAIL (degeneracy present — see list); manual reads still owed

side-by-sides for your manual read: side_by_side_code.md (all 50), side_by_side_chat.md / side_by_side_prose.md (10 each)
