# Causal-mode quality eval — comparison report

generations: results/20260612-195456-causal_eval_smoke2/

## structured (automated)

- normalized exact-match causal vs Gemma 4: **0.000** (n=2)
- JSON-valid: causal 0.000 | gemma4 1.000

## code (automated; correctness is your manual read)

- Python syntax-valid: causal 0.000 | gemma4 1.000 (n=2)
- median output tokens: causal 39 | gemma4 503

## degeneracy screen (all 200 causal outputs)

3 flagged:
  - code/code-001: length_outlier(causal=45,gemma4=512)
  - code/code-002: length_outlier(causal=33,gemma4=494)
  - structured/structured-002: length_outlier(causal=16,gemma4=72)

## per-domain degeneracy counts

domain         n  degenerate mean_rep3
structured     2           1     0.000
code           2           2     0.000

## automated bucket pointer

points to FAIL (degeneracy present — see list); manual reads still owed

side-by-sides for your manual read: side_by_side_code.md (all 50), side_by_side_chat.md / side_by_side_prose.md (10 each)
