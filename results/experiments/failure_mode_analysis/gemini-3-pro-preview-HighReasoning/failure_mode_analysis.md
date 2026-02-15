# Failure-Mode Analysis

- Total subpasses: 285
- Candidate rows (failed + low-score pass): 123
- Judged rows: 123
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 27 | 21.95% |
| Trivialized / Misframed | 11 | 8.94% |
| Runaway Overthinking | 0 | 0.00% |
| Local-Only (Global Constraint Integration Failure) | 63 | 51.22% |
| Near-Miss Edge Case | 22 | 17.89% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 24 | 24 | 0 | 100.00% |
| Q4 - Tetrahedron Shadow Coverage | 15 | 15 | 0 | 100.00% |
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
| Q57 - VGB5 — Two Segments | 3 | 3 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 3)
- Score: 0.0
- Confidence: 0.95
- Verifier signal: Skipped due to earlyFail (first subpass scored under 0%)
- Judge justification: No output was produced and the verifier skipped evaluation due to early failure, leaving no usable bricks list or structured response.

### Trivialized / Misframed
- Task: Q11 - Hyper-snake Challenge (subpass 1)
- Score: 0.4851120776179324
- Confidence: 0.78
- Verifier signal: Visited 29/61 cells (48.5%)
- Judge justification: The path is syntactically valid and obeys movement rules, but stops after limited coverage (29/61 cells) despite the instruction to go for as long as possible. No verifier errors indicate constraint violations; the fa...

### Local-Only (Global Constraint Integration Failure)
- Task: Q2 - Build a Lego(tm) hemispherical shell (subpass 0)
- Score: 0.019653927890399204
- Confidence: 0.74
- Verifier signal: Result Volume: 189264.08 Reference Volume: 547897.63 Intersection Volume: 187118.66 Difference Volume: 360238.47 Score was renormalised: 0.01 -> 0.02
- Judge justification: The attempt provides a well-formed schema with many locally plausible placements and correct layer heights, but the verifier reports an extremely low score driven by large volume difference versus the ideal shell. Thi...

### Near-Miss Edge Case
- Task: Q3 - CSG Union of Polyhedra (subpass 14)
- Score: 0.0
- Confidence: 0.72
- Verifier signal: Early failure: Face 1 is non-planar: vertex 1 is 1.0000 from plane
- Judge justification: Verifier flags a single non-planar face while the rest of the construction appears structurally coherent, suggesting a small geometric defect rather than systemic topology failure.
