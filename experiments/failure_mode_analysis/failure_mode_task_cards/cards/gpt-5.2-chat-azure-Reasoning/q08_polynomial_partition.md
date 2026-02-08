# Task q08: Fit a curve to partition 2D ascii patterns via cubic polynomials
- Source file: `8.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Test symbolic program synthesis under strict syntax limits: produce a function whose sign partitions a 2D target pattern.

## Output Contract
- Return JSON with `reasoning` and `function`.
- `function` must include `def f(x, y):` and a `return`.
- Return expression must use only permitted arithmetic/power syntax and include both `x` and `y`.

## Hard Constraints (Verifier-Checked)
- Character/signature whitelist.
- Executable function (safe eval path).
- Non-uniform output over grid.
- Score thresholding: low match rates are zeroed.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Invalid function signature ...` | Output not in required callable form | `Evasion`, `Trivialized` |
| `Invalid characters in answer ...` | Violates restricted syntax contract | `Trivialized`, `Runaway` |
| `Error evaluating AI-generated python function` | Runtime-invalid function | `Near-Miss`, `Runaway` |
| `Output was uniformly valued` | Function ignores partition objective | `Trivialized` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing function body or non-code answer.
- `Trivialized / Misframed`: Constant/degenerate function, or ignores allowed grammar.
- `Runaway Overthinking`: COT shows spiraling symbolic derivation producing an overly complex expression that violates parser/eval constraints.
- `Local-Only (Global Constraint Integration Failure)`: Partial local fit but poor full-grid match under threshold.
- `Near-Miss Edge Case`: Valid function with small mismatch or one parse/eval defect.

## Judge Input Bundle
1. Prompt (ASCII/image subpass details).
2. Raw output.
3. Parsed function string.
4. Verifier parse/eval/match message.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q08 with one failure mode using syntax-validity and verifier match signals.
If output is syntactically valid but globally mismatched, prefer Local-Only.
Return JSON: failure_mode, confidence, justification.
```

