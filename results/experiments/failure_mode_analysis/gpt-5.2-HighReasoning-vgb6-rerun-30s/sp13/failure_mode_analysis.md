# Failure-Mode Analysis

- Total subpasses: 1
- Candidate rows (failed + low-score pass): 1
- Judged rows: 1
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 1 | 100.00% |
| Trivialized / Misframed | 0 | 0.00% |
| Runaway Overthinking | 0 | 0.00% |
| Local-Only (Global Constraint Integration Failure) | 0 | 0.00% |
| Near-Miss Edge Case | 0 | 0.00% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q55 - VGB6 — Delaunay Triangulation | 1 | 1 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q55 - VGB6 — Delaunay Triangulation (subpass 13)
- Score: 0.0
- Confidence: 0.98
- Verifier signal: (none)
- Judge justification: The submitted output contains an explicitly empty triangle list (`{'triangles': []}`), which violates the requirement to return the exact Delaunay triangulation. The chain-of-thought repeatedly states inability to com...
