"""Agreement metrics — pure functions over raw per-position arrays.

This is the heart of the Phase 1 deliverable and is fully testable without any
model (see tests/). Nothing here aggregates away the raw per-position data; the
JSONL records carry the arrays and these helpers derive summaries from them.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

from .types import BlockRecord, DraftBlock, VerifyResult


def content_length(ids: list[int], pad_id: int = 0) -> int:
    """Length of `ids` with the trailing <pad> run removed.

    DiffusionGemma commits a fixed 256-token canvas and fills everything after
    its stop token with <pad> (id 0). Those positions are not real drafted
    tokens — measuring agreement over them collapses per-token `p` for short
    answers (structured) while leaving the meaningful prefix untouched. We trim
    only the *trailing* pad run (pad never appears mid-content), so the model's
    stop token (<end_of_turn>/<eos>) is kept as a real committed token.
    """
    n = len(ids)
    while n > 0 and ids[n - 1] == pad_id:
        n -= 1
    return n


def compute_match(draft_ids: list[int], argmax_ids: list[int]) -> list[bool]:
    if len(draft_ids) != len(argmax_ids):
        raise ValueError(
            f"length mismatch: {len(draft_ids)} draft vs {len(argmax_ids)} argmax"
        )
    return [d == a for d, a in zip(draft_ids, argmax_ids)]


def accepted_prefix_len(match: list[bool]) -> int:
    """Number of leading positions before the first disagreement.

    This is the prefix-acceptance length: how many tokens a greedy speculative
    loop could commit from this block before it would have to resample.
    """
    for i, m in enumerate(match):
        if not m:
            return i
    return len(match)


def block_agreement(match: list[bool]) -> float:
    return (sum(match) / len(match)) if match else 0.0


def speedup_estimate(apl: int, denoise_steps: int | None) -> float | None:
    """Accepted tokens per weight pass.

    Weight passes for one block = denoise_steps (drafter) + 1 (verifier pass).
    A value of 1.0 means break-even with plain autoregressive decoding.

    Returns None when denoise_steps is unknown — the public generate() API does
    not expose per-block step counts, so this metric requires the optional
    internals-capture path. We never fabricate a step count.
    """
    if denoise_steps is None:
        return None
    return apl / (denoise_steps + 1)


def build_record(
    domain: str,
    prompt_id: str,
    block: DraftBlock,
    verify: VerifyResult,
) -> BlockRecord:
    match = compute_match(block.draft_ids, verify.argmax_ids)
    apl = accepted_prefix_len(match)
    rec = BlockRecord(
        domain=domain,
        prompt_id=prompt_id,
        block_index=block.block_index,
        draft_ids=list(block.draft_ids),
        argmax_ids=list(verify.argmax_ids),
        logprob_of_draft=list(verify.logprob_of_draft),
        match=match,
        commit_entropy=(list(block.commit_entropy) if block.commit_entropy is not None else None),
        denoise_steps=block.denoise_steps,
        accepted_prefix_len=apl,
        p_block=block_agreement(match),
        speedup_estimate=speedup_estimate(apl, block.denoise_steps),
    )
    return rec


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / math.sqrt(sxx * syy)


def _percentile(sorted_vals: list[float], q: float) -> float:
    """Linear-interpolation percentile, q in [0, 1]. Input must be sorted."""
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    idx = q * (len(sorted_vals) - 1)
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return float(sorted_vals[lo])
    frac = idx - lo
    return float(sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac)


@dataclass
class DomainSummary:
    domain: str
    n_blocks: int
    n_positions: int
    # Per-token greedy agreement over all positions in the domain.
    p: float
    # Accepted-prefix-length distribution.
    apl_mean: float
    apl_median: float
    apl_p90: float
    apl_histogram: dict[int, int]
    # Aggregate implied speedup: total accepted tokens / total weight passes.
    # None when no block has a known denoise-step count.
    speedup: float | None
    # corr(commit entropy, disagreement). Positive => higher entropy predicts
    # more disagreement (the drafter's own confidence is informative).
    entropy_disagreement_corr: float | None

    def to_json(self) -> dict:
        return {
            "domain": self.domain,
            "n_blocks": self.n_blocks,
            "n_positions": self.n_positions,
            "p": self.p,
            "apl_mean": self.apl_mean,
            "apl_median": self.apl_median,
            "apl_p90": self.apl_p90,
            "apl_histogram": {str(k): v for k, v in sorted(self.apl_histogram.items())},
            "speedup": self.speedup,
            "entropy_disagreement_corr": self.entropy_disagreement_corr,
        }


def summarize(records: list[BlockRecord], domain: str = "ALL") -> DomainSummary:
    n_blocks = len(records)
    total_match = sum(sum(r.match) for r in records)
    n_positions = sum(len(r.match) for r in records)
    p = (total_match / n_positions) if n_positions else 0.0

    apls = [r.accepted_prefix_len for r in records]
    apls_sorted = sorted(apls)
    apl_mean = statistics.fmean(apls) if apls else 0.0
    apl_median = statistics.median(apls) if apls else 0.0
    apl_p90 = _percentile([float(a) for a in apls_sorted], 0.90) if apls else 0.0

    hist: dict[int, int] = {}
    for a in apls:
        hist[a] = hist.get(a, 0) + 1

    # Aggregate speedup only over blocks whose denoise_steps are known. If none
    # are known (public-API capture path), speedup is None, not a fake number.
    known = [r for r in records if r.denoise_steps is not None]
    if known:
        total_accepted = sum(r.accepted_prefix_len for r in known)
        total_passes = sum(r.denoise_steps + 1 for r in known)
        speedup = (total_accepted / total_passes) if total_passes else 0.0
    else:
        speedup = None

    # Entropy vs disagreement correlation across every position that has entropy.
    ent: list[float] = []
    dis: list[float] = []
    for r in records:
        if r.commit_entropy is None:
            continue
        for e, m in zip(r.commit_entropy, r.match):
            ent.append(e)
            dis.append(0.0 if m else 1.0)
    corr = _pearson(ent, dis) if ent else None

    return DomainSummary(
        domain=domain,
        n_blocks=n_blocks,
        n_positions=n_positions,
        p=p,
        apl_mean=apl_mean,
        apl_median=apl_median,
        apl_p90=apl_p90,
        apl_histogram=hist,
        speedup=speedup,
        entropy_disagreement_corr=corr,
    )
