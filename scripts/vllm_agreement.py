#!/usr/bin/env python
"""vLLM-backed agreement measurement for the NVFP4 (or bf16) checkpoint pair.

Mirror of the transformers harness, but loads through vLLM (the only stack that
loads these NVFP4/modelopt checkpoints on SM120). Drafter generates committed
blocks; the AR verifier scores each block via prompt_logprobs. Output is the
SAME blocks.jsonl schema as the harness, so compare_runs.py / recompute_summary
work unchanged. No speedup column — vLLM doesn't surface tokens_per_forward, so
denoise_steps is None and speedup reports n/a.

Run this in the SEPARATE vLLM venv. The transformers harness is untouched.

Modes:
  (full)            generate drafts with the drafter, score with the verifier
  --rescore-from R  skip generation; re-score run R's existing drafts with the
                    verifier (used for the cross-stack control against a bf16
                    transformers run)
  --control         with --rescore-from, also report per-position match
                    agreement vs the source run (acceptance gate)

The vLLM-touching functions (vllm_generate_drafts / vllm_score) are isolated;
the parsing (parse_prompt_logprobs, slice_into_blocks) is pure and unit-tested.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.metrics import build_record, content_length, summarize  # noqa: E402
from harness.types import DraftBlock, VerifyResult  # noqa: E402


# ----------------------------- pure helpers --------------------------------

def slice_into_blocks(continuation_ids, block_size, pad_id=0):
    """Trim the trailing <pad> run, then slice into block_size chunks (drop empty)."""
    n = content_length(list(continuation_ids), pad_id)
    cont = list(continuation_ids)[:n]
    return [cont[i : i + block_size] for i in range(0, len(cont), block_size) if cont[i : i + block_size]]


def _argmax_token(dist):
    """dist: {token_id: Logprob-like(.logprob,.rank)} -> token id of rank 0 (argmax)."""
    best_tok, best_lp = None, None
    for tok, lp in dist.items():
        if getattr(lp, "rank", None) == 0:
            return tok
        val = getattr(lp, "logprob", float("-inf"))
        if best_lp is None or val > best_lp:
            best_tok, best_lp = tok, val
    return best_tok


def parse_prompt_logprobs(prompt_logprobs, n_prefix, draft_ids):
    """Extract per-drafted-position verifier argmax + drafted-token logprob.

    prompt_logprobs[i] is the predicted distribution for sequence position i
    (given 0..i-1); element 0 is None. Drafted token j sits at absolute position
    n_prefix + j, so its predicting distribution is prompt_logprobs[n_prefix + j].
    """
    argmax_ids, logprob_of_draft = [], []
    for j, dtok in enumerate(draft_ids):
        dist = prompt_logprobs[n_prefix + j]
        argmax_ids.append(_argmax_token(dist))
        lp = dist.get(dtok)
        logprob_of_draft.append(getattr(lp, "logprob", float("nan")) if lp is not None else float("nan"))
    return VerifyResult(argmax_ids=argmax_ids, logprob_of_draft=logprob_of_draft)


# ----------------------------- vLLM glue -----------------------------------

def vllm_generate_drafts(model_path, prompt_ids_list, canvas_length, max_new_tokens, gpu_mem, max_model_len):
    """Return a list of continuation-token-id lists (generated only, no prompt)."""
    from vllm import LLM, SamplingParams

    llm = LLM(
        model=model_path,
        # Validated by probe_vllm.py before any real run — these mirror the
        # published recipe; adjust there if the probe shows a different surface.
        hf_overrides={
            "diffusion_sampler": "entropy_bound",
            "diffusion_entropy_bound": 0.1,
            "diffusion_config": {"canvas_length": canvas_length},
        },
        gpu_memory_utilization=gpu_mem,
        max_model_len=max_model_len,
    )
    sp = SamplingParams(temperature=0.0, max_tokens=max_new_tokens)
    prompts = [{"prompt_token_ids": list(ids)} for ids in prompt_ids_list]
    outs = llm.generate(prompts, sp)
    return [list(o.outputs[0].token_ids) for o in outs]


def vllm_score(model_path, sequences, n_prefixes, drafts, gpu_mem, max_model_len, top_logprobs=5):
    """Score each (prefix+draft) sequence; return a VerifyResult per item."""
    from vllm import LLM, SamplingParams

    llm = LLM(model=model_path, gpu_memory_utilization=gpu_mem, max_model_len=max_model_len)
    sp = SamplingParams(temperature=0.0, max_tokens=1, prompt_logprobs=top_logprobs)
    prompts = [{"prompt_token_ids": list(seq)} for seq in sequences]
    outs = llm.generate(prompts, sp)
    results = []
    for o, n_prefix, draft in zip(outs, n_prefixes, drafts):
        results.append(parse_prompt_logprobs(o.prompt_logprobs, n_prefix, draft))
    return results


# ----------------------------- orchestration --------------------------------

def _read_source_drafts(run_dir):
    """From a run's blocks.jsonl: {pid: [draft_ids,...]}, {pid: domain}, {(pid,bi): match}."""
    drafts, domains, src_match = {}, {}, {}
    rows = []
    for line in open(os.path.join(run_dir, "blocks.jsonl"), encoding="utf-8"):
        if line.strip():
            rows.append(json.loads(line))
    rows.sort(key=lambda r: (r["domain"], r["prompt_id"], r["block_index"]))
    for r in rows:
        pid = r["prompt_id"]
        drafts.setdefault(pid, []).append(r["draft_ids"])
        domains[pid] = r["domain"]
        src_match[(pid, r["block_index"])] = r["match"]
    return drafts, domains, src_match


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="vLLM-backed agreement run (NVFP4 or bf16).")
    p.add_argument("--drafter-path", required=True)
    p.add_argument("--verifier-path", required=True)
    p.add_argument("--domains", nargs="+", default=["code", "structured", "chat", "prose"])
    p.add_argument("--prompts-dir", default="prompts")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--tag", default="vllm")
    p.add_argument("--max-prompts", type=int, default=None)
    p.add_argument("--max-blocks", type=int, default=8)
    p.add_argument("--block-size", type=int, default=256, help="canvas length")
    p.add_argument("--quant-label", default="nvfp4", help="recorded in config.json")
    p.add_argument("--rescore-from", default=None, help="re-score this run's drafts (control)")
    p.add_argument("--control", action="store_true", help="report match agreement vs --rescore-from")
    p.add_argument("--gpu-mem", type=float, default=0.85)
    p.add_argument("--max-model-len", type=int, default=8192)
    args = p.parse_args(argv)

    from transformers import AutoTokenizer

    from harness.chat import render_user_prompt
    from harness.prompts import load_all
    from harness.results_io import ResultsWriter, write_summary
    from harness.tokenizer_check import check_tokenizers

    vtok = AutoTokenizer.from_pretrained(args.verifier_path)
    dtok = AutoTokenizer.from_pretrained(args.drafter_path)
    print("Verifying tokenizer identity...", file=sys.stderr)
    check_tokenizers(dtok, vtok)

    prompts = load_all(args.prompts_dir, args.domains, limit=args.max_prompts)
    rendered = {pr.id: (pr, render_user_prompt(vtok, pr.prompt)) for pr in prompts}

    # ---- drafts: generate, or read from a source run (control) ----
    if args.rescore_from:
        src_drafts, _, src_match = _read_source_drafts(args.rescore_from)
        prompt_blocks = {pid: src_drafts[pid] for pid in src_drafts if pid in rendered}
    else:
        src_match = {}
        order = [pid for pid in rendered]
        conts = vllm_generate_drafts(
            args.drafter_path,
            [rendered[pid][1] for pid in order],
            args.block_size, args.block_size * args.max_blocks, args.gpu_mem, args.max_model_len,
        )
        pad_id = vtok.pad_token_id or 0
        prompt_blocks = {}
        for pid, cont in zip(order, conts):
            prompt_blocks[pid] = slice_into_blocks(cont, args.block_size, pad_id)[: args.max_blocks]

    # ---- build the verifier scoring work-list (one sequence per block) ----
    seqs, n_prefixes, drafts, meta = [], [], [], []
    for pid, blocks in prompt_blocks.items():
        pr, prompt_ids = rendered[pid]
        prefix = list(prompt_ids)
        for bi, block in enumerate(blocks):
            seqs.append(prefix + list(block))
            n_prefixes.append(len(prefix))
            drafts.append(list(block))
            meta.append((pr.domain, pid, bi))
            prefix = prefix + list(block)

    print(f"Scoring {len(seqs)} blocks with the verifier...", file=sys.stderr)
    verifies = vllm_score(args.verifier_path, seqs, n_prefixes, drafts, args.gpu_mem, args.max_model_len)

    # ---- write records (same schema; denoise_steps=None -> speedup n/a) ----
    writer = ResultsWriter.create(args.results_dir, args.tag)
    runtime = {"quant_label": args.quant_label, "drafter_path": args.drafter_path,
               "verifier_path": args.verifier_path, "block_size": args.block_size,
               "mode": "rescore" if args.rescore_from else "full"}
    try:
        import vllm  # type: ignore
        runtime["vllm_version"] = vllm.__version__
    except Exception:  # noqa: BLE001
        pass
    try:
        import transformers  # type: ignore
        runtime["transformers_version"] = transformers.__version__
    except Exception:  # noqa: BLE001
        pass
    with open(os.path.join(writer.run_dir, "config.json"), "w", encoding="utf-8") as fh:
        json.dump({"tag": args.tag, "domains": args.domains, "max_blocks_per_prompt": args.max_blocks,
                   "max_prompts_per_domain": args.max_prompts, "_runtime": runtime}, fh, indent=2, sort_keys=True)

    records = []
    for (domain, pid, bi), draft, verify in zip(meta, drafts, verifies):
        block = DraftBlock(block_index=bi, draft_ids=draft, denoise_steps=None, commit_entropy=None)
        rec = build_record(domain, pid, block, verify)
        writer.write_block(rec)
        records.append(rec)
    writer.close()
    summary_path = write_summary(writer.run_dir, records)
    print(f"Wrote {len(records)} block records.\n  blocks : {writer.run_dir}/blocks.jsonl\n  summary: {summary_path}")

    # ---- control: per-position match agreement vs the source run ----
    if args.control and src_match:
        same = total = 0
        for (domain, pid, bi), rec in zip(meta, records):
            ref = src_match.get((pid, bi))
            if ref is None:
                continue
            for a, b in zip(rec.match, ref):
                total += 1
                same += int(a == b)
        agree = same / total if total else float("nan")
        print(f"\n=== CROSS-STACK CONTROL ===\nper-position match agreement vs {args.rescore_from}: "
              f"{agree:.4f} ({same}/{total})\nacceptance >= 0.99: {'PASS' if agree >= 0.99 else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
