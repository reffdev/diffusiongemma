"""End-to-end pipeline smoke test using mock models (no GPU / no transformers).

This is the "start tiny, end-to-end, with assertions" check from the plan,
run against synthetic drafter/verifier so the metrics + JSONL + summary IO are
exercised on any machine before touching real weights.
"""

import json
import os

from harness.cli import run
from harness.config import RunConfig


def test_mock_run_produces_artifacts(tmp_path):
    cfg = RunConfig(
        domains=("code",),
        prompts_dir="prompts",
        results_dir=str(tmp_path),
        tag="pytest",
        max_prompts_per_domain=3,
        max_blocks_per_prompt=3,
        seed=0,
        mock=True,
    )
    run_dir = run(cfg, mock_agree_rate=0.8)

    blocks_path = os.path.join(run_dir, "blocks.jsonl")
    config_path = os.path.join(run_dir, "config.json")
    summary_path = os.path.join(run_dir, "summary.md")
    assert os.path.exists(blocks_path)
    assert os.path.exists(config_path)
    assert os.path.exists(summary_path)

    # 3 prompts * 3 blocks each = 9 records, each well-formed.
    with open(blocks_path, encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    assert len(records) == 9
    for r in records:
        assert len(r["draft_ids"]) == len(r["argmax_ids"]) == len(r["match"])
        assert 0 <= r["accepted_prefix_len"] <= len(r["match"])
        assert 0.0 <= r["p_block"] <= 1.0

    # Config snapshot round-trips and records mock mode.
    with open(config_path, encoding="utf-8") as fh:
        snap = json.load(fh)
    assert snap["mock"] is True
    assert snap["tag"] == "pytest"

    summary = open(summary_path, encoding="utf-8").read()
    assert "Agreement summary" in summary
    assert "code" in summary
