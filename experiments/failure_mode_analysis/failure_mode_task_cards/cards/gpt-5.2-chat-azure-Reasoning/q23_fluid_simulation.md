# Task q23: Fluid simulation
- Source file: `23.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Evaluate simulator-aware terrain editing: craft earthworks that induce target water behavior after rainfall and voxel physics.

## Output Contract
- Return JSON with `reasoning` and `earthworks`.
- `earthworks` is list of edits with `xyzMin`, `xyzMax`, and `material` (`Rock` or `Air`).
- Invalid edits may be skipped by grader; overall plan is still judged by simulation outcomes.

## Hard Constraints (Verifier-Checked)
- `earthworks` list and edit schema.
- Edit bounds within world dimensions.
- Rock stability and post-edit simulation effects.
- Subpass-specific water objectives (surface area, counts, depth, levels, visibility, exact totals, etc.).

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `earthworks must be a list` | Contract failure | `Evasion`, `Trivialized` |
| `Found X water voxels ...` / `Found X bodies ...` | Objective metric summary | `Near-Miss`, `Local-Only` |
| `No ring-shaped lake found` | Required morphology not achieved | `Local-Only` |
| `Found N visible water voxels - must have NO visible water` | Hidden-water constraint failure | `Local-Only` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Missing/empty earthworks with no meaningful attempt.
- `Trivialized / Misframed`: Edits ignore simulator objective (e.g., random/no-op plan).
- `Runaway Overthinking`: Large complicated edit program that destabilizes/undoes goals.
- `Local-Only (Global Constraint Integration Failure)`: Some metrics improve but multi-condition objective fails globally.
- `Near-Miss Edge Case`: Close on counts/depth/levels with one threshold miss.

## Judge Input Bundle
1. Prompt and subpass objective.
2. Raw output.
3. Parsed earthworks.
4. Verifier simulation summary.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q23 with one failure mode.
Focus on simulator metrics and objective thresholds over qualitative prose.
Return JSON: failure_mode, confidence, justification.
```

