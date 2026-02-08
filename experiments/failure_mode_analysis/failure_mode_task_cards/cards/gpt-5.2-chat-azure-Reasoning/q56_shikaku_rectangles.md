# Task q56: VGB7 - Shikaku Rectangles
- Source file: `56.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Test exact puzzle partition reasoning: cover a grid with rectangles matching clue-area constraints and full coverage rules.

## Output Contract
- Prompted format is typically a bare list of rectangle bounds (often preceded by a `<thinking>...</thinking>` block, which the parser strips).
- The grader accepts either a raw list *or* an object with `rectangles`.
- `rectangles` is list of `[left, top, right, bottom]` integer bounds.

## Hard Constraints (Verifier-Checked)
- Rectangle schema validity.
- Full partition coverage with no invalid overlap/gaps.
- Exactly one clue per rectangle and rectangle area equals clue value.
- Curated expected result diff.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `errors: ['cell_..._uncovered']` | Coverage partition failed | `Local-Only` |
| `errors: ['box_..._clue_count_...']` | Clue assignment or area semantics failed | `Local-Only`, `Near-Miss` |
| `missing/extra` | Set-level mismatch vs expected | `Local-Only`, `Near-Miss` |
| Schema parse failures | Invalid rectangle payload | `Evasion`, `Trivialized` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing/empty `rectangles`.
- `Trivialized / Misframed`: Rectangles do not respect clue semantics.
- `Runaway Overthinking`: COT shows spiraling partition reasoning that produces diverse error types (coverage gaps AND clue mismatches AND overlaps).
- `Local-Only (Global Constraint Integration Failure)`: Local boxes plausible but global partition validity fails.
- `Near-Miss Edge Case`: One clue or one uncovered-cell defect.

## Judge Input Bundle
1. Prompt with grid clues.
2. Raw output.
3. Parsed `rectangles`.
4. Verifier diff and error list.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q56 with one failure mode.
Use clue-count and coverage errors as primary evidence.
Return JSON: failure_mode, confidence, justification.
```
