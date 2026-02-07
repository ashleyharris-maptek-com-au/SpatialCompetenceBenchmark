def build_budget_informed_prefix(max_output_tokens: int) -> str:
  if int(max_output_tokens) > 4096:
    return (
      "[Output Token Budget: effectively unlimited]\n"
      "You are not output-token constrained for this run.\n"
    )
  return (
    f"[Output Token Budget: {max_output_tokens}]\n"
    f"You must keep your final answer within {max_output_tokens} output tokens.\n"
  )


def apply_budget_informed_prefix(prompt: str, max_output_tokens: int) -> str:
  prefix = build_budget_informed_prefix(max_output_tokens)
  if str(prompt).startswith(prefix):
    return prompt
  return f"{prefix}\n\n{prompt}"
