def get_response(subPass: int):
  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  moves = []
  for _ in range(60):
    moves.append(rng.choice(["n", "s", "e", "w", "ne", "nw", "se", "sw"]))
  return " ".join(moves), "Random guess"
