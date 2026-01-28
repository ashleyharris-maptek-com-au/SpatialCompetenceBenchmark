def get_response(subPass: int):
  g = {}
  exec(open("35.py").read(), g)

  # I had to write a solver to generate 'expected' in order to grade these questions,
  # and I'm just going to re-use that same solver here.
  return {"gears": g["gear_systems"][subPass]["expected"]}, "Placebo thinking... hmmm..."


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  g = {}
  exec(open("35.py").read(), g)
  gears_def = g["gear_systems"][subPass]["gears_def"]
  gears = []
  for idx in range(len(gears_def)):
    gears.append({
      "gearNumber": idx + 1,
      "direction": rng.choice(["clockwise", "counterclockwise", "stopped"]),
      "rpm": rng.uniform(0.0, 2000.0),
    })
  return {"reasoning": "Random guess", "gears": gears}, "Random guess"
