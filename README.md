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

| Domain | Per-token agreement `p` | Accepted-prefix length (median) | Read |
|---|---|---|---|
| structured (JSON / extraction) | **0.99** | 36 | drafts accepted essentially whole — speculative decoding viable immediately |
| code | **0.90** | 5 | viable with small blocks (~16–32 tokens); light distillation would compound quickly |
| chat | **0.80** | 4 | marginal — block-size tuning required |
| prose / creative | **0.65** | 2 | not viable stock; distillation-first territory |

Interpretation in brief: a speculative loop accepts the longest drafted
prefix the verifier agrees with, so the accepted-prefix length (APL) — not
raw agreement — is what buys speed. The ordering above is exactly the
entropy ordering theory predicts: parallel drafting mines the predictable
structure of text, so low-entropy domains (structured output, code) parallelize
well and open-ended prose does not. Note that structured's APL is largely
capped by content length — most drafts are accepted to the end of the output.

**Caveats that bound these numbers:** greedy (temperature-0) agreement only;
50 prompts/domain; instruction-tuned checkpoints as released in June 2026;
deterministic decoding rather than the stock stochastic temperature schedule
(configurable — see below). Treat this as a measurement note, not a paper.

## Block-size sweep: where each domain pays off

The stock 256-token canvas is the wrong block size for everything but
structured. Re-segmenting the per-position agreement data into smaller
proposals (offline, from `blocks.jsonl`, via `scripts/block_size_sweep.py`)
gives an implied speedup as a function of block size `B` — accepted tokens per
weight pass, where **1.0 = autoregressive break-even**:

| B | structured | code | chat | prose |
|---|---|---|---|---|
| 4 | 2.9 | 2.6 | 1.9 | 1.05 |
| 8 | 4.6 | 3.8 | 2.2 | 0.98 |
| 16 | 6.3 | **4.5** | 2.1 | 0.72 |
| 32 | 7.5 | 4.2 | 1.5 | 0.52 |
| 64 | 8.0 | 2.9 | 0.9 | 0.35 |
| 256 | **8.3** | 0.76 | 0.38 | 0.21 |

Peak per domain: **structured 8.3× (large B), code 4.5× @ B≈16, chat 2.2× @
B≈8, prose ~1.05× @ B≈4.** Tuning the block size flips code from a 0.76× *loss*
at the stock 256 to a 4.5× win; only prose stays marginal. structured rises
with `B` and plateaus because its drafts are accepted to the end of the (short)
output — content-capped, so longer structured outputs would push it higher, not
lower.

**The two-pass floor caveat.** Every speculative round costs at least two weight
passes — one drafter denoise pass and one verifier pass — so realized speedup at
block size `B` cannot exceed `B/2` (you accept at most `B` tokens per round).
The sweep holds total denoise cost constant (it re-segments the drafter's
*existing* trajectory rather than re-canvassing after each rejection), so it
ignores that floor and **overstates the smallest blocks**: any entry above `B/2`
— e.g. structured and code at `B=4`, structured at `B=8` — is an optimistic
upper bound. Read the *shape* and the mid-range optima (`B≈8–16`), not the
small-`B` tail. Validate empirically by running with `SamplerConfig.block_size`
set to a candidate `B` and reading the real `tokens_per_forward`.

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
  metrics.py        agreement metrics (pure, fully tested)
  results_io.py     timestamped run dir, blocks.jsonl, summary.md
  cli.py            orchestration entry point
prompts/<domain>.jsonl   versioned prompt sets (code, structured, chat, prose)
results/<date>-<tag>/    config.json + blocks.jsonl + summary.md per run
scripts/            sanity_check, probe_drafts, recompute_summary
tests/              model-free unit + mock end-to-end tests
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
  `modeling_diffusiongemma.py` denoise loop — inspect the source first,
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
- `torch_dtype` is deprecated → harness passes `dtype=`.
- `ModuleNotFoundError: harness` under pytest → `python -m pytest` (or rely
  on `pythonpath = ["."]` in `pyproject.toml`).

## What this is not (yet)

- **No speculative sampler is implemented here.** This is the Phase-1
  measurement that decides whether/where one is worth building. The planned
  arc (see [`initial_plan.md`](initial_plan.md)): greedy-exact verify loop →
  proper lossless rejection sampling using captured draft probabilities →
  vLLM integration via its existing speculative-decoding accounting →
  optionally a weight-shared (frozen AR base + diffusion adapter) variant
  and drafter→verifier distillation.
- Stochastic (lossless rejection-sampling) acceptance rates are not yet
  measured — that needs draft-side commit probabilities from
  `--capture-internals`.
- Single model pair, single hardware config, English prompts.

## Contributing / using the data

Issues and PRs welcome — particularly: additional prompt domains,
`--capture-internals` hardening against new `transformers` releases, and
replication on other hardware. If you use the numbers or the harness,
a link back here is appreciated.
