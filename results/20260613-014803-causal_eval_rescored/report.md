# Causal-mode quality eval — comparison report

generations: results/20260613-013652-causal_eval_gen

## structured (automated)

- normalized exact-match causal vs Gemma 4: **0.980** (n=50)
- JSON-valid: causal 0.860 | gemma4 0.860

## code (automated; correctness is your manual read)

- Python syntax-valid: causal 0.960 | gemma4 0.880 (n=50)
- median output tokens: causal 504 | gemma4 512

## degeneracy screen (all 200 causal outputs)

1 flagged:
  - chat/chat-017: causal_specific_runon

## per-domain degeneracy counts

domain         n  degenerate mean_rep3
structured    50           0     0.032
code          50           0     0.052
chat          50           1     0.030
prose         50           0     0.005

## termination — causal vs Gemma 4 cap-hits (both at max_new; cap-hit = long answer, not failure)

domain      causal_cap gemma4_cap causal_med gemma4_med
structured           0          0         50         46
code                22         36        504        512
chat                38         39        512        512
prose               14         25        458        508

## automated bucket pointer (manual call is yours)

- structured content match 0.980 (PASS-consistent).
- real causal degeneracy (empty / causal-specific run-on / repetition): 1/200.
- cap-hits reflect answer length (Gemma 4 hits the cap as much or more); NOT a termination failure.
- code/chat/prose content quality is the manual side-by-side read — not auto-concluded.

side-by-sides: side_by_side_code.md (all 50), side_by_side_chat.md / side_by_side_prose.md (10 each)
