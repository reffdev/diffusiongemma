#!/usr/bin/env python
"""Diagnose why some prompts yield zero committed blocks.

Loads the drafter ONCE and, for every prompt, runs generate() the exact way the
harness does (verifier-tokenizer render + bare input_ids + ones attention mask)
AND the way the working probe did (drafter processor render). Reports the
continuation length from each path so we can see:

  - whether the two render paths produce identical prompt token IDs (they must,
    or the harness is feeding the drafter mis-tokenized prompts), and
  - whether 'empty' generations are render-path-specific or genuine.

Usage:
  python scripts/probe_drafts.py --domains code --limit 12
  python scripts/probe_drafts.py --domains code structured chat prose
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _device(model):
    dev = getattr(model, "device", None)
    return dev if dev is not None else next(model.parameters()).device


def _continuation(out, prompt_ids):
    sequences = getattr(out, "sequences", out)
    if hasattr(sequences, "tolist"):
        sequences = sequences.tolist()
    seq = sequences[0] if sequences and isinstance(sequences[0], list) else sequences
    plist = list(prompt_ids)
    cont = seq[len(plist):] if seq[: len(plist)] == plist else seq
    return seq, cont


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Per-prompt draft-generation diagnostic.")
    p.add_argument("--domains", nargs="+", default=["code"])
    p.add_argument("--limit", type=int, default=12, help="prompts per domain (0 = all)")
    p.add_argument("--max-new-tokens", type=int, default=768)
    args = p.parse_args(argv)

    import torch

    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.models import load_drafter, load_tokenizer
    from harness.prompts import load_domain

    cfg = ModelConfig(drafter_quant="bf16")
    print("Loading drafter (bf16)...", file=sys.stderr)
    loaded = load_drafter(cfg)
    model = loaded.model
    proc = loaded.processor
    device = _device(model)
    vtok = load_tokenizer(cfg.verifier_model_id, cfg.hf_cache_dir)

    n_zero_harness = n_total = 0
    for domain in args.domains:
        prompts = load_domain("prompts", domain, limit=(args.limit or None))
        print(f"\n===== domain: {domain} ({len(prompts)} prompts) =====")
        print(f"{'id':<16} {'v_len':>5} {'d_len':>5} {'same':>4} {'noseed':>6} {'seeded':>6}  first_text")
        for pr in prompts:
            n_total += 1
            v_ids = render_user_prompt(vtok, pr.prompt)
            d_enc = proc.apply_chat_template(
                [{"role": "user", "content": pr.prompt}],
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(device)
            d_ids = d_enc["input_ids"][0].tolist()
            same = "yes" if v_ids == d_ids else "NO"

            ii = torch.tensor([v_ids], dtype=torch.long, device=device)
            am = torch.ones_like(ii)

            # contA: NO seed reset (what this diagnostic did before — it worked).
            with torch.no_grad():
                outA = model.generate(input_ids=ii, attention_mask=am,
                                      max_new_tokens=args.max_new_tokens, do_sample=False)
            _, contA = _continuation(outA, v_ids)

            # contS: WITH torch.manual_seed(0) before generate — exactly what the
            # harness drafter.draft does. If this is empty while contA is not,
            # the per-call global seed reset is the bug.
            torch.manual_seed(0)
            with torch.no_grad():
                outS = model.generate(input_ids=ii, attention_mask=am,
                                      max_new_tokens=args.max_new_tokens, do_sample=False)
            _, contS = _continuation(outS, v_ids)

            if not contS:
                n_zero_harness += 1
            snippet = proc.decode(contA[:40], skip_special_tokens=True).replace("\n", "\\n") if contA else ""
            print(f"{pr.id:<16} {len(v_ids):>5} {len(d_ids):>5} {same:>4} "
                  f"{len(contA):>5} {len(contS):>5}  {snippet[:50]!r}")

    print(f"\nseeded-path empty continuations: {n_zero_harness}/{n_total}")
    print("Interpretation:")
    print("  - 'seeded'=0 while 'noseed'>0  -> torch.manual_seed(0) before each")
    print("    generate is the bug; remove it from harness/drafter.py.")
    print("  - both columns >0 everywhere   -> seed is not the cause; check run1's")
    print("    max_blocks (max_new_tokens = block_size * max_blocks may differ).")
    print("  - same=NO anywhere             -> verifier vs drafter templates diverge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
