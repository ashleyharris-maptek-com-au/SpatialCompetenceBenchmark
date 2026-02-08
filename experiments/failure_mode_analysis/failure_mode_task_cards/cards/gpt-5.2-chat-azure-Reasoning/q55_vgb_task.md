# Task q55: VGB6 - Delaunay Triangulation
- Source file: `55.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Evaluate exact combinatorial geometry output: recover Delaunay triangulation triangles for curated point sets.

## Output Contract
- Prompted format is typically a bare list of triangle index triplets (often preceded by a `<thinking>...</thinking>` block, which the parser strips).
- The grader accepts either a raw list *or* an object with `triangles`.
- Each triangle is an index triplet `[i, j, k]` (integers).

## Hard Constraints (Verifier-Checked)
- Triangle triplet schema.
- Exact set equality with curated expected triangulation.
- Missing/extra/error diff reporting.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `missing: [...]` | Required Delaunay triangles omitted | `Local-Only`, `Near-Miss` |
| `extra: [...]` | Non-Delaunay triangles included | `Local-Only`, `Near-Miss` |
| `errors: [...]` | Schema or parse issue | `Trivialized`, `Evasion` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing or empty `triangles`.
- `Trivialized / Misframed`: Output not triangulation indices.
- `Runaway Overthinking`: Overspecified triangle sets with many extras.
- `Local-Only (Global Constraint Integration Failure)`: Several missing/extra triangles.
- `Near-Miss Edge Case`: One triangle difference.

## Judge Input Bundle
1. Prompt with points.
2. Raw output.
3. Parsed `triangles`.
4. Verifier diff.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q55 with one failure mode.
Use missing/extra triangle diffs as primary evidence.
Return JSON: failure_mode, confidence, justification.
```
