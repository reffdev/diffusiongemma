# DiffusionGemma drafter / Gemma 4 verifier — Phase 1 agreement harness

Measurement-only harness for the speculative-diffusion prototype described in
[`initial_plan.md`](initial_plan.md). Phase 1 produces exactly one thing: the
per-token greedy agreement rate `p` between DiffusionGemma's committed draft
blocks and Gemma 4's argmax predictions, broken down by content domain — plus
the accepted-prefix-length distribution and an implied speedup estimate.

**No speculative sampler is built in this phase.** See the plan's decision gates
for what the numbers mean.

## Layout

```
harness/            measurement package
  config.py         run / model / sampler config dataclasses
  prompts.py        load prompts/<domain>.jsonl
  tokenizer_check.py assert drafter/verifier tokenizer identity (hard gate)
  models.py         load drafter + verifier (fp8 / int8 / bf16)
  chat.py           render the shared chat template once, reuse token IDs
  drafter.py        DiffusionGemma generate + slice into committed blocks
                    (optional internals capture is the inspect-first seam)
  verifier.py       Gemma 4 teacher-forcing pass
  metrics.py        agreement metrics (pure, fully tested)
  results_io.py     timestamped run dir, blocks.jsonl, summary.md
  cli.py            orchestration entry point
prompts/<domain>.jsonl   versioned, rerunnable prompt sets
results/<date>-<tag>/     config.json + blocks.jsonl + summary.md per run
tests/              model-free unit + mock end-to-end tests
```

## Quick start (local, no GPU)

The mock mode runs the full metrics + IO pipeline with synthetic models, so you
can validate the harness on any machine (e.g. this Windows box) before touching
weights:

```bash
python -m harness.cli --mock --domains code --max-prompts 3 --max-blocks 3 --tag smoke
pytest            # unit + end-to-end mock tests
```

This writes `results/<timestamp>-smoke/{config.json,blocks.jsonl,summary.md}`.

## Real run (on the GPU box)

```bash
# Python 3.11+. DiffusionGemma needs a recent transformers (released 2026-06-10).
python -m venv .venv && . .venv/bin/activate
pip install -U transformers torch accelerate     # per the model card
pip install -e ".[quant]"                         # adds bitsandbytes (+ torchvision, pillow)

# Authenticate for the gated Gemma repos (new HF CLI: `hf`, not `huggingface-cli`).
# Accept each model's license on its HF page first, then:
hf auth login                       # paste a token from huggingface.co/settings/tokens

# Defaults: bf16 weights, two-pass sequential (one model resident at a time).
python -m harness.cli --domains code structured chat prose --tag run1
```

The harness loads the drafter alone (generates all drafts), frees it, then loads
the verifier alone — so the two 26B models never co-reside. This is why bf16 is
the default and fits: peak VRAM is one model (~52 GB), not both (~104 GB). Pass
`--no-sequential` only if both models fit at once (multi-GPU / >110 GB).

Weights (~60 GB combined) download to `~/.cache/huggingface/` on first run and
are reused after that (set `HF_HOME` to relocate; `HF_HUB_OFFLINE=1` to force
cache-only). Verify auth cheaply before the full pull:

```bash
hf auth whoami
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('google/gemma-4-26B-A4B-it')"
```

### What runs today vs. what needs more work

The **agreement measurement runs via the public API** — no source hacking
required. DiffusionGemma's documented `DiffusionGemmaForBlockDiffusion.generate()`
is deterministic at temp-0, so committed 256-token canvas blocks are the
generated continuation sliced into chunks (`harness/drafter.py`). That gives the
primary Phase-1 numbers: per-token agreement `p`, accepted-prefix length, and
their histograms — the decision gates depend only on these.

What is **not** available from the public API, and what to do about it:

1. **Per-block denoise steps + commit entropy** feed the *speedup* and
   *entropy~disagreement* metrics. `generate()` doesn't expose them, so those
   two columns report `n/a` unless you pass `--capture-internals`, which
   requires wiring `_InternalsCapture` in `harness/drafter.py` against the
   installed `modeling_diffusiongemma.py` denoise/commit loop. Inspect first,
   then code — don't guess attribute names. The core run does not need this.
2. **Tokenizer identity is a hard gate.** `tokenizer_check` stops the run if the
   drafter and verifier tokenizers differ in vocab, special tokens, or
   chat-template token IDs. Agreement across mismatched tokenizers is meaningless.
3. **Determinism.** The harness decodes greedily (`do_sample=False`) for
   reproducibility, which diverges from the stock stochastic 0.8→0.4 temperature
   schedule. Set `SamplerConfig.deterministic=False` to measure under the stock
   sampler instead, and note which you used in the run notes.
4. **Quantization.** Default is bf16 (see Troubleshooting for why fp8 doesn't
   run on SM120). `--drafter-quant int8` / `--verifier-quant int8` (bitsandbytes)
   works but barely shrinks this MoE model.

## Troubleshooting / known-good environment

Hard-won notes from bringing this up on an RTX PRO 6000 Blackwell (SM120) in
WSL2 Ubuntu. Pin these once you have a working venv.

- **`ModuleNotFoundError: No module named 'harness'` under `pytest`.** Run
  `python -m pytest`, or rely on the `pythonpath = ["."]` in `pyproject.toml`.
- **`Gemma4Processor requires the PIL library`** → `pip install pillow`.
- **`No module named 'torchvision'`** (Gemma 4 image processor imports it) →
  `pip install torchvision`. Both are now in the dependency list.
- **`kernels` is a trap, not a fix.** Installing the latest `kernels` breaks
  transformers at import (`LayerRepository ... Either a revision or a version
  must be specified`). And the fp8 path *requires* `kernels`, so you can't win
  on fp8 by toggling it. See the fp8 note below. If you must have it, pin to the
  range from `python -c "from transformers.dependency_versions_table import deps;
  print(deps.get('kernels'))"`.
- **fp8 does NOT run on this GPU.** The fp8 grouped-MoE matmul needs DeepGEMM
  (Hopper SM90 / datacenter-Blackwell SM100); on SM120 it falls back to a Triton
  kernel that rejects this model's expert dim (`K (704) must be divisible by
  block_k (128)`). Use **bf16** (default). fp8 is for SM90/SM100 datacenter parts.
- **int8 barely helps here.** bitsandbytes only quantizes `nn.Linear`; this
  model's weight is dominated by fused MoE experts that stay bf16, so int8 ≈
  49.5 GB vs bf16 ≈ 52 GB. Two int8 models still don't co-reside in 96 GB —
  which is the whole reason the harness defaults to two-pass sequential.
- **`weight_scale_inv ... MISSING / newly initialized`** on load is benign fp8
  boilerplate (the bf16 checkpoint has no fp8 scales); irrelevant in bf16.
- **`torch_dtype` is deprecated** → the harness uses `dtype=`.
- **`hf` is the current CLI**, not `huggingface-cli` (`hf auth login`).

## Conventions

- Every run snapshots its full config (incl. torch/transformers versions) to
  `config.json`. Raw `blocks.jsonl` is the artifact; `summary.md` is derived and
  never the source of truth — never aggregate away the per-position arrays.
- When the model's internals contradict the plan or this README, trust the
  installed source and say so explicitly in the run notes.
