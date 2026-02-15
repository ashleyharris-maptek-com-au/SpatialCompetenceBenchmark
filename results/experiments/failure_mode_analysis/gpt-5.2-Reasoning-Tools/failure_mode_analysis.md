# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 101
- Judged rows: 101
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 44 | 43.56% |
| Trivialized / Misframed | 3 | 2.97% |
| Runaway Overthinking | 4 | 3.96% |
| Local-Only (Global Constraint Integration Failure) | 29 | 28.71% |
| Near-Miss Edge Case | 21 | 20.79% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q55 - VGB6 — Delaunay Triangulation | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 7 | 7 | 0 | 100.00% |
| Q51 - VGB1 — Topology Enumeration | 7 | 7 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 7 | 7 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 6 | 6 | 0 | 100.00% |
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 6 | 6 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 5 | 5 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 5 | 5 | 0 | 100.00% |
| Q16 - Pack rectangular prisms | 5 | 5 | 0 | 100.00% |
| Q6 - Voxel Grid Projection - shadow coverage and no symmetries | 4 | 4 | 0 | 100.00% |
| Q54 - VGB4 — Half Subdivision Neighbours | 4 | 4 | 0 | 100.00% |
| Q57 - VGB5 — Two Segments | 3 | 3 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.0
- Confidence: 0.95
- Verifier signal: Content violation: Invalid prompt: your prompt was flagged as potentially violating our usage policy. Please try again with a different prompt: https://platform.openai.com/docs/guides/reasoning#advice-on-prompting
- Judge justification: No usable bricks assembly was produced; the run terminated with a content/prompt violation and returned no valid JSON with a bricks list, matching a forfeit condition.

### Trivialized / Misframed
- Task: Q3 - CSG Union of Polyhedra (subpass 8)
- Score: 0.0
- Confidence: 0.9
- Verifier signal: Result Volume: 1288.90 Reference Volume: 0.00 Intersection Volume: 1000.30 Difference Volume: 853.07 OpenSCAD error for reference.scad: stderr: CGAL error: assertion violation! Expression : File : /Users/distiller/lib...
- Judge justification: The model returned the cube and tetrahedron as separate closed meshes within one JSON object rather than computing their constructive-solid-geometry union. This misframes the task by listing primitives instead of prod...

### Runaway Overthinking
- Task: Q3 - CSG Union of Polyhedra (subpass 11)
- Score: 0.0
- Confidence: 0.88
- Verifier signal: Early failure: 77 winding error(s): Edge (104, 48) appears twice in same direction (faces 57 and 62); Edge (56, 30) appears twice in same direction (faces 59 and 70); Edge (56, 55) appears twice in same direction (fac...
- Judge justification: The chain-of-thought shows extensive, spiraling reasoning and ad hoc geometry construction. The verifier reports many diverse error types simultaneously (winding errors, boundary edges, and non-manifold edges), satisf...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 1)
- Score: 0.0
- Confidence: 0.85
- Verifier signal: Brick {'Centroid': [-8.0, 0.0, 62.4], 'RotationDegrees': 0} is floating (not supported from below or held from above)
- Judge justification: A large, detailed assembly was provided, but the verifier flagged an unsupported (floating) brick, indicating failure to satisfy global buildability/support constraints despite locally plausible placements. Errors are...

### Near-Miss Edge Case
- Task: Q4 - Tetrahedron Shadow Coverage (subpass 16)
- Score: 0.44904768526084593
- Confidence: 0.7
- Verifier signal: Result Volume: 0.70 Reference Volume: 0.61 Intersection Volume: 0.61 Difference Volume: 0.06 Tetrahedrons 0 and 1 intersect. 50% penalty.
- Judge justification: Coverage is very close to the reference (Difference Volume 0.06) with a single reported intersection between tetrahedrons 0 and 1. This matches a near-miss: one intersection issue with otherwise strong coverage.
