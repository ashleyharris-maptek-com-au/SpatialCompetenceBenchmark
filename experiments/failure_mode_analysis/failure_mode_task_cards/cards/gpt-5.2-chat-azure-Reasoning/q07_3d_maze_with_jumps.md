# Task q07: 3D maze - solution requires jumping over gaps
- Source file: `7.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Measure structured generation under global path constraints: build a valid ASCII maze with a unique solution requiring jumps and sufficient path complexity.

## Output Contract
- Return plain maze text only.
- Exactly `size` rows and `size` columns.
- Allowed characters: digits `0-9`, `A`, `B`.

## Hard Constraints (Verifier-Checked)
- Exactly one `A` and one `B`.
- Valid grid shape and characters.
- Elevation usage distribution cap.
- Exactly one valid path from A to B.
- Path coverage minimum and jump-count minimum.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Maze must have exactly one A and one B` | Core format invalid | `Evasion`, `Trivialized` |
| `Maze must have exactly {size} rows` / `Maze must have exactly {size} columns` | Dimensional contract failure | `Near-Miss`, `Trivialized` |
| `Maze must have all rows the same width` | Non-rectangular grid (ragged rows) | `Near-Miss`, `Trivialized` |
| `Invalid character in maze: X` | Output contains characters outside `0-9`, `A`, `B` | `Trivialized`, `Near-Miss` |
| `Elevation H occupies more than 30% of the grid` | Elevation distribution cap violated | `Near-Miss`, `Local-Only` |
| `No valid path from A to B` | Maze is unsolvable under walk/jump rules | `Local-Only`, `Near-Miss` |
| `Multiple paths exist` | Global uniqueness failed | `Local-Only` |
| `Path visits only ... of cells (required: 20%)` | Path coverage minimum not achieved | `Near-Miss`, `Local-Only` |
| `Path has N jumps, but at least M required` | Complexity objective failed | `Near-Miss`, `Local-Only` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Non-maze answer or empty output.
- `Trivialized / Misframed`: Valid-looking maze that ignores jump/uniqueness requirements.
- `Runaway Overthinking`: COT shows spiraling maze design that produces diverse error types (connectivity AND uniqueness AND jump violations).
- `Local-Only (Global Constraint Integration Failure)`: Local traversability present but global uniqueness/coverage fails.
- `Near-Miss Edge Case`: Single dimensional or jump threshold miss.

## Judge Input Bundle
1. Prompt with size and jump requirement.
2. Raw maze output.
3. Parsed maze and path diagnostics.
4. Verifier explanation.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q07 with one failure mode.
Use uniqueness/jump/path-coverage checks as primary signal.
Return JSON: failure_mode, confidence, justification.
```
