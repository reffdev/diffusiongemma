#!/usr/bin/env python
"""TEST 4: self-agreement — DiffusionGemma's causal mode scores its OWN drafts.

Re-scores the existing run_final drafts (no new drafting) using DiffusionGemma's
causal encoder+lm_head as the verifier, via the SAME teacher-forcing code
(RealGemmaVerifier). Emits the standard blocks.jsonl schema (speedup n/a) tagged
self_verify, so `compare_runs.py <run_final> <self_verify>` gives p_self next to
run_final's p_gemma4.

Decision: if structured p_self >= ~0.98, single-model self-verify is viable.

Run in the bf16 harness venv.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vllm_agreement import _read_source_drafts  # pure reader (no vllm import)


def assemble_worklist(prompt_ids_by_pid, blocks_by_pid, domain_by_pid):
    """Pure: -> list of (domain, pid, block_index, prefix_ids, draft_ids).

    The verifier scores each block against prompt + the prompt's OWN preceding
    blocks (measurement only), identical to the harness/vLLM flow.
    """
    work = []
    for pid, blocks in blocks_by_pid.items():
        if pid not in prompt_ids_by_pid:
            continue
        prefix = list(prompt_ids_by_pid[pid])
        for bi, block in enumerate(blocks):
            work.append((domain_by_pid[pid], pid, bi, list(prefix), list(block)))
            prefix = prefix + list(block)
    return work


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Self-agreement: causal DiffusionGemma scores its own drafts.")
    p.add_argument("--source", required=True, help="run_final dir whose drafts get re-scored")
    p.add_argument("--drafter-path", default="google/diffusiongemma-26B-A4B-it")
    p.add_argument("--domains", nargs="+", default=["code", "structured", "chat", "prose"])
    p.add_argument("--prompts-dir", default="prompts")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--tag", default="self_verify")
    args = p.parse_args(argv)

    from harness.causal import CausalLMWrapper
    from harness.chat import render_user_prompt
    from harness.config import ModelConfig
    from harness.metrics import build_record
    from harness.models import LoadedModel, load_drafter
    from harness.prompts import load_all
    from harness.results_io import ResultsWriter, write_summary
    from harness.types import DraftBlock
    from harness.verifier import RealGemmaVerifier

    loaded = load_drafter(ModelConfig(drafter_quant="bf16"))
    tok = loaded.processor.tokenizer
    scorer = RealGemmaVerifier(LoadedModel(model=CausalLMWrapper(loaded.model), tokenizer=tok,
                                           model_id=args.drafter_path, quant="bf16"))

    src_blocks, src_domains, _ = _read_source_drafts(args.source)
    prompts = {pr.id: pr for pr in load_all(args.prompts_dir, args.domains)}
    prompt_ids = {pid: render_user_prompt(tok, prompts[pid].prompt)
                  for pid in src_blocks if pid in prompts}
    blocks_by_pid = {pid: src_blocks[pid] for pid in src_blocks if pid in prompts}
    work = assemble_worklist(prompt_ids, blocks_by_pid, src_domains)

    writer = ResultsWriter.create(args.results_dir, args.tag)
    records = []
    for domain, pid, bi, prefix, draft in work:
        vr = scorer.verify_block(prefix, draft)
        rec = build_record(domain, pid, DraftBlock(block_index=bi, draft_ids=draft,
                                                   denoise_steps=None, commit_entropy=None), vr)
        writer.write_block(rec)
        records.append(rec)
    writer.close()
    write_summary(writer.run_dir, records)
    print(f"Wrote {len(records)} block records -> {writer.run_dir}")
    print(f"Now: python scripts/compare_runs.py {args.source} {writer.run_dir}  "
          "(p_cmp column = p_self; watch the structured row vs 0.98)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
