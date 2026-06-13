"""Drive DiffusionGemma's causal encoder pathway as a standard next-token LM.

DiffusionGemma exposes no native causal LM: the encoder returns hidden states
(no logits) and the lm_head lives on the block-diffusion head over the canvas.
This wrapper runs the causal ENCODER and applies the model's existing lm_head to
its last_hidden_state, exposing `model(input_ids=...).logits` so the existing
RealGemmaVerifier teacher-forcing (and greedy generation) work unchanged.

Validated empirically by scripts/probe_causal_mode.py (coherent greedy output)
before any use — this is the wrapper that probe tests, not a blind assumption.
"""

from __future__ import annotations

from types import SimpleNamespace

ENCODER_CLASSES = ("DiffusionGemmaEncoderModel", "DiffusionGemmaEncoderTextModel")


def find_encoder(model):
    for _, mod in model.named_modules():
        if type(mod).__name__ in ENCODER_CLASSES:
            return mod
    raise RuntimeError(
        f"no causal encoder submodule found (looked for {ENCODER_CLASSES}); "
        "inspect model.named_modules() — the structure differs from what was probed."
    )


class CausalLMWrapper:
    """Expose `encoder -> lm_head` as `model(input_ids=...).logits`."""

    def __init__(self, model):
        self._model = model
        self._encoder = find_encoder(model)
        self._lm_head = model.lm_head

    def __call__(self, input_ids=None, **_ignored):
        out = self._encoder(input_ids=input_ids)
        h = getattr(out, "last_hidden_state", None)
        if h is None:
            h = out[0]
        return SimpleNamespace(logits=self._lm_head(h))

    def parameters(self):
        return self._model.parameters()

    def eval(self):
        self._model.eval()
        return self
