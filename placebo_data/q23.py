import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    return {
      'earthworks': [{
        'xyzMin': [1, 1, 2],
        'xyzMax': [14, 14, 2],
        'material': 'Air'
      }]
    }, "Trivial. I just read the question."

  if subPass == 1:
    return {
      'earthworks': [{
        'xyzMin': [1, 1, 2],
        'xyzMax': [2, 2, 2],
        'material': 'Air'
      }, {
        'xyzMin': [1, 4, 2],
        'xyzMax': [2, 5, 2],
        'material': 'Air'
      }, {
        'xyzMin': [4, 4, 2],
        'xyzMax': [5, 5, 2],
        'material': 'Air'
      }]
    }, "Trivial. Just thinking about it and filling in the JSON"

  if subPass == 2:
    return {
      'earthworks': [{
        "xyzMin": [2, 2, 3],
        "xyzMax": [30, 30, 6],
        "material": "Rock"
      }, {
        "xyzMin": [3, 3, 3],
        "xyzMax": [29, 29, 6],
        "material": "Air"
      }]
    }, "Trivial. Just thinking about it and filling in the JSON"

  if subPass == 3:
    return {
      'earthworks': [{
        "xyzMin": [1, 1, 1],
        "xyzMax": [38, 38, 1],
        "material": "Air"
      }, {
        "xyzMin": [20, 20, 1],
        "xyzMax": [20, 20, 2],
        "material": "Air"
      }, {
        "xyzMin": [20, 20, 4],
        "xyzMax": [20, 20, 4],
        "material": "Rock"
      }, {
        "xyzMin": [21, 20, 2],
        "xyzMax": [21, 20, 4],
        "material": "Rock"
      }]
    }, "Take out a slice of dirt at z = 1. Add an airshaft. And a block above to ensure hidden. Add support for block."

  if subPass == 4:
    # 3 lakes on 3 different z levels (48x48 world)
    return {
      'earthworks': [

        # Lip around the world to make it a giant high lake with 3 chasms
        {
          "xyzMin": [0, 0, 2],
          "xyzMax": [47, 47, 6],
          "material": "Rock"
        },
        {
          "xyzMin": [1, 1, 6],
          "xyzMax": [46, 46, 6],
          "material": "Air"
        },
        {  # Tiny drainhole to stop it being one big lake
          "xyzMin": [46, 46, 6],
          "xyzMax": [47, 47, 6],
          "material": "Air"
        },

        # Chasms
        {
          "xyzMin": [5, 5, 1],
          "xyzMax": [6, 6, 6],
          "material": "Air"
        },
        {
          "xyzMin": [10, 10, 2],
          "xyzMax": [11, 11, 6],
          "material": "Air"
        },
        {
          "xyzMin": [15, 15, 3],
          "xyzMax": [16, 16, 6],
          "material": "Air"
        },
      ]
    }, "Create three separate basins at different heights"

  if subPass == 5:
    # Lake at least 6 voxels deep (56x56 world)
    # Dig at z=1 to create floor at z=0, then build walls from z=1-6 (6 levels: 1,2,3,4,5,6)
    return {
      'earthworks': [
        {
          "xyzMin": [10, 10, 1],
          "xyzMax": [40, 40, 7],
          "material": "Rock"
        },
        {
          "xyzMin": [11, 11, 1],
          "xyzMax": [39, 39, 7],
          "material": "Air"
        },
      ]
    }, "Dig to z=0 floor, walls z=1-6 for 6-deep water"

  if subPass == 6:
    # 2 lakes, each over 200 voxels in volume (64x64 world)
    return {
      'earthworks': [
        {
          "xyzMin": [1, 1, 1],
          "xyzMax": [29, 62, 5],
          "material": "Air"
        },
        {
          "xyzMin": [31, 1, 1],
          "xyzMax": [62, 62, 5],
          "material": "Air"
        },
      ]
    }, "Two walled containers for 200+ voxel lakes"

  if subPass == 7:
    # Ring-shaped lake surrounding a dry 3x3 center (48x48 world)
    # Dig moat around a central island at ground level
    return {
      'earthworks': [
        # Dig out a large area at z=2
        {
          "xyzMin": [15, 15, 2],
          "xyzMax": [32, 32, 2],
          "material": "Air"
        },
        # Put back a 3x3 island in the center
        {
          "xyzMin": [22, 22, 2],
          "xyzMax": [24, 24, 2],
          "material": "Rock"
        },
      ]
    }, "Dig moat around 3x3 island"

  if subPass == 8:
    # Water at z=3 AND z=6, but NO water at z=4 or z=5 (56x56 world)
    # Need two open basins at different heights - water fills from rain
    return {
      'earthworks': [
        # Lower basin: walls at z=2-3, floor stays solid, water at z=3
        {
          "xyzMin": [5, 5, 2],
          "xyzMax": [15, 5, 3],
          "material": "Rock"
        },
        {
          "xyzMin": [5, 15, 2],
          "xyzMax": [15, 15, 3],
          "material": "Rock"
        },
        {
          "xyzMin": [5, 6, 2],
          "xyzMax": [5, 14, 3],
          "material": "Rock"
        },
        {
          "xyzMin": [15, 6, 2],
          "xyzMax": [15, 14, 3],
          "material": "Rock"
        },
        {
          "xyzMin": [6, 6, 3],
          "xyzMax": [14, 14, 3],
          "material": "Air"
        },
        # Upper basin: build platform at z=5, walls at z=6, water at z=6
        {
          "xyzMin": [25, 25, 2],
          "xyzMax": [35, 35, 5],
          "material": "Rock"
        },
        {
          "xyzMin": [25, 25, 6],
          "xyzMax": [35, 25, 6],
          "material": "Rock"
        },
        {
          "xyzMin": [25, 35, 6],
          "xyzMax": [35, 35, 6],
          "material": "Rock"
        },
        {
          "xyzMin": [25, 26, 6],
          "xyzMax": [25, 34, 6],
          "material": "Rock"
        },
        {
          "xyzMin": [35, 26, 6],
          "xyzMax": [35, 34, 6],
          "material": "Rock"
        },
        {
          "xyzMin": [26, 26, 6],
          "xyzMax": [34, 34, 6],
          "material": "Air"
        },
      ]
    }, "Two open basins at z=3 and z=6"

  if subPass == 9:
    # EXACTLY 100 voxels of water (48x48 world)
    # 10x10x1 = 100 voxels exactly
    return {
      'earthworks': [
        {
          "xyzMin": [10, 10, 2],
          "xyzMax": [19, 19, 2],
          "material": "Air"
        },
      ]
    }, "10x10x1 pit = exactly 100 water voxels"

  if subPass == 10:
    # 4 separate underground lakes, each at least 5 voxels, none visible (64x64 world)
    # Each water voxel needs rock DIRECTLY above it. Use same approach as subpass 3.
    # Dig chambers at z=1, put rock cap at z=2 covering same x,y, fill rest with rock
    return {
      'earthworks': [
        # Chamber 1: 3x3 = 9 voxels at z=1, rock column above
        {
          "xyzMin": [5, 5, 1],
          "xyzMax": [7, 7, 3],
          "material": "Air"
        },
        {
          "xyzMin": [5, 5, 7],
          "xyzMax": [7, 7, 7],
          "material": "Rock"
        },
        {
          "xyzMin": [4, 4, 2],
          "xyzMax": [7, 4, 7],
          "material": "Rock"
        },

        # Chamber 2
        {
          "xyzMin": [50, 5, 1],
          "xyzMax": [52, 7, 3],
          "material": "Air"
        },
        {
          "xyzMin": [50, 5, 7],
          "xyzMax": [52, 7, 7],
          "material": "Rock"
        },
        {
          "xyzMin": [50, 4, 2],
          "xyzMax": [50, 4, 7],
          "material": "Rock"
        },
        # Chamber 3
        {
          "xyzMin": [5, 50, 1],
          "xyzMax": [7, 52, 3],
          "material": "Air"
        },
        {
          "xyzMin": [5, 50, 7],
          "xyzMax": [7, 52, 7],
          "material": "Rock"
        },
        {
          "xyzMin": [4, 50, 2],
          "xyzMax": [4, 50, 7],
          "material": "Rock"
        },
        # Chamber 4
        {
          "xyzMin": [50, 50, 1],
          "xyzMax": [52, 52, 3],
          "material": "Air"
        },
        {
          "xyzMin": [50, 50, 7],
          "xyzMax": [52, 52, 7],
          "material": "Rock"
        },
        {
          "xyzMin": [49, 50, 2],
          "xyzMax": [49, 50, 7],
          "material": "Rock"
        },
      ]
    }, "Four underground chambers with rock columns above"
