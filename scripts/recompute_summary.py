#!/usr/bin/env python
"""Regenerate a run's summary from its blocks.jsonl with padding trimmed.

Older runs measured agreement over the full padded 256-token canvas, which
collapses per-token `p` for short answers. This re-derives the metrics over the
real drafted content only (trailing <pad> removed) — no model reload needed,
since blocks.jsonl already stores the per-position arrays.

Usage:
  python scripts/recompute_summary.py results/<run-dir>
Writes <run-dir>/summary_corrected.md and prints the table.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv=None) -> int:
    args = (argv if argv is not None else sys.argv[1:])
    if len(args) != 1:
        print("usage: python scripts/recompute_summary.py <run-dir>", file=sys.stderr)
        return 2
    run_dir = args[0]
    blocks_path = os.path.join(run_dir, "blocks.jsonl")
    if not os.path.exists(blocks_path):
        print(f"no blocks.jsonl in {run_dir}", file=sys.stderr)
        return 2

    from harness.metrics import build_record, content_length, summarize
    from harness.results_io import write_summary
    from harness.types import DraftBlock, VerifyResult

    records = []
    dropped = 0
    for line in open(blocks_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        cl = content_length(r["draft_ids"])  # pad_id defaults to 0
        if cl == 0:
            dropped += 1
            continue
        ce = r.get("commit_entropy")
        block = DraftBlock(
            block_index=r["block_index"],
            draft_ids=r["draft_ids"][:cl],
            denoise_steps=r.get("denoise_steps"),
            commit_entropy=(ce[:cl] if ce else None),
        )
        verify = VerifyResult(
            argmax_ids=r["argmax_ids"][:cl],
            logprob_of_draft=r["logprob_of_draft"][:cl],
        )
        records.append(build_record(r["domain"], r["prompt_id"], block, verify))

    # Write the corrected summary next to the original (non-destructive).
    path = write_summary(run_dir, records)
    corrected = os.path.join(run_dir, "summary_corrected.md")
    os.replace(path, corrected)

    # Print a compact per-domain table.
    by = {}
    for rec in records:
        by.setdefault(rec.domain, []).append(rec)
    print(f"recomputed {len(records)} blocks ({dropped} all-pad blocks dropped)\n")
    print(f"{'domain':<12}{'blocks':>7}{'p':>8}{'APLmed':>8}{'APLmean':>9}")
    for dom in sorted(by):
        s = summarize(by[dom], dom)
        print(f"{dom:<12}{s.n_blocks:>7}{s.p:>8.3f}{s.apl_median:>8.1f}{s.apl_mean:>9.1f}")
    s = summarize(records, "ALL")
    print(f"{'ALL':<12}{s.n_blocks:>7}{s.p:>8.3f}{s.apl_median:>8.1f}{s.apl_mean:>9.1f}")
    print(f"\nwrote {corrected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
