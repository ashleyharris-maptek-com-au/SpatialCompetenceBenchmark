# Task q54: VGB4 - Half Subdivision Neighbours
- Source file: `54.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Test exact discrete neighbor inference in recursively subdivided spaces using bitstring leaf identifiers.

## Output Contract
- Prompted format is a comma-separated list of leaf labels (quotes optional); the prompt may also request a leading `<thinking>...</thinking>` block (which the parser strips).
- The grader accepts either a raw list / comma-separated sequence *or* an object with `neighbors`.
- Neighbor labels are bitstring leaf identifiers (strings of `0/1`, with `""` allowed for the root in some cases).

## Hard Constraints (Verifier-Checked)
- Neighbor label schema.
- Exact expected neighbor set match.
- Order-independent comparison; duplicates are invalid.
- Handles varied axis-ordering/task variants through curated dataset.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `missing: [...]` | Required neighbors omitted | `Local-Only`, `Near-Miss` |
| `extra: [...]` | Non-neighbors included | `Local-Only`, `Near-Miss` |
| `errors: [...]` | Invalid label format/structure | `Trivialized`, `Evasion` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing `neighbors` payload.
- `Trivialized / Misframed`: Non-bitstring or unrelated output form.
- `Runaway Overthinking`: Complex derivation with malformed neighbor identifiers.
- `Local-Only (Global Constraint Integration Failure)`: Broad neighbor-set mismatch.
- `Near-Miss Edge Case`: Single neighbor missing/extra.

## Judge Input Bundle
1. Prompt (subdivision tree + target leaf).
2. Raw output.
3. Parsed `neighbors`.
4. Verifier diff.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q54 with one failure mode.
Prioritize schema validity and neighbor-set diff size.
Return JSON: failure_mode, confidence, justification.
```
