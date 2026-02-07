# Task q09: Hamiltonian Loop on Grid
- Source file: `9.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Assess whether the model can produce a complete closed Hamiltonian loop visiting every allowed cell exactly once on constrained grids.

## Output Contract
- Return JSON with `steps`.
- Each step has `xy` coordinate pair.
- Total steps must equal the number of valid (non-blocked) cells.

## Hard Constraints (Verifier-Checked)
- Exact step count.
- Bounds and blocked-cell validity.
- Side-adjacent movement only.
- No repeated cells.
- Final step adjacent to first (loop closure).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `No steps provided` | No attempt artifact | `Evasion / Forfeit` |
| `Expected N steps, got M` | Incomplete/oversized loop | `Trivialized`, `Near-Miss` |
| `Out of bounds!` | Step goes outside grid bounds | `Near-Miss`, `Local-Only` |
| `You visited an invalid cell [x, y]!` | Step enters a blocked/disallowed cell | `Near-Miss`, `Local-Only` |
| `didn't step side-adjacent` | Invalid movement transition | `Near-Miss`, `Local-Only` |
| `visited (x, y) more than once!` | Loop invalid due to reuse | `Local-Only` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Empty `steps` or explicit refusal-style output.
- `Trivialized / Misframed`: Short path that does not attempt full Hamiltonian requirement.
- `Runaway Overthinking`: Long narrative with still-invalid path artifact.
- `Local-Only (Global Constraint Integration Failure)`: Many locally valid moves but full-cycle constraints fail.
- `Near-Miss Edge Case`: Off-by-one step count or one bad transition.

## Judge Input Bundle
1. Prompt with grid/block mask.
2. Raw output.
3. Parsed `steps`.
4. Verifier diagnostics.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q09 with one failure mode.
Prioritize count/adjacency/repeat/closure verifier evidence over prose.
Return JSON: failure_mode, confidence, justification.
```
