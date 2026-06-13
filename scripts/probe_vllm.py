#!/usr/bin/env python
"""GATE: confirm vLLM exposes what the adapter needs, before any real run.

Run in the vLLM venv. Two checks:
  1. DRAFTER: does DiffusionGemma generation expose committed token IDs cleanly
     (RequestOutput.outputs[0].token_ids, nonempty, decodable)?
  2. VERIFIER: does prompt_logprobs come back per-position for the AR Gemma 4?

If check 1 fails (no/empty token_ids), STOP — the adapter's block capture can't
work and we need a different approach. If check 2 fails, the scoring path is wrong.

Usage:
  python scripts/probe_vllm.py --drafter-path <D> --verifier-path <V>
"""

from __future__ import annotations

import argparse
import sys


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--drafter-path", required=True)
    p.add_argument("--verifier-path", required=True)
    p.add_argument("--gpu-mem", type=float, default=0.85)
    p.add_argument("--max-model-len", type=int, default=8192)
    args = p.parse_args(argv)

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    tok = AutoTokenizer.from_pretrained(args.verifier_path)
    prompt_ids = tok.apply_chat_template(
        [{"role": "user", "content": "Name three primary colors, then count to five."}],
        add_generation_prompt=True, tokenize=True,
    )

    print("\n=== CHECK 1: drafter generation exposes committed token IDs ===", file=sys.stderr)
    drafter = LLM(
        model=args.drafter_path,
        hf_overrides={"diffusion_sampler": "entropy_bound", "diffusion_entropy_bound": 0.1,
                      "diffusion_config": {"canvas_length": 256}},
        gpu_memory_utilization=args.gpu_mem, max_model_len=args.max_model_len,
    )
    out = drafter.generate([{"prompt_token_ids": prompt_ids}], SamplingParams(temperature=0.0, max_tokens=256))
    co = out[0].outputs[0]
    tids = list(getattr(co, "token_ids", []) or [])
    print(f"token_ids present: {bool(tids)} | count: {len(tids)}")
    print(f"first 16 ids: {tids[:16]}")
    print(f"decoded[:160]: {tok.decode(tids, skip_special_tokens=True)[:160]!r}")
    print("CHECK 1:", "PASS" if tids else "FAIL — no committed token IDs; STOP and reconsider")

    print("\n=== CHECK 2: verifier prompt_logprobs ===", file=sys.stderr)
    del drafter  # free the GPU before loading the verifier
    verifier = LLM(model=args.verifier_path, gpu_memory_utilization=args.gpu_mem, max_model_len=args.max_model_len)
    seq = list(prompt_ids) + tids[:8]
    vout = verifier.generate([{"prompt_token_ids": seq}],
                             SamplingParams(temperature=0.0, max_tokens=1, prompt_logprobs=5))
    plp = vout[0].prompt_logprobs
    ok = plp is not None and len(plp) == len(seq)
    print(f"prompt_logprobs present: {plp is not None} | length == seq ({len(seq)}): {ok}")
    if ok:
        i = len(prompt_ids)  # first drafted position
        entry = plp[i]
        print(f"sample entry at first drafted pos {i}: {[(t, round(lp.logprob, 2), lp.rank) for t, lp in list(entry.items())[:3]]}")
    print("CHECK 2:", "PASS" if ok else "FAIL — scoring path needs adjustment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
