import itertools
import math
import sys

title = "Build a Lego(tm) hemispherical shell"

prompt = """
You have an unlimited number of Lego(tm) bricks, each of individual size 31.8mm * 15.8mm * 11.4mm but when assembled they are 
32mm * 16mm * 9.6mm due to interlocking studs and voids. Each brick has 8 studs, in a 2x4 layout. 

These bricks snap together. For example: A brick at (centroid=[0, 0, 4.8],r=90) is resting on the ground centred over the origin, 
and a second brick at (centroid=[0, 0, 14.4],r=180) is resting on the first brick with 4 interlocked studs (out of 8). A third brick at 
(centroid=[24, 0, 24],r=0) is snapped into 2 studs of the second brick, forming a 75% overhang. Were that third brick at 
[22,0,24] instead, its shell would intersect 2 studs of the Lego brick below it, and thus not be buildable.

Assemble the bricks such that they resemble a 3D hemispherical shell, with inner radius PARAM_A cm and outer radius PARAM_B cm, 
the centre of the hemisphere is at the origin (0,0,0).

Since it's impossible to create a perfect curve, the best score is one which is closer to the ideal curve, with
scoring being calculated based on the volume difference between the ideal curve and the actual brick structure. 
The structure needs to be buildable in 3D, so bricks can not overlap or be floating in mid air. A great answer does not 
contain any holes or missing bricks.

Blocks are being placed directly on a flat surface, i.e. without a base plate, so those resting on the ground can have
any orientation and are not confined to a specific grid structure. Connected blocks must follow legal Lego(tm) connection
rules and must not fall over when built.

Return a list of the bricks (location in xyz mm relative to the origin and rotation in degrees). 
"""

# Run the test 3 times, if the average score is below 0.1, consider all following
# tests a failure to save tokens, as they only get harder.
earlyFail = True
earlyFailThreshold = 0.1
earlyFailSubpassSampleCount = 3

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string",
      "description": "Optional explanation of your structure and build process."
    },
    "bricks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "Centroid": {
            "type": "array",
            "items": {
              "type": "number"
            }
          },
          "RotationDegrees": {
            "type": "number"
          }
        },
        "propertyOrdering": ["Centroid", "RotationDegrees"],
        "required": ["Centroid", "RotationDegrees"],
        "additionalProperties": False
      }
    }
  },
  "propertyOrdering": ["reasoning", "bricks"],
  "required": ["reasoning", "bricks"],
  "additionalProperties": False
}

referenceScad = """


module reference()
{
    difference()
    {
        sphere(PARAM_B * 10, $fn=16);
        sphere(PARAM_A * 10, $fn=16);
        translate([0,0,-500]) cube([1000,1000,1000], center=true);
    }
}
"""

promptChangeSummary = "Inner and outer radius parameters increase progressively across subpasses"

subpassParamSummary = [
  "4cm inner, 7cm outer. ~120 bricks", "8cm inner, 11cm outer. ~300 bricks",
  "15cm inner, 17cm outer ~400 bricks"
]

testParams = [(4, 7), (5, 8), (6, 9), (7, 10), (9, 13), (11, 15), (13, 16), (15, 17)]


def prepareSubpassPrompt(index):
  #if index == 1: raise StopIteration  # HACK while developing to save costs.
  if index >= len(testParams):
    raise StopIteration
  return prompt.replace("PARAM_A", str(testParams[index][0])).replace("PARAM_B",
                                                                      str(testParams[index][1]))


def prepareSubpassReferenceScad(index):
  if index >= len(testParams):
    raise StopIteration
  return referenceScad.replace("PARAM_A",
                               str(testParams[index][0])).replace("PARAM_B",
                                                                  str(testParams[index][1]))


#noMinkowski = True
usePreviewModeForRendering = True


def resultToScad(result, aiEngineName):
  import scad_format, OpenScad

  if len(result["bricks"]) == 0:
    return ""

  colors = [
    "\"White\"", "\"Black\"", "\"Red\"", "\"Blue\"", "\"Yellow\"", "\"Green\"", "[0,0,0.5]",
    "[0.5,0,0]", "\"Orange\"", "[210/255, 180/255, 140/255]", "[170/255, 140/255, 100/255]",
    "[92/255, 64/255, 51/255]", "[62/255, 38/255, 20/255]"
  ]

  scad = " {"
  for brick, colour in zip(result["bricks"], itertools.cycle(colors)):
    scad += "color(" + colour + ") "
    scad += "translate([" + str(brick["Centroid"][0]) + "," + \
      str(brick["Centroid"][1]) + "," + str(brick["Centroid"][2]) + "]) rotate([0,0," + \
      str(brick["RotationDegrees"]) + "]) cube([32,16,9.6], center=true);\n"

  return scad_format.format_code("module result(){ " + scad + "}}\n\n", OpenScad.formatConfig)


def validatePostVolume(result, score, resultVolume, referenceVolume, intersectionVolume,
                       differenceVolume):
  brickCount = len(result["bricks"])
  expectedBrickCount = referenceVolume / 9.6 / 16 / 32

  delta = abs(brickCount - expectedBrickCount)

  if delta < 1000:
    return score, ""

  print("Structure has " + str(brickCount) + \
      " bricks, but the union of the bricks created a volume of " + str(resultVolume) + " mm^3," +\
           " the expected volume is " + str(expectedBrickCount * 9.6 * 16 * 32))
  return score - 0.5, "50% penalty due to bricks overlapping: Volume error of " + str(
    round(delta)) + "mm3"


def postProcessScore(score, subPassIndex):
  # Packing efficiency of rectangle prism in sphere is about 75%. I couldn't find an exact figure
  # but it's close enough for this test.
  return min(1, score / 0.75)


def _get_brick_corners_xy(brick):
  """Get the 4 XY corner points of a brick, accounting for rotation."""
  cx, cy, _ = brick["Centroid"]
  rot_rad = math.radians(brick["RotationDegrees"])
  cos_r, sin_r = math.cos(rot_rad), math.sin(rot_rad)
  # Half-dimensions of brick
  hx, hy = 16, 8
  corners = []
  for dx, dy in [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]:
    rx = dx * cos_r - dy * sin_r
    ry = dx * sin_r + dy * cos_r
    corners.append((cx + rx, cy + ry))
  return corners


def _get_brick_aabb(brick):
  """Get axis-aligned bounding box for a brick (minx, max x, min y, max y, min z, max z)."""
  cx, cy, cz = brick["Centroid"]
  corners = _get_brick_corners_xy(brick)
  xs = [c[0] for c in corners]
  ys = [c[1] for c in corners]
  return (min(xs), max(xs), min(ys), max(ys), cz - 4.8, cz + 4.8)


def _boxes_overlap(b1, b2):
  """Check if two axis-aligned boxes overlap (strictly, not just touching)."""
  eps = 0.01  # Small tolerance to allow touching
  return (b1[0] < b2[1] - eps and b1[1] > b2[0] + eps and  # X overlap
          b1[2] < b2[3] - eps and b1[3] > b2[2] + eps and  # Y overlap
          b1[4] < b2[5] - eps and b1[5] > b2[4] + eps)  # Z overlap


def _boxes_support(upper, lower):
  """Check if lower brick can support upper brick (XY overlap and Z touching)."""
  eps = 0.5  # Tolerance for Z touching
  # Upper brick's bottom should be near lower brick's top
  z_touch = abs(upper[4] - lower[5]) < eps
  # XY must overlap
  xy_overlap = (upper[0] < lower[1] and upper[1] > lower[0] and upper[2] < lower[3]
                and upper[3] > lower[2])
  return z_touch and xy_overlap


def _bricks_connect(brick1, bounds1, brick2, bounds2):
  """Check if two bricks are connected (touching in Z with XY overlap)."""
  eps = 0.5
  # Check if they're in adjacent layers (Z touching)
  z_touch = (abs(bounds1[4] - bounds2[5]) < eps or abs(bounds2[4] - bounds1[5]) < eps)
  if not z_touch:
    return False
  # Check XY overlap
  xy_overlap = (bounds1[0] < bounds2[1] and bounds1[1] > bounds2[0] and bounds1[2] < bounds2[3]
                and bounds1[3] > bounds2[2])
  return xy_overlap


def _get_stud_grid_key(brick):
  """Get the stud grid origin for a brick, normalized to [0,8) range.
  
  Lego studs are on an 8mm grid. For bricks to connect, their stud grids must align.
  We compute where the brick's stud grid origin falls, modulo 8mm.
  """
  cx, cy, _ = brick["Centroid"]
  rot_rad = math.radians(brick["RotationDegrees"])
  cos_r, sin_r = math.cos(rot_rad), math.sin(rot_rad)

  # Transform brick center to its local coordinate system
  # In local coords, studs are at multiples of 8mm from center
  # We need to find where (0,0) of the global 8mm grid maps in local coords

  # Actually, simpler: find the global position of one stud, then mod 8
  # First stud is at local (-12, -4) for a 2x4 brick, or we can use the center
  # The center of a 2x4 is between studs, so studs are at offsets:
  # x: -12, -4, 4, 12 (for the 4-stud direction)
  # y: -4, 4 (for the 2-stud direction)

  # For grid alignment, we just need any stud position mod 8
  # Use the stud at local offset (-12, -4)
  local_stud_x, local_stud_y = -12, -4
  global_stud_x = cx + local_stud_x * cos_r - local_stud_y * sin_r
  global_stud_y = cy + local_stud_x * sin_r + local_stud_y * cos_r

  # Normalize to [0, 8) range
  grid_x = global_stud_x % 8
  grid_y = global_stud_y % 8

  return (round(grid_x, 2), round(grid_y, 2))


def _stud_grids_compatible(key1, key2):
  """Check if two stud grid keys are compatible (same grid, within tolerance).
  
  Also handles 90° relative rotations - when grids are rotated 90° they can still
  mesh because the stud pattern is on a square grid.
  """
  tol = 0.5

  def check_match(k1, k2):
    dx = abs(k1[0] - k2[0])
    dy = abs(k1[1] - k2[1])
    # Handle wraparound at 8mm boundary
    dx = min(dx, 8 - dx)
    dy = min(dy, 8 - dy)
    return dx < tol and dy < tol

  # Direct match
  if check_match(key1, key2):
    return True

  # 90° rotation: swap x and y of key2
  if check_match(key1, (key2[1], key2[0])):
    return True

  return False


def _convex_hull(points):
  """Compute convex hull of 2D points using Graham scan. Returns points in CCW order."""
  points = sorted(set(points))
  if len(points) <= 1:
    return points

  def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

  lower = []
  for p in points:
    while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
      lower.pop()
    lower.append(p)

  upper = []
  for p in reversed(points):
    while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
      upper.pop()
    upper.append(p)

  return lower[:-1] + upper[:-1]


def _point_in_convex_polygon(point, polygon):
  """Check if a point is inside a convex polygon (CCW order). Uses cross product."""
  if len(polygon) < 3:
    return False

  px, py = point
  n = len(polygon)
  for i in range(n):
    x1, y1 = polygon[i]
    x2, y2 = polygon[(i + 1) % n]
    # Cross product: if negative, point is outside (right of edge)
    cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    if cross < -0.01:  # Small tolerance
      return False
  return True


def _check_component_stability(component_indices, bricks, all_bounds):
  """Check if a connected component is stable (CoM over support polygon).
  
  Returns None if stable, or an error message if unstable.
  """
  if len(component_indices) == 1:
    return None  # Single brick on ground is always stable

  # Find ground-level bricks (layer 0) in this component
  ground_indices = []
  for idx in component_indices:
    layer = round((bricks[idx]["Centroid"][2] - 4.8) / 9.6)
    if layer == 0:
      ground_indices.append(idx)

  if not ground_indices:
    return None  # No ground bricks means floating - caught elsewhere

  # Collect all XY corner points of ground bricks to form support polygon
  support_points = []
  for idx in ground_indices:
    corners = _get_brick_corners_xy(bricks[idx])
    support_points.extend(corners)

  # Compute convex hull of support polygon
  support_hull = _convex_hull(support_points)
  if len(support_hull) < 3:
    return None  # Degenerate case

  # Calculate center of mass (all bricks equal mass, so average of centroids)
  total_x, total_y = 0, 0
  for idx in component_indices:
    cx, cy, _ = bricks[idx]["Centroid"]
    total_x += cx
    total_y += cy
  com_x = total_x / len(component_indices)
  com_y = total_y / len(component_indices)

  # Check if CoM is inside support polygon
  if not _point_in_convex_polygon((com_x, com_y), support_hull):
    return (f"Structure unstable: center of mass ({com_x:.1f}, {com_y:.1f}) "
            f"is outside support polygon of ground bricks")

  return None


def _find_connected_components(bricks, all_bounds):
  """Find connected components of bricks using union-find."""
  n = len(bricks)
  parent = list(range(n))

  def find(x):
    if parent[x] != x:
      parent[x] = find(parent[x])
    return parent[x]

  def union(x, y):
    px, py = find(x), find(y)
    if px != py:
      parent[px] = py

  # Check all pairs for connectivity
  for i in range(n):
    for j in range(i + 1, n):
      if _bricks_connect(bricks[i], all_bounds[i], bricks[j], all_bounds[j]):
        union(i, j)

  # Group by component
  components = {}
  for i in range(n):
    root = find(i)
    if root not in components:
      components[root] = []
    components[root].append(i)

  return list(components.values())


def earlyFailTest(result, subpass):
  # Get sphere radii in mm (params are in cm, *10 in scad)
  innerR, outerR = testParams[subpass]
  innerR *= 10
  outerR *= 10

  innerR2 = innerR * innerR
  outerR2 = outerR * outerR

  bricks = result["bricks"]

  # Check for empty result
  if len(bricks) == 0:
    return "No bricks provided"

  for i, brick in enumerate(bricks):
    cx, cy, cz = brick["Centroid"]

    # Z-level alignment check: bricks should be at layer heights
    # Layer 1 centroid at 4.8, layer 2 at 14.4, layer 3 at 24.0, etc.
    # z = 4.8 + n * 9.6 where n >= 0
    layer_index = (cz - 4.8) / 9.6
    if abs(layer_index - round(layer_index)) > 0.1:
      return f"Brick {brick} Z={cz} not at valid layer height (should be 4.8 + n*9.6)"

    # A brick below ground is invalid. Since it's 9.6mm tall, anything below 4.8 intersects
    # the ground.
    if cz < 4.8 - 0.1:
      return "A brick " + str(brick) + " below ground is invalid"

    cornerPoints = [[cx - 16, cy - 8, cz - 4.8], [cx + 16, cy - 8, cz - 4.8],
                    [cx + 16, cy + 8, cz - 4.8], [cx - 16, cy + 8, cz - 4.8],
                    [cx - 16, cy - 8, cz + 4.8], [cx + 16, cy - 8, cz + 4.8],
                    [cx + 16, cy + 8, cz + 4.8], [cx - 16, cy + 8, cz + 4.8]]

    # A brick wholly inside the inner sphere is invalid (in the hollow part)
    if all([p[0] * p[0] + p[1] * p[1] + p[2] * p[2] < innerR2 for p in cornerPoints]):
      return "A brick " + str(brick) + " wholly inside the inner sphere is redundant"

    # A brick wholly outside the outer sphere is invalid
    if all([p[0] * p[0] + p[1] * p[1] + p[2] * p[2] > outerR2 for p in cornerPoints]):
      return "A brick " + str(brick) + " wholly outside the outer sphere is a waste"

  # Check for duplicate bricks (same position and rotation)
  seen = set()
  for brick in bricks:
    key = (round(brick["Centroid"][0], 1), round(brick["Centroid"][1], 1),
           round(brick["Centroid"][2], 1), round(brick["RotationDegrees"] % 180, 0))
    if key in seen:
      return f"Duplicate brick at {brick}"
    seen.add(key)


def lateFailTest(result, subpass):
  # Get sphere radii in mm (params are in cm, *10 in scad)
  innerR, outerR = testParams[subpass]
  innerR *= 10
  outerR *= 10

  bricks = result["bricks"]

  # Precompute bounds for all bricks
  all_bounds = []

  for i, brick in enumerate(bricks):
    bounds = _get_brick_aabb(brick)
    all_bounds.append(bounds)

  # Check stud grid alignment within connected components
  components = _find_connected_components(bricks, all_bounds)
  for component in components:
    if len(component) < 2:
      continue  # Single brick, no alignment needed
    # Check each pair of adjacent bricks for stud compatibility
    for i, idx1 in enumerate(component):
      for idx2 in component[i + 1:]:
        b1, b2 = bricks[idx1], bricks[idx2]
        # Same XY center: studs align only if relative rotation is multiple of 90°
        dx = abs(b1["Centroid"][0] - b2["Centroid"][0])
        dy = abs(b1["Centroid"][1] - b2["Centroid"][1])
        if dx < 0.5 and dy < 0.5:
          rel_rot = abs(b1["RotationDegrees"] - b2["RotationDegrees"]) % 90
          if rel_rot < 1 or rel_rot > 89:  # Within 1° of a 90° multiple
            continue  # Same center, 90° multiple rotation, compatible
          return (f"Stud grid misalignment: bricks at same center but "
                  f"{abs(b1['RotationDegrees'] - b2['RotationDegrees']):.1f}° relative rotation")
        # Otherwise check stud grid alignment
        key1 = _get_stud_grid_key(b1)
        key2 = _get_stud_grid_key(b2)
        if not _stud_grids_compatible(key1, key2):
          return (f"Stud grid misalignment in connected component: "
                  f"brick {b1} grid {key1} vs brick {b2} grid {key2}")

  # Check stability of each connected component (CoM must be over support polygon)
  for component in components:
    stability_error = _check_component_stability(component, bricks, all_bounds)
    if stability_error:
      return stability_error

  # Check that all bricks are supported (on ground, by brick below, or hanging from above)
  # Group bricks by layer
  layer_bricks = {}
  for i, brick in enumerate(bricks):
    layer = round((brick["Centroid"][2] - 4.8) / 9.6)
    if layer not in layer_bricks:
      layer_bricks[layer] = []
    layer_bricks[layer].append((i, all_bounds[i]))

  # Track which bricks are supported
  supported_bricks = set()

  # Pass 1: Walk ground-up, marking bricks supported from below
  for layer in sorted(layer_bricks.keys()):
    if layer == 0:
      # Ground layer bricks are always supported
      for idx, _ in layer_bricks[layer]:
        supported_bricks.add(idx)
      continue

    for idx, bounds in layer_bricks[layer]:
      # Check if resting on any supported brick in the layer below
      if layer - 1 in layer_bricks:
        for lower_idx, lower_bounds in layer_bricks[layer - 1]:
          if lower_idx in supported_bricks and _boxes_support(bounds, lower_bounds):
            supported_bricks.add(idx)
            break

  # Pass 2: Walk top-down, marking bricks that hang from supported bricks above
  # (Lego studs can hold bricks from above due to interlocking)
  changed = True
  while changed:
    changed = False
    for layer in sorted(layer_bricks.keys(), reverse=True):
      if layer + 1 not in layer_bricks:
        continue
      for idx, bounds in layer_bricks[layer]:
        if idx in supported_bricks:
          continue  # Already supported
        # Check if hanging from any supported brick in the layer above
        for upper_idx, upper_bounds in layer_bricks[layer + 1]:
          if upper_idx in supported_bricks and _boxes_support(upper_bounds, bounds):
            supported_bricks.add(idx)
            changed = True
            break

  # Check if any bricks are still unsupported
  for layer in layer_bricks:
    for idx, _ in layer_bricks[layer]:
      if idx not in supported_bricks:
        return f"Brick {bricks[idx]} is floating (not supported from below or held from above)"


highLevelSummary = """
Lego bricks look like they'd benefit from voxelization, but they really don't.
<br><br>
So most reasoning models try to voxelise the problem in Python, and then struggle to convert
that back to Lego bricks.<br><br>They end up losing points for overlapping bricks or bricks
entirely underground or outside of the hemispheres.
"""

if __name__ == "__main__":

  def runBothTests(bricks: list):
    """Run both early and late fail tests, return first error or None."""
    result = {"bricks": bricks}
    errors = earlyFailTest(result, 0)
    if errors:
      return errors
    errors = lateFailTest(result, 0)
    return errors

  def shouldPass(case: str, bricks: list):
    errors = runBothTests(bricks)
    if errors:
      print("Failure: (" + case + " ): " + errors)
      sys.exit(1)
    print("Successfully marked valid - " + case)

  def shouldFail(case: str, bricks: list):
    errors = runBothTests(bricks)
    if not errors:
      print("Didn't fail: (" + case + " )!")
      sys.exit(1)
    print("Successfully failed - " + case)

  shouldFail("Empty", [])

  shouldFail("Single brick intersecting the ground", [{
    "Centroid": [55, 0, 0],
    "RotationDegrees": 0
  }])

  shouldFail("Single brick in the centre of the inner sphere", [{
    "Centroid": [0, 0, 4.8],
    "RotationDegrees": 0
  }])

  shouldPass("Single brick between the two spheres", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }])

  shouldFail("Floating brick", [{"Centroid": [55, 0, 10], "RotationDegrees": 0}])

  shouldPass("Two disconnected off rotation bricks", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }, {
    "Centroid": [-55, 0, 4.8],
    "RotationDegrees": 5
  }])

  # Stacked bricks tests
  shouldPass("Two stacked bricks", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }, {
    "Centroid": [55, 0, 14.4],
    "RotationDegrees": 0
  }])

  # Stacked bricks tests
  shouldPass("Two stacked bricks at 90 degree angles - central 4 studs interlock",
             [{
               "Centroid": [55, 0, 4.8],
               "RotationDegrees": 0
             }, {
               "Centroid": [55, 0, 14.4],
               "RotationDegrees": 90
             }])

  shouldPass("Two stacked bricks at 90 degree angles but off axis - central 4 studs interlock",
             [{
               "Centroid": [55, 0, 4.8],
               "RotationDegrees": -45
             }, {
               "Centroid": [55, 0, 14.4],
               "RotationDegrees": 45
             }])

  # +---+---+      +---------+
  # |   |   |      |         |
  # |   |   |  and +---------+
  # |   |   |      |         |
  # +---+---+      +---------+

  shouldPass(
    "Two adjacent bricks with two adjacent bricks stacked on top, rotated 90 degrees, should also obviously work",
    [{
      "Centroid": [55, -8, 4.8],
      "RotationDegrees": 0
    }, {
      "Centroid": [55, 8, 4.8],
      "RotationDegrees": 180
    }, {
      "Centroid": [55 - 8, 0, 14.4],
      "RotationDegrees": 90
    }, {
      "Centroid": [55 + 8, 0, 14.4],
      "RotationDegrees": 270
    }])

  shouldFail("Two stacked bricks at same center but 30 degree relative rotation",
             [{
               "Centroid": [55, 0, 4.8],
               "RotationDegrees": 0
             }, {
               "Centroid": [55, 0, 14.4],
               "RotationDegrees": 30
             }])

  shouldFail(
    "Brick at wrong Z level",
    [
      {
        "Centroid": [55, 0, 4.8],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55, 0, 12.0],  # Should be 14.4
        "RotationDegrees": 0
      }
    ])

  # Duplicate brick test
  shouldFail("Duplicate bricks", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }, {
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }])

  # Stud grid alignment tests
  shouldPass(
    "Two stacked bricks with 8mm offset (valid stud alignment)",
    [
      {
        "Centroid": [55, 0, 4.8],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 8, 0, 14.4],  # Shifted by one stud
        "RotationDegrees": 0
      }
    ])

  shouldFail(
    "Two stacked bricks with invalid stud alignment",
    [
      {
        "Centroid": [55, 0, 4.8],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 5, 0, 14.4],  # 5mm offset doesn't align studs
        "RotationDegrees": 0
      }
    ])

  # Stability tests
  shouldPass(
    "Stable overhang (CoM over base)",
    [
      {
        "Centroid": [55, 0, 4.8],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 8, 0, 14.4],  # Small overhang
        "RotationDegrees": 0
      }
    ])

  shouldFail("Unstable staircase (CoM outside base)", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }, {
    "Centroid": [55 + 24, 0, 14.4],
    "RotationDegrees": 0
  }, {
    "Centroid": [55 + 48, 0, 24.0],
    "RotationDegrees": 0
  }, {
    "Centroid": [55 + 72, 0, 33.6],
    "RotationDegrees": 0
  }])

  # Rotated brick tests
  shouldPass("Brick at 90 degrees", [{"Centroid": [55, 0, 4.8], "RotationDegrees": 90}])

  shouldPass("Brick at 45 degrees (arbitrary rotation allowed on ground)", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 45
  }])

  # Outside outer sphere
  shouldFail("Brick outside outer sphere", [{"Centroid": [100, 0, 4.8], "RotationDegrees": 0}])

  # Ring of bricks (stable structure)
  shouldPass("Ring of 4 bricks on ground (stable)", [{
    "Centroid": [55, 0, 4.8],
    "RotationDegrees": 0
  }, {
    "Centroid": [0, 55, 4.8],
    "RotationDegrees": 90
  }, {
    "Centroid": [-55, 0, 4.8],
    "RotationDegrees": 0
  }, {
    "Centroid": [0, -55, 4.8],
    "RotationDegrees": 90
  }])

  # Hanging brick tests (held from above by interlocking studs)
  shouldPass(
    "Brick hanging from supported brick above",
    [
      {
        "Centroid": [55, 0, 4.8],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55, 0, 14.4],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 8, 0, 24.0],  # Top brick, supported from below
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 8, 0, 14.4],  # This brick hangs from the one above
        "RotationDegrees": 0
      }
    ])

  shouldFail(
    "Brick hanging from unsupported brick",
    [
      {
        "Centroid": [55, 0, 4.8],
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 40, 0, 24.0],  # Floating brick (no support)
        "RotationDegrees": 0
      },
      {
        "Centroid": [55 + 40, 0, 14.4],  # Can't hang from floating brick
        "RotationDegrees": 0
      }
    ])

  print("\nAll tests passed!")
