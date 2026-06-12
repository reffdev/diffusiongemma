#!/usr/bin/env python
"""Compare native small-canvas runs against the sweep + floor-corrected predictions.

Sibling to block_size_sweep.py. The sweep predicted speedups by re-segmenting the
256-canvas trajectory (denoise held constant). This script checks those predictions
against runs done with a NATIVE B-token canvas (harness --block-size B, which sets
config.canvas_length=B).

For each native run and domain it reports measured native APL, native denoise
passes/block, measured speedup (verify pass included), and measured per-token p,
side by side with two predictions derived from the baseline (B=256) run:
  - sweep-predicted: total_accepted(B) / (total_denoise + n_proposals)  [optimistic]
  - floor-corrected: total_accepted(B) / (n_proposals * (max(1, B/tpf) + 1))
    [each block pays >=1 denoise pass + 1 verify pass]

Usage:
  python scripts/validate_block_size.py --baseline results/<run_final> \
      results/<b8> results/<b16> results/<b32>
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

DOMAINS = ["code", "chat", "prose"]


def load_rows(run_dir):
    return [json.loads(l) for l in open(os.path.join(run_dir, "blocks.jsonl"), encoding="utf-8") if l.strip()]


def run_block_size(run_dir):
    c = json.load(open(os.path.join(run_dir, "config.json")))
    return int(c["sampler"]["block_size"])


def leading(window):
    a = 0
    for x in window:
        if x:
            a += 1
        else:
            break
    return a


def domain_measured(rows, dom):
    rs = [r for r in rows if r["domain"] == dom]
    if not rs:
        return None
    pos = sum(len(r["match"]) for r in rs)
    agree = sum(sum(r["match"]) for r in rs)
    apls = [r["accepted_prefix_len"] for r in rs]
    den = [r["denoise_steps"] for r in rs if r.get("denoise_steps")]
    accepted = sum(apls)
    passes = sum((r.get("denoise_steps") or 0) + 1 for r in rs)
    return {
        "n": len(rs),
        "p": agree / pos if pos else 0.0,
        "apl_med": statistics.median(apls),
        "apl_mean": statistics.fmean(apls),
        "den_per_blk": statistics.fmean(den) if den else float("nan"),
        "speedup": accepted / passes if passes else 0.0,
    }


def domain_predictions(base_rows, dom, B):
    rs = [r for r in base_rows if r["domain"] == dom]
    tpf = statistics.fmean(len(r["match"]) / r["denoise_steps"] for r in rs if r.get("denoise_steps"))
    total_denoise = sum(r["denoise_steps"] for r in rs if r.get("denoise_steps"))
    accepted = n_prop = 0
    for r in rs:
        m = r["match"]
        i = 0
        while i < len(m):
            accepted += leading(m[i : i + B])
            n_prop += 1
            i += B
    sweep = accepted / (total_denoise + n_prop) if (total_denoise + n_prop) else 0.0
    floor = accepted / (n_prop * (max(1.0, B / tpf) + 1)) if n_prop else 0.0
    return sweep, floor, tpf


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, help="B=256 run dir (run_final)")
    ap.add_argument("native", nargs="+", help="native small-canvas run dirs (b8, b16, b32)")
    args = ap.parse_args(argv)

    base_rows = load_rows(args.baseline)
    base_p = {d: domain_measured(base_rows, d)["p"] for d in DOMAINS}
    native = []
    for d in args.native:
        native.append((run_block_size(d), load_rows(d)))
    native.sort()

    print("=== native block-size validation: predicted vs measured speedup ===\n")
    print(f"{'domain':<7}{'B':>4}{'sweep':>8}{'floor':>8}{'MEASURED':>10}{'meas_p':>8}{'base_p256':>10}{'natAPLmed':>10}{'den/blk':>9}")
    for dom in DOMAINS:
        for B, rows in native:
            m = domain_measured(rows, dom)
            if m is None:
                continue
            sweep, floor, _ = domain_predictions(base_rows, dom, B)
            print(f"{dom:<7}{B:>4}{sweep:>8.2f}{floor:>8.2f}{m['speedup']:>10.2f}"
                  f"{m['p']:>8.3f}{base_p[dom]:>10.3f}{m['apl_med']:>10.1f}{m['den_per_blk']:>9.2f}")
        # baseline B=256 row for reference
        bm = domain_measured(base_rows, dom)
        print(f"{dom:<7}{256:>4}{'—':>8}{'—':>8}{bm['speedup']:>10.2f}{bm['p']:>8.3f}{base_p[dom]:>10.3f}{bm['apl_med']:>10.1f}{bm['den_per_blk']:>9.2f}")
        print()

    # (a) where does code cross 1.0 / peak, from MEASURED points
    print("(a) code, measured speedup by B (incl. baseline):")
    pts = sorted([(B, domain_measured(rows, "code")["speedup"]) for B, rows in native]
                 + [(256, domain_measured(base_rows, "code")["speedup"])])
    print("    " + "  ".join(f"B={b}:{s:.2f}" for b, s in pts))
    best = max(pts, key=lambda x: x[1])
    crosses = [b for b, s in pts if s >= 1.0]
    print(f"    peak: B={best[0]} -> {best[1]:.2f}x ;  >=1.0x at B in {crosses or 'none'}")

    # (b) native p vs baseline p
    print("\n(b) per-token p: native small canvas vs B=256 baseline (does lost lookahead hurt agreement?):")
    for dom in DOMAINS:
        deltas = []
        for B, rows in native:
            m = domain_measured(rows, dom)
            if m:
                deltas.append(f"B={B}:{m['p']:.3f}({m['p']-base_p[dom]:+.3f})")
        print(f"    {dom:<7} base256={base_p[dom]:.3f}  " + "  ".join(deltas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
