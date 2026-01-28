def get_response(subPass: int):
  return {
    "q1": False,
    "q2": False,
    "q3": False,
    "q4": False,
    "q5": 1 if subPass >= 2 else 0,
    "imageDescription": "Something SFW"
  }, ""


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  return {
    "q1": rng.choice([False, True]),
    "q2": rng.choice([False, True]),
    "q3": rng.choice([False, True]),
    "q4": rng.choice([False, True]),
    "q5": rng.randint(0, 3),
    "imageDescription": "Random guess",
  }, "Random guess"
