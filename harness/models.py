"""Load the drafter (DiffusionGemma) and verifier (Gemma 4) with quantization.

Both models must be resident simultaneously in production (96 GB Blackwell).
During bring-up you can load sequentially. FP8 is preferred; int8 (bitsandbytes)
is the documented fallback if FP8 paths in the installed stack are immature.

This module is import-light: torch/transformers are imported lazily inside the
functions so the metrics/IO pipeline (and the mock mode) run on machines with
no GPU or no transformers install.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import ModelConfig


@dataclass
class LoadedModel:
    model: object
    tokenizer: object         # for the drafter this is processor.tokenizer
    model_id: str
    quant: str
    processor: object = None  # drafter only (AutoProcessor); None for verifier


def _quantization_config(quant: str):
    """Return a transformers quantization config (or None for bf16).

    NOTE: FP8 config wiring depends on the installed transformers/accelerate
    versions and may move. Verify against the installed source on bring-up.
    """
    quant = quant.lower()
    if quant == "bf16":
        return None
    if quant == "int8":
        from transformers import BitsAndBytesConfig

        return BitsAndBytesConfig(load_in_8bit=True)
    if quant == "fp8":
        # Placeholder: FP8 is evolving in transformers. If unavailable in the
        # installed build, fall back to int8 and record the perf cost in notes.
        try:
            from transformers import FineGrainedFP8Config  # type: ignore

            return FineGrainedFP8Config()
        except Exception:  # noqa: BLE001
            raise RuntimeError(
                "fp8 quantization config not available in the installed transformers; "
                "use --drafter-quant int8 / --verifier-quant int8 (bitsandbytes) and "
                "note the perf cost, per the plan."
            )
    raise ValueError(f"unknown quant {quant!r} (expected fp8|int8|bf16)")


def load_tokenizer(model_id: str, cache_dir: str | None = None):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(
        model_id, cache_dir=cache_dir, trust_remote_code=True
    )


def load_verifier(cfg: ModelConfig) -> LoadedModel:
    import torch
    from transformers import AutoModelForCausalLM

    tok = load_tokenizer(cfg.verifier_model_id, cfg.hf_cache_dir)
    model = AutoModelForCausalLM.from_pretrained(
        cfg.verifier_model_id,
        device_map=cfg.device_map,
        quantization_config=_quantization_config(cfg.verifier_quant),
        dtype=torch.bfloat16,  # `torch_dtype` is deprecated in current transformers
        cache_dir=cfg.hf_cache_dir,
        trust_remote_code=True,
    )
    model.eval()
    return LoadedModel(model=model, tokenizer=tok, model_id=cfg.verifier_model_id, quant=cfg.verifier_quant)


def load_drafter(cfg: ModelConfig) -> LoadedModel:
    """Load DiffusionGemma via its documented public API.

    Per the HF model card / developer guide (2026-06-10): the loader class is
    `DiffusionGemmaForBlockDiffusion` and inputs go through an `AutoProcessor`
    (the model is multimodal). Requires a transformers build new enough to
    include the diffusiongemma model code (`pip install -U transformers`).
    """
    import torch
    from transformers import AutoProcessor, DiffusionGemmaForBlockDiffusion

    processor = AutoProcessor.from_pretrained(cfg.drafter_model_id, cache_dir=cfg.hf_cache_dir)
    model = DiffusionGemmaForBlockDiffusion.from_pretrained(
        cfg.drafter_model_id,
        device_map=cfg.device_map,
        quantization_config=_quantization_config(cfg.drafter_quant),
        dtype=torch.bfloat16,  # `torch_dtype` is deprecated in current transformers
        cache_dir=cfg.hf_cache_dir,
    )
    model.eval()
    return LoadedModel(
        model=model,
        tokenizer=processor.tokenizer,
        model_id=cfg.drafter_model_id,
        quant=cfg.drafter_quant,
        processor=processor,
    )
