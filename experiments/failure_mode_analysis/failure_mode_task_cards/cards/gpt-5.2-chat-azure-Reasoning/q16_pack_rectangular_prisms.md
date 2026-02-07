# Task q16: Pack rectangular prisms
- Source file: `16.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Measure 3D packing quality under strict inventory and validity constraints while maximizing packing efficiency.

## Output Contract
- Return JSON with `boxes`.
- Each box has `XyzMin:[x,y,z]` and `XyzMax:[x,y,z]`.
- Coordinates represent axis-aligned prism bounds.

## Hard Constraints (Verifier-Checked)
- Valid coordinate tuple shapes for every box.
- No overlaps; union volume consistency.
- Exact counts per required prism size.
- No negative coordinates.
- Efficiency scored from bounding volume.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `Answer volume ... Expected volume ... Boxes are overlapping ...` | Global geometric validity broken | `Local-Only` |
| `Box count mismatch for ...` | Inventory constraints failed | `Trivialized`, `Near-Miss` |
| `Box with negative coordinates detected` | Invalid placement domain | `Near-Miss`, `Local-Only` |
| `Packing efficiency ...` | Validity passed; quality measured | `Near-Miss` when barely failing target |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Empty or unusable `boxes`.
- `Trivialized / Misframed`: Ignores required prism inventory.
- `Runaway Overthinking`: Excessive arrangement complexity still yielding overlaps.
- `Local-Only (Global Constraint Integration Failure)`: Individual boxes plausible but full packing constraints fail.
- `Near-Miss Edge Case`: One count/coordinate/overlap defect in otherwise coherent pack.

## Judge Input Bundle
1. Prompt with prism inventory and objective.
2. Raw output.
3. Parsed boxes.
4. Verifier volume/count/overlap diagnostics.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q16 with one failure mode.
Treat overlap and inventory mismatches as primary evidence.
Return JSON: failure_mode, confidence, justification.
```

