# Task q30: What's the largest prime number you can 3D print without supports?
- Source file: `30.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Test constrained combinatorial reasoning: produce a long prime digit stack respecting printable orientation transitions and anti-repetition rules.

## Output Contract
- Return JSON with `reasoning` and `numberSequence`.
- `numberSequence` entries include `digit` and `orientation`.
- Sequence order defines stack from bottom to top.

## Hard Constraints (Verifier-Checked)
- Non-empty sequence.
- No repeated 3-digit tuple windows.
- Orientation validity (no forbidden overhang configurations).
- Pairwise stackability of adjacent digits.
- Resulting number must be prime.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Empty number` | No attempt artifact | `Evasion / Forfeit` |
| `contains a sequence of 3 digits repeated more than once` | Core uniqueness rule broken | `Near-Miss`, `Local-Only` |
| `Digit ... has overhangs` | Orientation invalid | `Local-Only` |
| `cannot be printed on top of ...` | Transition stackability invalid | `Local-Only` |
| `N is not prime` | Numeric objective failure | `Near-Miss`, `Trivialized` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Empty sequence or no parseable structured answer.
- `Trivialized / Misframed`: Very short obvious primes without meaningful optimization attempt.
- `Runaway Overthinking`: COT shows spiraling number-theory reasoning that produces diverse error types (primality AND transition AND length failures).
- `Local-Only (Global Constraint Integration Failure)`: Local digit choices valid but full stackability/primality rules fail.
- `Near-Miss Edge Case`: One tuple-repeat/primality/transition issue in otherwise coherent sequence.

## Judge Input Bundle
1. Full prompt and rule clarifications.
2. Raw output.
3. Parsed `numberSequence`.
4. Verifier violations and score rationale.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q30 with one failure mode.
Use stackability + tuple-repeat + primality checks as decisive evidence.
Return JSON: failure_mode, confidence, justification.
```

