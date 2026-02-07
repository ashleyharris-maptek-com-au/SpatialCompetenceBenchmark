# Task q11: Hyper-snake Challenge
- Source file: `11.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Test high-dimensional path planning under strict local movement rules and global self-avoidance/food constraints.

## Output Contract
- Return JSON with `path`.
- Each path element is `{pos: [int,...]}`.
- `path[0].pos` must equal start position and match configured dimension length.

## Hard Constraints (Verifier-Checked)
- Correct dimensionality in every `pos`.
- Unit movement in exactly one dimension per step.
- No out-of-bounds coordinates, wall hits, or revisits.
- Food collection affects score/quality.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `No path in answer` / `Empty path` | No usable attempt | `Evasion / Forfeit` |
| `Move i changed N dimensions` | Illegal movement semantics | `Near-Miss`, `Local-Only` |
| `Position ... visited more than once` | Global self-avoidance failed | `Local-Only` |
| `Position ... is a wall/out of bounds` | Feasibility constraint broken | `Near-Miss`, `Local-Only` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing path or placeholder output.
- `Trivialized / Misframed`: Extremely short path that ignores target coverage/food.
- `Runaway Overthinking`: Rare in this task; only use when long reasoning replaces valid artifact.
- `Local-Only (Global Constraint Integration Failure)`: Local moves appear valid but global coverage/self-avoidance breaks.
- `Near-Miss Edge Case`: One bad move or one repeat in otherwise coherent path.

## Judge Input Bundle
1. Prompt with dimensions, walls, food, and start.
2. Raw output.
3. Parsed `path`.
4. Verifier step-by-step failures.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q11 with one failure mode.
Use movement legality and global self-avoidance constraints as primary evidence.
Return JSON: failure_mode, confidence, justification.
```

