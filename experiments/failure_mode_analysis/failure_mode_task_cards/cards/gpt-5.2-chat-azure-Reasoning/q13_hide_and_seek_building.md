# Task q13: Hide and seek behind a building
- Source file: `13.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Test multi-agent spatial placement under occlusion and non-overlap constraints at increasing population scale.

## Output Contract
- Return JSON with `people`.
- Each person is `{xy:[x,y]}`.
- Count must match subpass requirement exactly.

## Hard Constraints (Verifier-Checked)
- Exact number of people.
- Valid coordinate schema.
- Max distance from building center.
- No person-person overlap.
- No person-building overlap.
- Visibility check from sniper viewpoint.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Expected N people, got M` | Output cardinality mismatch | `Trivialized`, `Near-Miss` |
| `Overlap detected ...` | Physical placement invalid | `Local-Only` |
| `intersects with building` | Hard collision violation | `Local-Only` |
| `N red pixels visible` | Occlusion objective failed | `Local-Only`, `Near-Miss` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing people list or malformed coordinates.
- `Trivialized / Misframed`: Under-populated solution or ignores hide objective.
- `Runaway Overthinking`: COT shows spiraling placement strategy that produces diverse error types (collisions AND visibility AND count failures).
- `Local-Only (Global Constraint Integration Failure)`: Local placement mostly valid but global occlusion/collision constraints fail.
- `Near-Miss Edge Case`: Small count miss or minor residual visibility.

## Judge Input Bundle
1. Prompt with building/sniper/population parameters.
2. Raw output.
3. Parsed people positions.
4. Verifier messages (count/collision/visibility).
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q13 with one failure mode.
Prioritize exact-count and occlusion/collision verifier outcomes.
Return JSON: failure_mode, confidence, justification.
```

