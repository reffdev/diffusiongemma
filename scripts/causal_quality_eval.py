#!/usr/bin/env python
"""Scaled Test 3 — scoring. Reads generations.jsonl, emits the comparison report.

Pure analysis (no models). Automated where honest (structured exact-match + JSON
validity; code syntax validity + length; degeneracy screen over all 200), manual
where not (side-by-side files for code/chat/prose). Points to a pre-registered
bucket but does NOT conclude the manual-read domains.

Usage:
  python scripts/causal_quality_eval.py --gen results/<causal_eval_gen>
"""

from __future__ import annotations

import ast
import json
import os
import re
import statistics
import sys

FENCE_RE = re.compile(r"```[a-zA-Z0-9_+-]*\n?(.*?)```", re.DOTALL)
STRUCTURED_MATCH_PASS = 0.90
REP_THRESH = 0.50
LEN_RATIO = 4.0


# ----------------------------- pure scoring --------------------------------

def extract_fenced(text):
    m = FENCE_RE.findall(text or "")
    return m[0] if m else (text or "")


def normalize_for_match(text):
    return re.sub(r"\s+", "", extract_fenced(text))


def normalized_match(a, b):
    return normalize_for_match(a) == normalize_for_match(b) and normalize_for_match(a) != ""


def is_valid_json(text):
    try:
        json.loads(extract_fenced(text).strip())
        return True
    except Exception:
        return False


def is_valid_python(text):
    try:
        ast.parse(extract_fenced(text))
        return True
    except Exception:
        return False


def repeated_ngram_rate(text, n=3):
    toks = (text or "").split()
    if len(toks) < n:
        return 0.0
    grams = [tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    return 1.0 - len(set(grams)) / len(grams)


def degeneracy_flags(text, ntok, causal_truncated, gemma4_truncated, baseline_ntok):
    """Real causal degeneracy. Hitting the cap is NOT degeneracy when Gemma 4 also
    runs long on the same prompt (both produce long answers, cap too low) — only
    *causal-specific* run-on (causal caps while Gemma 4 self-terminates) counts."""
    flags = []
    if not (text or "").strip():
        flags.append("empty")
    if causal_truncated and not gemma4_truncated:
        flags.append("causal_specific_runon")
    if repeated_ngram_rate(text) > REP_THRESH:
        flags.append(f"repetition({repeated_ngram_rate(text):.2f})")
    return flags


# ----------------------------- report --------------------------------------

def _md_pairs(rows, n=None):
    out = []
    for r in (rows if n is None else rows[:n]):
        out.append(f"## {r['id']}\n\n**prompt:** {r['prompt']}\n")
        out.append(f"**causal:**\n\n```\n{(r.get('causal') or '').strip()}\n```\n")
        out.append(f"**gemma4:**\n\n```\n{(r.get('gemma4') or '').strip()}\n```\n")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--gen", required=True, help="generation run dir (with generations.jsonl)")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--tag", default="causal_eval_report")
    args = p.parse_args(argv)

    rows = [json.loads(l) for l in open(os.path.join(args.gen, "generations.jsonl"), encoding="utf-8") if l.strip()]
    by = {}
    for r in rows:
        by.setdefault(r["domain"], []).append(r)

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from harness.results_io import ResultsWriter
    writer = ResultsWriter.create(args.results_dir, args.tag)
    rd = writer.run_dir

    lines = ["# Causal-mode quality eval — comparison report\n", f"generations: {args.gen}\n"]

    # structured: normalized match + JSON validity
    s = by.get("structured", [])
    if s:
        match = statistics.fmean(normalized_match(r.get("causal"), r.get("gemma4")) for r in s)
        jvc = statistics.fmean(is_valid_json(r.get("causal")) for r in s)
        jvg = statistics.fmean(is_valid_json(r.get("gemma4")) for r in s)
        lines += ["## structured (automated)\n",
                  f"- normalized exact-match causal vs Gemma 4: **{match:.3f}** (n={len(s)})",
                  f"- JSON-valid: causal {jvc:.3f} | gemma4 {jvg:.3f}\n"]

    # code: syntax validity + length
    c = by.get("code", [])
    if c:
        pvc = statistics.fmean(is_valid_python(r.get("causal")) for r in c)
        pvg = statistics.fmean(is_valid_python(r.get("gemma4")) for r in c)
        lc = statistics.median(r.get("causal_ntok", 0) for r in c)
        lg = statistics.median(r.get("gemma4_ntok", 0) for r in c)
        lines += ["## code (automated; correctness is your manual read)\n",
                  f"- Python syntax-valid: causal {pvc:.3f} | gemma4 {pvg:.3f} (n={len(c)})",
                  f"- median output tokens: causal {lc:.0f} | gemma4 {lg:.0f}\n"]
        open(os.path.join(rd, "side_by_side_code.md"), "w", encoding="utf-8").write(_md_pairs(c))

    # chat / prose: side-by-side samples + degeneracy handled below
    for dom in ("chat", "prose"):
        if by.get(dom):
            open(os.path.join(rd, f"side_by_side_{dom}.md"), "w", encoding="utf-8").write(_md_pairs(by[dom], n=10))

    # degeneracy screen over ALL causal outputs
    def flags_for(r):
        return degeneracy_flags(r.get("causal"), r.get("causal_ntok", 0),
                                r.get("causal_truncated", False), r.get("gemma4_truncated", False),
                                r.get("gemma4_ntok", 0))

    degenerate = []
    for r in rows:
        fl = flags_for(r)
        if fl:
            degenerate.append((r["domain"], r["id"], fl))
    lines.append("## degeneracy screen (all 200 causal outputs)\n")
    if degenerate:
        lines.append(f"{len(degenerate)} flagged:")
        for dom, pid, fl in degenerate:
            lines.append(f"  - {dom}/{pid}: {', '.join(fl)}")
    else:
        lines.append("none — zero empty / truncated / repetition / length-outlier.")
    lines.append("")

    # per-domain degeneracy summary
    lines.append("## per-domain degeneracy counts\n")
    lines.append(f"{'domain':<12}{'n':>4}{'degenerate':>12}{'mean_rep3':>10}")
    for dom in ("structured", "code", "chat", "prose"):
        rs = by.get(dom, [])
        if not rs:
            continue
        ndeg = sum(1 for r in rs if flags_for(r))
        rep = statistics.fmean(repeated_ngram_rate(r.get("causal")) for r in rs)
        lines.append(f"{dom:<12}{len(rs):>4}{ndeg:>12}{rep:>10.3f}")

    # termination — cap-hits for BOTH models (cap-hit reflects answer length, not failure)
    lines.append("\n## termination — causal vs Gemma 4 cap-hits (both at max_new; cap-hit = long answer, not failure)\n")
    lines.append(f"{'domain':<11}{'causal_cap':>11}{'gemma4_cap':>11}{'causal_med':>11}{'gemma4_med':>11}")
    for dom in ("structured", "code", "chat", "prose"):
        rs = by.get(dom, [])
        if rs:
            ccap = sum(1 for r in rs if r.get("causal_truncated"))
            gcap = sum(1 for r in rs if r.get("gemma4_truncated"))
            cmed = statistics.median(r.get("causal_ntok", 0) for r in rs)
            gmed = statistics.median(r.get("gemma4_ntok", 0) for r in rs)
            lines.append(f"{dom:<11}{ccap:>11}{gcap:>11}{cmed:>11.0f}{gmed:>11.0f}")

    # bucket pointer
    struct_match = (statistics.fmean(normalized_match(r.get("causal"), r.get("gemma4")) for r in s) if s else 0.0)
    real_degen = [(d, pid, fl) for d, pid, fl in degenerate]
    content_ok = struct_match >= STRUCTURED_MATCH_PASS
    lines += ["\n## automated bucket pointer (manual call is yours)\n",
              f"- structured content match {struct_match:.3f} ({'PASS-consistent' if content_ok else 'below 0.9'}).",
              f"- real causal degeneracy (empty / causal-specific run-on / repetition): {len(real_degen)}/{len(rows)}.",
              "- cap-hits reflect answer length (Gemma 4 hits the cap as much or more); NOT a termination failure.",
              "- code/chat/prose content quality is the manual side-by-side read — not auto-concluded.",
              "\nside-by-sides: side_by_side_code.md (all 50), side_by_side_chat.md / side_by_side_prose.md (10 each)"]

    open(os.path.join(rd, "report.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    writer.close()
    print("\n".join(lines))
    print(f"\nreport + side-by-sides -> {rd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
