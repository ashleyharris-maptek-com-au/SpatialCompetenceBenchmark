# Task q52: VGB2 - Topology Edge Tasks: Enumerate Edges
- Source file: `52.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Judge whether the model can enumerate all deterministic edge connections for labeled square cases under varying corner/edge orderings.

## Output Contract
- Return object with `edges`.
- `edges` is nested list format of edge pair sets.
- Parser tolerates raw list output but canonical field is `edges`.

## Hard Constraints (Verifier-Checked)
- Nested integer-pair schema.
- Exact diff match against curated expected edge sets.
- Supports per-record ordering variants.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `missing: [...]` | Indices of cases where predicted edge pairs do not match ground truth | `Local-Only`, `Near-Miss` |
| `errors: [...]` | Parse/validation errors (e.g. `parse_failure`, `length_mismatch`, bad pair format/order) | `Trivialized`, `Evasion` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: Empty/invalid edges payload.
- `Trivialized / Misframed`: Wrong task interpretation (classification text instead of edge enumeration).
- `Runaway Overthinking`: Long prose and/or large edge lists that still fail basic parse/format checks.
- `Local-Only (Global Constraint Integration Failure)`: Broad mismatch in deterministic edge structure.
- `Near-Miss Edge Case`: One-case mismatch with otherwise correct structure.

## Judge Input Bundle
1. Prompt with tuple set and ordering.
2. Raw output.
3. Parsed `edges`.
4. Verifier diff summary.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q52 with one failure mode.
Treat `missing` indices and `errors` as primary evidence.
Return JSON: failure_mode, confidence, justification.
```
