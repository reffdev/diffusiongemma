# Scaled Test 3 — causal-mode quality eval: pre-registered reads

Recorded BEFORE generating/scoring. The automated metrics point to a bucket; the
final call on the manual-read domains (code/chat/prose) is the operator's.

## Stop condition (documented, since it was the earlier artifact)

- **Causal-mode generation:** greedy, stop on `<eos>` (**1**) or `<end_of_turn>`
  (**107**) — but only after **MIN_STOP=16** generated tokens. The causal encoder
  emits a *spurious* 107 right after an opening code fence (~position 3), which
  truncated the earlier run; the MIN_STOP guard skips that one while still
  terminating naturally at the answer's real end. `max_new_tokens`=512 cap.
  Decoded with `skip_special_tokens=True`. A generation that hits the cap without
  a natural stop is `truncated`, but truncation is counted as **degeneracy only
  when causal-specific** (causal ran on while Gemma 4 finished); if both hit the
  cap it's a too-low cap on a long prompt, not a causal failure.
- **Gemma 4:** stock `generate(do_sample=False)` with its own generation_config
  stopping (its native eos/end_of_turn), same `max_new_tokens` cap.
- Both use the same chat render as run_final (shared tokenizer, gated identical).

## Pre-registered buckets

- **PASS** ("causal mode is Gemma-4-class" claimable; loop scoping proceeds on a
  lossless-ish framing): structured normalized-match vs Gemma 4 ≥ ~0.9, **zero
  degeneracy across all four domains**, AND the operator's manual read of
  code/chat/prose finds parity.
- **QUALITY FLOOR** (rung-1 survives, reframed as quality/speed tradeoff, not
  lossless): coherent everywhere, no degeneracy, but visibly below Gemma 4 in the
  manual reads.
- **FAIL** (quality claim dies): degeneracy or systematic breakage in any domain.

## Metrics

- structured (50): normalized exact-match causal-vs-Gemma4 (strip code fences +
  all whitespace); JSON-validity rate for each model independently.
- code (50): Python syntax-validity rate (`ast.parse`) for each; output-length
  stats; side-by-side of all 50 pairs (NO auto-grading of correctness).
- chat/prose (50 each): degeneracy stats only; side-by-side of a 10-prompt sample.
- ALL 200 causal: degeneracy screen — empty, truncated, repetition loop
  (repeated-3gram rate > 0.5), length outlier (|causal ntok| vs Gemma4 ntok off
  by > 4x). Every degenerate output listed individually.
