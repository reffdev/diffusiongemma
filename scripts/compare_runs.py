#!/usr/bin/env python
"""Per-domain delta between two runs' blocks.jsonl (e.g. bf16 run_final vs nvfp4).

Pure analysis, no models. Reports p, APL median, implied speedup for each run,
Δp (compare - baseline), and flags if structured's p drops below 0.98 in the
compare run.

Usage:
  python scripts/compare_runs.py results/<run_final> results/<nvfp4_run>
"""

from __future__ import annotations

import json
import os
import statistics
import sys

DOMAINS = ["code", "structured", "chat", "prose"]
STRUCTURED_FLOOR = 0.98


def load_rows(run_dir):
    return [json.loads(l) for l in open(os.path.join(run_dir, "blocks.jsonl"), encoding="utf-8") if l.strip()]


def domain_stats(rows, dom):
    rs = [r for r in rows if r["domain"] == dom]
    if not rs:
        return None
    pos = sum(len(r["match"]) for r in rs)
    agree = sum(sum(r["match"]) for r in rs)
    apls = [r["accepted_prefix_len"] for r in rs]
    den = [r["denoise_steps"] for r in rs if r.get("denoise_steps")]
    if den and len(den) == len(rs):
        acc = sum(apls)
        passes = sum((r["denoise_steps"] or 0) + 1 for r in rs)
        speedup = acc / passes if passes else 0.0
    else:
        speedup = None  # n/a (e.g. vLLM run has no tokens_per_forward)
    return {"n": len(rs), "p": agree / pos if pos else 0.0,
            "apl_med": statistics.median(apls), "speedup": speedup}


def _fmt(x):
    return "n/a" if x is None else f"{x:.3f}"


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print("usage: python scripts/compare_runs.py <baseline_run> <compare_run>", file=sys.stderr)
        return 2
    base_dir, cmp_dir = args
    base, cmp = load_rows(base_dir), load_rows(cmp_dir)

    print(f"baseline: {base_dir}\ncompare : {cmp_dir}\n")
    print(f"{'domain':<11}{'p_base':>8}{'p_cmp':>8}{'Δp':>9}{'APL_base':>10}{'APL_cmp':>9}{'spd_base':>10}{'spd_cmp':>9}")
    flags = []
    for dom in DOMAINS:
        b, c = domain_stats(base, dom), domain_stats(cmp, dom)
        if b is None or c is None:
            print(f"{dom:<11}  (missing in one run)")
            continue
        dp = c["p"] - b["p"]
        print(f"{dom:<11}{b['p']:>8.3f}{c['p']:>8.3f}{dp:>+9.3f}"
              f"{b['apl_med']:>10.1f}{c['apl_med']:>9.1f}{_fmt(b['speedup']):>10}{_fmt(c['speedup']):>9}")
        if dom == "structured" and c["p"] < STRUCTURED_FLOOR:
            flags.append(f"structured p={c['p']:.3f} < {STRUCTURED_FLOOR} in compare run")

    print("\n" + ("FLAGS:\n  - " + "\n  - ".join(flags) if flags
                  else f"OK: structured p stayed >= {STRUCTURED_FLOOR}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
