#!/usr/bin/env python
"""Scaled Test 3 — generation pass. Causal DiffusionGemma + Gemma 4, all prompts.

Two sequential model loads (bf16 harness venv). Greedy both. Saves raw
generations.jsonl (retained per-model artifact) consumed by causal_quality_eval.py.

Stop condition (see results/causal_quality_eval_preregistration.md):
  causal: greedy, stop on <eos>=1 or --max-new; 107 (<end_of_turn>) is NOT a stop
          (it's emitted spuriously mid-stream); decode skips special tokens.
  gemma4: stock generate(do_sample=False) with its native stopping.
Causal generation is naive full-recompute (the probe-validated path) — SLOW by
design; correctness over speed for an eval.

Usage:
  python scripts/causal_quality_gen.py --domains code structured chat prose --tag causal_eval_gen
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EOS_ID = 1          # <eos>
MIN_STOP = 16
# Stop on <eos> only. The causal encoder has NO reliable stop signal: 107
# (<end_of_turn>) is emitted as mid-answer noise (stopping on it truncates the
# answer to ~16-45 tokens), and <eos> is essentially never produced — so causal
# generation runs to the cap. This is a real finding (broken standalone
# termination), reported by the eval; we still capture the (good) content + the
# cap-hit so quality can be read from the extractable answer.
STOP_IDS = (EOS_ID,)


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--domains", nargs="+", default=["code", "structured", "chat", "prose"])
    p.add_argument("--drafter-path", default="google/diffusiongemma-26B-A4B-it")
    p.add_argument("--verifier-path", default="google/gemma-4-26B-A4B-it")
    p.add_argument("--max-new", type=int, default=512)
    p.add_argument("--max-prompts", type=int, default=None)
    p.add_argument("--results-dir", default="results")
    p.add_argument("--tag", default="causal_eval_gen")
    args = p.parse_args(argv)

    import torch

    from harness.causal import CausalLMWrapper
    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.models import load_drafter, load_verifier
    from harness.prompts import load_all
    from harness.results_io import ResultsWriter

    prompts = load_all("prompts", args.domains, limit=args.max_prompts)
    gens = {pr.id: {"domain": pr.domain, "id": pr.id, "prompt": pr.prompt} for pr in prompts}

    # ---- pass 1: causal DiffusionGemma ----
    print("Pass 1/2: causal DiffusionGemma (slow, full-recompute)...", file=sys.stderr)
    loaded = load_drafter(ModelConfig(drafter_quant="bf16"))
    tok = loaded.processor.tokenizer
    wrapper = CausalLMWrapper(loaded.model)
    device = next(loaded.model.parameters()).device
    for pr in prompts:
        ids = list(render_user_prompt(tok, pr.prompt))
        n0 = len(ids)
        stopped = False
        for step in range(args.max_new):
            with torch.no_grad():
                logits = wrapper(input_ids=torch.tensor([ids], dtype=torch.long, device=device)).logits
            nxt = int(logits[0, -1].argmax().item())
            ids.append(nxt)
            if nxt in STOP_IDS and (step + 1) >= MIN_STOP:
                stopped = True
                break
        gen = ids[n0:]
        gens[pr.id]["causal"] = tok.decode(gen, skip_special_tokens=True)
        gens[pr.id]["causal_ntok"] = len(gen)
        gens[pr.id]["causal_truncated"] = not stopped
        print(f"  causal {pr.domain}/{pr.id}: {len(gen)} tok", file=sys.stderr)
    del wrapper, loaded
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ---- pass 2: Gemma 4 ----
    print("Pass 2/2: Gemma 4 bf16...", file=sys.stderr)
    cfg = ModelConfig(verifier_quant="bf16")
    cfg.verifier_model_id = args.verifier_path
    vloaded = load_verifier(cfg)
    vtok = vloaded.tokenizer
    vdev = next(vloaded.model.parameters()).device
    for pr in prompts:
        enc = vtok.apply_chat_template([{"role": "user", "content": pr.prompt}],
                                       add_generation_prompt=True, tokenize=True,
                                       return_dict=True, return_tensors="pt").to(vdev)
        n0 = enc["input_ids"].shape[-1]
        with torch.no_grad():
            out = vloaded.model.generate(**enc, max_new_tokens=args.max_new, do_sample=False)
        gen = out[0][n0:].tolist()
        gens[pr.id]["gemma4"] = vtok.decode(gen, skip_special_tokens=True)
        gens[pr.id]["gemma4_ntok"] = len(gen)
        gens[pr.id]["gemma4_truncated"] = len(gen) >= args.max_new
        print(f"  gemma4 {pr.domain}/{pr.id}: {len(gen)} tok", file=sys.stderr)

    writer = ResultsWriter.create(args.results_dir, args.tag)
    with open(os.path.join(writer.run_dir, "generations.jsonl"), "w", encoding="utf-8") as fh:
        for pr in prompts:
            fh.write(json.dumps(gens[pr.id], ensure_ascii=False) + "\n")
    with open(os.path.join(writer.run_dir, "config.json"), "w", encoding="utf-8") as fh:
        json.dump({"domains": args.domains, "max_new": args.max_new, "eos_id": EOS_ID,
                   "stop": "causal: eos=1 or max_new (107 excluded); gemma4: native generate",
                   "drafter_path": args.drafter_path, "verifier_path": args.verifier_path}, fh, indent=2)
    writer.close()
    print(f"\nWrote {len(prompts)} generation pairs -> {writer.run_dir}/generations.jsonl")
    print(f"Next: python scripts/causal_quality_eval.py --gen {writer.run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
