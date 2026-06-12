"""Unit tests for the agreement metrics — fully model-free."""

from harness.metrics import (
    accepted_prefix_len,
    block_agreement,
    build_record,
    speedup_estimate,
    summarize,
)
from harness.types import DraftBlock, VerifyResult


def test_accepted_prefix_len_all_match():
    assert accepted_prefix_len([True, True, True]) == 3


def test_accepted_prefix_len_first_disagreement():
    assert accepted_prefix_len([True, True, False, True]) == 2
    assert accepted_prefix_len([False, True, True]) == 0
    assert accepted_prefix_len([]) == 0


def test_block_agreement():
    assert block_agreement([True, True, False, False]) == 0.5
    assert block_agreement([]) == 0.0


def test_speedup_estimate():
    # 6 accepted tokens over (4 denoise + 1 verify) passes = 1.2
    assert speedup_estimate(6, 4) == 6 / 5


def test_build_record_derives_fields():
    block = DraftBlock(
        block_index=0,
        draft_ids=[10, 11, 12, 13],
        denoise_steps=4,
        commit_entropy=[0.001, 0.002, 0.05, 0.06],
    )
    verify = VerifyResult(
        argmax_ids=[10, 11, 99, 13],  # disagree at index 2
        logprob_of_draft=[-0.1, -0.1, -5.0, -0.2],
    )
    rec = build_record("code", "p1", block, verify)
    assert rec.match == [True, True, False, True]
    assert rec.accepted_prefix_len == 2
    assert rec.p_block == 0.75
    assert rec.speedup_estimate == 2 / 5


def test_build_record_unknown_denoise_steps():
    # Public-API capture path: no denoise steps / entropy -> speedup is None.
    block = DraftBlock(block_index=0, draft_ids=[1, 2, 3], denoise_steps=None)
    verify = VerifyResult(argmax_ids=[1, 2, 9], logprob_of_draft=[-0.1, -0.1, -4.0])
    rec = build_record("code", "p1", block, verify)
    assert rec.accepted_prefix_len == 2
    assert rec.speedup_estimate is None
    s = summarize([rec], "code")
    assert s.speedup is None
    assert s.entropy_disagreement_corr is None


def test_summarize_aggregates():
    blocks = [
        (DraftBlock(0, [1, 2, 3], 4, [0.001, 0.002, 0.09]),
         VerifyResult([1, 2, 9], [-0.1, -0.1, -4.0])),  # apl=2
        (DraftBlock(1, [4, 5, 6], 4, [0.001, 0.09, 0.001]),
         VerifyResult([9, 5, 6], [-4.0, -0.1, -0.1])),  # apl=0
    ]
    recs = [build_record("code", "p1", b, v) for b, v in blocks]
    s = summarize(recs, "code")
    assert s.n_blocks == 2
    assert s.n_positions == 6
    # 4 of 6 positions match -> p = 4/6
    assert abs(s.p - 4 / 6) < 1e-9
    # accepted prefixes are 2 and 0
    assert s.apl_histogram == {2: 1, 0: 1}
    # speedup = (2 + 0) accepted / (5 + 5) passes
    assert s.speedup == 2 / 10
    # higher entropy positions are exactly the disagreements -> positive corr
    assert s.entropy_disagreement_corr is not None
    assert s.entropy_disagreement_corr > 0
