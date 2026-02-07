# Failure-Mode Analysis

- Total subpasses: 212
- Candidate rows (failed + low-score pass): 168
- Judged rows: 168
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 50 | 29.76% |
| Trivialized / Misframed | 19 | 11.31% |
| Runaway Overthinking | 8 | 4.76% |
| Local-Only (Global Constraint Integration Failure) | 80 | 47.62% |
| Near-Miss Edge Case | 11 | 6.55% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 34 | 34 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 19 | 19 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 13 | 13 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 10 | 10 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials | 8 | 8 | 0 | 100.00% |
| Q6 - Voxel Grid Projection - shadow coverage and no symmetries | 6 | 6 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 6 | 6 | 0 | 100.00% |
| Q9 - Hamiltonian Loop on Grid | 6 | 6 | 0 | 100.00% |
| Q16 - Pack rectangular prisms | 6 | 6 | 0 | 100.00% |
| Q56 - VGB7 — Shikaku Rectangles | 6 | 6 | 0 | 100.00% |
| Q23 - Fluid simulation | 5 | 5 | 0 | 100.00% |
| Q51 - VGB1 — Topology Enumeration | 4 | 4 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 3)
- Score: 0.0
- Confidence: 0.97
- Verifier signal: Skipped due to earlyFail (first subpass scored under 0%)
- Judge justification: No output or bricks were provided for this subpass due to early termination, resulting in no usable assembly.

### Trivialized / Misframed
- Task: Q7 - 3D maze - solution requires jumping over gaps (subpass 0)
- Score: 0.0
- Confidence: 0.84
- Verifier signal: No valid path from A to B (showing longest reachable path from A)
- Judge justification: The attempt outputs a valid-looking ASCII grid with A and B, but the verifier reports no valid path from A to B. This indicates the core task intent (constructing a solvable maze with required jumps and uniqueness) wa...

### Runaway Overthinking
- Task: Q4 - Tetrahedron Shadow Coverage (subpass 7)
- Score: 0.0
- Confidence: 0.84
- Verifier signal: Result Volume: 0.98 Reference Volume: 0.71 Intersection Volume: 0.30 Difference Volume: 1.15 Tetrahedrons 0 and 1 intersect. 50% penalty.Results were cached .
- Judge justification: Excessive number of tetrahedra arranged in dense grids leads to avoidable intersections (50% penalty) and over/under-coverage, reflecting an overbuilt approach that increases collisions rather than integrating constra...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.0
- Confidence: 0.83
- Verifier signal: Structure unstable: center of mass (0.0, 44.0) is outside support polygon of ground bricks
- Judge justification: The assembly provides a non-trivial bricks list with valid layering, but fails the global physical stability constraint: the verifier reports the center of mass lies outside the support polygon. This indicates locally...

### Near-Miss Edge Case
- Task: Q3 - CSG Union of Polyhedra (subpass 17)
- Score: 0.0
- Confidence: 0.86
- Verifier signal: Early failure: Edge (0, 3) appears twice in same direction (faces 0 and 2) - inconsistent winding
- Judge justification: The intended union shape is essentially correct, but the verifier flags a single inconsistent winding/edge duplication causing a topology failure, consistent with a small, localized defect.
