import math
import hashlib
import os, sys
import tempfile
import time
import numpy as np
from textwrap import dedent

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
  height_hash = hashlib.md5(b"v6" + heightMap.tobytes()).hexdigest()
  cache_file = os.path.join(cache_dir, f"subpass{subPass}_{height_hash}.npz")

  if os.path.exists(cache_file):
    try:
      with np.load(cache_file, allow_pickle=True) as data:
        cached_hash = data.get("height_hash", None)
        if isinstance(cached_hash, np.ndarray):
          try:
            cached_hash = cached_hash.item()
          except Exception:
            cached_hash = str(cached_hash)

        if cached_hash == height_hash:
          print("Cache hit: " + cache_file)
          return {"blasts": list(data["blasts"])}, "Cached blasting plan"
    except Exception:
      pass

  if __name__ != "__main__":
    print("Cache didn't hit? Did you remember to run --setup? This will be slow!")
    print(cache_file)
  bestPlan = 0, []

  passCount = 0
  while True:
    passCount += 1
    if passCount > 20:
      break

    print(f"Running pass {passCount}")

    continuousSize, xyList = g["_largest_flat_region"](heightMap)

    if continuousSize > bestPlan[0]:
      # store a copy so later mutations don't corrupt the best plan
      bestPlan = continuousSize, list(blasts)

    heightSum = 0
    for y, x in xyList:
      heightSum += heightMap[y][x]

    targetHeight = heightSum / continuousSize - passCount / 20

    print(f"Got a flat area of size {continuousSize} at level {targetHeight:.1f}")

    if continuousSize > size * size * 0.9:
      print("Flat area is large enough - aborting and keeping it.")
      break

    if targetHeight < 1:
      print("Target height is too low - aborting")
      break

    for y in range(0, size):
      for x in range(0, size):
        if heightMap[y][x] > targetHeight:
          blasts.append({"x": x, "y": y, "z": heightMap[y][x] - targetHeight})
          heightMap[y][x] -= 1

    t = time.time()
    heightMap = g["gradeAnswer"]({"blasts": blasts}, subPass, "placebo", True)
    duration = time.time() - t
    if duration > 120 and __name__ != "__main__":
      print("Physics sim took " + str(duration) +
            " seconds. Aborting as we're impatient and --setup apepars to not have been run?")
      break

  continuousSize, xyList = g["_largest_flat_region"](heightMap)
  if continuousSize > bestPlan[0]:
    bestPlan = continuousSize, blasts

  if bestPlan[0] > 0:
    blasts = list(bestPlan[1])
    print("Reverted to best plan : with flat area of " + str(bestPlan[0]))
  try:
    np.savez_compressed(cache_file, blasts=np.array(blasts, dtype=object), height_hash=height_hash)
  except Exception:
    pass

  return {
    "blasts": blasts
  }, "Lots of tiny blasts, starting from the maximas and working our way"\
  " down in steps, repeating the top blasts as needed."


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  g = {}
  exec(open("28.py").read(), g)
  size = g["sizes"][subPass]
  blasts = []
  for _ in range(10):
    blasts.append({
      "x": rng.randint(0, size - 1),
      "y": rng.randint(0, size - 1),
      "z": rng.uniform(0.1, 2.0),
    })
  return {"blasts": blasts}, "Random guess"


def cache_solutions():
  r = list(range(8))
  r.reverse()

  import subprocess
  t = []
  for sp in r:
    t.append(subprocess.Popen([sys.executable, __file__, str(sp)]))
    if len(t) > 8:
      t.pop().wait()
      while t and t[0].poll() is not None:
        t.pop().wait()

  while t:
    t.pop().wait()


if __name__ == "__main__":
  if len(sys.argv) > 1:
    subPass = sys.argv[1]
    print(f"Running subpass {subPass}")
    get_response(int(subPass))
  else:
    cache_solutions()
