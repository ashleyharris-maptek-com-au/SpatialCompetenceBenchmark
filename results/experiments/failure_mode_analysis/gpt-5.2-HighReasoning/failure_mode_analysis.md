# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 137
- Judged rows: 137
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 106 | 77.37% |
| Trivialized / Misframed | 1 | 0.73% |
| Runaway Overthinking | 1 | 0.73% |
| Local-Only (Global Constraint Integration Failure) | 29 | 21.17% |
| Near-Miss Edge Case | 0 | 0.00% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 21 | 21 | 0 | 100.00% |
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 19 | 19 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 12 | 12 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 9 | 9 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q51 - VGB1 — Topology Enumeration | 7 | 7 | 0 | 100.00% |
| Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials | 6 | 6 | 0 | 100.00% |
| Q16 - Pack rectangular prisms | 6 | 6 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 6 | 6 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 5 | 5 | 0 | 100.00% |
| Q9 - Hamiltonian Loop on Grid | 5 | 5 | 0 | 100.00% |
| Q6 - Voxel Grid Projection - shadow coverage and no symmetries | 4 | 4 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 3 | 3 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.0
- Confidence: 0.96
- Verifier signal: (none)
- Judge justification: The output is an empty JSON object with no `bricks` list, violating the output contract. Verifier score is 0.0 with no usable assembly provided.

### Trivialized / Misframed
- Task: Q3 - CSG Union of Polyhedra (subpass 16)
- Score: 0.5207559236248205
- Confidence: 0.91
- Verifier signal: (none)
- Judge justification: The output returns a simple rectangular box that merely bounds the sphere and cube instead of representing the actual CSG union, ignoring the required sphere approximation and boolean trimming. This constitutes a misf...

### Runaway Overthinking
- Task: Q55 - VGB6 — Delaunay Triangulation (subpass 14)
- Score: 0.0
- Confidence: 0.64
- Verifier signal: (none)
- Judge justification: The attempt contains an extremely long, spiraling chain-of-thought with repeated shifts in strategy (convex hulls, Bowyer–Watson, arbitrary fan triangulations, placeholder insertions) and explicit admissions of uncert...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 1)
- Score: 0.0
- Confidence: 0.74
- Verifier signal: (none)
- Judge justification: The attempt provides a very large, detailed brick list and extensive reasoning, indicating non-trivial engagement. However, the score is 0.0 and there are no verifier signals indicating diverse error types. Without ex...
