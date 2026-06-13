"""Unit tests for the vLLM adapter's pure logic (no vLLM / no GPU / no weights)."""

from collections import namedtuple

from scripts.compare_runs import domain_stats
from scripts.vllm_agreement import parse_prompt_logprobs, slice_into_blocks

Lp = namedtuple("Lp", "logprob rank")


def test_slice_into_blocks_trims_pad():
    # trailing pad (0) removed, then sliced into size-2 chunks
    assert slice_into_blocks([1, 2, 3, 4, 5, 0, 0, 0], 2, pad_id=0) == [[1, 2], [3, 4], [5]]


def test_slice_into_blocks_full_blocks():
    assert slice_into_blocks([7, 8, 9, 10], 2, pad_id=0) == [[7, 8], [9, 10]]


def test_parse_prompt_logprobs_alignment_and_argmax():
    n_prefix = 3
    draft_ids = [10, 11, 12]
    # positions 0..5; 0 is None (no prediction for first token)
    prompt_logprobs = [
        None,
        {1: Lp(-0.5, 0)},
        {2: Lp(-0.5, 0)},
        {10: Lp(-0.10, 0), 99: Lp(-2.0, 1)},   # pos 3 predicts draft[0]=10 -> argmax 10 (match)
        {88: Lp(-0.20, 0), 11: Lp(-1.5, 1)},   # pos 4 predicts draft[1]=11 -> argmax 88 (miss)
        {12: Lp(-0.05, 0)},                     # pos 5 predicts draft[2]=12 -> argmax 12 (match)
    ]
    vr = parse_prompt_logprobs(prompt_logprobs, n_prefix, draft_ids)
    assert vr.argmax_ids == [10, 88, 12]
    assert vr.logprob_of_draft == [-0.10, -1.5, -0.05]
    # match (computed downstream) would be [True, False, True]
    assert [a == d for a, d in zip(vr.argmax_ids, draft_ids)] == [True, False, True]


def test_parse_prompt_logprobs_argmax_without_rank():
    # if rank is missing, fall back to max logprob
    Lp2 = namedtuple("Lp2", "logprob")
    dist = {5: Lp2(-3.0), 6: Lp2(-0.2), 7: Lp2(-1.0)}
    vr = parse_prompt_logprobs([None, dist], 1, [7])
    assert vr.argmax_ids == [6]  # 6 has the highest logprob


def test_compare_domain_stats_and_speedup_na():
    rows = [
        {"domain": "code", "accepted_prefix_len": 2, "match": [True, True, False], "denoise_steps": None},
        {"domain": "code", "accepted_prefix_len": 0, "match": [False, True], "denoise_steps": None},
    ]
    s = domain_stats(rows, "code")
    assert s["n"] == 2
    # 3 of 5 positions agree
    assert abs(s["p"] - 3 / 5) < 1e-9
    assert s["speedup"] is None  # no denoise_steps -> n/a


def test_compare_structured_floor_logic():
    rows = [{"domain": "structured", "accepted_prefix_len": 1, "match": [True] + [False] * 9,
             "denoise_steps": None}]
    s = domain_stats(rows, "structured")
    assert s["p"] < 0.98  # would trip the structured flag in compare_runs
