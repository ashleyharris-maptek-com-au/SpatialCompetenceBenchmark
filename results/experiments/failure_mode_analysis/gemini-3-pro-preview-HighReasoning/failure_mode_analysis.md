# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 132
- Judged rows: 132
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 38 | 28.79% |
| Trivialized / Misframed | 10 | 7.58% |
| Runaway Overthinking | 0 | 0.00% |
| Local-Only (Global Constraint Integration Failure) | 67 | 50.76% |
| Near-Miss Edge Case | 17 | 12.88% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 24 | 24 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 15 | 15 | 0 | 100.00% |
| Q57 - VGB5 — Two Segments | 12 | 12 | 0 | 100.00% |
| Q11 - Hyper-snake Challenge | 9 | 9 | 0 | 100.00% |
| Q28 - AI controlling explosives, what could possibly go wrong? | 9 | 9 | 0 | 100.00% |
| Q29 - Cage match. Can LLMs design interlocking parts for 3D printing? | 9 | 9 | 0 | 100.00% |
| Q2 - Build a Lego(tm) hemispherical shell | 8 | 8 | 0 | 100.00% |
| Q3 - CSG Union of Polyhedra | 7 | 7 | 0 | 100.00% |
| Q53 - VGB3 — Topology Edge Tasks: Classify Behaviour | 7 | 7 | 0 | 100.00% |
| Q12 - Fit a loop into a square that's perimeter is smaller than the total length | 6 | 6 | 0 | 100.00% |
| Q23 - Fluid simulation | 4 | 4 | 0 | 100.00% |
| Q56 - VGB7 — Shikaku Rectangles | 4 | 4 | 0 | 100.00% |
| Q7 - 3D maze - solution requires jumping over gaps | 3 | 3 | 0 | 100.00% |
| Q8 - Fit a curve to partition 2D ascii patterns via cubic polynomials | 3 | 3 | 0 | 100.00% |
| Q9 - Hamiltonian Loop on Grid | 3 | 3 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 3)
- Score: 0.0
- Confidence: 0.95
- Verifier signal: Skipped due to earlyFail (first subpass scored under 0%)
- Judge justification: No output or bricks were provided for this subpass, and it was skipped due to early failure. This constitutes a forfeit with no usable assembly to evaluate.

### Trivialized / Misframed
- Task: Q11 - Hyper-snake Challenge (subpass 1)
- Score: 0.4851120776179324
- Confidence: 0.62
- Verifier signal: Visited 29/61 cells (48.5%)
- Judge justification: The path is syntactically valid and reaches the food, but it stops early with only ~48% coverage despite ample remaining free space and no verifier-reported constraint violations. This reflects under-optimization of t...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.019653927890399034
- Confidence: 0.79
- Verifier signal: Result Volume: 189264.08 Reference Volume: 547897.63 Intersection Volume: 187118.66 Difference Volume: 360238.47 Score was renormalised: 0.01 -> 0.02
- Judge justification: A nontrivial multi-layer assembly was produced with valid schema and layering, but the verifier shows a very low intersection/reference volume ratio and large difference volume, indicating major missing regions or poo...

### Near-Miss Edge Case
- Task: Q3 - CSG Union of Polyhedra (subpass 20)
- Score: 0.0
- Confidence: 0.69
- Verifier signal: Result Volume: 1252.60 Reference Volume: 1252.60 Intersection Volume: 0.00 Difference Volume: 0.00 OpenSCAD render timed out after 1200 seconds OpenSCAD render timed out after 1200 seconds
- Judge justification: Verifier volume metrics exactly match the reference (zero difference and zero intersection), indicating the global CSG union geometry is essentially correct. No explicit topology errors (non-manifold, open edges, wind...
