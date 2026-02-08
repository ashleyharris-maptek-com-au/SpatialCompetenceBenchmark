# Task q04: Tetrahedron Shadow Coverage
- Source file: `4.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Assess transformed-primitive composition: place tetrahedra so their projected shadow covers a target region while keeping transforms valid and solids non-intersecting. (Rotation is applied about the global origin *before* translation; the origin is not the tetrahedron centroid.)

## Output Contract
- Return JSON with `tetrahedrons`.
- Each element has numeric `x,y,z,q0,q1,q2,q3`.
- Quaternion is interpreted as orientation before translation.

## Hard Constraints (Verifier-Checked)
- Quaternion normalization tolerance.
- Pairwise intersection checks between tetrahedra.
- Coverage score against target projection (via volume-difference between projected shadow and a thin reference extrusion).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Quaternion is not normalised. 75% penalty.` | Transform validity failure | `Near-Miss`, `Local-Only` |
| `Tetrahedrons i and j intersect. 50% penalty.` | Global assembly invalid | `Local-Only` |
| `Result Volume:` / `Intersection Volume:` / `Difference Volume:` | Shadow coverage mismatch vs reference target | `Local-Only`, `Near-Miss` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing or malformed tetrahedron list.
- `Trivialized / Misframed`: Tiny/simple placement that does not attempt target coverage.
- `Runaway Overthinking`: Excessive tetrahedra causing avoidable collisions.
- `Local-Only (Global Constraint Integration Failure)`: Pieces locally placed but global coverage/intersection checks fail.
- `Near-Miss Edge Case`: One normalization/intersection issue with otherwise close coverage.

## Judge Input Bundle
1. Prompt for current shape target.
2. Raw model output.
3. Parsed transform list.
4. Verifier penalties/metrics.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q04 with one failure mode.
Treat quaternion/intersection penalties as primary evidence, then coverage metrics.
Return JSON: failure_mode, confidence, justification.
```
