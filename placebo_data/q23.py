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

  return None
