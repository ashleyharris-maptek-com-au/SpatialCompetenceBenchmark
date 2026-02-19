# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 190
- Judged rows: 190
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 24 | 12.63% |
| Trivialized / Misframed | 3 | 1.58% |
| Runaway Overthinking | 5 | 2.63% |
| Local-Only (Global Constraint Integration Failure) | 129 | 67.89% |
| Near-Miss Edge Case | 29 | 15.26% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 26 | 26 | 0 | 100.00% |
| Q55 - VGB6 — Delaunay Triangulation | 23 | 23 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 19 | 19 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 13 | 13 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 11 | 11 | 0 | 100.00% |
| Q57 - VGB5 — Two Segments | 10 | 10 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials | 8 | 8 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 8 | 8 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 7 | 7 | 0 | 100.00% |
| Q52 - VGB2 — Topology Edge Tasks: Enumerate Edges | 7 | 7 | 0 | 100.00% |
| Q54 - VGB4 — Half Subdivision Neighbours | 7 | 7 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 6 | 6 | 0 | 100.00% |
| Q51 - VGB1 — Topology Enumeration | 6 | 6 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 3)
- Score: 0.0
- Confidence: 0.97
- Verifier signal: Skipped due to earlyFail (first subpass scored under 0%)
- Judge justification: No output was produced for this subpass and it was skipped due to earlyFail from a prior zero score, yielding no usable bricks or schema-compliant content.

### Trivialized / Misframed
- Task: Q3 - CSG Union of Polyhedra (subpass 16)
- Score: 0.0
- Confidence: 0.86
- Verifier signal: Early failure: Face 212 has invalid vertex index 214 (valid range: 0-213)
- Judge justification: Verifier reports an early schema/index failure: a face references an invalid vertex index (214 out of range 0–213). This is a fundamental output contract violation rather than a near-correct geometric miss. Such index...

### Runaway Overthinking
- Task: Q4 - Tetrahedron Shadow Coverage (subpass 7)
- Score: 0.0
- Confidence: 0.88
- Verifier signal: Result Volume: 0.00 Reference Volume: 0.71 Intersection Volume: 0.00 Difference Volume: 0.70 Error OpenSCAD error for result.scad: stderr: CGAL error: assertion violation! Expression : File : /Users/REDACTED/librarie...
- Judge justification: The attempt shows extensive, spiraling reasoning with an overcomplicated construction strategy, and the verifier reports multiple diverse failure types: CGAL runtime assertion violations, zero result volume, intersect...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.0
- Confidence: 0.82
- Verifier signal: Stud grid misalignment in connected component: brick {'Centroid': [64.0, 0.0, 4.8], 'RotationDegrees': 0} grid (4.0, 4.0) vs brick {'Centroid': [55.43, 32.0, 4.8], 'RotationDegrees': 30} grid (7.04, 6.54)
- Judge justification: The verifier reports stud grid misalignment within a connected component, indicating that while many local placements were attempted, the global stud-grid compatibility constraint was violated. The assembly is extensi...

### Near-Miss Edge Case
- Task: Q3 - CSG Union of Polyhedra (subpass 14)
- Score: 0.0
- Confidence: 0.78
- Verifier signal: Early failure: Face 32 is degenerate (zero or near-zero area)
- Judge justification: Verifier flags a single degenerate face (zero or near-zero area) without reporting broader manifold, winding, or volume mismatches. This aligns with an otherwise comprehensive union that fails due to a small, localize...
