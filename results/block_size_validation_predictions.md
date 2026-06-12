# Empirical block-size validation — predictions (pre-registered)

Recorded BEFORE running the native B=8/16/32 sweep, so the result is a test, not
a postdiction. Domains: code, chat, prose (structured settled, large-B regime).

## Model behind the predictions

The offline `block_size_sweep.py` re-segments the existing 256-canvas trajectory,
which charges each small block a *fractional* denoise cost (e.g. ~0.7 passes per
16-token block). Real blocks pay a hard floor: ≥1 denoise pass + 1 verify pass =
**2 weight passes per block**. So the realistic ceiling at block size B is
~**APL(B) / 2**, and any sweep entry above B/2 is unphysical.

## Predictions (realized speedup, 1.0 = AR break-even)

| domain | sweep said | floor-corrected prediction |
|---|---|---|
| code @ B=16  | 4.5x | **~2.5–3.5x** |
| code @ B=8   | 3.8x | ~2–3x |
| code @ B=32  | 4.2x | ~3–4x (closer to sweep; less floor pressure) |
| chat @ B=8   | 2.2x | **~2x at best** (sweep sits on the floor) |
| chat @ B=16  | 2.1x | ~1.5–2x |
| prose @ B=8  | 0.98x | **<1.0 — fails break-even** |
| prose @ B=16 | 0.72x | <1.0 |
| structured   | 8.3x | not re-measured (large-B, unaffected) |

Headline calls:
- code: crosses 1.0 well below B=32 and peaks somewhere B≈16–32, but at a lower
  peak than the sweep's 4.5x.
- chat: marginal win (~2x) only at the smallest blocks.
- prose: does NOT break even at any tested B.

## Second hypothesis (question b): native p vs re-segmented p

The sweep assumed per-token agreement `p` is unchanged by block size. But a native
B-token canvas denoises with **less bidirectional lookahead** than a 256-canvas.
Prediction: **native p at small B ≤ the B=256 baseline p** (agreement may degrade
because the drafter has less context to denoise against). If so, realized speedups
fall *below* even the floor-corrected predictions above. Report per-token p at each
native B against the B=256 baseline to test this.

## Status: BLOCKED before run — see report

The harness `block_size` knob does NOT set the native canvas (it only sets
max_new_tokens + output slicing). `canvas_length` is a model-config attribute
(default 256), not a documented generate() arg. Whether a native sub-256 canvas
is even runnable on the installed build is unconfirmed — pending inspection of the
installed modeling source.
