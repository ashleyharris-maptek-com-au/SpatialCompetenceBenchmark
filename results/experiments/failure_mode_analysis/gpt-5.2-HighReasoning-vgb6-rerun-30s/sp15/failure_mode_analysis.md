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
- Task: Q55 - VGB6 — Delaunay Triangulation (subpass 15)
- Score: 0.0
- Confidence: 0.97
- Verifier signal: (none)
- Judge justification: The model returned an explicit empty triangulation (`{'triangles': []}`), which constitutes missing all required Delaunay triangles. Per task-specific tie-breaks, missing or empty `triangles` is classified as Evasion ...
