# Task q12: Fit a loop into a square that's perimeter is smaller than the total length
- Source file: `12.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Evaluate constrained geometric synthesis: produce a closed polyline with unit segments that satisfies subpass-specific global rules (crossings, turns, centroid, hull, edge touching, etc.).

## Output Contract
- Return JSON with `points`.
- `points` is a list of `{x:number, y:number}`.
- Point count must equal the subpass pipe count.

## Hard Constraints (Verifier-Checked)
- Numeric point schema and minimum cardinality.
- In-bounds points within `[0, boundary]`.
- Every segment length (including closing segment) within tolerance around 1.
- No duplicate vertices; no illegal backtracking.
- Subpass preset constraints (crossing counts, turns, centroid box, hull area, edge touch, straight-run cap, etc.).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Validation failed: ...` | One or more hard constraints violated | `Local-Only`, `Near-Miss` |
| `Crossing detected` / crossing count mismatch | Topological global failure | `Local-Only` |
| `Segment length ... expected 1.0 ± 0.05` | Metric tolerance failure | `Near-Miss` |
| `Expected N points ... got M` | Contract/complexity mismatch | `Trivialized`, `Near-Miss` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing or invalid `points` structure.
- `Trivialized / Misframed`: Simple loop that ignores preset-specific constraints.
- `Runaway Overthinking`: COT shows the model spiraling on an overcomplicated construction strategy (e.g. analytically deriving exact tiling, multi-loop designs) that produces diverse, coupled error types (wrong point count AND bad lengths AND crossings simultaneously).
- `Local-Only (Global Constraint Integration Failure)`: Local step geometry works but global preset conditions fail.
- `Near-Miss Edge Case`: One boundary/length/count/touching miss in otherwise valid loop.

## Judge Input Bundle
1. Prompt including preset details for subpass.
2. Raw output.
3. Parsed points list.
4. Verifier failures and any structured diagnostics.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q12 with one failure mode using preset-aware verifier signals.
If many coupled checks fail, prefer Local-Only; if a single tolerance/count issue, prefer Near-Miss.
Return JSON: failure_mode, confidence, justification.
```

