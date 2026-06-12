#!/usr/bin/env python
"""Sanity-check the real models before trusting any agreement numbers.

Loads the verifier and/or drafter *exactly as the harness does* (same loaders,
same quantization), decodes a short greedy completion from each, reports VRAM
use, and runs the tokenizer-identity gate. Phase 1 is measurement-only, so a
broken load is worse than a crash — it produces plausible-looking but wrong
agreement numbers.

Read the output:
  - Coherent completions  -> the chosen quantization is fine; go run the harness.
  - Gibberish/empty       -> the quant path is broken (e.g. fp8 on this stack).
                             Re-run with --verifier-quant int8 --drafter-quant int8
                             (bitsandbytes) and note the perf cost.
  - Tokenizer mismatch    -> STOP. Agreement across mismatched tokenizers is
                             meaningless; the harness would refuse the run too.

Usage (from the project root, inside the venv):
  python scripts/sanity_check.py                       # both models, fp8
  python scripts/sanity_check.py --only verifier
  python scripts/sanity_check.py --verifier-quant int8 --drafter-quant int8
"""

from __future__ import annotations

import argparse
import os
import sys

# Make `harness` importable no matter the cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_PROMPT = "Name three primary colors, then count from one to five."


def _device(model):
    dev = getattr(model, "device", None)
    if dev is not None:
        return dev
    return next(model.parameters()).device


def _vram() -> str:
    import torch

    if not torch.cuda.is_available():
        return "no CUDA visible"
    alloc = torch.cuda.memory_allocated() / 1e9
    reserved = torch.cuda.memory_reserved() / 1e9
    return f"VRAM: {alloc:.1f} GB allocated / {reserved:.1f} GB reserved"


def check_verifier(cfg, prompt: str, max_new: int):
    import torch

    from harness.models import load_verifier

    print("\n=== Loading VERIFIER (Gemma 4) ===", file=sys.stderr)
    loaded = load_verifier(cfg)
    tok = loaded.tokenizer
    enc = tok.apply_chat_template(
        [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(_device(loaded.model))
    n_prompt = enc["input_ids"].shape[-1]
    with torch.no_grad():
        out = loaded.model.generate(**enc, max_new_tokens=max_new, do_sample=False)
    text = tok.decode(out[0][n_prompt:], skip_special_tokens=True)
    print(f"\n[VERIFIER {cfg.verifier_model_id} | quant={cfg.verifier_quant}] {_vram()}")
    print(f"PROMPT : {prompt}")
    print(f"OUTPUT : {text.strip()!r}")
    return loaded


def check_drafter(cfg, prompt: str, max_new: int):
    import torch

    from harness.models import load_drafter

    print("\n=== Loading DRAFTER (DiffusionGemma) ===", file=sys.stderr)
    loaded = load_drafter(cfg)
    proc = loaded.processor
    enc = proc.apply_chat_template(
        [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(_device(loaded.model))
    n_prompt = enc["input_ids"].shape[-1]
    print(f"\n[DRAFTER {cfg.drafter_model_id} | quant={cfg.drafter_quant}] {_vram()}")
    print(f"PROMPT : {prompt}")
    print(f"prompt_len = {n_prompt} tokens\n")

    # Probe generate() under several configs: the model card example passes NO
    # sampling args; our harness was passing do_sample=False (greedy AR), which
    # may be invalid for a diffusion sampler. Print what each returns so we can
    # see whether tokens come out and whether output includes the prompt prefix.
    configs = [
        ("model-card default (no args)", {}),
        ("do_sample=False (what harness did)", {"do_sample": False}),
        ("do_sample=True", {"do_sample": True}),
    ]
    for label, kwargs in configs:
        try:
            with torch.no_grad():
                out = loaded.model.generate(**enc, max_new_tokens=max_new, **kwargs)
            # out is a DiffusionGemmaGenerationOutput (ModelOutput), not a tensor.
            sequences = getattr(out, "sequences", out)
            if hasattr(sequences, "tolist"):
                sequences = sequences.tolist()
            seq = sequences[0] if sequences and isinstance(sequences[0], list) else sequences
            plist = enc["input_ids"][0].tolist()
            cont = seq[len(plist):] if seq[: len(plist)] == plist else seq
            cont_text = proc.decode(cont, skip_special_tokens=True) if cont else ""
            full_text = proc.decode(seq, skip_special_tokens=True)
            print(f"--- {label} ---")
            print(f"    returned_len={len(seq)}  continuation_len={len(cont)}  "
                  f"(>{n_prompt} prompt => {'includes prompt' if len(seq) > n_prompt else 'NO new tokens / continuation-only'})")
            print(f"    continuation[:160] = {cont_text[:160]!r}")
            if not cont:
                print(f"    full[:160]         = {full_text[:160]!r}  (sliced-off; output may be continuation-only)")
            print()
        except Exception as exc:  # noqa: BLE001
            print(f"--- {label} ---\n    RAISED: {type(exc).__name__}: {exc}\n")
    print("Interpretation:")
    print("  - If 'model-card default' yields tokens but 'do_sample=False' does not,")
    print("    the harness must stop forcing greedy on the diffusion drafter.")
    print("  - If returned_len <= prompt_len everywhere, generate() returns")
    print("    continuation-only and drafter.py must NOT strip the prompt prefix.")
    return loaded


def run_tokenizer_gate(drafter_loaded, verifier_loaded):
    from harness.tokenizer_check import TokenizerMismatch, check_tokenizers

    print("\n=== Tokenizer-identity gate ===")
    try:
        res = check_tokenizers(drafter_loaded.tokenizer, verifier_loaded.tokenizer)
        print(
            f"OK: tokenizers identical (vocab size {res.vocab_size_drafter}). "
            "Agreement measurement is well-defined."
        )
    except TokenizerMismatch as exc:
        print("MISMATCH — the harness would refuse this run:\n")
        print(str(exc))
        return False
    return True


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Pre-run sanity check for the agreement harness.")
    p.add_argument("--only", choices=["verifier", "drafter", "both"], default="both")
    p.add_argument("--prompt", default=DEFAULT_PROMPT)
    p.add_argument("--max-new-tokens", type=int, default=48)
    p.add_argument("--verifier-quant", default="bf16", choices=["fp8", "int8", "bf16"])
    p.add_argument("--drafter-quant", default="bf16", choices=["fp8", "int8", "bf16"])
    p.add_argument("--no-tokenizer-check", action="store_true")
    args = p.parse_args(argv)

    from harness.config import ModelConfig

    cfg = ModelConfig(verifier_quant=args.verifier_quant, drafter_quant=args.drafter_quant)

    verifier_loaded = drafter_loaded = None
    if args.only in ("verifier", "both"):
        verifier_loaded = check_verifier(cfg, args.prompt, args.max_new_tokens)
    if args.only in ("drafter", "both"):
        drafter_loaded = check_drafter(cfg, args.prompt, args.max_new_tokens)

    ok = True
    if not args.no_tokenizer_check and verifier_loaded and drafter_loaded:
        ok = run_tokenizer_gate(drafter_loaded, verifier_loaded)

    print("\n" + ("All checks passed — safe to run the harness." if ok else "Check FAILED — see above."))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
