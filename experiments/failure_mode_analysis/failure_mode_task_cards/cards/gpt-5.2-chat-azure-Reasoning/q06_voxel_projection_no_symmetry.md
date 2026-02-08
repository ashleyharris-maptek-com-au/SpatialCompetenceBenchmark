# Task q06: Voxel Grid Projection - shadow coverage and no symmetries
- Source file: `6.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Judge whether the model can satisfy multiple coupled global constraints in a voxel construction: exact count, complete projections, and no trivial symmetry.

## Output Contract
- Return JSON with `voxels`.
- Each voxel must resolve to integer `x,y,z` coordinates in bounds.
- Accepted encodings are permissive, but parsed result is canonical coordinates.

## Hard Constraints (Verifier-Checked)
- Exact voxel count for subpass.
- Coordinate bounds and uniqueness.
- Full XY/XZ/YZ projection coverage with no holes.
- No trivial rotational/reflection symmetry.
- Subpass-specific extra constraints (forbidden digit in coordinate sums, where applicable).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `voxels must be a list` | Wrong top-level type for voxel payload | `Evasion`, `Trivialized` |
| `Invalid voxel entry: ...` | Unparseable voxel encoding or non-integer/out-of-bounds coordinate | `Trivialized`, `Near-Miss` |
| `Voxel (...) has a coordinate sum ... with a 7 in it` | Subpass-specific extra constraint violated | `Near-Miss`, `Local-Only` |
| `Incorrect voxel count N, expected M` | Cardinality target not met | `Trivialized`, `Near-Miss` |
| `Duplicate voxel coordinates detected. Voxel (...) is repeated.` | Output integrity failure | `Near-Miss`, `Local-Only` |
| `XY projection has holes or gaps` | Global coverage failure (XY plane) | `Local-Only` |
| `XZ projection has holes or gaps` | Global coverage failure (XZ plane) | `Local-Only` |
| `YZ projection has holes or gaps` | Global coverage failure (YZ plane) | `Local-Only` |
| `Shape has a trivial symmetry (rotation/reflection)` | Anti-symmetry objective failed | `Local-Only` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Empty or unparseable voxel output.
- `Trivialized / Misframed`: Simple shape that ignores anti-symmetry/projection goals.
- `Runaway Overthinking`: COT shows spiraling coordinate derivation that produces diverse error types (projection AND symmetry AND count failures).
- `Local-Only (Global Constraint Integration Failure)`: Some constraints pass but projections/symmetry fail globally.
- `Near-Miss Edge Case`: One count, one duplicate, or one small projection defect.

## Judge Input Bundle
1. Exact prompt and subpass parameters (`N`, voxel target, extra rules).
2. Raw output.
3. Parsed voxel set.
4. Verifier failure string(s).
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q06 with one failure mode based on strict verifier constraints.
If failure is a single local defect, prefer Near-Miss; if multiple coupled constraints fail, prefer Local-Only.
Return JSON: failure_mode, confidence, justification.
```
