"""Unit tests for the causal-quality eval scoring (pure, no models)."""

import json

from scripts.causal_quality_eval import (
    degeneracy_flags,
    extract_fenced,
    is_valid_json,
    is_valid_python,
    main,
    normalized_match,
    repeated_ngram_rate,
)


def test_extract_fenced():
    assert extract_fenced("pre ```json\n{\"a\":1}\n``` post").strip() == '{"a":1}'
    assert extract_fenced("no fence here") == "no fence here"


def test_normalized_match_ignores_whitespace_and_fences():
    a = '```json\n{\n  "x": 1\n}\n```'
    b = '```json\n{"x": 1}\n```'
    assert normalized_match(a, b)
    assert not normalized_match(a, '```json\n{"x": 2}\n```')
    assert not normalized_match("", "")  # empty never matches


def test_json_and_python_validity():
    assert is_valid_json('```json\n{"a": [1,2,3]}\n```')
    assert not is_valid_json('```json\n{bad}\n```')
    assert is_valid_python("```python\ndef f(x):\n    return x+1\n```")
    assert not is_valid_python("```python\ndef f(x)\n    return\n```")  # syntax error


def test_repeated_ngram_rate():
    assert repeated_ngram_rate("a b c d e") == 0.0
    assert repeated_ngram_rate("ha ha ha ha ha ha", n=2) > 0.5  # repetition loop


def test_degeneracy_flags():
    assert "empty" in degeneracy_flags("   ", 0, False, False, 50)
    # causal-specific run-on: causal capped while gemma4 self-terminated
    assert "causal_specific_runon" in degeneracy_flags("text", 512, True, False, 50)
    # BOTH capped = long answer on a long prompt, NOT degeneracy
    assert degeneracy_flags("text", 512, True, True, 600) == []
    assert degeneracy_flags("a coherent short answer here", 30, False, False, 35) == []


def test_eval_end_to_end(tmp_path):
    gen_dir = tmp_path / "gen"
    gen_dir.mkdir()
    rows = [
        {"domain": "structured", "id": "s1", "prompt": "p", "causal": '```json\n{"a": 1}\n```',
         "gemma4": '```json\n{"a":1}\n```', "causal_ntok": 8, "causal_truncated": False, "gemma4_ntok": 7},
        {"domain": "code", "id": "c1", "prompt": "p", "causal": "```python\nx=1\n```",
         "gemma4": "```python\nx = 1\n```", "causal_ntok": 5, "causal_truncated": False, "gemma4_ntok": 6},
    ]
    (gen_dir / "generations.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    rc = main(["--gen", str(gen_dir), "--results-dir", str(tmp_path / "out"), "--tag", "t"])
    assert rc == 0
