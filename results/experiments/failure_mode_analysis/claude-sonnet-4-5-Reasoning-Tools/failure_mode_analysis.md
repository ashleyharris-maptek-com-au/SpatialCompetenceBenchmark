# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 178
- Judged rows: 178
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 70 | 39.33% |
| Trivialized / Misframed | 6 | 3.37% |
| Runaway Overthinking | 9 | 5.06% |
| Local-Only (Global Constraint Integration Failure) | 78 | 43.82% |
| Near-Miss Edge Case | 15 | 8.43% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 29 | 29 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 20 | 20 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 13 | 13 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 12 | 12 | 0 | 100.00% |
| Q54 - VGB4 — Half Subdivision Neighbours | 11 | 11 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q55 - VGB6 — Delaunay Triangulation | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials | 8 | 8 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 8 | 8 | 0 | 100.00% |
| Q57 - VGB5 — Two Segments | 7 | 7 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 6 | 6 | 0 | 100.00% |
| Q9 - Hamiltonian Loop on Grid | 4 | 4 | 0 | 100.00% |
| Q13 - Hide and seek behind a building | 4 | 4 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 3)
- Score: 0.0
- Confidence: 0.99
- Verifier signal: Skipped due to earlyFail (first subpass scored under 0%)
- Judge justification: No raw output was produced (0 characters) and thus no JSON with a usable `bricks` list could be parsed or verified. The run was skipped due to earlyFail, consistent with providing no assembly at all.

### Trivialized / Misframed
- Task: Q3 - CSG Union of Polyhedra (subpass 20)
- Score: 0.0
- Confidence: 0.94
- Verifier signal: Result Volume: 8.01 Reference Volume: 1252.60 Intersection Volume: 4.01 Difference Volume: 1243.71 Results were cached .
- Judge justification: The raw output is just the example unit-cube mesh with vertices at ±1, not the requested union of a 24-sided cone (r=8,h=15) and a 10cm cube centered at (0,0,5). The verifier reports a massive volume mismatch (Result ...

### Runaway Overthinking
- Task: Q4 - Tetrahedron Shadow Coverage (subpass 1)
- Score: 0.0
- Confidence: 0.78
- Verifier signal: Result Volume: 0.00 Reference Volume: 1.27 Intersection Volume: 0.00 Difference Volume: 1.26 Error OpenSCAD error for result.scad: stderr: WARNING: Minkowski: Nef polyhedron converted from mesh is invalid! WARNING: [m...
- Judge justification: Chain-of-thought shows repeated re-planning and overcomplicated scripting/optimization attempts (multiple "step back", "refine", "run script" loops). Verifier signals include diverse severe failures: OpenSCAD/CGAL Min...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.0
- Confidence: 0.92
- Verifier signal: Stud grid misalignment in connected component: brick {'Centroid': [55.0, 0.0, 4.8], 'RotationDegrees': 0.0} grid (3.0, 4.0) vs brick {'Centroid': [47.63, 27.5, 4.8], 'RotationDegrees': 30.0} grid (7.24, 2.04)
- Judge justification: Verifier flags a hard buildability violation: stud-grid misalignment within a connected component (bricks have incompatible grid coordinates given their rotations/centroids). The attempt focuses on locally plausible r...

### Near-Miss Edge Case
- Task: Q4 - Tetrahedron Shadow Coverage (subpass 3)
- Score: 0.49504950496633193
- Confidence: 0.84
- Verifier signal: Result Volume: 0.69 Reference Volume: 0.70 Intersection Volume: 0.70 Difference Volume: 0.00 Tetrahedrons 0 and 1 intersect. 50% penalty.Results were cached .
- Judge justification: Verifier shows essentially perfect shadow match (Difference Volume: 0.00; Intersection Volume equals Reference Volume), but a single global validity violation remains: tetrahedrons 0 and 1 intersect (50% penalty). Thi...
