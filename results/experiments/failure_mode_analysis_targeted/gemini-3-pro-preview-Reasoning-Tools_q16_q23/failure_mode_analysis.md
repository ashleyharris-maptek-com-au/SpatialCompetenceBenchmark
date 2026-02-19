# Failure-Mode Analysis

- Total subpasses: 20
- Candidate rows (failed + low-score pass): 5
- Judged rows: 5
- Judge errors: 0

## Mode Distribution (Judged Rows)

| Mode | Count | Share |
|---|---:|---:|
| Evasion / Forfeit | 5 | 100.00% |
| Trivialized / Misframed | 0 | 0.00% |
| Runaway Overthinking | 0 | 0.00% |
| Local-Only (Global Constraint Integration Failure) | 0 | 0.00% |
| Near-Miss Edge Case | 0 | 0.00% |

## Task Hotspots

| Task | Candidates | Judged | Judge Errors | Coverage |
|---|---:|---:|---:|---:|
| Q23 - Fluid simulation | 3 | 3 | 0 | 100.00% |
| Q16 - Pack rectangular prisms | 2 | 2 | 0 | 100.00% |

## Evidence Samples

### Evasion / Forfeit
- Task: Q16 - Pack rectangular prisms (subpass 3)
- Score: 0.0
- Confidence: 0.98
- Verifier signal: (none)
- Judge justification: No raw output was provided (output_text_chars = 0; Raw Output: none), so there is no usable JSON with `boxes` to evaluate against packing constraints.
