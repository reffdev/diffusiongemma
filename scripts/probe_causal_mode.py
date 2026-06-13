#!/usr/bin/env python
"""GATE for rung-1: can DiffusionGemma be driven as a causal next-token LM?

DiffusionGemma exposes no native causal LM (no ForCausalLM, encoder returns
hidden states only, lm_head lives on the block-diffusion head over the canvas).
The only causal route is a WRAPPER: run the causal ENCODER, then apply the
existing lm_head to its last_hidden_state to get next-token logits. This probe
tests whether that wrapper produces coherent greedy generation.

Run in the bf16 harness venv (loads the bf16 drafter, which already works).
Slow generation is fine (naive O(n^2) greedy, no KV cache reuse).

Read the output:
  - coherent completions  -> the causal wrapper is viable; rung-1 is alive.
  - gibberish / repetition / empty -> the encoder isn't next-token-predictive;
    rung-1 is dead and the Docker dual-model route becomes the Phase-2 plan.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ENCODER_CLASSES = ("DiffusionGemmaEncoderTextModel", "DiffusionGemmaEncoderModel")


def main() -> int:
    import torch

    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.models import load_drafter
    from harness.prompts import load_domain

    loaded = load_drafter(ModelConfig(drafter_quant="bf16"))
    model = loaded.model
    tok = loaded.processor.tokenizer
    device = getattr(model, "device", None) or next(model.parameters()).device

    # --- locate the causal encoder submodule and the lm_head ---
    print("=== top-level children ===")
    for name, child in model.named_children():
        print(f"  {name}: {type(child).__name__}")
    encoder, enc_name = None, None
    for name, mod in model.named_modules():
        if type(mod).__name__ in ENCODER_CLASSES:
            encoder, enc_name = mod, name
            break  # first/outermost encoder match
    lm_head = getattr(model, "lm_head", None)
    print(f"\nencoder: {enc_name} ({type(encoder).__name__ if encoder else None})")
    print(f"lm_head: {type(lm_head).__name__ if lm_head is not None else None}")
    if encoder is None or lm_head is None:
        print("\nFAIL: could not locate encoder and/or lm_head — paths differ from "
              "the inspected source; print named_modules and adjust ENCODER_CLASSES.")
        return 1

    def causal_logits(ids):
        with torch.no_grad():
            out = encoder(input_ids=torch.tensor([ids], dtype=torch.long, device=device))
            h = out.last_hidden_state if hasattr(out, "last_hidden_state") else out[0]
            return lm_head(h)[0, -1]  # next-token logits at the last position

    prompts = load_domain("prompts", "structured", limit=1) + load_domain("prompts", "code", limit=1)
    for pr in prompts:
        ids = list(render_user_prompt(tok, pr.prompt))
        n0 = len(ids)
        try:
            for _ in range(40):
                nxt = int(causal_logits(ids).argmax().item())
                ids.append(nxt)
                if nxt in (tok.eos_token_id, 1, 107):
                    break
        except Exception as exc:  # noqa: BLE001
            print(f"\n[{pr.id}] encoder/lm_head call RAISED: {type(exc).__name__}: {exc}")
            print("  (encoder forward signature differs — report this, do not work around it)")
            return 1
        text = tok.decode(ids[n0:], skip_special_tokens=True)
        print(f"\n[{pr.domain}/{pr.id}] greedy causal-mode completion:\n  {text.strip()[:300]!r}")

    print("\nInterpretation: coherent text => causal wrapper viable (rung-1 alive); "
          "gibberish/repetition => rung-1 dead, go Docker dual-model.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
