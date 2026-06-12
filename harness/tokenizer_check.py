"""Verify the drafter and verifier share an identical tokenization.

Agreement measurement is meaningless across mismatched tokenizers. Per the
plan: if vocab, special tokens, or chat-template token IDs differ in *any* way,
stop and report. This module raises TokenizerMismatch on any discrepancy.
"""

from __future__ import annotations

from dataclasses import dataclass

# A short fixed probe set. The chat-template render of a probe must produce
# identical IDs under both tokenizers, which exercises special/template tokens.
_PROBE_STRINGS = [
    "Hello, world!",
    "def add(a, b):\n    return a + b\n",
    '{"name": "x", "values": [1, 2, 3]}',
    "Explain the difference between a list and a tuple.",
    "  leading and trailing whitespace  ",
]


class TokenizerMismatch(RuntimeError):
    pass


@dataclass
class TokenizerCheckResult:
    ok: bool
    vocab_size_drafter: int
    vocab_size_verifier: int
    details: list[str]


def _special_tokens_map(tok) -> dict:
    # special_tokens_map values can be strings or AddedToken; stringify for compare.
    return {k: str(v) for k, v in getattr(tok, "special_tokens_map", {}).items()}


def check_tokenizers(drafter_tok, verifier_tok) -> TokenizerCheckResult:
    """Compare two HF tokenizers. Raises TokenizerMismatch on any difference."""
    details: list[str] = []

    d_vocab = drafter_tok.get_vocab()
    v_vocab = verifier_tok.get_vocab()
    if len(d_vocab) != len(v_vocab):
        details.append(f"vocab size differs: drafter={len(d_vocab)} verifier={len(v_vocab)}")
    elif d_vocab != v_vocab:
        # Same size, different mapping — report a few diffs.
        diffs = [t for t in d_vocab if v_vocab.get(t) != d_vocab[t]][:10]
        details.append(f"vocab mapping differs for tokens (sample): {diffs}")

    d_special = _special_tokens_map(drafter_tok)
    v_special = _special_tokens_map(verifier_tok)
    if d_special != v_special:
        details.append(f"special_tokens_map differs: drafter={d_special} verifier={v_special}")

    # Encode probes WITHOUT special tokens (raw vocab agreement)...
    for s in _PROBE_STRINGS:
        d_ids = drafter_tok.encode(s, add_special_tokens=False)
        v_ids = verifier_tok.encode(s, add_special_tokens=False)
        if d_ids != v_ids:
            details.append(f"encode mismatch (no special) for {s!r}: {d_ids} != {v_ids}")

    # ...and through the chat template (special/template token IDs).
    for s in _PROBE_STRINGS:
        try:
            d_ids = drafter_tok.apply_chat_template(
                [{"role": "user", "content": s}], add_generation_prompt=True, tokenize=True
            )
            v_ids = verifier_tok.apply_chat_template(
                [{"role": "user", "content": s}], add_generation_prompt=True, tokenize=True
            )
        except Exception as exc:  # noqa: BLE001 - surface template incompatibility
            details.append(f"apply_chat_template raised for {s!r}: {exc!r}")
            continue
        if d_ids != v_ids:
            details.append(f"chat-template token IDs differ for {s!r}: {d_ids} != {v_ids}")

    result = TokenizerCheckResult(
        ok=not details,
        vocab_size_drafter=len(d_vocab),
        vocab_size_verifier=len(v_vocab),
        details=details,
    )
    if not result.ok:
        raise TokenizerMismatch(
            "drafter/verifier tokenizers are not identical — agreement measurement "
            "would be meaningless. Discrepancies:\n  - " + "\n  - ".join(details)
        )
    return result
