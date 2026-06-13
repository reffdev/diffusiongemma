# Causal-mode quality eval — comparison report

generations: results/20260612-201135-causal_eval_smoke3/

## structured (automated)

- normalized exact-match causal vs Gemma 4: **1.000** (n=2)
- JSON-valid: causal 1.000 | gemma4 1.000

## code (automated; correctness is your manual read)

- Python syntax-valid: causal 1.000 | gemma4 1.000 (n=2)
- median output tokens: causal 426 | gemma4 503

## degeneracy screen (all 200 causal outputs)

none — zero empty / truncated / repetition / length-outlier.

## per-domain degeneracy counts

domain         n  degenerate mean_rep3
structured     2           0     0.025
code           2           0     0.008

## termination (standalone causal generation)

  structured : 0/2 causal outputs ran to the cap (no <eos> self-termination)
  code       : 0/2 causal outputs ran to the cap (no <eos> self-termination)

## automated bucket pointer (manual call is yours)

- CONTENT (extractable answers): structured match 1.000 (PASS-consistent); code syntax-validity + manual read pending.
- STANDALONE GENERATION: 0/4 ran to cap with no self-termination — if systematic, standalone-generation quality FAILs on termination regardless of content.
- NOTE: termination is irrelevant to the verifier role (teacher-forced); rung-1's loop use is unaffected. The 'Gemma-4-class' claim splits into content (maybe) vs standalone-gen (no).

side-by-sides for your manual read: side_by_side_code.md (all 50), side_by_side_chat.md / side_by_side_prose.md (10 each)
