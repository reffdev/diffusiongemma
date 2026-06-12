"""Results IO: timestamped run dir, config snapshot, JSONL records, summary.

Every run produces results/<date>-<tag>/{config.json, blocks.jsonl, summary.md}.
Raw blocks.jsonl is THE artifact (one record per committed block, full
per-position arrays). summary.md is derived and never the source of truth.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from .config import RunConfig
from .metrics import DomainSummary, summarize
from .types import BlockRecord


class ResultsWriter:
    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        os.makedirs(run_dir, exist_ok=True)
        self._blocks_path = os.path.join(run_dir, "blocks.jsonl")
        self._fh = open(self._blocks_path, "w", encoding="utf-8")

    @classmethod
    def create(cls, results_dir: str, tag: str, now: datetime | None = None) -> "ResultsWriter":
        now = now or datetime.now(timezone.utc)
        stamp = now.strftime("%Y%m%d-%H%M%S")
        run_dir = os.path.join(results_dir, f"{stamp}-{tag}")
        return cls(run_dir)

    def write_config(self, cfg: RunConfig, extra: dict | None = None) -> None:
        payload = cfg.to_dict()
        if extra:
            payload["_runtime"] = extra
        with open(os.path.join(self.run_dir, "config.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)

    def write_block(self, rec: BlockRecord) -> None:
        self._fh.write(json.dumps(rec.to_json(), ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    def __enter__(self) -> "ResultsWriter":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def _fmt(x) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.4f}"
    return str(x)


def write_summary(run_dir: str, records: list[BlockRecord]) -> str:
    """Compute per-domain + overall summaries and write summary.md. Returns path."""
    by_domain: dict[str, list[BlockRecord]] = {}
    for r in records:
        by_domain.setdefault(r.domain, []).append(r)

    summaries: list[DomainSummary] = [summarize(recs, d) for d, recs in sorted(by_domain.items())]
    overall = summarize(records, "ALL")

    lines: list[str] = []
    lines.append("# Agreement summary\n")
    lines.append(
        "Per-token greedy agreement `p`, accepted-prefix-length (APL) distribution, "
        "implied speedup (accepted tokens / weight passes), and the "
        "commit-entropy vs disagreement correlation. Derived from blocks.jsonl.\n"
    )
    header = (
        "| domain | blocks | positions | p | APL mean | APL median | APL p90 | speedup | entropy~disagree corr |"
    )
    sep = "|---|---|---|---|---|---|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for s in summaries + [overall]:
        lines.append(
            f"| {s.domain} | {s.n_blocks} | {s.n_positions} | {_fmt(s.p)} | "
            f"{_fmt(s.apl_mean)} | {_fmt(s.apl_median)} | {_fmt(s.apl_p90)} | "
            f"{_fmt(s.speedup)} | {_fmt(s.entropy_disagreement_corr)} |"
        )

    lines.append("\n## Accepted-prefix-length histograms\n")
    for s in summaries:
        lines.append(f"### {s.domain}")
        lines.append("```")
        for apl, count in sorted(s.apl_histogram.items()):
            lines.append(f"{apl:>4}: {'#' * min(count, 60)} ({count})")
        lines.append("```")

    lines.append("\n## Decision gates (per the plan)\n")
    lines.append("- code p ≳ 0.90 and median APL ≳ 10  → Phase 2 viable with small blocks")
    lines.append("- p 0.7–0.9  → viable with reduced block size / light distillation")
    lines.append("- p < 0.7  → Phase 2 becomes a distillation project first")

    text = "\n".join(lines) + "\n"
    path = os.path.join(run_dir, "summary.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path
