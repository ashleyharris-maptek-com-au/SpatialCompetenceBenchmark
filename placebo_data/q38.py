from pathlib import Path
import runpy
import random


_QUESTION_FILE = Path(__file__).resolve().parent.parent / "38.py"
_PROBLEM_CACHE = None


def _load_problems():
  global _PROBLEM_CACHE
  if _PROBLEM_CACHE is None:
    namespace = runpy.run_path(str(_QUESTION_FILE))
    _PROBLEM_CACHE = namespace.get("problems", [])
  return _PROBLEM_CACHE


def _blank_response(reasoning_text: str):
  return {
    "reasoning": reasoning_text,
    "looseStackable": False,
    "looseTippingBlock": 0,
    "gluedStable": False,
    "gluedFirstContact": 0,
    "gluedRestingBlocks": [],
    "degreesToTip": 0.0,
  }


def get_response(subPass: int):
  problems = _load_problems()
  if subPass < 0 or subPass >= len(problems):
    raise IndexError(f"Subpass {subPass} out of range for question 38")

  prob = problems[subPass]
  response = {
    "reasoning": f"Using precomputed physics for subpass {subPass + 1}: {prob.get('name', 'tower')}.",
    "looseStackable": prob.get("loose_stackable", False),
    "looseTippingBlock": prob.get("loose_tipping_block", 0),
    "gluedStable": prob.get("glued_stable", False),
    "gluedFirstContact": prob.get("glued_first_contact", 0),
    "gluedRestingBlocks": prob.get("glued_resting_blocks", []),
    "degreesToTip": prob.get("degrees_to_tip", 0.0),
  }
  return response, "Reference answer from human-with-tools"


def get_guess(subPass: int, rng):
  problems = _load_problems()
  if subPass < 0 or subPass >= len(problems):
    return _blank_response("Random guess"), "Random guess"

  prob = problems[subPass]
  n_blocks = max(1, len(prob.get("objects", [])))

  loose_stackable = rng.choice([True, False])
  loose_tip_block = 0 if loose_stackable else rng.randint(1, n_blocks)
  glued_stable = rng.choice([True, False])
  glued_first_contact = 0 if glued_stable else rng.randint(1, n_blocks)

  # Random subset for resting blocks
  block_indices = list(range(1, n_blocks + 1))
  rng.shuffle(block_indices)
  subset_size = rng.randint(0, n_blocks) if glued_stable else rng.randint(1, n_blocks)
  resting_blocks = sorted(block_indices[:subset_size])

  response = {
    "reasoning": "Random guess",
    "looseStackable": loose_stackable,
    "looseTippingBlock": loose_tip_block,
    "gluedStable": glued_stable,
    "gluedFirstContact": glued_first_contact,
    "gluedRestingBlocks": resting_blocks,
    "degreesToTip": round(rng.uniform(0.0, 90.0), 1),
  }
  return response, "Random guess"


def get_always_wrong(subPass: int):
  problems = _load_problems()
  if subPass < 0 or subPass >= len(problems):
    return _blank_response("Always wrong"), "Always-wrong placeholder"

  prob = problems[subPass]
  n_blocks = max(1, len(prob.get("objects", [])))

  # Flip booleans and change numeric answers to be incorrect.
  loose_stackable = not prob.get("loose_stackable", False)

  expected_tip = prob.get("loose_tipping_block", 0)
  loose_tip_block = expected_tip + 1 if expected_tip < n_blocks else max(0, expected_tip - 1)
  if loose_tip_block == expected_tip:
    loose_tip_block = (expected_tip + 1) % (n_blocks + 1)
  if loose_tip_block == 0:
    loose_tip_block = 1  # ensure non-zero when flipping from stackable

  glued_stable = not prob.get("glued_stable", False)

  expected_first = prob.get("glued_first_contact", 0)
  glued_first_contact = expected_first + 1 if expected_first < n_blocks else max(0, expected_first - 1)
  if glued_first_contact == expected_first:
    glued_first_contact = (expected_first + 1) % (n_blocks + 1)
  if glued_first_contact == 0:
    glued_first_contact = 1  # ensure non-zero when flipping from stable

  expected_resting = set(prob.get("glued_resting_blocks", []))
  all_blocks = list(range(1, n_blocks + 1))
  wrong_resting = [b for b in all_blocks if b not in expected_resting]
  if not wrong_resting:
    # if expected was all blocks, choose a different singleton (e.g., first block only)
    wrong_resting = [1] if n_blocks >= 1 else []

  degrees_to_tip = prob.get("degrees_to_tip", 0.0)
  wrong_degrees = degrees_to_tip + 25 if degrees_to_tip <= 50 else max(0.0, degrees_to_tip - 25)

  response = {
    "reasoning": "Deliberately incorrect placeholder",
    "looseStackable": loose_stackable,
    "looseTippingBlock": loose_tip_block,
    "gluedStable": glued_stable,
    "gluedFirstContact": glued_first_contact,
    "gluedRestingBlocks": wrong_resting,
    "degreesToTip": round(wrong_degrees, 1),
  }
  return response, "Always-wrong placeholder"
