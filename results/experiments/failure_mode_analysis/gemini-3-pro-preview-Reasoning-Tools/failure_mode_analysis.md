# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 96
- Judged rows: 96
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 31 | 32.29% |
| Trivialized / Misframed | 1 | 1.04% |
| Runaway Overthinking | 0 | 0.00% |
| Local-Only (Global Constraint Integration Failure) | 45 | 46.88% |
| Near-Miss Edge Case | 19 | 19.79% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 15 | 15 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 11 | 11 | 0 | 100.00% |
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 9 | 9 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 7 | 7 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 7 | 7 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 6 | 6 | 0 | 100.00% |
| Q51 - VGB1 — Topology Enumeration | 5 | 5 | 0 | 100.00% |
| Q23 - Fluid simulation | 3 | 3 | 0 | 100.00% |
| Q57 - VGB5 — Two Segments | 3 | 3 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 2 | 2 | 0 | 100.00% |
| Q9 - Hamiltonian Loop on Grid | 2 | 2 | 0 | 100.00% |
| Q16 - Pack rectangular prisms | 2 | 2 | 0 | 100.00% |
| Q52 - VGB2 — Topology Edge Tasks: Enumerate Edges | 2 | 2 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q9 - Hamiltonian Loop on Grid (subpass 8)
- Score: 0.0
- Confidence: 0.95
- Verifier signal: (none)
- Judge justification: The raw output is `{}` with no `steps` provided, so there is no path attempt to verify, matching the task-card definition of a forfeit-style/empty artifact.

### Trivialized / Misframed
- Task: Q12 - Fit a loop into a square that's perimeter is smaller than the total length (subpass 12)
- Score: 0.0
- Confidence: 0.72
- Verifier signal: Validation failed: 1. angle_range: Angle at vertex 1 is 180.0° (expected 60°-150°) @ {'vertex_index': 1} 2. angle_range: Angle at vertex 8 is 180.0° (expected 60°-150°) @ {'vertex_index': 8} 3. angle_range: Angle at v...
- Judge justification: The produced loop is essentially an axis-aligned grid walk with multiple collinear runs, violating the preset’s required angle bounds. Verifier reports several 180° angles (vertices 1, 8, 13, 18), indicating the const...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 1)
- Score: 0.0
- Confidence: 0.78
- Verifier signal: Result Volume: 904396.80 Reference Volume: 759985.50 Intersection Volume: 0.00 Difference Volume: 1051159.31 Error OpenSCAD error for result.scad: stderr: WARNING: Minkowski: Nef polyhedron converted from mesh is inva...
- Judge justification: The attempt provides a large brick list (so not a forfeit/trivial), but the verifier reports Intersection Volume = 0.00 with severe OpenSCAD/CGAL Minkowski failures and an empty top-level object, indicating the genera...

### Near-Miss Edge Case
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 4)
- Score: 0.32427940653548154
- Confidence: 0.67
- Verifier signal: Result Volume: 1514022.26 Reference Volume: 2882790.53 Intersection Volume: 1399781.70 Difference Volume: 1584284.92 Score was renormalised: 0.21 -> 0.32
- Judge justification: This run passes to volumetric scoring with a nonzero score (0.32) and substantial intersection volume, with no reported schema/buildability errors; the main signal is imperfect volume match (Difference Volume still la...
