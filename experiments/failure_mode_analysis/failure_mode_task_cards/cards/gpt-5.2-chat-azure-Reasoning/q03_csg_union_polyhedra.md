# Task q03: CSG Union of Polyhedra
- Source file: `3.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Evaluate whether the model can output a single valid polyhedron representing the exact constructive-solid-geometry union of described primitives.

## Output Contract
- Return JSON object with `polyhedron`.
- `polyhedron.vertex` is list of `{xyz:[x,y,z]}`.
- `polyhedron.faces` is list of `{vertex:[indices...]}`.

## Hard Constraints (Verifier-Checked)
- Output must represent one union result, not disjoint primitive list.
- Mesh must be topologically valid (watertight/oriented/manifold under verifier) with consistent winding; internal/self-crossing geometry is disallowed by prompt and commonly triggers early rejection.
- Geometry must match target union.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Edge ... appears twice ... inconsistent winding` | Mesh orientation/manifold violation | `Local-Only` |
| `Edge ... is only used by one face - mesh is not watertight (boundary edge)` | Open boundary (non-watertight mesh) | `Local-Only` |
| `Edge ... is used by ... faces - non-manifold geometry` | Non-manifold adjacency | `Local-Only` |
| `Polyhedron has zero volume (degenerate or flat)` | Degenerate/invalid solid | `Trivialized / Misframed`, `Local-Only` |
| `Face ... is non-planar: ...` / `Face ... is degenerate ...` | Invalid face geometry | `Local-Only`, `Near-Miss` |
| `Missing 'polyhedron' in result` / `Polyhedron missing 'vertex' or 'faces'` | Output missing required fields | `Evasion / Forfeit`, `Trivialized / Misframed` |
| `Vertex ... missing 'xyz' field` / `Vertex ... has non-numeric coordinates ...` | Vertex schema/type failure | `Trivialized / Misframed` |
| `Face ... has invalid vertex index ...` / `Face ... vertex ... is not an integer ...` | Face index/schema failure | `Trivialized / Misframed`, `Local-Only` |
| `Result Volume:` / `Intersection Volume:` / `Difference Volume:` | Geometric mismatch vs reference union (volume-difference scoring) | `Local-Only`, `Near-Miss` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing/empty `polyhedron`.
- `Trivialized / Misframed`: Returns a primitive or partial shape instead of full union.
- `Runaway Overthinking`: Unnecessarily complex mesh with redundant/internal geometry.
- `Local-Only (Global Constraint Integration Failure)`: Local faces seem plausible but global topology or volume is wrong.
- `Near-Miss Edge Case`: Single small topology defect with close overall union.

## Judge Input Bundle
1. Exact union prompt for subpass.
2. Raw output.
3. Parsed polyhedron object.
4. Verifier text including topology and volume diagnostics.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q03 with one failure mode. Prioritize verifier topology/volume signals over stylistic output quality.
Return JSON: failure_mode, confidence, justification.
```
