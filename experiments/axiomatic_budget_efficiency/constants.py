from pathlib import Path

EXPERIMENT_NAME = "axiomatic_budget_sweep"
EXPERIMENT_TAG = "axiomatic-budget-efficiency"

AXIOMATIC_TEST_IDS = (51, 52, 53, 54, 57)

# Output-token budgets to sweep, ending with a large "effectively unlimited" proxy cap.
BUDGETS = (256, 512, 4096, 65536)

DEFAULT_BASE_MODEL_CONFIG_NAME = "gpt-5.2-chat-azure"
MODEL_NAME_ALIASES = {
  "gpt-5.2-chat": "gpt-5.2-chat-azure",
}

RESULTS_DIR = Path("results") / "experiments" / EXPERIMENT_NAME
