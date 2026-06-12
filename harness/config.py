"""Configuration dataclasses for the agreement harness.

These are intentionally boring and explicit. Every run snapshots its full
config to results/<run>/config.json so any number can be traced back to the
exact settings (and model/transformers versions) that produced it.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

# Model identifiers (per the initial plan). Override on the CLI if the actual
# published repo names differ from these — they were written before release.
# Verified against the Hugging Face Hub (released 2026-06-10). Repo IDs are
# case-sensitive — the verifier is "...26B-A4B-it", not lowercase.
DRAFTER_MODEL_ID = "google/diffusiongemma-26B-A4B-it"
VERIFIER_MODEL_ID = "google/gemma-4-26B-A4B-it"  # autoregressive verifier (instruct)

DOMAINS = ("code", "structured", "chat", "prose")


@dataclass
class SamplerConfig:
    """DiffusionGemma sampler settings.

    Defaults are the documented model-card recommendations (HF model card /
    developer guide, 2026-06-10): canvas 256, max denoise steps 48, entropy
    bound 0.1, stopping entropy 0.005, recommended temp schedule 0.8 -> 0.4.

    NOTE on determinism: the plan wants temperature-0 / deterministic decoding
    for reproducible agreement measurement, which diverges from the stock
    stochastic 0.8->0.4 schedule. `deterministic=True` selects greedy decoding;
    set it False to measure under the stock recommended sampler instead (and
    record which you used in the run notes).
    """

    block_size: int = 256                 # canvas length / committed block width
    entropy_bound: float = 0.1            # entropy-bounded denoising
    stopping_entropy_threshold: float = 0.005
    stability_steps: int = 2              # stability across N consecutive steps
    max_denoise_steps: int = 48           # model-card recommended max
    deterministic: bool = True            # greedy / temp-0 for measurement
    temperature: float = 0.0              # used only when deterministic is False


@dataclass
class ModelConfig:
    drafter_model_id: str = DRAFTER_MODEL_ID
    verifier_model_id: str = VERIFIER_MODEL_ID
    # Quantization. "bf16" = no quant (default). "int8" = bitsandbytes. "fp8" =
    # FineGrainedFP8 — NOTE: fp8 grouped-MoE matmul does NOT run on SM120
    # (RTX PRO 6000 Blackwell workstation): DeepGEMM needs SM90/SM100, and the
    # Triton fallback rejects this model's expert dim (704 % 128 != 0). Use
    # bf16 (default) on this hardware. fp8 is for SM90/SM100 datacenter parts.
    drafter_quant: str = "bf16"
    verifier_quant: str = "bf16"
    device_map: str = "auto"
    hf_cache_dir: str | None = None


@dataclass
class RunConfig:
    domains: tuple[str, ...] = DOMAINS
    prompts_dir: str = "prompts"
    results_dir: str = "results"
    tag: str = "dev"
    max_prompts_per_domain: int | None = None   # None = all; small int for "start tiny"
    max_blocks_per_prompt: int = 8              # cap blocks so prompts terminate
    seed: int = 0
    mock: bool = False                          # synthetic models for local pipeline tests
    # Two-pass measurement: load the drafter alone and generate all drafts, free
    # it, then load the verifier alone and teacher-force. Peak VRAM = one model,
    # so two 26B models don't need to co-reside (they don't fit in 96 GB at
    # bf16/int8, and fp8 MoE doesn't run on SM120). Default True for real runs.
    sequential: bool = True
    # Opt-in: instrument DiffusionGemma's internal denoise loop to capture
    # per-block denoise-step counts + commit-time entropy (needed for the
    # speedup and entropy~disagreement metrics). Requires reading the installed
    # modeling source — see drafter.py. Off => those metrics report None.
    capture_internals: bool = False

    sampler: SamplerConfig = field(default_factory=SamplerConfig)
    models: ModelConfig = field(default_factory=ModelConfig)

    # Populated at runtime for the config snapshot; not set by the user.
    transformers_version: str | None = None
    torch_version: str | None = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
