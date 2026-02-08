# Task qXX: <title>
- Source file: `<path/to/task.py>`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/<run_name>/`

## Intent
<One paragraph: what capability this task probes.>

## Output Contract
- <Exact schema/format expected by grader/parser.>
- <Common malformed formats to reject.>

## Hard Constraints (Verifier-Checked)
- <Hard check 1>
- <Hard check 2>
- <Hard check 3>

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `<signal>` | <what it means> | <labels> |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: <task-specific cue>
- `Trivialized / Misframed`: <task-specific cue>
- `Runaway Overthinking`: <task-specific cue>
- `Local-Only (Global Integration Failure)`: <task-specific cue>
- `Near-Miss Edge Case`: <task-specific cue>

## Judge Input Bundle
1. Exact prompt text.
2. Raw model output.
3. Parsed output object (if available).
4. Structured verifier summary (`score`, `signals`, `details`).
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
You are labeling one task attempt with exactly one failure mode.
Use only the provided prompt/output/verifier evidence.
Pick one of:
- Evasion / Forfeit
- Trivialized / Misframed
- Runaway Overthinking
- Local-Only (Global Integration Failure)
- Near-Miss Edge Case

Return JSON:
{
  "failure_mode": "...",
  "confidence": 0.0,
  "justification": "3-6 sentences grounded in verifier and output evidence."
}
```

