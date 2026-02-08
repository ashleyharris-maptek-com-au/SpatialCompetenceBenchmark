# Failure-Mode Task Cards

This package contains classifier-facing task cards for failure-mode judgment on the active non-skipped tasks in run `gpt-5.2-chat-azure-Reasoning`.

The cards are designed to be consumed by an LLM judge using:

1. Exact task prompt.
2. Raw model output.
3. Parsed output (if any).
4. Verifier summary/signals.
5. Optional reasoning summary.

Each card follows a fixed contract:

1. `Task qXX: <title>`
2. `Intent`
3. `Output Contract`
4. `Hard Constraints (Verifier-Checked)`
5. `Verifier Signals`
6. `Failure-Mode Tie-Breaks (Task-Specific)`
7. `Judge Input Bundle`
8. `Classification Prompt Snippet`

Taxonomy alignment:
- `FAILURE_TAXONOMY.md`

Primary artifacts:
- Card index: `experiments/failure_mode_analysis/failure_mode_task_cards/index.md`
- Per-task cards: `experiments/failure_mode_analysis/failure_mode_task_cards/cards/gpt-5.2-chat-azure-Reasoning/`
- Path helpers: `experiments/failure_mode_analysis/failure_mode_task_cards/paths.py`

## Programmatic Usage

```python
from experiments.failure_mode_analysis.failure_mode_task_cards.paths import get_task_card_path

path = get_task_card_path("gpt-5.2-chat-azure-Reasoning", 12)
```
