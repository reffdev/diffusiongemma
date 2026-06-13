"""Unit tests for the causal self-verify pure logic (no torch / no weights)."""

import json

from scripts.causal_quality_compare import build_sidebyside_md
from scripts.causal_self_agreement import assemble_worklist
from scripts.vllm_agreement import _read_source_drafts


def test_assemble_worklist_grows_prefix():
    prompt_ids = {"p1": [9, 9]}
    blocks = {"p1": [[1, 2], [3, 4]]}
    domains = {"p1": "code"}
    work = assemble_worklist(prompt_ids, blocks, domains)
    assert work == [
        ("code", "p1", 0, [9, 9], [1, 2]),
        ("code", "p1", 1, [9, 9, 1, 2], [3, 4]),  # prefix includes block 0
    ]


def test_assemble_worklist_skips_unknown_prompt():
    work = assemble_worklist({"p1": [9]}, {"p2": [[1]]}, {"p2": "code"})
    assert work == []


def test_read_source_drafts_groups_and_orders(tmp_path):
    rows = [
        {"domain": "code", "prompt_id": "a", "block_index": 1, "draft_ids": [3, 4], "match": [True, False]},
        {"domain": "code", "prompt_id": "a", "block_index": 0, "draft_ids": [1, 2], "match": [True, True]},
        {"domain": "structured", "prompt_id": "b", "block_index": 0, "draft_ids": [5], "match": [True]},
    ]
    f = tmp_path / "blocks.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    drafts, domains, src_match = _read_source_drafts(str(tmp_path))
    assert drafts["a"] == [[1, 2], [3, 4]]  # ordered by block_index
    assert domains == {"a": "code", "b": "structured"}
    assert src_match[("a", 0)] == [True, True]


def test_build_sidebyside_md():
    md = build_sidebyside_md([{"id": "x1", "prompt": "do thing", "causal": "C", "diffusion": "D", "gemma4": "G"}])
    assert "## x1" in md and "do thing" in md
    for label in ("causal", "diffusion", "gemma4"):
        assert f"**{label}:**" in md
