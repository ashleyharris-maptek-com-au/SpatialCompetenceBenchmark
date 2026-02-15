# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 122
- Judged rows: 122
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 83 | 68.03% |
| Trivialized / Misframed | 2 | 1.64% |
| Runaway Overthinking | 1 | 0.82% |
| Local-Only (Global Constraint Integration Failure) | 24 | 19.67% |
| Near-Miss Edge Case | 12 | 9.84% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 21 | 21 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 19 | 19 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q51 - VGB1 — Topology Enumeration | 7 | 7 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 6 | 6 | 0 | 100.00% |
| Q16 - Pack rectangular prisms | 6 | 6 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 6 | 6 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 5 | 5 | 0 | 100.00% |
| Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials | 5 | 5 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 4 | 4 | 0 | 100.00% |
| Q6 - Voxel Grid Projection - shadow coverage and no symmetries | 4 | 4 | 0 | 100.00% |
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 4 | 4 | 0 | 100.00% |
| Q54 - VGB4 — Half Subdivision Neighbours | 3 | 3 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.0
- Confidence: 0.97
- Verifier signal: (none)
- Judge justification: The output is an empty JSON object with no `bricks` list, yielding no usable assembly. This matches a forfeit/empty response per the task’s Output Contract and verifier guidance.

### Trivialized / Misframed
- Task: Q3 - CSG Union of Polyhedra (subpass 8)
- Score: 0.0
- Confidence: 0.92
- Verifier signal: Result Volume: 1288.90 Reference Volume: 0.00 Intersection Volume: 1000.30 Difference Volume: 853.07 OpenSCAD error for reference.scad: stderr: CGAL error: assertion violation! Expression : File : /Users/REDACTED/lib...
- Judge justification: The output simply concatenates the cube faces and the tetrahedron faces as separate solids without performing a true CSG union. This violates the hard constraint that the result must be a single union mesh. The verifi...

### Runaway Overthinking
- Task: Q3 - CSG Union of Polyhedra (subpass 11)
- Score: 0.0
- Confidence: 0.89
- Verifier signal: Result Volume: 1914.16 Reference Volume: 1914.16 Intersection Volume: 0.00 Difference Volume: 1913.60 OpenSCAD error for compare1.scad: stderr: CGAL error: assertion violation! Expression : File : /Users/REDACTED/lib...
- Judge justification: The chain-of-thought shows extensive, spiraling and overcomplicated reasoning about intersections, orientations, and splitting strategies. Despite this, the verifier reports severe topology/manifold CGAL errors and a ...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 1)
- Score: 0.0
- Confidence: 0.88
- Verifier signal: Brick {'Centroid': [40, 0, 33.6], 'RotationDegrees': 90} is floating (not supported from below or held from above)
- Judge justification: A large, detailed brick list is provided, but the verifier flags at least one brick as floating (unsupported). This indicates locally plausible placements without satisfying global support/buildability constraints. Al...

### Near-Miss Edge Case
- Task: Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials (subpass 1)
- Score: 0.0
- Confidence: 0.77
- Verifier signal: Error evaluating AI-generated python function: unexpected indent ( , line 6)
- Judge justification: The verifier reports a runtime evaluation error (unexpected indent) for an otherwise well-formed polynomial attempt. This is a single parse/eval defect rather than a conceptual forfeit or degenerate output. Although t...
