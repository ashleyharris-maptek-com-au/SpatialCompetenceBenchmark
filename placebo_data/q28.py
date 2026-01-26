import math
import hashlib
import os
import tempfile
import numpy as np
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  g = {}
  exec(open("28.py").read(), g)
  sizes = g["sizes"]
  size = sizes[subPass]

  heightMap = np.array(g["heightMaps"][subPass], dtype=float)  # Copy to avoid corrupting original

  blasts = []

  cache_dir = os.path.join(tempfile.gettempdir(), "q28_solver_cache")
  os.makedirs(cache_dir, exist_ok=True)

  # Cache based on current terrain state (input heightmap hash)
  height_hash = hashlib.md5(b"v3" + heightMap.tobytes()).hexdigest()
  cache_file = os.path.join(cache_dir, f"subpass{subPass}_{height_hash}.npz")

  if os.path.exists(cache_file):
    try:
      with np.load(cache_file, allow_pickle=True) as data:
        if data.get("height_hash", None) == height_hash:
          return {"blasts": list(data["blasts"])}, "Cached blasting plan"
    except Exception:
      pass

  for p in range(10):
    print(f"Running pass {p}")
    for y in range(0, size):
      for x in range(0, size):
        if heightMap[y][x] > 4 - p / 10:
          blasts.append({"x": x, "y": y, "z": 1.2})
          heightMap[y][x] -= 1

    heightMap = g["gradeAnswer"]({"blasts": blasts}, subPass, "placebo", True)

  try:
    np.savez_compressed(cache_file, blasts=np.array(blasts, dtype=object), height_hash=height_hash)
  except Exception:
    pass

  return {
    "blasts": blasts
  }, "Lots of tiny blasts, starting from the maximas and working our way"\
  " down in steps, repeating the top blasts as needed."
