def get_response(subPass: int):
  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  perpendicular = {
    "X+": ["Y+", "Y-", "Z+", "Z-"],
    "X-": ["Y+", "Y-", "Z+", "Z-"],
    "Y+": ["X+", "X-", "Z+", "Z-"],
    "Y-": ["X+", "X-", "Z+", "Z-"],
    "Z+": ["X+", "X-", "Y+", "Y-"],
    "Z-": ["X+", "X-", "Y+", "Y-"],
  }
  connectors = []
  for idx in range(5):
    label = rng.choice(["X+", "X-", "Y+", "Y-", "Z+", "Z-"])
    connectors.append({
      "partNumber":
      rng.choice(["P101", "P102", "P103", "P104", "P105", "P106", "P107", "P108"]),
      "connections": [{
        "extrusionNumber": idx,
        "label": label,
        "orientationOfWhiteSide": rng.choice(perpendicular[label])
      }]
    })
  return {"connectors": connectors}, "Random guess"
