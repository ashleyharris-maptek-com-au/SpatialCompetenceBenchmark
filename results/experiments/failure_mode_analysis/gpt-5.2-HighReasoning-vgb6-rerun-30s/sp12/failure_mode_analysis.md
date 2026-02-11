# Failure-Mode Analysis

- Total subpasses: 1
- Candidate rows (failed + low-score pass): 1
- Judged rows: 1
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 0 | 0.00% |
| Trivialized / Misframed | 0 | 0.00% |
| Runaway Overthinking | 0 | 0.00% |
| Local-Only (Global Constraint Integration Failure) | 1 | 100.00% |
| Near-Miss Edge Case | 0 | 0.00% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 1 | 1 | 0 | 100.00% |

## Evidence Samples

### Local-Only (Global Constraint Integration Failure)
- Task: Q55 - VGB6 — Delaunay Triangulation (subpass 12)
- Score: 0.0
- Confidence: 0.91
- Verifier signal: (none)
- Judge justification: The output provides a large, patterned set of triangle index triplets that systematically connect many consecutive indices to fixed hubs (e.g., 38 and 46), indicating a locally constructed or templated triangulation r...
