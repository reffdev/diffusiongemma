#!/usr/bin/env python
"""Find out what the drafter's generation output exposes for speedup/entropy.

Before instrumenting modeling_diffusiongemma.py, check what's already in the
public output. The output object has a `tokens_per_forward` field — if that
gives committed-tokens-per-forward-pass, we can compute speedup (accepted tokens
per weight pass) directly, no source hook. Also probes whether
return_dict_in_generate/output_scores expose per-step logits (for entropy).

Usage:
  python scripts/probe_internals.py --limit 4
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _device(model):
    dev = getattr(model, "device", None)
    return dev if dev is not None else next(model.parameters()).device


def _value(v):
    """Full value for small tensors/scalars, else a shape/type description."""
    if hasattr(v, "numel"):
        try:
            if v.numel() <= 8:
                return {"tensor_values": v.detach().float().cpu().tolist(), "shape": list(v.shape)}
            return {"shape": list(v.shape), "dtype": str(v.dtype)}
        except Exception:  # noqa: BLE001
            return {"shape": list(getattr(v, "shape", []))}
    if v is None or isinstance(v, (int, float, bool, str)):
        return v
    return type(v).__name__


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--domains", nargs="+", default=["code", "structured"])
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--max-new-tokens", type=int, default=768)
    args = p.parse_args(argv)

    import torch

    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.metrics import content_length
    from harness.models import load_drafter, load_tokenizer

    cfg = ModelConfig(drafter_quant="bf16")
    print("Loading drafter (bf16)...", file=sys.stderr)
    loaded = load_drafter(cfg)
    model, device = loaded.model, _device(loaded.model)
    vtok = load_tokenizer(cfg.verifier_model_id, cfg.hf_cache_dir)
    pad_id = getattr(loaded.tokenizer, "pad_token_id", 0) or 0

    from harness.prompts import load_all

    prompts = load_all("prompts", args.domains, limit=args.limit)
    print(f"\n{'id':<16}{'content':>8}{'blocks':>7}{'tok/fwd':>9}{'fwd_passes':>11}{'tok/block':>10}")
    for pr in prompts:
        ids = render_user_prompt(vtok, pr.prompt)
        ii = torch.tensor([ids], dtype=torch.long, device=device)
        am = torch.ones_like(ii)
        with torch.no_grad():
            out = model.generate(input_ids=ii, attention_mask=am,
                                  max_new_tokens=args.max_new_tokens, do_sample=False)
        seq = out.sequences[0].tolist()
        cont = seq[len(ids):] if seq[: len(ids)] == ids else seq
        cont = cont[: content_length(cont, pad_id)]
        n_blocks = max(1, (len(cont) + 255) // 256)
        tpf = float(out.tokens_per_forward[0]) if out.tokens_per_forward is not None else float("nan")
        fwd = (len(cont) / tpf) if tpf else float("nan")
        print(f"{pr.id:<16}{len(cont):>8}{n_blocks:>7}{tpf:>9.2f}{fwd:>11.1f}{len(cont)/n_blocks:>10.1f}")

    # One full field dump (values for small tensors) so we see everything available.
    print("\n=== full output fields (last prompt), values shown for small tensors ===")
    for k in out.keys():
        print(f"  {k}: {_value(out[k])}")

    # Does the model expose per-step scores/logits for entropy?
    print("\n=== probing return_dict_in_generate + output_scores ===")
    try:
        with torch.no_grad():
            out2 = model.generate(input_ids=ii, attention_mask=am, max_new_tokens=256,
                                  do_sample=False, return_dict_in_generate=True, output_scores=True)
        keys = list(out2.keys())
        print("  fields:", keys)
        for k in keys:
            if k not in out.keys():
                print(f"    NEW field {k}: {_value(out2[k])}")
    except Exception as exc:  # noqa: BLE001
        print(f"  output_scores not supported: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
