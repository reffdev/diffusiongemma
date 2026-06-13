# Can DiffusionGemma draft for Gemma 4?

**Per-domain measurements of draft-verifier agreement between Google's
DiffusionGemma (26B-A4B) and its autoregressive sibling, Gemma 4 26B-A4B —
the gating numbers for diffusion-based speculative decoding.**

DiffusionGemma generates ~4x faster than its AR sibling but benchmarks below
it. The obvious idea — and many people will have it — is the best of both:
let the diffusion model **draft** blocks of tokens in parallel and let the AR
model **verify** them in a single teacher-forced pass, keeping AR-exact
output at diffusion-class speed. Whether that architecture is worth building
hinges on one empirical number nobody had published: **how often does a stock
DiffusionGemma draft token match what Gemma 4 would have produced?**

This repo measures that number. It contains the measurement harness, the
prompt sets, the raw per-position results, and the bring-up notes for running
both 26B models on a single consumer-Blackwell GPU.

## Headline results

200 prompts (50 per domain), greedy decoding both sides, bf16, single
RTX PRO 6000 Blackwell (96 GB), June 2026 model releases:

| Domain | Per-token agreement `p` | Accepted-prefix length (median) | Implied speedup (native canvas) | Read |
|---|---|---|---|---|
| structured (JSON / extraction) | **0.99** | 36 | **~8×** | the one clear speculative win — drafts accepted ~whole, big speedup |
| code | **0.90** | 5 | 0.76× | high agreement but **< break-even** at every block size (see below) — a quality signal, not a speed win |
| chat | **0.80** | 4 | 0.38× | below break-even at any block size |
| prose / creative | **0.65** | 2 | 0.21× | not viable; distillation territory |

Interpretation in brief: a speculative loop accepts the longest drafted
prefix the verifier agrees with, so accepted-prefix length (APL) — not raw
agreement — is what buys speed, and APL only converts to speedup if the
drafter is cheap per accepted token. **Only structured clears that bar.** The
agreement ordering follows the entropy ordering theory predicts (low-entropy
structure parallelizes, open-ended prose doesn't), but high agreement on code
does **not** translate to a speedup — the diffusion drafter spends ~11 denoise
passes per block to land ~5 accepted tokens. Block-size tuning was tested and
does **not** fix this (next section). structured's APL is content-capped — most
drafts are accepted to the end of the (short) output.

**Caveats that bound these numbers:** greedy (temperature-0) agreement only;
50 prompts/domain; instruction-tuned checkpoints as released in June 2026;
deterministic decoding rather than the stock stochastic temperature schedule
(configurable — see below). Treat this as a measurement note, not a paper.

## Block size: the "sweet spot" is a mirage (predicted, then refuted)

An offline re-segmentation of the agreement data (`scripts/block_size_sweep.py`)
*predicted* that smaller proposal blocks would rescue code/chat — e.g. code 4.5×
at `B≈16` vs 0.76× at the stock 256. **Native runs at `B`=16/32 refuted it.**
Driving the model at a true small canvas (`SamplerConfig.block_size` →
`config.canvas_length`) and measuring (`scripts/validate_block_size.py`):

| domain | sweep predicted @16 | **measured @16** | **measured @32** | measured @256 |
|---|---|---|---|---|
| code | 4.5× | **0.29×** | 0.97× | 0.76× |
| chat | 2.1× | **0.16×** | 0.33× | 0.38× |
| prose | 0.72× | **0.08×** | 0.16× | 0.21× |

**No domain crosses break-even at any block size.** The sweep's fatal assumption
was that denoise cost scales with block size; empirically the diffusion model's
denoise-step count is **roughly canvas-independent** (~11–12 passes/block for
`B`≥32, ballooning to ~24 at `B`=16 from lost lookahead context). So shrinking
the canvas commits fewer tokens for the same iteration budget — efficiency
*collapses*. The parallelism that makes diffusion fast comes from the large
canvas amortizing those iterations across many tokens; small blocks throw it
away. **structured (large canvas, ~8×) is the only speculative win, and
block-size tuning cannot create others.**

## Single-model self-verify: you may not need Gemma 4 at all

DiffusionGemma's encoder runs causally (it does prefill), and that pathway plus
the model's own `lm_head` can be driven as an autoregressive next-token LM
(`harness/causal.py`) — so DiffusionGemma can **verify its own drafts**, no
second model. Pointing the existing teacher-forcing scorer at this causal mode
(`scripts/causal_self_agreement.py`) and re-scoring the same drafts:

| domain | `p_self` (causal scores its own drafts) | `p` vs Gemma 4 |
|---|---|---|
| structured | **0.995** | 0.993 |
| code | 0.916 | 0.899 |
| chat | 0.821 | 0.796 |
| prose | 0.678 | 0.647 |

`p_self ≥ p` in every domain — the model agrees with its own drafts at least as
well as the external verifier. And a 200-prompt standalone-quality eval
(`scripts/causal_quality_gen.py` + `causal_quality_eval.py`) is **automated-PASS-
consistent**: causal vs Gemma 4 structured normalized-match **0.98**, causal code
syntax-validity **0.96** (≥ Gemma 4's 0.88), ~0 degeneracy (1/200), and causal
self-terminates as well as Gemma 4 (cap-hits reflect long answers, which Gemma 4
produces *more* of). Final code/chat/prose content-quality is a manual read of
the side-by-side artifacts and is **not yet concluded** — but the verifier role
(teacher-forced) is solid regardless. This makes a **single-model speculative
loop** (one DiffusionGemma: diffusion-mode drafts + causal-mode verify) the
front-runner, and sidesteps the dead-end quantization/serving routes below.

## How it's measured

1. **Draft.** DiffusionGemma generates via its public
   `DiffusionGemmaForBlockDiffusion.generate()` (deterministic at temp-0);
   the committed 256-token canvas blocks are captured as raw token IDs.
2. **Verify.** Each drafted block is teacher-forced through Gemma 4 in one
   parallel pass — prompt + previously verified tokens + drafted block —
   recording, per position, whether the verifier's argmax matches the draft,
   plus the verifier's logprob of the drafted token.
3. **Score.** Per-token agreement, first-disagreement position (= accepted
   prefix length), histograms, and an implied speedup estimate — accepted
   tokens per weight pass, with the drafter's per-block denoise-pass count
   taken from the public `tokens_per_forward` output field — per block /
   prompt / domain. Trailing-pad runs are trimmed before scoring; because
   the verifier pass is causally masked, trimming a trailing pad run cannot
   change any content-position result.

Both models share a tokenizer lineage, and the harness hard-gates on
programmatic tokenizer identity (vocab, special tokens, chat-template IDs)
before any run — agreement across mismatched tokenizers is meaningless.

Raw `blocks.jsonl` (one record per block, with per-position arrays) is the
artifact of record; `summary.md` is derived and reproducible from it via
`scripts/recompute_summary.py` with no model reload.

## Repo layout

```
harness/            measurement package
  config.py         run / model / sampler config dataclasses
  prompts.py        load prompts/<domain>.jsonl
  tokenizer_check.py assert drafter/verifier tokenizer identity (hard gate)
  models.py         load drafter + verifier (bf16 / int8)
  chat.py           render the shared chat template once, reuse token IDs
  drafter.py        DiffusionGemma generate + slice into committed blocks
  verifier.py       Gemma 4 teacher-forcing pass
  causal.py         drive DiffusionGemma's encoder+lm_head as a causal LM (self-verify)
  metrics.py        agreement metrics (pure, fully tested)
  results_io.py     timestamped run dir, blocks.jsonl, summary.md
  cli.py            orchestration entry point
prompts/<domain>.jsonl   versioned prompt sets (code, structured, chat, prose)
results/<date>-<tag>/    config.json + blocks.jsonl + summary.md per run
scripts/            block_size_sweep + validate_block_size (block-size study),
                    causal_self_agreement + causal_quality_gen/eval (self-verify),
                    compare_runs, recompute_summary, sanity_check, probe_*
tests/              model-free unit + mock end-to-end tests (run: `pytest`)
```

## Reproducing

### No GPU needed: mock mode

Runs the full metrics + IO pipeline with synthetic models — validates the
harness on any machine before touching weights:

```bash
python -m harness.cli --mock --domains code --max-prompts 3 --max-blocks 3 --tag smoke
pytest
```

### Real run

Requires ~60 GB VRAM headroom for one 26B model at a time (the harness runs
**two-pass sequential** by default: drafter alone, freed, then verifier alone —
so the models never co-reside and bf16 fits in 96 GB).

```bash
# Python 3.11+. DiffusionGemma needs transformers >= the 2026-06-10 release.
python -m venv .venv && . .venv/bin/activate
pip install -U transformers torch accelerate
pip install -e ".[quant]"            # bitsandbytes (+ torchvision, pillow)

# Gated repos: accept each model's license on its HF page, then
hf auth login                        # note: `hf`, not `huggingface-cli`

python -m harness.cli --domains code structured chat prose --tag run1
```

Weights (~60 GB combined) cache to `~/.cache/huggingface/` (`HF_HOME` to
relocate, `HF_HUB_OFFLINE=1` for cache-only). Cheap pre-flight:

```bash
hf auth whoami
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('google/gemma-4-26B-A4B-it')"
```

### Options worth knowing

- The **speedup** column is populated by default from the public
  `tokens_per_forward` output field — no source hook needed.
- `--capture-internals` adds per-position commit-time entropy, which feeds the
  **entropy~disagreement** column (otherwise `n/a`). It hooks the installed
  `modeling_diffusion_gemma.py` denoise loop — inspect the source first,
  attribute names are not stable on a model this new.
- `SamplerConfig.deterministic=False` measures under the stock stochastic
  temperature schedule (0.8→0.4) instead of greedy. Record which you used.
- `--drafter-quant int8` / `--verifier-quant int8` work but barely shrink
  this model (see below for why).
- `--no-sequential` co-loads both models — only for multi-GPU / >110 GB.

## Known-good environment (consumer Blackwell / SM120, WSL2)

Hard-won bring-up notes; these cost real time, pin them once working.

- **fp8 does not run on SM120.** The fp8 grouped-MoE matmul needs DeepGEMM
  (Hopper SM90 / datacenter Blackwell SM100); on SM120 it falls back to a
  Triton kernel that rejects this model's expert dim (`K (704) must be
  divisible by block_k (128)`). Use bf16 — it's the default here.
- **int8 barely helps on this model.** bitsandbytes quantizes `nn.Linear`
  only; the fused MoE experts (most of the weight) stay bf16: ~49.5 GB int8
  vs ~52 GB bf16. Two int8 models still don't co-reside in 96 GB — hence
  two-pass sequential as the default.
- **Don't install latest `kernels`.** It breaks transformers at import
  (`LayerRepository ... revision or version must be specified`), and since
  fp8 needs `kernels` but fp8 can't run on SM120 anyway, there's no winning
  move there. If required, pin to the range from
  `python -c "from transformers.dependency_versions_table import deps; print(deps.get('kernels'))"`.
- `Gemma4Processor requires PIL` → `pip install pillow`; torchvision is
  imported by the image processor → `pip install torchvision` (both are in
  the dependency list).
- `weight_scale_inv ... MISSING / newly initialized` on load is benign fp8
  boilerplate when loading the bf16 checkpoint; ignore in bf16.
- **NVFP4 doesn't load via Transformers.** The published NVFP4 checkpoints are
  `quant_method: modelopt`, which Transformers 5.11 has no quantizer for — it
  *silently skips quantization and loads random experts*. A bare `nvidia-modelopt`
  install doesn't register a Transformers quantizer either (and it can *downgrade*
  transformers, breaking DiffusionGemma — keep the bf16 venv clean). pip vLLM
  also lacks a native DiffusionGemma model (its generic Transformers backend
  crashes on the denoiser's forward signature). Only the `vllm/vllm-openai:gemma`
  Docker image loads NVFP4 — a server, not the offline API. Single-model
  self-verify made this route unnecessary for the research question.
- `torch_dtype` is deprecated → harness passes `dtype=`.
- `ModuleNotFoundError: harness` under pytest → `python -m pytest` (or rely
  on `pythonpath = ["."]` in `pyproject.toml`).

## What this is not (yet)

- **No speculative sampler is implemented here.** This is the measurement that
  decides whether/where one is worth building. What it has decided so far:
  speculative diffusion is a **narrow win — structured/low-entropy only** (~8×);
  block-size tuning does *not* extend that to code/chat/prose; and a
  **single-model self-verify** loop (one DiffusionGemma drafting + self-verifying)
  is the front-runner architecture, no second model or exotic quant needed.
- **Next** (see [`initial_plan.md`](initial_plan.md) for the original arc): a
  realized tokens/sec measurement (the speedups here are *implied* — accepted
  tokens per weight pass — not wall-clock), then the self-verify loop scoped to
  structured, then optionally lossless rejection sampling using captured draft
  logprobs. Distillation (for the failed domains) and the NVFP4/Docker serving
  route are parked.
- The causal-mode standalone **content-quality** call (PASS vs quality-floor) is
  pending a manual read of the side-by-side artifacts.
- Single model pair, single hardware config, English prompts.

## Contributing / using the data

Issues and PRs welcome — particularly: additional prompt domains,
`--capture-internals` hardening against new `transformers` releases, and
replication on other hardware. If you use the numbers or the harness,
a link back here is appreciated.
