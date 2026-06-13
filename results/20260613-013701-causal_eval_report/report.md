# Causal-mode quality eval — comparison report

generations: results/20260613-013652-causal_eval_gen/

## structured (automated)

- normalized exact-match causal vs Gemma 4: **0.980** (n=50)
- JSON-valid: causal 0.860 | gemma4 0.860

## code (automated; correctness is your manual read)

- Python syntax-valid: causal 0.960 | gemma4 0.880 (n=50)
- median output tokens: causal 504 | gemma4 512

## degeneracy screen (all 200 causal outputs)

74 flagged:
  - code/code-003: ran_to_cap
  - code/code-007: ran_to_cap
  - code/code-013: ran_to_cap
  - code/code-018: ran_to_cap
  - code/code-019: ran_to_cap
  - code/code-021: ran_to_cap
  - code/code-022: ran_to_cap
  - code/code-023: ran_to_cap
  - code/code-024: ran_to_cap
  - code/code-028: ran_to_cap
  - code/code-029: ran_to_cap
  - code/code-030: ran_to_cap
  - code/code-036: ran_to_cap
  - code/code-038: ran_to_cap
  - code/code-039: ran_to_cap
  - code/code-040: ran_to_cap
  - code/code-042: ran_to_cap
  - code/code-044: ran_to_cap
  - code/code-046: ran_to_cap
  - code/code-048: ran_to_cap
  - code/code-049: ran_to_cap
  - code/code-050: ran_to_cap
  - chat/chat-001: ran_to_cap
  - chat/chat-003: ran_to_cap
  - chat/chat-005: ran_to_cap
  - chat/chat-006: ran_to_cap
  - chat/chat-008: ran_to_cap
  - chat/chat-009: ran_to_cap
  - chat/chat-011: ran_to_cap
  - chat/chat-012: ran_to_cap
  - chat/chat-013: ran_to_cap
  - chat/chat-015: ran_to_cap
  - chat/chat-016: ran_to_cap
  - chat/chat-017: ran_to_cap
  - chat/chat-018: ran_to_cap
  - chat/chat-019: ran_to_cap
  - chat/chat-020: ran_to_cap
  - chat/chat-022: ran_to_cap
  - chat/chat-023: ran_to_cap
  - chat/chat-024: ran_to_cap
  - chat/chat-026: ran_to_cap
  - chat/chat-027: ran_to_cap
  - chat/chat-028: ran_to_cap
  - chat/chat-029: ran_to_cap
  - chat/chat-030: ran_to_cap
  - chat/chat-031: ran_to_cap
  - chat/chat-034: ran_to_cap
  - chat/chat-035: ran_to_cap
  - chat/chat-036: ran_to_cap
  - chat/chat-038: ran_to_cap
  - chat/chat-039: ran_to_cap
  - chat/chat-040: ran_to_cap
  - chat/chat-042: ran_to_cap
  - chat/chat-043: ran_to_cap
  - chat/chat-044: ran_to_cap
  - chat/chat-045: ran_to_cap
  - chat/chat-046: ran_to_cap
  - chat/chat-047: ran_to_cap
  - chat/chat-048: ran_to_cap
  - chat/chat-049: ran_to_cap
  - prose/prose-006: ran_to_cap
  - prose/prose-008: ran_to_cap
  - prose/prose-013: ran_to_cap
  - prose/prose-023: ran_to_cap
  - prose/prose-026: ran_to_cap
  - prose/prose-030: ran_to_cap
  - prose/prose-032: ran_to_cap
  - prose/prose-034: ran_to_cap
  - prose/prose-037: ran_to_cap
  - prose/prose-039: ran_to_cap
  - prose/prose-040: ran_to_cap
  - prose/prose-041: ran_to_cap
  - prose/prose-042: ran_to_cap
  - prose/prose-049: ran_to_cap

## per-domain degeneracy counts

domain         n  degenerate mean_rep3
structured    50           0     0.032
code          50          22     0.052
chat          50          38     0.030
prose         50          14     0.005

## termination (standalone causal generation)

  structured : 0/50 causal outputs ran to the cap (no <eos> self-termination)
  code       : 22/50 causal outputs ran to the cap (no <eos> self-termination)
  chat       : 38/50 causal outputs ran to the cap (no <eos> self-termination)
  prose      : 14/50 causal outputs ran to the cap (no <eos> self-termination)

## automated bucket pointer (manual call is yours)

- CONTENT (extractable answers): structured match 0.980 (PASS-consistent); code syntax-validity + manual read pending.
- STANDALONE GENERATION: 74/200 ran to cap with no self-termination — if systematic, standalone-generation quality FAILs on termination regardless of content.
- NOTE: termination is irrelevant to the verifier role (teacher-forced); rung-1's loop use is unaffected. The 'Gemma-4-class' claim splits into content (maybe) vs standalone-gen (no).

side-by-sides for your manual read: side_by_side_code.md (all 50), side_by_side_chat.md / side_by_side_prose.md (10 each)
