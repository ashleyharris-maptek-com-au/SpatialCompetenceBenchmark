def get_response(subPass: int):
  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  return {"reasoning": "Random guess", "answer": rng.choice(["A", "B", "C", "D", "E"])}
