# Speculative Diffusion: DiffusionGemma drafter / Gemma 4 verifier

## What this project is

Prototype of weight-adjacent speculative decoding where Google's DiffusionGemma
(26B-A4B, discrete text diffusion) acts as a parallel block *drafter* and the
autoregressive Gemma 4 26B-A4B acts as the *verifier*. Long-term goal: lossless
(or greedy-exact) AR-quality output at diffusion-class throughput on a single
local GPU.

**Current phase (Phase 1) is measurement only. Do not build the speculative
sampler yet.** The entire project gates on one empirical number: the per-token
agreement rate `p` between DiffusionGemma's committed drafts and Gemma 4's
greedy predictions. Everything in this phase exists to produce that number and
its distribution, broken down by content domain.

## Hardware / environment

- Single NVIDIA RTX PRO 6000 Blackwell, 96 GB VRAM, Linux.
- Both models must be resident simultaneously. Budget: quantize to FP8 (or
  int8 via bitsandbytes if FP8 paths are immature in the installed stack);
  each model ~26–30 GB, leaving headroom for KV cache and canvases.
- Prefer Hugging Face Transformers for Phase 1 (simplicity, hackability).
  vLLM is for Phase 2+; its DiffusionGemma support is relevant later as the
  integration target, not now.

## Models

- Drafter: `google/diffusiongemma-26B-A4B-it` (Hugging Face)
- Verifier: the autoregressive Gemma 4 26B-A4B instruction-tuned model
- Both derive from the same backbone and tokenizer family. **Verify tokenizer
  identity programmatically** (same vocab, same special tokens, same chat
  template token IDs). If they differ in any way, stop and report — agreement
  measurement is meaningless across mismatched tokenizations.

## Phase 1 deliverable: the agreement harness

A small Python package (`harness/`) plus a CLI that:

1. **Generates with DiffusionGemma** using its stock recommended sampler
   (entropy-bounded denoising, adaptive stopping — per the model card:
   entropy bound 0.1, stopping entropy threshold 0.005, stability across two
   consecutive steps). Use temperature-0 / deterministic settings wherever the
   sampler allows.
2. **Captures committed canvas blocks**, not just final detokenized text.
   We need the exact token IDs of each committed 256-token block, in order,
   plus per-block metadata: number of denoise steps used, per-position entropy
   at commit time if accessible.
3. **Teacher-forces each draft through the verifier**: one parallel forward
   pass of Gemma 4 over (prompt + previously verified tokens + drafted block),
   recording at every drafted position whether the verifier's argmax token
   equals the drafted token. Also record the verifier's logprob of the drafted
   token (we'll want soft-agreement stats later, not just greedy match).
4. **Computes and logs metrics** per block, per prompt, per domain:
   - per-token greedy agreement rate `p`
   - position of first disagreement in each block (the prefix-acceptance length)
   - histogram of accepted-prefix lengths
   - mean/median/p90 of accepted prefix length
   - implied speedup estimate: accepted tokens per (denoise_steps + 1) weight
     passes, computed per block and aggregated
   - correlation between commit-time entropy and disagreement (does the
     drafter's own confidence predict verifier agreement?)
5. **Writes results as JSONL** (one record per block) plus a summary table.
   Raw JSONL is the artifact; summaries are derived. Never aggregate away the
   raw per-position data.

### Evaluation prompt sets (separate domains, ~50–100 prompts each to start)

- `code`: HumanEval-style completion prompts and short "edit this function"
  tasks (low-entropy target, expected best case)
- `structured`: JSON extraction / table filling / format-following tasks
- `chat`: short open-ended assistant-style questions
- `prose`: creative/long-form continuation (high-entropy, expected worst case)

Keep prompt sets in `prompts/<domain>.jsonl` so they're versioned and rerunnable.

### Important implementation cautions

- **DiffusionGemma is days old; its modeling code and sampler API may not
  match any prior assumptions or this document.** Before writing the capture
  hook, read the actual installed modeling/sampling source
  (`transformers` model code or the model repo's custom code) and identify
  where committed canvases exist as token IDs. Inspect first, then code.
- The model is encoder–denoiser: the encoder runs causally for prefill and
  builds KV cache; the denoiser runs bidirectionally over the canvas. The
  capture point is the commit step (canvas → KV cache append).
- Chat-template parity matters: the same prompt must be rendered identically
  for both models. Render once, reuse token IDs.
- Greedy determinism: fix seeds, disable any stochastic renoising where
  configurable, and document any nondeterminism you can't remove.
- Memory: load drafter and verifier sequentially if needed during bring-up;
  the production harness should hold both. If FP8 of either model misbehaves,
  fall back to verifier in FP8 + drafter in bf16-with-offload and note the
  perf cost — Phase 1 cares about correctness of measurement, not speed.
- Start tiny: 5 prompts, 1 domain, end-to-end, with assertions — before
  scaling to full sets.

### Decision gates (what the numbers mean)

- Code-domain greedy agreement ≳ 0.90 and median accepted prefix ≳ 10:
  → Phase 2 (greedy-verified speculative loop) is viable with small blocks.
- Agreement 0.7–0.9: → viable only with reduced block size and/or light
  distillation; quantify the block-size sweet spot from the histograms.
- Agreement < 0.7: → stock drafts can't serve this verifier; Phase 2 becomes
  a distillation project (Hackable Diffusion recipes) before any sampler work.

## Phase 2+ (do not start; context only)

1. Greedy-exact verify loop in the harness (accept matched prefix, resample
   point of divergence with verifier, re-canvas from there). Measure realized
   tokens/sec vs plain AR and vs stock DiffusionGemma.
2. Proper lossless rejection sampling using captured draft probabilities.
3. vLLM integration via its existing speculative-decoding accounting (their
   DiffusionGemma blog post documents the scheduler hooks).
4. Optional: adapter-isolated single-backbone variant (frozen Gemma 4 +
   diffusion LoRA) to collapse VRAM to one model.
5. Optional: distillation of the drafter toward the verifier's conditionals.

## References to consult (fetch as needed)

- Model card / sampler best practices:
  https://huggingface.co/google/diffusiongemma-26B-A4B-it
- Google model docs: https://ai.google.dev/gemma/docs/diffusiongemma
- Developer guide (training recipes, Hackable Diffusion):
  https://developers.googleblog.com/diffusiongemma-the-developer-guide/
- vLLM integration internals (Phase 2 target):
  https://vllm.ai/blog/2026-06-10-diffusion-gemma

## Working conventions

- Python 3.11+, `uv` or venv; pin versions in `pyproject.toml`.
- Every run produces a timestamped results dir with config snapshot
  (`results/<date>-<tag>/{config.json, blocks.jsonl, summary.md}`).
- Small, reviewable commits; the harness is the experiment notebook — keep it
  boring and deterministic.
- When something about the model's internals contradicts this document,
  trust the installed source code and say so explicitly in the run notes.
