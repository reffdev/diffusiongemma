#!/usr/bin/env python
"""Speedup-vs-block-size sweep from an existing run's blocks.jsonl (no GPU).

For each candidate block size B we re-segment each measured 256-canvas block's
per-position match array into fixed B-windows ("proposals"), accept the leading
agreements in each, and score:

    speedup(B) = total_accepted(B) / ( total_denoise + n_proposals(B) )

  - total_accepted(B): sum of leading agreements over all B-windows. Smaller B
    lets agreements *after* a block's first disagreement still count (a big
    window stops at the first miss), so accepted rises as B shrinks.
  - n_proposals(B): number of B-windows = one verifier pass each. Rises as B
    shrinks. This is the cost of smaller blocks.
  - total_denoise: sum of per-block denoise_steps (drafter weight passes). Held
    constant in B (see CAVEAT).

This definition reconciles with the run's reported speedup at B=256 (one window
per block, accepted = APL, n_proposals = n_blocks).

CAVEAT: total_denoise is held constant because we re-segment the drafter's
*existing* trajectory rather than re-canvassing after each correction. Real
greedy speculative decoding re-denoises from each rejection point, so actual
denoise at small B would be higher and these small-B speedups are upper bounds.
The empirical check is to run the harness with SamplerConfig.block_size = B and
read tokens_per_forward directly. This sweep predicts where that's worth doing.

Usage: python scripts/block_size_sweep.py results/<run-dir>
"""

from __future__ import annotations

import json
import os
import statistics
import sys

B_GRID = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
DOMAINS = ["structured", "code", "chat", "prose"]


def leading_agreements(window) -> int:
    a = 0
    for x in window:
        if x:
            a += 1
        else:
            break
    return a


def sweep_domain(blocks):
    total_denoise = sum(r["denoise_steps"] for r in blocks if r.get("denoise_steps"))
    curve = {}
    for B in B_GRID:
        accepted = 0
        n_prop = 0
        for r in blocks:
            m = r["match"]
            i = 0
            while i < len(m):
                accepted += leading_agreements(m[i : i + B])
                n_prop += 1
                i += B
        curve[B] = accepted / (total_denoise + n_prop) if (total_denoise + n_prop) else 0.0
    return curve


def crossing(curve) -> float | None:
    """Smallest B at which speedup crosses 1.0 (linear interp between grid points)."""
    items = sorted(curve.items())
    cross = None
    for (b0, s0), (b1, s1) in zip(items, items[1:]):
        if (s0 < 1.0 <= s1) or (s0 >= 1.0 > s1):
            frac = (1.0 - s0) / (s1 - s0) if s1 != s0 else 0.0
            b = b0 + frac * (b1 - b0)
            cross = b if cross is None else cross
    # also handle "already >1 at smallest B"
    if items[0][1] >= 1.0 and cross is None:
        return items[0][0]
    return cross


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: python scripts/block_size_sweep.py <run-dir>", file=sys.stderr)
        return 2
    path = os.path.join(args[0], "blocks.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    by = {d: [r for r in rows if r["domain"] == d] for d in DOMAINS}

    # ---- speedup vs B ----
    print("=== implied speedup vs block size B (1.0 = AR break-even) ===\n")
    header = "B".rjust(5) + "".join(d[:8].rjust(9) for d in DOMAINS)
    print(header)
    curves = {d: sweep_domain(by[d]) for d in DOMAINS}
    for B in B_GRID:
        row = f"{B:>5}" + "".join(f"{curves[d][B]:>9.2f}" for d in DOMAINS)
        print(row)
    print("\n  crossing B (speedup -> 1.0) and best B (max speedup):")
    for d in DOMAINS:
        c = crossing(curves[d])
        bestB = max(curves[d], key=lambda b: curves[d][b])
        cross_s = f"B*~{c:.0f}" if c is not None else "never crosses 1.0"
        print(f"    {d:<11} {cross_s:<22} best: B={bestB} -> {curves[d][bestB]:.2f}x  (B=256 -> {curves[d][256]:.2f}x)")

    # ---- APL normalized by content length (content-cap vs disagreement-cap) ----
    print("\n=== APL / content_length: is acceptance capped by content or by disagreement? ===\n")
    print(f"{'domain':<11}{'meanAPL/clen':>14}{'%fully_accepted':>17}{'med_content_len':>17}")
    for d in DOMAINS:
        ratios = []
        full = 0
        clens = []
        for r in by[d]:
            clen = len(r["match"])
            if clen == 0:
                continue
            apl = r["accepted_prefix_len"]
            ratios.append(apl / clen)
            clens.append(clen)
            if apl == clen:
                full += 1
        print(f"{d:<11}{statistics.fmean(ratios):>14.2f}{100*full/len(ratios):>16.0f}%{statistics.median(clens):>17.0f}")
    print("\n  ratio~1.0 + high %fully_accepted => content-capped: the drafter agrees on")
    print("  the WHOLE answer and acceptance is limited only by how short the answer is.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
