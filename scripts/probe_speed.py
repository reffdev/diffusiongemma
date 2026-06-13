#!/usr/bin/env python
"""Realized wall-clock speed: DiffusionGemma diffusion-mode vs plain AR (Gemma 4).

The speculative premise assumes the diffusion drafter is actually FASTER than AR
in wall-clock. The published "~4x" is a datacenter fp8 number; this box is SM120
in bf16 (fp8 doesn't run here). If diffusion tokens/sec is not clearly above AR
tokens/sec, speculative self-verify cannot pay off here regardless of agreement.

Measures real tokens/sec (CUDA-synchronized, warmup excluded), two sequential
loads. Run in the bf16 harness venv.

  diffusion: DiffusionGemmaForBlockDiffusion.generate (block-diffusion sampler)
  AR:        Gemma 4 generate(do_sample=False) — native KV-cached autoregressive

Usage:
  python scripts/probe_speed.py --domains structured code --n-prompts 8
"""

from __future__ import annotations

import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _timed(fn):
    import torch
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    out = fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return out, time.perf_counter() - t0


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--domains", nargs="+", default=["structured", "code"])
    p.add_argument("--drafter-path", default="google/diffusiongemma-26B-A4B-it")
    p.add_argument("--verifier-path", default="google/gemma-4-26B-A4B-it")
    p.add_argument("--n-prompts", type=int, default=8, help="prompts per domain (timed)")
    p.add_argument("--warmup", type=int, default=2, help="leading prompts excluded from stats")
    p.add_argument("--max-new", type=int, default=256)
    args = p.parse_args(argv)

    import torch

    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.metrics import content_length
    from harness.models import load_drafter, load_verifier
    from harness.prompts import load_all

    prompts = load_all("prompts", args.domains, limit=args.n_prompts)
    samples = {"diffusion": [], "ar": []}  # (domain, ntok, secs)

    # ---- diffusion-mode (the drafter) ----
    print("Loading DiffusionGemma (diffusion mode)...", file=sys.stderr)
    dl = load_drafter(ModelConfig(drafter_quant="bf16"))
    dtok = dl.processor.tokenizer
    ddev = next(dl.model.parameters()).device
    for i, pr in enumerate(prompts):
        ids = render_user_prompt(dtok, pr.prompt)
        ii = torch.tensor([ids], dtype=torch.long, device=ddev)
        am = torch.ones_like(ii)
        with torch.no_grad():
            out, secs = _timed(lambda: dl.model.generate(input_ids=ii, attention_mask=am,
                                                          max_new_tokens=args.max_new, do_sample=False))
        seq = out.sequences[0].tolist() if hasattr(out, "sequences") else out[0].tolist()
        cont = seq[len(ids):] if seq[: len(ids)] == list(ids) else seq
        # content tokens only — the canvas is pad-filled after a short answer, and
        # counting padding as "generated" inflates structured throughput ~6x.
        pad_id = dtok.pad_token_id or 0
        ntok = content_length(cont, pad_id)
        if i % args.n_prompts >= args.warmup:  # exclude leading warmups per domain order
            samples["diffusion"].append((pr.domain, ntok, secs))
        print(f"  diff {pr.domain}/{pr.id}: {ntok} tok in {secs:.2f}s = {ntok/secs:.1f} tok/s", file=sys.stderr)
    del dl
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ---- plain AR (Gemma 4) ----
    print("Loading Gemma 4 (AR)...", file=sys.stderr)
    cfg = ModelConfig(verifier_quant="bf16")
    cfg.verifier_model_id = args.verifier_path
    vl = load_verifier(cfg)
    vtok = vl.tokenizer
    vdev = next(vl.model.parameters()).device
    for i, pr in enumerate(prompts):
        enc = vtok.apply_chat_template([{"role": "user", "content": pr.prompt}], add_generation_prompt=True,
                                       tokenize=True, return_dict=True, return_tensors="pt").to(vdev)
        n0 = enc["input_ids"].shape[-1]
        with torch.no_grad():
            out, secs = _timed(lambda: vl.model.generate(**enc, max_new_tokens=args.max_new, do_sample=False))
        ntok = out.shape[-1] - n0
        if i % args.n_prompts >= args.warmup:
            samples["ar"].append((pr.domain, ntok, secs))
        print(f"  ar   {pr.domain}/{pr.id}: {ntok} tok in {secs:.2f}s = {ntok/secs:.1f} tok/s", file=sys.stderr)

    # ---- report tokens/sec ----
    def toks_per_sec(rows, dom=None):
        rs = [(t, s) for d, t, s in rows if dom is None or d == dom]
        tot_t = sum(t for t, _ in rs)
        tot_s = sum(s for _, s in rs)
        return (tot_t / tot_s) if tot_s else 0.0

    print("\n=== realized tokens/sec (bf16, this GPU; warmup excluded) ===")
    print(f"{'domain':<12}{'diffusion':>12}{'AR(gemma4)':>12}{'speedup':>10}")
    for dom in args.domains + [None]:
        d = toks_per_sec(samples["diffusion"], dom)
        a = toks_per_sec(samples["ar"], dom)
        label = dom if dom else "ALL"
        ratio = (d / a) if a else float("nan")
        print(f"{label:<12}{d:>12.1f}{a:>12.1f}{ratio:>9.2f}x")
    print("\nIf diffusion speedup <= ~1x, the drafter has no wall-clock advantage on this")
    print("hardware -> speculative self-verify cannot pay off here, and rung-1 ends as a")
    print("correctness result without a speed win. (fp8 datacenter parts would differ.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
