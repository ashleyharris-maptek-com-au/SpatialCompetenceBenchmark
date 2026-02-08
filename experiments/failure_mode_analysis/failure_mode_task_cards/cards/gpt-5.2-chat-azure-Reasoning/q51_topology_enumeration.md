# Task q51: VGB1 - Topology Enumeration
- Source file: `51.py`
- Taxonomy: `FAILURE_TAXONOMY.md`
- Run cards dir: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`

## Intent
Evaluate discrete topological reasoning by enumerating corner-label configuration classes that guarantee interface behavior.

## Output Contract
- Return object with `configs`.
- `configs` is a list of 4-integer tuples/lists.
- Parser can recover from raw list output, but canonical field is `configs`.

## Hard Constraints (Verifier-Checked)
- Structure must match 4-item label tuple schema.
- Predicted set must match curated ground truth exactly.
- Order-independent set comparison with `missing/extra/errors`.

## Verifier Signals
| Signal/Error | Meaning | Likely failure mode(s) |
| --- | --- | --- |
| `passed: False` + `missing` | Omitted required configurations | `Local-Only`, `Near-Miss` |
| `passed: False` + `extra` | Added invalid configurations | `Local-Only`, `Near-Miss` |
| Schema extraction failure | Not a valid `configs` payload | `Evasion`, `Trivialized` |

## Failure-Mode Tie-Breaks (Task-Specific)
- `Evasion / Forfeit`: No parseable configs.
- `Trivialized / Misframed`: Wrong output form or misunderstanding of tuple-equivalence setup.
- `Runaway Overthinking`: COT shows spiraling enumeration reasoning that produces diverse error types (malformed format AND wrong count AND invalid configurations).
- `Local-Only (Global Constraint Integration Failure)`: Many missing/extra configurations.
- `Near-Miss Edge Case`: One configuration mismatch only.

## Judge Input Bundle
1. Prompt including corner-order/canonicalization rules.
2. Raw output.
3. Parsed `configs`.
4. Verifier diff object.
5. Optional reasoning summary.

## Classification Prompt Snippet
```text
Classify q51 with one failure mode.
Use verifier diff cardinality (missing/extra/errors) as primary evidence.
Return JSON: failure_mode, confidence, justification.
```

