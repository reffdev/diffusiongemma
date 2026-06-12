"""Shared record types passed between drafter, verifier, and metrics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DraftBlock:
    """One committed canvas block emitted by the drafter.

    `draft_ids` are the newly committed block tokens whose agreement we measure
    (the running prefix is reconstructed by the caller from preceding blocks).

    `denoise_steps` and `commit_entropy` are only available when the internal
    denoise loop is instrumented (the optional source-hook capture path); the
    public generate() API does not expose them, so they are None by default.
    Metrics that depend on them (speedup, entropy~disagreement correlation)
    degrade to None rather than fabricating values.
    """

    block_index: int
    draft_ids: list[int]
    denoise_steps: int | None = None
    commit_entropy: list[float] | None = None


@dataclass
class VerifyResult:
    """Verifier's parallel teacher-forced pass over a draft block."""

    # Verifier argmax token at each drafted position (greedy prediction).
    argmax_ids: list[int]
    # Verifier logprob assigned to the *drafted* token at each position.
    logprob_of_draft: list[float]


@dataclass
class BlockRecord:
    """One JSONL record. Raw per-position arrays are never aggregated away."""

    domain: str
    prompt_id: str
    block_index: int

    draft_ids: list[int]
    argmax_ids: list[int]
    logprob_of_draft: list[float]
    match: list[bool]
    commit_entropy: list[float] | None
    denoise_steps: int | None

    # Derived per-block metrics (also recomputable from the raw arrays).
    accepted_prefix_len: int = 0
    p_block: float = 0.0
    # None when denoise_steps is unknown (public-API capture path).
    speedup_estimate: float | None = None

    extra: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        return {
            "domain": self.domain,
            "prompt_id": self.prompt_id,
            "block_index": self.block_index,
            "draft_ids": self.draft_ids,
            "argmax_ids": self.argmax_ids,
            "logprob_of_draft": self.logprob_of_draft,
            "match": self.match,
            "commit_entropy": self.commit_entropy,
            "denoise_steps": self.denoise_steps,
            "accepted_prefix_len": self.accepted_prefix_len,
            "p_block": self.p_block,
            "speedup_estimate": self.speedup_estimate,
            **({"extra": self.extra} if self.extra else {}),
        }
