# Task q53: VGB3 - Topology Edge Tasks: Classify Behaviour
- Source file: `53.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Assess symbolic classification of topology behavior classes (`known behaviour`, `three domains meeting`, `ambiguous`) across ordering variants.

## Output Contract
- Return object with `labels`.
- `labels` is list of allowed enum strings only.

## Hard Constraints (Verifier-Checked)
- Enum membership for every label.
- Exact comparison with curated expected labels.
- Record-wise ordering alignment.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `missing: [...]` | Indices of cases where predicted labels do not match ground truth | `Local-Only`, `Near-Miss` |
| `errors: [...]` | Parse/validation errors (e.g. `parse_failure`, `length_mismatch`, invalid label string) | `Trivialized`, `Evasion` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing `labels` output.
- `Trivialized / Misframed`: Uses labels outside allowed enum or wrong task form.
- `Runaway Overthinking`: COT shows spiraling classification reasoning that produces diverse error types (invalid labels AND wrong format AND mismatched counts).
- `Local-Only (Global Constraint Integration Failure)`: Multiple classification mismatches.
- `Near-Miss Edge Case`: One label mismatch in otherwise correct sequence.

## Judge Input Bundle
1. Prompt with cases and label definitions.
2. Raw output.
3. Parsed `labels`.
4. Verifier diff object.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q53 with one failure mode.
Use enum validity and diff mismatch count as key evidence.
Return JSON: failure_mode, confidence, justification.
```
