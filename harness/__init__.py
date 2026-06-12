"""Phase 1 agreement-measurement harness.

Measures the per-token greedy agreement rate `p` between DiffusionGemma's
committed draft blocks and Gemma 4's argmax predictions, broken down by
content domain. This package produces *measurement only* — it does not
implement the speculative sampler (that is Phase 2+).

Module map:
    config           run/model/sampler configuration dataclasses
    prompts          load versioned prompt sets from prompts/<domain>.jsonl
    tokenizer_check  assert drafter/verifier tokenizer identity
    models           load drafter + verifier (FP8/int8 quantization)
    drafter          generate with DiffusionGemma, capture committed blocks
    verifier         teacher-force a draft block through Gemma 4
    metrics          per-block + aggregate agreement metrics (pure functions)
    results_io       timestamped results dir, JSONL records, summary.md
    cli              orchestration entry point
"""

__version__ = "0.1.0"
