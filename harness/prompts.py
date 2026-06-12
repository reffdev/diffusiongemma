"""Load versioned prompt sets from prompts/<domain>.jsonl.

Each line is a JSON object: {"id": "<stable id>", "prompt": "<user turn text>"}.
The harness renders each prompt through the *shared* chat template exactly once
(see verifier.render_chat) and reuses the resulting token IDs for both models.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class Prompt:
    domain: str
    id: str
    prompt: str


def load_domain(prompts_dir: str, domain: str, limit: int | None = None) -> list[Prompt]:
    path = os.path.join(prompts_dir, f"{domain}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"prompt set not found: {path}")
    out: list[Prompt] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "id" not in obj or "prompt" not in obj:
                raise ValueError(f"{path}:{lineno}: each line needs 'id' and 'prompt'")
            out.append(Prompt(domain=domain, id=str(obj["id"]), prompt=str(obj["prompt"])))
            if limit is not None and len(out) >= limit:
                break
    return out


def load_all(prompts_dir: str, domains, limit: int | None = None) -> list[Prompt]:
    prompts: list[Prompt] = []
    for d in domains:
        prompts.extend(load_domain(prompts_dir, d, limit=limit))
    return prompts
