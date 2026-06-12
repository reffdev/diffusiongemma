"""Verifier: teacher-force a draft block through Gemma 4 in one parallel pass.

Given (prefix_ids + draft_ids), a single forward pass of the AR verifier yields,
at every drafted position, the logits used to predict the *next* token. We
record, per drafted position:
  - the verifier's argmax token (its greedy prediction), and
  - the verifier's logprob of the *drafted* token (for soft-agreement later).

Greedy match at position i means: argmax of verifier logits at the position
that predicts draft token i  ==  draft token i.
"""

from __future__ import annotations

from typing import Protocol

from .types import VerifyResult


class Verifier(Protocol):
    def verify_block(self, prefix_ids: list[int], draft_ids: list[int]) -> VerifyResult:
        ...


class RealGemmaVerifier:
    """Single parallel teacher-forced pass through the AR verifier.

    Standard next-token alignment: feeding [prefix + draft], the logits at
    sequence index (len(prefix) + i - 1) predict draft token i. We slice that
    window, take argmax and the drafted-token logprob at each position.
    """

    def __init__(self, loaded):
        self.loaded = loaded

    def verify_block(self, prefix_ids: list[int], draft_ids: list[int]) -> VerifyResult:
        import torch

        model = self.loaded.model
        device = next(model.parameters()).device
        seq = prefix_ids + draft_ids
        input_ids = torch.tensor([seq], dtype=torch.long, device=device)

        with torch.no_grad():
            out = model(input_ids=input_ids)
            logits = out.logits[0]  # [seq_len, vocab]

        n_prefix = len(prefix_ids)
        n_draft = len(draft_ids)
        # Position that predicts draft token i is (n_prefix + i - 1).
        start = n_prefix - 1
        window = logits[start : start + n_draft]  # [n_draft, vocab]
        logprobs = torch.log_softmax(window.float(), dim=-1)

        argmax_ids = window.argmax(dim=-1).tolist()
        draft_tensor = torch.tensor(draft_ids, device=logits.device)
        lp_of_draft = logprobs.gather(1, draft_tensor.unsqueeze(1)).squeeze(1).tolist()

        return VerifyResult(argmax_ids=argmax_ids, logprob_of_draft=lp_of_draft)


class MockVerifier:
    """Deterministic synthetic verifier for local pipeline tests.

    Agrees with the drafted token at a fixed fraction of positions, with
    disagreements placed deterministically so accepted-prefix-length and the
    entropy/disagreement correlation are predictable and assertable.
    """

    def __init__(self, agree_rate: float = 0.8, seed: int = 0, vocab_size: int = 256000):
        self.agree_rate = agree_rate
        self.seed = seed
        self.vocab_size = vocab_size

    def verify_block(self, prefix_ids: list[int], draft_ids: list[int]) -> VerifyResult:
        import math
        import random

        rng = random.Random(f"{self.seed}-{len(prefix_ids)}-{draft_ids[:4]}")
        argmax_ids: list[int] = []
        logprob_of_draft: list[float] = []
        for i, tok in enumerate(draft_ids):
            agree = rng.random() < self.agree_rate
            if agree:
                argmax_ids.append(tok)
                logprob_of_draft.append(-0.05)  # high logprob when agreeing
            else:
                # A different token id (avoid collision with the drafted one).
                argmax_ids.append((tok + 1) % self.vocab_size)
                logprob_of_draft.append(-math.log(self.vocab_size))  # ~uniform
        return VerifyResult(argmax_ids=argmax_ids, logprob_of_draft=logprob_of_draft)
