"""Orchestration entry point for the Phase 1 agreement harness.

Flow:
  1. Load prompt sets for the requested domains.
  2. (real mode) Load drafter + verifier; assert tokenizer identity; render
     each prompt once through the shared chat template.
  3. For each prompt, iteratively draft committed blocks; teacher-force each
     block through the verifier; build a BlockRecord; write JSONL.
  4. Write summary.md.

Run `--mock` to exercise the whole pipeline with synthetic models (no GPU /
no transformers needed) — start tiny, with assertions, before scaling up.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import prompts as prompts_mod
from .config import DOMAINS, RunConfig
from .metrics import build_record
from .results_io import ResultsWriter, write_summary
from .types import BlockRecord


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agreement-harness",
        description="Phase 1: measure DiffusionGemma↔Gemma 4 per-token agreement.",
    )
    p.add_argument("--domains", nargs="+", default=list(DOMAINS), choices=list(DOMAINS))
    p.add_argument("--prompts-dir", default="prompts")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--tag", default="dev")
    p.add_argument("--max-prompts", type=int, default=None, help="cap prompts per domain")
    p.add_argument("--max-blocks", type=int, default=8, help="cap blocks per prompt")
    p.add_argument(
        "--block-size",
        type=int,
        default=None,
        help="native diffusion canvas length (sets config.canvas_length); default 256",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--mock", action="store_true", help="use synthetic models (no GPU)")
    p.add_argument(
        "--capture-internals",
        action="store_true",
        help="instrument the denoise loop for per-block steps + entropy (requires source hook)",
    )
    p.add_argument("--drafter-quant", default="bf16", choices=["fp8", "int8", "bf16"])
    p.add_argument("--verifier-quant", default="bf16", choices=["fp8", "int8", "bf16"])
    p.add_argument(
        "--no-sequential",
        dest="sequential",
        action="store_false",
        help="load both models at once instead of two passes (needs both to fit in VRAM)",
    )
    p.set_defaults(sequential=True)
    p.add_argument("--mock-agree-rate", type=float, default=0.8, help="mock verifier agreement")
    return p


def _free_vram() -> None:
    """Release CUDA memory after the caller has dropped its model references."""
    import gc

    gc.collect()
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:  # noqa: BLE001
        pass


def _verify_blocks(verifier, prompt_ids, blocks, domain, prompt_id, writer, records):
    """Teacher-force each committed block against the prompt + the drafter's OWN
    preceding blocks (measurement only — no verifier correction in Phase 1)."""
    prefix = list(prompt_ids)
    for block in blocks:
        vr = verifier.verify_block(prefix, block.draft_ids)
        rec = build_record(domain, prompt_id, block, vr)
        writer.write_block(rec)
        records.append(rec)
        prefix = prefix + block.draft_ids


def _run_mock(cfg, prompts, writer, mock_agree_rate) -> list[BlockRecord]:
    from .drafter import MockDrafter
    from .verifier import MockVerifier

    drafter = MockDrafter(cfg.sampler, seed=cfg.seed)
    verifier = MockVerifier(agree_rate=mock_agree_rate, seed=cfg.seed)
    records: list[BlockRecord] = []
    for pr in prompts:
        prompt_ids = [ord(c) % 256 for c in pr.prompt[:32]] or [1]
        blocks = drafter.draft(prompt_ids, cfg.max_blocks_per_prompt)
        _verify_blocks(verifier, prompt_ids, blocks, pr.domain, pr.id, writer, records)
    return records


def _run_coresident(cfg, prompts, writer) -> list[BlockRecord]:
    """Load both models at once and stream prompt-by-prompt (needs both to fit)."""
    from .chat import render_user_prompt
    from .drafter import RealDiffusionGemmaDrafter
    from .models import load_drafter, load_verifier
    from .tokenizer_check import check_tokenizers
    from .verifier import RealGemmaVerifier

    print("Loading verifier (Gemma 4)...", file=sys.stderr)
    verifier_loaded = load_verifier(cfg.models)
    print("Loading drafter (DiffusionGemma)...", file=sys.stderr)
    drafter_loaded = load_drafter(cfg.models)
    print("Verifying tokenizer identity...", file=sys.stderr)
    check_tokenizers(drafter_loaded.tokenizer, verifier_loaded.tokenizer)

    drafter = RealDiffusionGemmaDrafter(
        drafter_loaded, cfg.sampler, seed=cfg.seed, capture_internals=cfg.capture_internals
    )
    verifier = RealGemmaVerifier(verifier_loaded)
    tok = verifier_loaded.tokenizer

    records: list[BlockRecord] = []
    for pr in prompts:
        prompt_ids = render_user_prompt(tok, pr.prompt)
        blocks = drafter.draft(prompt_ids, cfg.max_blocks_per_prompt)
        _verify_blocks(verifier, prompt_ids, blocks, pr.domain, pr.id, writer, records)
    return records


def _run_sequential(cfg, prompts, writer) -> list[BlockRecord]:
    """Two passes: drafter alone -> drafts in RAM -> free -> verifier alone.

    Peak VRAM is a single model, so two 26B models never co-reside. Draft token
    IDs are tiny, so all drafts are held in CPU RAM between passes.
    """
    from .chat import render_user_prompt
    from .drafter import RealDiffusionGemmaDrafter
    from .models import load_drafter, load_tokenizer, load_verifier
    from .tokenizer_check import check_tokenizers
    from .verifier import RealGemmaVerifier

    # Tokenizer-identity gate up front using tokenizers only (cheap — no weights).
    from transformers import AutoProcessor

    drafter_processor = AutoProcessor.from_pretrained(
        cfg.models.drafter_model_id, cache_dir=cfg.models.hf_cache_dir
    )
    verifier_tok = load_tokenizer(cfg.models.verifier_model_id, cfg.models.hf_cache_dir)
    print("Verifying tokenizer identity...", file=sys.stderr)
    check_tokenizers(drafter_processor.tokenizer, verifier_tok)
    rendered = [(pr, render_user_prompt(verifier_tok, pr.prompt)) for pr in prompts]

    # ---- Pass 1: drafter alone -------------------------------------------
    print("Pass 1/2: loading drafter (DiffusionGemma), generating drafts...", file=sys.stderr)
    drafter_loaded = load_drafter(cfg.models)
    drafter = RealDiffusionGemmaDrafter(
        drafter_loaded, cfg.sampler, seed=cfg.seed, capture_internals=cfg.capture_internals
    )
    # Fail-loud instrumentation: log per-prompt draft diagnostics as JSONL and
    # RAISE on the first empty generation with the full dump, so we capture the
    # exact state at the failure instead of silently dropping the prompt.
    diag_path = os.path.join(writer.run_dir, "pass1_diag.jsonl")
    drafts = []  # (prompt, prompt_ids, blocks)
    with open(diag_path, "w", encoding="utf-8") as diag_fh:
        for pr, prompt_ids in rendered:
            blocks = drafter.draft(prompt_ids, cfg.max_blocks_per_prompt)
            diag = dict(drafter.last_diagnostics)
            diag["prompt_id"] = pr.id
            diag["domain"] = pr.domain
            diag["n_blocks"] = len(blocks)
            diag_fh.write(json.dumps(diag) + "\n")
            diag_fh.flush()
            if not blocks:
                print("\n=== FIRST EMPTY-GENERATION FAILURE (Pass 1) ===", file=sys.stderr)
                print(json.dumps(diag, indent=2), file=sys.stderr)
                raise RuntimeError(
                    f"empty generation for {pr.domain}/{pr.id}: drafter returned "
                    f"{diag['returned_len']} tokens for a {diag['input_token_count']}-token "
                    f"prompt (continuation_len={diag['continuation_len']}). Full dump above; "
                    f"per-prompt log at {diag_path}."
                )
            drafts.append((pr, prompt_ids, blocks))
            print(f"  drafted {pr.domain}/{pr.id}: {len(blocks)} block(s)", file=sys.stderr)
    # Drop references in THIS scope so the drafter's VRAM is actually released
    # before the verifier loads (passing them to a helper would not free them).
    del drafter, drafter_loaded
    _free_vram()

    # ---- Pass 2: verifier alone ------------------------------------------
    print("Pass 2/2: loading verifier (Gemma 4), teacher-forcing drafts...", file=sys.stderr)
    verifier_loaded = load_verifier(cfg.models)
    verifier = RealGemmaVerifier(verifier_loaded)
    records: list[BlockRecord] = []
    for pr, prompt_ids, blocks in drafts:
        _verify_blocks(verifier, prompt_ids, blocks, pr.domain, pr.id, writer, records)
    return records


def run(cfg: RunConfig, mock_agree_rate: float = 0.8) -> str:
    """Execute a full run. Returns the run directory path."""
    all_prompts = prompts_mod.load_all(cfg.prompts_dir, cfg.domains, limit=cfg.max_prompts_per_domain)
    if not all_prompts:
        raise SystemExit("no prompts loaded — check --prompts-dir and --domains")

    runtime = {"mock": cfg.mock, "sequential": cfg.sequential}
    try:
        import torch  # type: ignore

        runtime["torch_version"] = torch.__version__
    except Exception:  # noqa: BLE001
        pass
    try:
        import transformers  # type: ignore

        runtime["transformers_version"] = transformers.__version__
    except Exception:  # noqa: BLE001
        pass

    writer = ResultsWriter.create(cfg.results_dir, cfg.tag)
    writer.write_config(cfg, extra=runtime)
    try:
        if cfg.mock:
            records = _run_mock(cfg, all_prompts, writer, mock_agree_rate)
        elif cfg.sequential:
            records = _run_sequential(cfg, all_prompts, writer)
        else:
            records = _run_coresident(cfg, all_prompts, writer)
    finally:
        writer.close()

    summary_path = write_summary(writer.run_dir, records)
    print(f"Wrote {len(records)} block records.")
    print(f"  blocks : {writer.run_dir}/blocks.jsonl")
    print(f"  config : {writer.run_dir}/config.json")
    print(f"  summary: {summary_path}")
    return writer.run_dir


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    cfg = RunConfig(
        domains=tuple(args.domains),
        prompts_dir=args.prompts_dir,
        results_dir=args.results_dir,
        tag=args.tag,
        max_prompts_per_domain=args.max_prompts,
        max_blocks_per_prompt=args.max_blocks,
        seed=args.seed,
        mock=args.mock,
        capture_internals=args.capture_internals,
        sequential=args.sequential,
    )
    cfg.models.drafter_quant = args.drafter_quant
    cfg.models.verifier_quant = args.verifier_quant
    if args.block_size is not None:
        cfg.sampler.block_size = args.block_size
    run(cfg, mock_agree_rate=args.mock_agree_rate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
