import math
from textwrap import dedent
import random


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    return {
      "voxels": [{
        "xyz": [0, 0, 0]
      }, {
        "xyz": [0, 0, 1]
      }, {
        "xyz": [0, 0, 2]
      }, {
        "xyz": [0, 0, 3]
      }, {
        "xyz": [0, 0, 4]
      }, {
        "xyz": [0, 0, 5]
      }, {
        "xyz": [0, 1, 0]
      }, {
        "xyz": [0, 1, 1]
      }, {
        "xyz": [0, 1, 2]
      }, {
        "xyz": [0, 1, 3]
      }, {
        "xyz": [0, 1, 4]
      }, {
        "xyz": [0, 1, 5]
      }, {
        "xyz": [0, 2, 0]
      }, {
        "xyz": [0, 2, 1]
      }, {
        "xyz": [0, 2, 2]
      }, {
        "xyz": [0, 2, 3]
      }, {
        "xyz": [0, 2, 4]
      }, {
        "xyz": [0, 3, 3]
      }, {
        "xyz": [0, 4, 4]
      }, {
        "xyz": [0, 5, 5]
      }, {
        "xyz": [1, 0, 1]
      }, {
        "xyz": [1, 1, 2]
      }, {
        "xyz": [1, 2, 3]
      }, {
        "xyz": [1, 3, 4]
      }, {
        "xyz": [1, 4, 5]
      }, {
        "xyz": [1, 5, 0]
      }, {
        "xyz": [2, 0, 2]
      }, {
        "xyz": [2, 1, 3]
      }, {
        "xyz": [2, 2, 4]
      }, {
        "xyz": [2, 3, 5]
      }, {
        "xyz": [2, 4, 0]
      }, {
        "xyz": [2, 5, 1]
      }, {
        "xyz": [3, 0, 3]
      }, {
        "xyz": [3, 1, 4]
      }, {
        "xyz": [3, 2, 5]
      }, {
        "xyz": [3, 3, 0]
      }, {
        "xyz": [3, 4, 1]
      }, {
        "xyz": [3, 5, 2]
      }, {
        "xyz": [4, 0, 4]
      }, {
        "xyz": [4, 1, 5]
      }, {
        "xyz": [4, 2, 0]
      }, {
        "xyz": [4, 3, 1]
      }, {
        "xyz": [4, 4, 2]
      }, {
        "xyz": [4, 5, 3]
      }, {
        "xyz": [5, 0, 5]
      }, {
        "xyz": [5, 1, 0]
      }, {
        "xyz": [5, 2, 1]
      }, {
        "xyz": [5, 3, 2]
      }, {
        "xyz": [5, 4, 3]
      }, {
        "xyz": [5, 5, 4]
      }]
    }, "Placebo thinking... hmmm..."

  if subPass == 1:
    return {
      'voxels': [{
        'xyz': [5.0, 1.0, 6.0]
      }, {
        'xyz': [0.0, 7.0, 7.0]
      }, {
        'xyz': [2.0, 0.0, 2.0]
      }, {
        'xyz': [7.0, 3.0, 2.0]
      }, {
        'xyz': [4.0, 0.0, 4.0]
      }, {
        'xyz': [3.0, 5.0, 0.0]
      }, {
        'xyz': [6.0, 0.0, 6.0]
      }, {
        'xyz': [2.0, 1.0, 3.0]
      }, {
        'xyz': [0.0, 3.0, 3.0]
      }, {
        'xyz': [2.0, 5.0, 7.0]
      }, {
        'xyz': [6.0, 6.0, 4.0]
      }, {
        'xyz': [2.0, 7.0, 1.0]
      }, {
        'xyz': [5.0, 2.0, 7.0]
      }, {
        'xyz': [4.0, 7.0, 3.0]
      }, {
        'xyz': [1.0, 4.0, 5.0]
      }, {
        'xyz': [3.0, 6.0, 1.0]
      }, {
        'xyz': [6.0, 2.0, 0.0]
      }, {
        'xyz': [3.0, 4.0, 7.0]
      }, {
        'xyz': [4.0, 1.0, 5.0]
      }, {
        'xyz': [1.0, 0.0, 1.0]
      }, {
        'xyz': [3.0, 0.0, 3.0]
      }, {
        'xyz': [7.0, 2.0, 1.0]
      }, {
        'xyz': [5.0, 4.0, 1.0]
      }, {
        'xyz': [0.0, 4.0, 4.0]
      }, {
        'xyz': [6.0, 7.0, 5.0]
      }, {
        'xyz': [7.0, 4.0, 3.0]
      }, {
        'xyz': [1.0, 5.0, 6.0]
      }, {
        'xyz': [2.0, 2.0, 4.0]
      }, {
        'xyz': [1.0, 7.0, 0.0]
      }, {
        'xyz': [4.0, 2.0, 6.0]
      }, {
        'xyz': [6.0, 1.0, 7.0]
      }, {
        'xyz': [3.0, 7.0, 2.0]
      }, {
        'xyz': [6.0, 3.0, 1.0]
      }, {
        'xyz': [4.0, 4.0, 0.0]
      }, {
        'xyz': [3.0, 1.0, 4.0]
      }, {
        'xyz': [5.0, 5.0, 2.0]
      }, {
        'xyz': [7.0, 5.0, 4.0]
      }, {
        'xyz': [0.0, 0.0, 0.0]
      }, {
        'xyz': [6.0, 4.0, 2.0]
      }, {
        'xyz': [2.0, 3.0, 5.0]
      }, {
        'xyz': [1.0, 1.0, 2.0]
      }, {
        'xyz': [7.0, 1.0, 0.0]
      }, {
        'xyz': [0.0, 5.0, 5.0]
      }, {
        'xyz': [4.0, 3.0, 7.0]
      }, {
        'xyz': [5.0, 6.0, 3.0]
      }, {
        'xyz': [0.0, 6.0, 6.0]
      }, {
        'xyz': [1.0, 6.0, 7.0]
      }, {
        'xyz': [7.0, 6.0, 5.0]
      }, {
        'xyz': [0.0, 1.0, 1.0]
      }, {
        'xyz': [5.0, 0.0, 5.0]
      }, {
        'xyz': [2.0, 6.0, 0.0]
      }, {
        'xyz': [4.0, 5.0, 1.0]
      }, {
        'xyz': [6.0, 5.0, 3.0]
      }, {
        'xyz': [4.0, 6.0, 2.0]
      }, {
        'xyz': [1.0, 2.0, 3.0]
      }, {
        'xyz': [7.0, 0.0, 7.0]
      }, {
        'xyz': [1.0, 3.0, 4.0]
      }, {
        'xyz': [3.0, 2.0, 5.0]
      }, {
        'xyz': [3.0, 3.0, 6.0]
      }, {
        'xyz': [5.0, 7.0, 4.0]
      }, {
        'xyz': [7.0, 7.0, 6.0]
      }, {
        'xyz': [0.0, 2.0, 2.0]
      }, {
        'xyz': [2.0, 4.0, 6.0]
      }, {
        'xyz': [5.0, 3.0, 0.0]
      }, {
        'xyz': [6.0, 6.0, 1.0]
      }, {
        'xyz': [3.0, 5.0, 4.0]
      }, {
        'xyz': [2.0, 6.0, 1.0]
      }, {
        'xyz': [5.0, 3.0, 4.0]
      }, {
        'xyz': [4.0, 4.0, 4.0]
      }, {
        'xyz': [2.0, 4.0, 3.0]
      }, {
        'xyz': [4.0, 5.0, 3.0]
      }, {
        'xyz': [7.0, 7.0, 7.0]
      }, {
        'xyz': [2.0, 3.0, 7.0]
      }, {
        'xyz': [5.0, 5.0, 0.0]
      }, {
        'xyz': [4.0, 4.0, 7.0]
      }, {
        'xyz': [7.0, 0.0, 1.0]
      }, {
        'xyz': [4.0, 1.0, 4.0]
      }, {
        'xyz': [5.0, 4.0, 3.0]
      }, {
        'xyz': [2.0, 4.0, 7.0]
      }, {
        'xyz': [5.0, 4.0, 6.0]
      }, {
        'xyz': [3.0, 3.0, 5.0]
      }, {
        'xyz': [5.0, 1.0, 4.0]
      }, {
        'xyz': [5.0, 4.0, 2.0]
      }, {
        'xyz': [0.0, 1.0, 0.0]
      }, {
        'xyz': [1.0, 4.0, 6.0]
      }, {
        'xyz': [0.0, 7.0, 2.0]
      }, {
        'xyz': [6.0, 1.0, 2.0]
      }, {
        'xyz': [5.0, 6.0, 7.0]
      }, {
        'xyz': [0.0, 7.0, 6.0]
      }, {
        'xyz': [1.0, 5.0, 4.0]
      }, {
        'xyz': [0.0, 1.0, 7.0]
      }, {
        'xyz': [6.0, 0.0, 1.0]
      }, {
        'xyz': [2.0, 7.0, 5.0]
      }, {
        'xyz': [4.0, 7.0, 2.0]
      }, {
        'xyz': [0.0, 3.0, 4.0]
      }, {
        'xyz': [2.0, 5.0, 3.0]
      }, {
        'xyz': [2.0, 7.0, 0.0]
      }, {
        'xyz': [0.0, 1.0, 5.0]
      }, {
        'xyz': [3.0, 3.0, 3.0]
      }, {
        'xyz': [5.0, 2.0, 1.0]
      }]
    }, ""

  if True:  # Catch-all for any subpass
    sizes = [6, 8, 12, 16, 24, 20]
    counts = [50, 100, 200, 400, 1000, 500]
    size = sizes[subPass]
    count = counts[subPass]

    if subPass == 5:
      # Special handling for subpass 5: need solid projections + no "7" in coord sum
      voxel_set = set()
      xy_covered = set()
      xz_covered = set()
      yz_covered = set()

      def is_valid(x, y, z):
        return "7" not in str(x + y + z)

      def add_voxel(x, y, z):
        if (x, y, z) not in voxel_set and is_valid(x, y, z):
          voxel_set.add((x, y, z))
          xy_covered.add((x, y))
          xz_covered.add((x, z))
          yz_covered.add((y, z))
          return True
        return False

      # First pass: add voxels where (x+y+z) % 20 == 0
      for y in range(size):
        for x in range(size):
          for z in range(size):
            if (x + y + z) % size == 0:
              add_voxel(x, y, z)

      # Fill XY projection holes
      for x in range(size):
        for y in range(size):
          if (x, y) not in xy_covered:
            for z in range(size):
              if add_voxel(x, y, z):
                break

      # Fill XZ projection holes
      for x in range(size):
        for z in range(size):
          if (x, z) not in xz_covered:
            for y in range(size):
              if add_voxel(x, y, z):
                break

      # Fill YZ projection holes
      for y in range(size):
        for z in range(size):
          if (y, z) not in yz_covered:
            for x in range(size):
              if add_voxel(x, y, z):
                break

      # Pad to exactly 500 voxels if needed
      while len(voxel_set) < count:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        z = random.randint(0, size - 1)
        add_voxel(x, y, z)

      # If we have too many, we need to trim (but keep projections solid)
      # For now just take first 500 - this shouldn't happen with proper generation
      voxels = [{"xyz": list(v)} for v in list(voxel_set)[:count]]
      return {"voxels": voxels}, "Placebo thinking... hmmm..."

    # Generic case for other subpasses
    voxels = []
    for y in range(size):
      for x in range(size):
        for z in range(size):
          if (x + y + z) % size == 0:
            voxels.append({"xyz": [x, y, z]})

    while len(voxels) < count:
      x = random.randint(0, size - 1)
      y = random.randint(0, size - 1)
      z = random.randint(0, size - 1)
      element = {"xyz": [x, y, z]}
      if element not in voxels:
        voxels.append(element)

    return {"voxels": voxels}, "Placebo thinking... hmmm..."

  return None
