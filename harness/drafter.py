"""Drafter: generate with DiffusionGemma and capture committed canvas blocks.

Two capture paths, by design:

1. PUBLIC-API path (default, fully implemented). DiffusionGemma's documented
   API is `DiffusionGemmaForBlockDiffusion.generate(...)`, which denoises the
   text in 256-token canvas blocks and returns the final committed token IDs.
   At temperature-0 / greedy this is deterministic, so the committed blocks are
   exactly the generated continuation sliced into canvas-sized chunks. That is
   all the *agreement* measurement needs (per-token p, accepted-prefix length).

2. INTERNALS path (opt-in, --capture-internals). Per-block denoise-step counts
   and commit-time entropy are NOT exposed by the public generate(); they feed
   the *speedup* and *entropy~disagreement* metrics. Capturing them requires
   instrumenting the model's internal denoise loop, which means reading the
   installed modeling source (transformers/models/diffusiongemma/
   modeling_diffusiongemma.py) and hooking the canvas->commit step. That seam
   is intentionally left as `_InternalsCapture` below: it raises with a precise
   checklist until wired, and the default path never touches it.
"""

from __future__ import annotations

from typing import Protocol

from .config import SamplerConfig
from .metrics import content_length
from .types import DraftBlock


class Drafter(Protocol):
    def draft(self, prompt_ids: list[int], max_blocks: int) -> list[DraftBlock]:
        """Generate a continuation and return it as ordered committed blocks."""
        ...


class _InternalsCapture:
    """Opt-in instrumentation of the internal denoise loop. NOT yet wired.

    To implement: read modeling_diffusiongemma.py, find the per-canvas denoise
    loop and the commit step (canvas -> KV-cache append), and register a hook /
    subclass that records, per committed block, the number of denoise steps used
    and the per-position commit-time entropy. Then fill denoise_steps()/entropy()
    to return those per block_index. Do NOT guess attribute names — read them.
    """

    def __init__(self, model, sampler: SamplerConfig):
        self.model = model
        self.sampler = sampler

    def __enter__(self):
        raise NotImplementedError(
            "--capture-internals is not wired yet. The public generate() API does "
            "not expose per-block denoise steps or commit entropy. To capture them, "
            "instrument modeling_diffusiongemma.py's denoise/commit loop (see "
            "harness/drafter.py _InternalsCapture). Run without --capture-internals "
            "to measure agreement (p, accepted-prefix length) via the public API; "
            "speedup and entropy~disagreement will report None until this is wired."
        )

    def __exit__(self, *exc):
        return False

    def denoise_steps(self, block_index: int) -> int | None:  # pragma: no cover
        return None

    def entropy(self, block_index: int) -> list[float] | None:  # pragma: no cover
        return None


def _describe(v):
    """Compact description of a generation-output field value (no big dumps)."""
    if hasattr(v, "shape"):
        return {"kind": "tensor", "shape": list(v.shape), "dtype": str(getattr(v, "dtype", ""))}
    if isinstance(v, (list, tuple)):
        return {"kind": "seq", "len": len(v)}
    if v is None or isinstance(v, (int, float, bool, str)):
        return {"kind": "scalar", "value": v}
    return {"kind": type(v).__name__}


def _introspect_output(out) -> dict:
    """Dump the structure of a generation output object (ModelOutput-like).

    This is where a stop reason / step count / per-step record would live if the
    model exposes one — list every field with its shape/value so we can see it.
    """
    info = {"type": type(out).__name__, "fields": {}}
    try:
        keys = list(out.keys())
    except Exception:  # noqa: BLE001
        keys = [k for k in getattr(out, "__dict__", {})]
    for k in keys:
        try:
            v = out[k]
        except Exception:  # noqa: BLE001
            v = getattr(out, k, None)
        info["fields"][str(k)] = _describe(v)
    return info


class RealDiffusionGemmaDrafter:
    """Generate with DiffusionGemma and slice the output into committed blocks."""

    def __init__(self, loaded, sampler: SamplerConfig, seed: int = 0, capture_internals: bool = False):
        self.loaded = loaded
        self.sampler = sampler
        self.seed = seed
        self.capture_internals = capture_internals
        # Populated on every draft() call; the Pass-1 loop reads it to log/raise.
        self.last_diagnostics: dict = {}

    def draft(self, prompt_ids: list[int], max_blocks: int) -> list[DraftBlock]:
        import torch

        model = self.loaded.model
        device = next(model.parameters()).device
        block = self.sampler.block_size

        # Reproducibility: diffusion decoding can be stochastic even when the
        # token argmax is taken — fix the seed per call.
        torch.manual_seed(self.seed)

        gen_kwargs: dict = {"max_new_tokens": block * max_blocks}
        if self.sampler.deterministic:
            gen_kwargs["do_sample"] = False  # greedy / temp-0 where the sampler allows
        else:
            gen_kwargs["do_sample"] = True
            gen_kwargs["temperature"] = self.sampler.temperature

        input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=device)
        # Pass an explicit attention_mask. The diffusion sampler needs it to lay
        # out the canvas; without it, generate() returns only the prompt (no new
        # tokens), which silently yields zero committed blocks.
        attention_mask = torch.ones_like(input_ids)
        gen_kwargs["attention_mask"] = attention_mask

        capture = _InternalsCapture(model, self.sampler) if self.capture_internals else None
        with torch.no_grad():
            if capture is not None:
                with capture:
                    out = model.generate(input_ids=input_ids, **gen_kwargs)
            else:
                out = model.generate(input_ids=input_ids, **gen_kwargs)

        # generate() returns a DiffusionGemmaGenerationOutput (a ModelOutput),
        # NOT a tensor. Its first field is `sequences` of shape [batch, seq];
        # indexing the object (out[0]) returns that whole tensor, so we must go
        # through .sequences and then take batch row 0.
        sequences = getattr(out, "sequences", out)
        if hasattr(sequences, "tolist"):
            sequences = sequences.tolist()
        seq = sequences[0] if sequences and isinstance(sequences[0], list) else sequences

        # Auto-detect whether generate returned prompt+continuation or just the
        # continuation, instead of assuming. Strip the prompt only if present.
        plist = list(prompt_ids)
        continuation = seq[len(plist):] if seq[: len(plist)] == plist else seq

        # Trim the canvas's trailing <pad> run: those positions are not real
        # drafted tokens and would pollute the per-token agreement (see
        # metrics.content_length). pad_token_id is read from the tokenizer.
        pad_id = getattr(self.loaded.tokenizer, "pad_token_id", None)
        pad_id = 0 if pad_id is None else pad_id
        continuation = continuation[: content_length(continuation, pad_id)]

        # Full diagnostics for the Pass-1 loop (fail-loud instrumentation).
        try:
            mem_allocated = int(torch.cuda.memory_allocated()) if torch.cuda.is_available() else None
        except Exception:  # noqa: BLE001
            mem_allocated = None
        self.last_diagnostics = {
            "input_token_count": len(prompt_ids),
            "returned_len": len(seq),
            "continuation_len": len(continuation),
            "prompt_prefix_present": seq[: len(plist)] == plist,
            "continuation_ids": list(continuation),
            "returned_ids": list(seq),
            # Not exposed by the public generate(); see output_object fields and
            # --capture-internals. We report None rather than fabricate.
            "denoise_steps": None,
            "stop_reason": None,
            "cuda_mem_allocated": mem_allocated,
            "output_object": _introspect_output(out),
            "gen_kwargs": {
                "max_new_tokens": gen_kwargs.get("max_new_tokens"),
                "do_sample": gen_kwargs.get("do_sample"),
                "attention_mask_shape": list(attention_mask.shape),
                "input_ids_shape": list(input_ids.shape),
            },
        }

        blocks: list[DraftBlock] = []
        for start in range(0, len(continuation), block):
            chunk = continuation[start : start + block]
            if not chunk:
                break
            bi = start // block
            blocks.append(
                DraftBlock(
                    block_index=bi,
                    draft_ids=chunk,
                    denoise_steps=(capture.denoise_steps(bi) if capture else None),
                    commit_entropy=(capture.entropy(bi) if capture else None),
                )
            )
            if len(blocks) >= max_blocks:
                break
        return blocks


class MockDrafter:
    """Deterministic synthetic drafter for local pipeline tests (no GPU).

    Produces reproducible blocks whose token IDs are a function of (seed,
    block_index), with synthetic denoise_steps and commit entropy so the full
    metrics path (including speedup and entropy~disagreement) is exercised. The
    numbers are meaningless as agreement data.
    """

    def __init__(
        self,
        sampler: SamplerConfig,
        seed: int = 0,
        vocab_size: int = 256000,
        n_blocks: int = 3,
        block_size: int | None = None,
    ):
        self.sampler = sampler
        self.seed = seed
        self.vocab_size = vocab_size
        self.n_blocks = n_blocks
        self.block_size = block_size or min(sampler.block_size, 16)

    def draft(self, prompt_ids: list[int], max_blocks: int) -> list[DraftBlock]:
        import random

        n = min(max_blocks, self.n_blocks)
        blocks: list[DraftBlock] = []
        for block_index in range(n):
            rng = random.Random(f"{self.seed}-{block_index}-{len(prompt_ids)}")
            draft_ids = [rng.randrange(self.vocab_size) for _ in range(self.block_size)]
            commit_entropy = [
                round(0.001 + 0.01 * (i / self.block_size), 6) for i in range(self.block_size)
            ]
            blocks.append(
                DraftBlock(
                    block_index=block_index,
                    draft_ids=draft_ids,
                    denoise_steps=4 + block_index,
                    commit_entropy=commit_entropy,
                )
            )
        return blocks
