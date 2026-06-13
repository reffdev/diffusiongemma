#!/usr/bin/env python
"""TEST 3: 3-way side-by-side quality artifact for a manual read.

For ~20 prompts (10 structured, 10 code), produce a Markdown table comparing:
  (causal)    DiffusionGemma driven causally (encoder+lm_head greedy)
  (diffusion) DiffusionGemma's diffusion-mode draft from run_final (decoded)
  (gemma4)    Gemma 4 bf16 greedy completion

Loads two models sequentially (DiffusionGemma, then Gemma 4). Slow is fine.
Run in the bf16 harness venv. Output: results/<tag>/sidebyside.md

Usage:
  python scripts/causal_quality_compare.py --source results/<run_final>
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vllm_agreement import _read_source_drafts

# Stop on true <eos> only. <end_of_turn> (107) is emitted prematurely by the
# causal encoder in *unanchored* free generation (it terminates after a markdown
# fence), so stopping on it truncates the quality read. Let generation run so we
# can actually see causal-mode output quality.
STOP_TOKENS = (1,)  # <eos>


def build_sidebyside_md(rows):
    """Pure: rows = [{id, prompt, causal, diffusion, gemma4}] -> markdown string."""
    out = ["# Causal vs diffusion vs Gemma 4 — manual quality read\n"]
    for r in rows:
        out.append(f"## {r['id']}\n")
        out.append(f"**prompt:** {r['prompt']}\n")
        for label in ("causal", "diffusion", "gemma4"):
            out.append(f"**{label}:**\n\n```\n{r[label].strip()}\n```\n")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="run_final dir (for diffusion-mode drafts)")
    p.add_argument("--drafter-path", default="google/diffusiongemma-26B-A4B-it")
    p.add_argument("--verifier-path", default="google/gemma-4-26B-A4B-it")
    p.add_argument("--per-domain", type=int, default=10)
    p.add_argument("--max-new", type=int, default=128)
    p.add_argument("--results-dir", default="results")
    p.add_argument("--tag", default="causal_quality")
    args = p.parse_args(argv)

    import torch

    from harness.causal import CausalLMWrapper
    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.models import load_drafter, load_verifier
    from harness.prompts import load_domain
    from harness.results_io import ResultsWriter

    prompts = (load_domain("prompts", "structured", limit=args.per_domain)
               + load_domain("prompts", "code", limit=args.per_domain))
    src_blocks, _, _ = _read_source_drafts(args.source)

    # ---- pass 1: DiffusionGemma (causal gen) + decode diffusion-mode drafts ----
    loaded = load_drafter(ModelConfig(drafter_quant="bf16"))
    tok = loaded.processor.tokenizer
    wrapper = CausalLMWrapper(loaded.model)
    device = next(loaded.model.parameters()).device

    def causal_gen(ids):
        cur = list(ids)
        for _ in range(args.max_new):
            with torch.no_grad():
                logits = wrapper(input_ids=torch.tensor([cur], dtype=torch.long, device=device)).logits
            nxt = int(logits[0, -1].argmax().item())
            cur.append(nxt)
            if nxt in STOP_TOKENS:
                break
        return tok.decode(cur[len(ids):], skip_special_tokens=True)

    rows = []
    for pr in prompts:
        ids = render_user_prompt(tok, pr.prompt)
        diffusion = tok.decode(sum(src_blocks.get(pr.id, []), []), skip_special_tokens=True) if pr.id in src_blocks else "(not in source run)"
        rows.append({"id": pr.id, "prompt": pr.prompt, "causal": causal_gen(ids),
                     "diffusion": diffusion, "gemma4": ""})
        print(f"  causal done: {pr.id}", file=sys.stderr)

    del wrapper, loaded
    import gc
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ---- pass 2: Gemma 4 greedy ----
    cfg = ModelConfig(verifier_quant="bf16")
    cfg.verifier_model_id = args.verifier_path
    vloaded = load_verifier(cfg)
    vtok = vloaded.tokenizer
    for r in rows:
        ids = vtok.apply_chat_template([{"role": "user", "content": r["prompt"]}],
                                       add_generation_prompt=True, tokenize=True, return_dict=True,
                                       return_tensors="pt").to(next(vloaded.model.parameters()).device)
        with torch.no_grad():
            out = vloaded.model.generate(**ids, max_new_tokens=args.max_new, do_sample=False)
        r["gemma4"] = vtok.decode(out[0][ids["input_ids"].shape[-1]:], skip_special_tokens=True)
        print(f"  gemma4 done: {r['id']}", file=sys.stderr)

    writer = ResultsWriter.create(args.results_dir, args.tag)
    path = os.path.join(writer.run_dir, "sidebyside.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(build_sidebyside_md(rows))
    writer.close()
    print(f"Wrote side-by-side artifact -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
