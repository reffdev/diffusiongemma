"""Chat-template rendering, done once and shared by both models.

Chat-template parity is a correctness requirement: the same prompt must be
rendered to the same token IDs for drafter and verifier. We render with one
tokenizer (after tokenizer_check has proven they are identical) and reuse the
IDs everywhere.
"""

from __future__ import annotations


def render_user_prompt(tokenizer, prompt_text: str) -> list[int]:
    """Render a single user turn into prompt token IDs with a generation prompt.

    Returns a flat list[int]. We are defensive about `apply_chat_template`
    return types because they vary across transformers versions:
      - some default `tokenize=False` and return the formatted *string*;
      - some return a dict/BatchEncoding when `return_dict` is on.
    Any non-int-list result is coerced to token IDs so downstream
    `torch.tensor(...)` never sees strings.
    """
    out = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt_text}],
        add_generation_prompt=True,
        tokenize=True,
    )
    # dict / BatchEncoding -> pull input_ids
    if hasattr(out, "get") and "input_ids" in out:
        out = out["input_ids"]
    # tensor -> list
    if hasattr(out, "tolist"):
        out = out.tolist()
    # nested [[...]] -> [...]
    if isinstance(out, list) and len(out) == 1 and isinstance(out[0], list):
        out = out[0]
    # still a string (tokenize ignored) -> encode the rendered template text
    if isinstance(out, str):
        out = tokenizer.encode(out, add_special_tokens=False)
    if not (isinstance(out, list) and all(isinstance(t, int) for t in out)):
        raise TypeError(
            f"render_user_prompt could not produce token IDs; got {type(out)}: {out!r:.80}"
        )
    return out
