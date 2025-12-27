import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    return {
      'reasoning':
      '',
      'voxels': [{
        'xyz': [5, 5, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 5, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 5, 2],
        'material': 'Air'
      }, {
        'xyz': [8, 5, 2],
        'material': 'Air'
      }, {
        'xyz': [9, 5, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 5, 2],
        'material': 'Air'
      }, {
        'xyz': [5, 6, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 6, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 6, 2],
        'material': 'Air'
      }, {
        'xyz': [8, 6, 2],
        'material': 'Air'
      }, {
        'xyz': [9, 6, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 6, 2],
        'material': 'Air'
      }, {
        'xyz': [5, 7, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 7, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 7, 2],
        'material': 'Air'
      }, {
        'xyz': [8, 7, 2],
        'material': 'Air'
      }, {
        'xyz': [9, 7, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 7, 2],
        'material': 'Air'
      }, {
        'xyz': [5, 8, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 8, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 8, 2],
        'material': 'Air'
      }, {
        'xyz': [8, 8, 2],
        'material': 'Air'
      }, {
        'xyz': [9, 8, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 8, 2],
        'material': 'Air'
      }, {
        'xyz': [5, 9, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 9, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 9, 2],
        'material': 'Air'
      }, {
        'xyz': [8, 9, 2],
        'material': 'Air'
      }, {
        'xyz': [9, 9, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 9, 2],
        'material': 'Air'
      }, {
        'xyz': [5, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [8, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [9, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 10, 2],
        'material': 'Air'
      }]
    }, ""

  if subPass == 1:
    return {
      'reasoning':
      '',
      'voxels': [{
        'xyz': [10, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [10, 13, 2],
        'material': 'Air'
      }, {
        'xyz': [11, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [11, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [11, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [11, 13, 2],
        'material': 'Air'
      }, {
        'xyz': [12, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [12, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [12, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [12, 13, 2],
        'material': 'Air'
      }, {
        'xyz': [13, 10, 2],
        'material': 'Air'
      }, {
        'xyz': [13, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [13, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [13, 13, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [6, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [7, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 12, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 11, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 12, 2],
        'material': 'Air'
      }]
    }, ""

  if subPass == 2:
    return {
      'reasoning':
      '',
      'voxels': [{
        'xyz': [13, 13, 5],
        'material': 'Dirt'
      }, {
        'xyz': [14, 13, 5],
        'material': 'Dirt'
      }, {
        'xyz': [15, 13, 5],
        'material': 'Dirt'
      }, {
        'xyz': [16, 13, 5],
        'material': 'Dirt'
      }, {
        'xyz': [17, 13, 5],
        'material': 'Dirt'
      }, {
        'xyz': [18, 13, 5],
        'material': 'Dirt'
      }, {
        'xyz': [13, 14, 5],
        'material': 'Dirt'
      }, {
        'xyz': [14, 14, 5],
        'material': 'Dirt'
      }, {
        'xyz': [15, 14, 5],
        'material': 'Dirt'
      }, {
        'xyz': [16, 14, 5],
        'material': 'Dirt'
      }, {
        'xyz': [17, 14, 5],
        'material': 'Dirt'
      }, {
        'xyz': [18, 14, 5],
        'material': 'Dirt'
      }, {
        'xyz': [13, 15, 5],
        'material': 'Dirt'
      }, {
        'xyz': [14, 15, 5],
        'material': 'Dirt'
      }, {
        'xyz': [15, 15, 5],
        'material': 'Dirt'
      }, {
        'xyz': [16, 15, 5],
        'material': 'Dirt'
      }, {
        'xyz': [17, 15, 5],
        'material': 'Dirt'
      }, {
        'xyz': [18, 15, 5],
        'material': 'Dirt'
      }, {
        'xyz': [13, 16, 5],
        'material': 'Dirt'
      }, {
        'xyz': [14, 16, 5],
        'material': 'Dirt'
      }, {
        'xyz': [15, 16, 5],
        'material': 'Dirt'
      }, {
        'xyz': [16, 16, 5],
        'material': 'Dirt'
      }, {
        'xyz': [17, 16, 5],
        'material': 'Dirt'
      }, {
        'xyz': [18, 16, 5],
        'material': 'Dirt'
      }, {
        'xyz': [13, 17, 5],
        'material': 'Dirt'
      }, {
        'xyz': [14, 17, 5],
        'material': 'Dirt'
      }, {
        'xyz': [15, 17, 5],
        'material': 'Dirt'
      }, {
        'xyz': [16, 17, 5],
        'material': 'Dirt'
      }, {
        'xyz': [17, 17, 5],
        'material': 'Dirt'
      }, {
        'xyz': [18, 17, 5],
        'material': 'Dirt'
      }, {
        'xyz': [13, 18, 5],
        'material': 'Dirt'
      }, {
        'xyz': [14, 18, 5],
        'material': 'Dirt'
      }, {
        'xyz': [15, 18, 5],
        'material': 'Dirt'
      }, {
        'xyz': [16, 18, 5],
        'material': 'Dirt'
      }, {
        'xyz': [17, 18, 5],
        'material': 'Dirt'
      }, {
        'xyz': [18, 18, 5],
        'material': 'Dirt'
      }, {
        'xyz': [13, 13, 6],
        'material': 'Dirt'
      }, {
        'xyz': [14, 13, 6],
        'material': 'Dirt'
      }, {
        'xyz': [15, 13, 6],
        'material': 'Dirt'
      }, {
        'xyz': [16, 13, 6],
        'material': 'Dirt'
      }, {
        'xyz': [17, 13, 6],
        'material': 'Dirt'
      }, {
        'xyz': [18, 13, 6],
        'material': 'Dirt'
      }, {
        'xyz': [13, 14, 6],
        'material': 'Dirt'
      }, {
        'xyz': [18, 14, 6],
        'material': 'Dirt'
      }, {
        'xyz': [13, 15, 6],
        'material': 'Dirt'
      }, {
        'xyz': [18, 15, 6],
        'material': 'Dirt'
      }, {
        'xyz': [13, 16, 6],
        'material': 'Dirt'
      }, {
        'xyz': [18, 16, 6],
        'material': 'Dirt'
      }, {
        'xyz': [13, 17, 6],
        'material': 'Dirt'
      }, {
        'xyz': [18, 17, 6],
        'material': 'Dirt'
      }, {
        'xyz': [13, 18, 6],
        'material': 'Dirt'
      }, {
        'xyz': [14, 18, 6],
        'material': 'Dirt'
      }, {
        'xyz': [15, 18, 6],
        'material': 'Dirt'
      }, {
        'xyz': [16, 18, 6],
        'material': 'Dirt'
      }, {
        'xyz': [17, 18, 6],
        'material': 'Dirt'
      }, {
        'xyz': [18, 18, 6],
        'material': 'Dirt'
      }, {
        'xyz': [13, 13, 7],
        'material': 'Dirt'
      }, {
        'xyz': [14, 13, 7],
        'material': 'Dirt'
      }, {
        'xyz': [15, 13, 7],
        'material': 'Dirt'
      }, {
        'xyz': [16, 13, 7],
        'material': 'Dirt'
      }, {
        'xyz': [17, 13, 7],
        'material': 'Dirt'
      }, {
        'xyz': [18, 13, 7],
        'material': 'Dirt'
      }, {
        'xyz': [13, 14, 7],
        'material': 'Dirt'
      }, {
        'xyz': [18, 14, 7],
        'material': 'Dirt'
      }, {
        'xyz': [13, 15, 7],
        'material': 'Dirt'
      }, {
        'xyz': [18, 15, 7],
        'material': 'Dirt'
      }, {
        'xyz': [13, 16, 7],
        'material': 'Dirt'
      }, {
        'xyz': [18, 16, 7],
        'material': 'Dirt'
      }, {
        'xyz': [13, 17, 7],
        'material': 'Dirt'
      }, {
        'xyz': [18, 17, 7],
        'material': 'Dirt'
      }, {
        'xyz': [13, 18, 7],
        'material': 'Dirt'
      }, {
        'xyz': [14, 18, 7],
        'material': 'Dirt'
      }, {
        'xyz': [15, 18, 7],
        'material': 'Dirt'
      }, {
        'xyz': [16, 18, 7],
        'material': 'Dirt'
      }, {
        'xyz': [17, 18, 7],
        'material': 'Dirt'
      }, {
        'xyz': [18, 18, 7],
        'material': 'Dirt'
      }]
    }, ""

  if subPass == 3:
    return {
      'reasoning':
      '',
      'voxels': [{
        'xyz': [19, 19, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 20, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 19, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 20, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 19, 1],
        'material': 'Air'
      }, {
        'xyz': [21, 19, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 19, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 20, 1],
        'material': 'Air'
      }, {
        'xyz': [21, 20, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 20, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 21, 1],
        'material': 'Air'
      }, {
        'xyz': [21, 21, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 22, 1],
        'material': 'Air'
      }, {
        'xyz': [21, 22, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 22, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 23, 1],
        'material': 'Air'
      }, {
        'xyz': [21, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 23, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 19, 1],
        'material': 'Air'
      }, {
        'xyz': [22, 19, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 19, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 20, 1],
        'material': 'Air'
      }, {
        'xyz': [22, 20, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 20, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 21, 1],
        'material': 'Air'
      }, {
        'xyz': [22, 21, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 22, 1],
        'material': 'Air'
      }, {
        'xyz': [22, 22, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 22, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 23, 1],
        'material': 'Air'
      }, {
        'xyz': [22, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 23, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 21, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 22, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 22, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 23, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 25, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 26, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 28, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 29, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 30, 3],
        'material': 'Dirt'
      }, {
        'xyz': [19, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [19, 30, 0],
        'material': 'Air'
      }]
    }, ""
  if subPass == 4:
    return {
      'reasoning':
      'Create a small walled catch-basin at z=3 directly under the rainfall so a stable surface lake forms there; once it fills, excess water overtops at z=4 and spills outward. Place a shallow dug pit (z=2) adjacent to the wall so the first overflow fills and becomes a second lake. Place a deeper dug pit (z=1) farther out and feed it via an open z=2 trench that also has a drain drop at the map edge, so any water left in the trench drains away, leaving the lowest lake’s top at z=1.',
      'voxels': [{
        'xyz': [21, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [23, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [25, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [26, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 21, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [22, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [23, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [25, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [26, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 22, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 22, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 23, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 23, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 25, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 25, 3],
        'material': 'Dirt'
      }, {
        'xyz': [21, 26, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 26, 3],
        'material': 'Dirt'
      }, {
        'xyz': [28, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [31, 23, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [31, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [31, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [31, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 23, 1],
        'material': 'Air'
      }, {
        'xyz': [35, 23, 1],
        'material': 'Air'
      }, {
        'xyz': [36, 23, 1],
        'material': 'Air'
      }, {
        'xyz': [37, 23, 1],
        'material': 'Air'
      }, {
        'xyz': [34, 24, 1],
        'material': 'Air'
      }, {
        'xyz': [35, 24, 1],
        'material': 'Air'
      }, {
        'xyz': [36, 24, 1],
        'material': 'Air'
      }, {
        'xyz': [37, 24, 1],
        'material': 'Air'
      }, {
        'xyz': [34, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [35, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [36, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [37, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [34, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [35, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [36, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [37, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [34, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 24, 1],
        'material': 'Air'
      }]
    }, ""

  if subPass == 5:
    return {
      'reasoning':
      'Create a contained, deep basin directly under the rainfall point so water cannot reach the map edges. Dig out a 6×6 pit down to z=1 (keep z=0 as dirt so water can’t touch the world bottom and drain), and build a 1-voxel-thick dirt retaining wall ring around it from z=3 up to z=7. With 1000s of rainfall voxels, this basin will fill to at least z=6, yielding a lake depth ≥6 (bottom at z=1, surface ≥z=6).',
      'voxels': [{
        'xyz': [25, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [25, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [25, 27, 1],
        'material': 'Air'
      }, {
        'xyz': [25, 28, 1],
        'material': 'Air'
      }, {
        'xyz': [25, 29, 1],
        'material': 'Air'
      }, {
        'xyz': [25, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [26, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [26, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [26, 27, 1],
        'material': 'Air'
      }, {
        'xyz': [26, 28, 1],
        'material': 'Air'
      }, {
        'xyz': [26, 29, 1],
        'material': 'Air'
      }, {
        'xyz': [26, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [27, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [27, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [27, 27, 1],
        'material': 'Air'
      }, {
        'xyz': [27, 28, 1],
        'material': 'Air'
      }, {
        'xyz': [27, 29, 1],
        'material': 'Air'
      }, {
        'xyz': [27, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [28, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [28, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [28, 27, 1],
        'material': 'Air'
      }, {
        'xyz': [28, 28, 1],
        'material': 'Air'
      }, {
        'xyz': [28, 29, 1],
        'material': 'Air'
      }, {
        'xyz': [28, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [29, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [29, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [29, 27, 1],
        'material': 'Air'
      }, {
        'xyz': [29, 28, 1],
        'material': 'Air'
      }, {
        'xyz': [29, 29, 1],
        'material': 'Air'
      }, {
        'xyz': [29, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [30, 25, 1],
        'material': 'Air'
      }, {
        'xyz': [30, 26, 1],
        'material': 'Air'
      }, {
        'xyz': [30, 27, 1],
        'material': 'Air'
      }, {
        'xyz': [30, 28, 1],
        'material': 'Air'
      }, {
        'xyz': [30, 29, 1],
        'material': 'Air'
      }, {
        'xyz': [30, 30, 1],
        'material': 'Air'
      }, {
        'xyz': [24, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 25, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 26, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 28, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 29, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 30, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 25, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 26, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 27, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 28, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 29, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 30, 3],
        'material': 'Dirt'
      }, {
        'xyz': [31, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [25, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [26, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [28, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [29, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [30, 24, 3],
        'material': 'Dirt'
      }, {
        'xyz': [25, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [26, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [27, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [28, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [29, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [30, 31, 3],
        'material': 'Dirt'
      }, {
        'xyz': [24, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 25, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 26, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 27, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 28, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 29, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 30, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 25, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 26, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 27, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 28, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 29, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 30, 4],
        'material': 'Dirt'
      }, {
        'xyz': [31, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [25, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [26, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [27, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [28, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [29, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [30, 24, 4],
        'material': 'Dirt'
      }, {
        'xyz': [25, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [26, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [27, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [28, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [29, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [30, 31, 4],
        'material': 'Dirt'
      }, {
        'xyz': [24, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 25, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 26, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 27, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 28, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 29, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 30, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 25, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 26, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 27, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 28, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 29, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 30, 5],
        'material': 'Dirt'
      }, {
        'xyz': [31, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [25, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [26, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [27, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [28, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [29, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [30, 24, 5],
        'material': 'Dirt'
      }, {
        'xyz': [25, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [26, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [27, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [28, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [29, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [30, 31, 5],
        'material': 'Dirt'
      }, {
        'xyz': [24, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 25, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 26, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 27, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 28, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 29, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 30, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 25, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 26, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 27, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 28, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 29, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 30, 6],
        'material': 'Dirt'
      }, {
        'xyz': [31, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [25, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [26, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [27, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [28, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [29, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [30, 24, 6],
        'material': 'Dirt'
      }, {
        'xyz': [25, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [26, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [27, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [28, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [29, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [30, 31, 6],
        'material': 'Dirt'
      }, {
        'xyz': [24, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 25, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 26, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 27, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 28, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 29, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 30, 7],
        'material': 'Dirt'
      }, {
        'xyz': [24, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 25, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 26, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 27, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 28, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 29, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 30, 7],
        'material': 'Dirt'
      }, {
        'xyz': [31, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [25, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [26, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [27, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [28, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [29, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [30, 24, 7],
        'material': 'Dirt'
      }, {
        'xyz': [25, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [26, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [27, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [28, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [29, 31, 7],
        'material': 'Dirt'
      }, {
        'xyz': [30, 31, 7],
        'material': 'Dirt'
      }]
    }, ""

  if subPass == 6:
    return {
      'reasoning':
      'Excavate two separate shallow basins (1 voxel deep) in the top dirt layer (z=2). Rainwater will seek these z=2 air pockets, fall in, and then be unable to drain further because z=1 remains solid dirt and the basins are fully surrounded by dirt at z=2 (no path to map edges). Each basin is 15×14=210 voxels, so when filled they form two distinct lakes, each >200 voxels in volume, while excess rain continues to run off the map edges.',
      'voxels': [{
        'xyz': [16, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 24, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 25, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 26, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 27, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 28, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 29, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 30, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 31, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 32, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 33, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 34, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 35, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 36, 2],
        'material': 'Air'
      }, {
        'xyz': [16, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [17, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [18, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [19, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [20, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [21, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [22, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [23, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [24, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [25, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [26, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [27, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [28, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [29, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [30, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [34, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [35, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [36, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [37, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [38, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [39, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [40, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [41, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [42, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [43, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [44, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [45, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [46, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [47, 37, 2],
        'material': 'Air'
      }, {
        'xyz': [48, 37, 2],
        'material': 'Air'
      }]
    }, ""

  return None
