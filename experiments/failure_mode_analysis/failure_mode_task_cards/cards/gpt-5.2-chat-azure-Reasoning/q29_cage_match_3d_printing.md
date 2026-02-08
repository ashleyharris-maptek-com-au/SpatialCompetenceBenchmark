# Task q29: Cage match. Can LLMs design interlocking parts for 3D printing?
- Source file: `29.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Evaluate end-to-end fabrication-aware geometric design: generate printable part artifacts that assemble correctly and satisfy dimensional/mechanical constraints.

## Output Contract
- Return JSON with `reasoning` and `parts`.
- Each part: `fileContents`, `fileType`, `transform` (16 numbers).
- Exactly 10 parts are required by the grader.
- Supported `fileType` values are: `stl`, `openscad`, `python generating openscad`, `python generating stl`.

## Hard Constraints (Verifier-Checked)
- Part count and file type validity.
- Artifact generation success and non-empty geometry.
- Watertight/manifold/self-intersection checks.
- Printability checks (build volume, bed contact, overhang constraints).
- Assembly checks (intersections, rod pass-through, support by rods).
- Dimensional checks (bar thickness and spacing constraints).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Answer did not contain a 'parts' key.` | Missing required payload | `Evasion`, `Trivialized` |
| `Answer contained too many parts...` / `Answer contained too few parts...` / `Expected 10 parts, got ...` | Part-count contract failure | `Trivialized`, `Evasion` |
| `Unknown file type '...'` / generator failures | Output not executable as artifact | `Trivialized`, `Runaway` |
| `not watertight` / `non-manifold` | Geometry validity failed | `Local-Only` |
| `intersects with part ...` / rod-fit/gap/thickness failures | Global assembly constraints failed | `Local-Only`, `Near-Miss` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing `parts` or unusable artifact payload.
- `Trivialized / Misframed`: Ignores core manufacturing/assembly contract (wrong part count/types).
- `Runaway Overthinking`: COT shows spiraling design that produces diverse error types (format AND assembly AND tolerance failures).
- `Local-Only (Global Constraint Integration Failure)`: Individual parts may parse but assembled system fails constraints.
- `Near-Miss Edge Case`: One tolerance-level issue (gap/thickness/clearance) in an otherwise valid build.

## Judge Input Bundle
1. Prompt with cage/print constraints.
2. Raw output.
3. Parsed parts metadata.
4. Verifier messages across geometry/printability/assembly.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q29 with one failure mode.
Prioritize executable artifact and assembled-constraint checks over prose quality.
Return JSON: failure_mode, confidence, justification.
```
