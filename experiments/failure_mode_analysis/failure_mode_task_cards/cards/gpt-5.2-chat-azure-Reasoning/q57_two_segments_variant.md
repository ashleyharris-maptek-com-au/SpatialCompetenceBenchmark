# Task q57: VGB5 - Two Segments
- Source file: `57.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Assess geometric partition reasoning by placing exactly two boundary-to-boundary segments that induce required polygon class counts.

## Output Contract
- Prompted format is typically a bare list describing exactly two segments (often preceded by a `<thinking>...</thinking>` block, which the parser strips).
- The grader accepts either a raw list *or* an object with `segments`.
- Exactly two segments.
- Each segment has two endpoints, each endpoint has two numeric coordinates.

## Hard Constraints (Verifier-Checked)
- Segment payload structure and cardinality.
- Endpoint bounds and geometric validity.
- Partitioned shape counts must match expected classes.
- Verifier returns `errors` plus `details` (expected vs observed polygon counts and the square corners used).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `errors: ['parse_failure']` | Could not parse into exactly two segments | `Evasion`, `Trivialized` |
| `errors: ['degenerate_segment']` | A segment collapses to a point after normalization | `Near-Miss`, `Local-Only` |
| `errors: ['point_off_grid']` | Endpoint violates the prompt’s discrete coordinate grid | `Near-Miss`, `Local-Only` |
| `errors: ['point_out_of_bounds']` | Endpoint violates geometric domain | `Near-Miss`, `Local-Only` |
| `errors: ['point_not_on_boundary']` | Endpoint is not on the square boundary | `Near-Miss`, `Local-Only` |
| `errors: ['segment_on_boundary_edge']` | Segment lies along the square edge (disallowed) | `Near-Miss`, `Trivialized` |
| `errors: ['counts_mismatch']` | Produced partition classes are wrong | `Local-Only` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing or empty `segments`.
- `Trivialized / Misframed`: Segments ignore partition-count objective.
- `Runaway Overthinking`: Complex coordinates without satisfying simple two-segment constraints.
- `Local-Only (Global Constraint Integration Failure)`: Endpoints/segments local-valid but global class counts fail.
- `Near-Miss Edge Case`: Single endpoint/grid/boundary error in an otherwise plausible construction.

## Judge Input Bundle
1. Prompt with square corners and target class counts.
2. Raw output.
3. Parsed `segments`.
4. Verifier diff and error details.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q57 with one failure mode.
Prioritize count-mismatch and bounds errors from verifier.
Return JSON: failure_mode, confidence, justification.
```
