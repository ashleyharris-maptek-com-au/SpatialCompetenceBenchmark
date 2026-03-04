import random, os, math, heapq
import numpy as np
from scipy.ndimage import gaussian_filter
import OpenScad as vc
from LLMBenchCore.ResultPaths import result_path

tags = ["3D", "Visual Memory", "Photo Stiching", "Voxels"]

title = "Can you navigate a mountain range without a heightmap?"
skip = True

# Heightmap parameters
MAP_SIZE = 64
HEIGHT_SCALE = 20.0
random.seed(44)
np.random.seed(44)


def generate_perlin_heightmap(size, octaves=4, persistence=0.5):
  """Generate a heightmap using layered noise (Perlin-like)."""
  heightmap = np.zeros((size, size))

  for octave in range(octaves):
    freq = 2**octave
    amplitude = persistence**octave

    # Generate random gradients at grid points
    grid_size = max(2, size // (freq * 4))
    noise = np.random.randn(grid_size, grid_size)

    # Upsample with interpolation
    from scipy.ndimage import zoom
    upsampled = zoom(noise, size / grid_size, order=3)

    # Crop to exact size if needed
    upsampled = upsampled[:size, :size]

    heightmap += upsampled * amplitude

  # Normalize to 0-1 range then scale
  heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())

  # Apply gaussian smoothing for nicer terrain
  heightmap = gaussian_filter(heightmap, sigma=1.5)

  return heightmap * HEIGHT_SCALE


def find_local_maxima(heightmap, min_distance=10):
  """Find local maxima (hilltops) in the heightmap."""
  from scipy.ndimage import maximum_filter

  neighborhood_size = min_distance
  local_max = maximum_filter(heightmap, size=neighborhood_size)
  peaks = (heightmap == local_max)

  # Get coordinates of peaks
  peak_coords = np.argwhere(peaks)
  peak_heights = [heightmap[y, x] for y, x in peak_coords]

  # Sort by height descending
  sorted_indices = np.argsort(peak_heights)[::-1]
  return [(peak_coords[i][1], peak_coords[i][0], peak_heights[i]) for i in sorted_indices]


def find_start_and_end(heightmap):
  """Find start (highest peak) and end (far-away high peak)."""
  peaks = find_local_maxima(heightmap, min_distance=8)

  if len(peaks) < 2:
    # Fallback: just use highest and a far point
    max_idx = np.unravel_index(np.argmax(heightmap), heightmap.shape)
    start = (max_idx[1], max_idx[0])
    # Find far corner with decent height
    corners = [(5, 5), (5, MAP_SIZE - 6), (MAP_SIZE - 6, 5), (MAP_SIZE - 6, MAP_SIZE - 6)]
    best_end = max(corners,
                   key=lambda c: heightmap[c[1], c[0]] - 0.1 * math.sqrt((c[0] - start[0])**2 +
                                                                         (c[1] - start[1])**2))
    return start, best_end

  start = (peaks[0][0], peaks[0][1])

  # Find a peak that's far away but still reasonably high
  best_end = None
  best_score = -float('inf')

  for x, y, h in peaks[1:20]:  # Check top 20 peaks
    dist = math.sqrt((x - start[0])**2 + (y - start[1])**2)
    if dist < MAP_SIZE * 0.4:  # Must be at least 40% of map size away
      continue
    # Score: balance height and distance
    score = h + dist * 0.3
    if score > best_score:
      best_score = score
      best_end = (x, y)

  if best_end is None:
    # Fallback: use second highest peak
    best_end = (peaks[1][0], peaks[1][1])

  return start, best_end


def calculate_slope(heightmap, x1, y1, x2, y2):
  """Calculate slope between two adjacent cells."""
  h1 = heightmap[y1, x1]
  h2 = heightmap[y2, x2]

  # Horizontal distance (diagonal = sqrt(2), cardinal = 1)
  horiz_dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

  # Slope = rise / run (absolute value since we care about steepness)
  return abs(h2 - h1) / horiz_dist


def solve_optimal_path(heightmap, start, end):
  """
  Find optimal path minimizing worst instantaneous slope using modified Dijkstra.
  This is a minimax path problem - minimize the maximum edge weight.
  """
  rows, cols = heightmap.shape

  # Priority queue: (max_slope_so_far, x, y)
  pq = [(0, start[0], start[1])]

  # Track best (minimum worst slope) to reach each cell
  best_worst_slope = np.full((rows, cols), float('inf'))
  best_worst_slope[start[1], start[0]] = 0

  # Track path
  came_from = {}

  # 8-directional movement
  directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

  while pq:
    worst_slope, x, y = heapq.heappop(pq)

    if (x, y) == end:
      break

    if worst_slope > best_worst_slope[y, x]:
      continue

    for dx, dy in directions:
      nx, ny = x + dx, y + dy

      if 0 <= nx < cols and 0 <= ny < rows:
        edge_slope = calculate_slope(heightmap, x, y, nx, ny)
        new_worst = max(worst_slope, edge_slope)

        if new_worst < best_worst_slope[ny, nx]:
          best_worst_slope[ny, nx] = new_worst
          came_from[(nx, ny)] = (x, y)
          heapq.heappush(pq, (new_worst, nx, ny))

  # Reconstruct path
  path = []
  current = end
  while current in came_from:
    path.append(current)
    current = came_from[current]
  path.append(start)
  path.reverse()

  return path, best_worst_slope[end[1], end[0]]


def path_to_directions(path):
  """Convert path coordinates to direction string (space-separated)."""
  directions = []
  for i in range(len(path) - 1):
    x1, y1 = path[i]
    x2, y2 = path[i + 1]
    dx, dy = x2 - x1, y2 - y1

    # Map dx, dy to direction string
    dir_map = {
      (1, 0): 'e',
      (-1, 0): 'w',
      (0, 1): 's',
      (0, -1): 'n',
      (1, 1): 'se',
      (1, -1): 'ne',
      (-1, 1): 'sw',
      (-1, -1): 'nw'
    }
    directions.append(dir_map.get((dx, dy), '?'))

  return ' '.join(directions)


# Generate the heightmap and find start/end
heightmap = generate_perlin_heightmap(MAP_SIZE)
_start, _end = find_start_and_end(heightmap)
start_pos = (int(_start[0]), int(_start[1]))
end_pos = (int(_end[0]), int(_end[1]))

# Solve optimal path
optimal_path, optimal_worst_slope = solve_optimal_path(heightmap, start_pos, end_pos)
optimal_directions = path_to_directions(optimal_path)


def renderHeightmapAsPng():
  """Render heightmap as 3D terrain with OpenSCAD."""
  import PIL.Image as Image

  scad = "// Heightmap terrain\n"

  # Create terrain as a polyhedron or as individual cubes
  # For simplicity, use scaled cubes at each grid point
  step = 2  # Sample every 2nd point to reduce complexity

  for y in range(0, MAP_SIZE, step):
    for x in range(0, MAP_SIZE, step):
      h = heightmap[y, x]
      norm_h = h / HEIGHT_SCALE
      r, g, b = 0.4 + norm_h * 0.3, 0.4 + norm_h * 0.3, 0.1

      r = np.clip(r, 0, 1)
      g = np.clip(g, 0, 1)
      b = np.clip(b, 0, 1)

      scad += f"translate([{x:.1f},{y:.1f},{h/2:.2f}]) color([{r:.2f},{g:.2f},{b:.2f}]) cube([{step},{step},{h:.2f}], center=true);\n"

  # Add start marker (red sphere)
  start_h = heightmap[start_pos[1], start_pos[0]]
  scad += f"translate([{start_pos[0]:.1f},{start_pos[1]:.1f},{start_h + 1:.2f}]) color([1,0,0]) sphere(r=1.5, $fn=30);\n"

  # Add end marker (blue sphere)
  end_h = heightmap[end_pos[1], end_pos[0]]
  scad += f"translate([{end_pos[0]:.1f},{end_pos[1]:.1f},{end_h + 1:.2f}]) color([0,0,1]) sphere(r=1.5, $fn=30);\n"

  # Add cardinal direction markers
  mid = MAP_SIZE / 2
  scad += f'color([0,1,0]) translate([-3,{mid:.1f},5]) linear_extrude(0.01) text("W", size=3, valign="center", halign="center");\n'
  scad += f'color([0,1,0]) translate([{MAP_SIZE+3:.1f},{mid:.1f},5]) linear_extrude(0.01) text("E", size=3, valign="center", halign="center");\n'
  scad += f'color([0,1,0]) translate([{mid:.1f},-3,5]) linear_extrude(0.01) text("N", size=3, valign="center", halign="center");\n'
  scad += f'color([0,1,0]) translate([{mid:.1f},{MAP_SIZE+3:.1f},5]) linear_extrude(0.01) text("S", size=3, valign="center", halign="center");\n'

  # Render multiple photos from above
  for i in range(50):
    terrain_img_path = result_path(f"44_terrain_{i}.png")
    while True:
      # Camera positions - from above looking down at terrain
      cam_x = random.random() * MAP_SIZE
      cam_y = random.random() * MAP_SIZE
      cam_z = 40 + random.random() * 20  # High above

      look_x = random.random() * MAP_SIZE
      look_y = random.random() * MAP_SIZE
      look_z = heightmap[int(min(look_y, MAP_SIZE - 1)), int(min(look_x, MAP_SIZE - 1))]

      # Ensure camera is looking at a reasonable distance
      horiz_dist = math.sqrt((cam_x - look_x)**2 + (cam_y - look_y)**2)
      if horiz_dist < 10:
        continue

      cameraArg = f"--camera={cam_x:.2f},{cam_y:.2f},{cam_z:.2f},{look_x:.2f},{look_y:.2f},{look_z:.2f}"

      vc.render_scadText_to_png(scad,
                                terrain_img_path,
                                cameraArg=cameraArg,
                                extraScadArgs=["--projection=p"])

      im = Image.open(terrain_img_path)
      colours = im.getcolors(maxcolors=10000)

      if colours is None:
        break  # Too many colors is fine for terrain

      blueColours = 0
      redColours = 0
      greenColours = 0

      for count, (r, g, b) in colours:
        if r > 200 and g < 100 and b < 100: redColours += count
        if b > 200 and r < 100 and g < 100: blueColours += count
        if g > 200 and r < 150 and b < 150: greenColours += count

      # Check for interesting content
      has_start = redColours > 50
      has_end = blueColours > 50
      has_markers = greenColours > 50

      interestingCount = int(has_start) + int(has_end) + int(has_markers)

      if interestingCount > 2 and not os.path.exists("images/44.png"):
        import shutil
        shutil.copy(terrain_img_path, "images/44.png")

      if interestingCount < 1:
        print(f"Redoing terrain photo {i} - no markers visible")
        continue

      break


if not os.path.exists(result_path("44_terrain_0.png")):
  renderHeightmapAsPng()

prompt = f"""
You must survey the path for a railway across a mountainous terrain from the red sphere (start) 
to the blue sphere (end).

The goal is NOT to find the shortest path, but to find the flattest path. Trains need
to travel on as flat as ground as possible, as grades get challenging the further away
from horizontal they go. The better your path, the less blasting, cuttings, viaducts, tunnels, 
sand, and brakepads are needed, so it's important you get this as flat as possible.

You do not need to consider 'straightness' here - a spiral track around a mountain speed limited
at 20kmph is infinitely better than a death drop or a megastructure bridge.

The terrain is a {MAP_SIZE}x{MAP_SIZE} grid.

You can move in 8 directions:
- n, s, e, w (cardinal directions)
- ne, nw, se, sw (diagonals)

Return your path as a sequence of directions. For example: "ne ne e e se s s sw"
means: go northeast twice, east twice, southeast once, south twice, southwest once.

Separate each step with a space. The path should minimize the steepest single step you take.

The terrain is not available as a heightmap - don't bother asking. If your response is 
"Need a heightmap, plz?", that will be interpreted as directions starting with 'NE', so try 
extra hard to solve this before giving up. It is solvable if you think a bit, but if you are 
totally unable to figure out this problem, that's ok, returning a partial solution is better 
than a useless "I can't figure out images and need a heightmap" answer.

Photos of the terrain are attached:
"""

structure = None
earlyFail = True


def prepareSubpassPrompt(index: int) -> str:
  images = list(range(50))
  images = images[0:50 - index * 10]

  if index == 5:
    raise StopIteration

  return prompt + "".join([f"[[image:{result_path(f'44_terrain_{i}.png')}]]" for i in images])


def parse_path(answer: str):
  """Parse a direction string into list of (dx, dy) moves."""
  dir_map = {
    'n': (0, -1),
    's': (0, 1),
    'e': (1, 0),
    'w': (-1, 0),
    'ne': (1, -1),
    'nw': (-1, -1),
    'se': (1, 1),
    'sw': (-1, 1)
  }

  # Handle both space-separated and concatenated formats
  answer = answer.strip().lower()

  # Try space-separated first
  parts = answer.replace(',', ' ').split()

  moves = []
  for part in parts:
    part = part.strip()
    if part in dir_map:
      moves.append((part, dir_map[part]))
    elif len(part) <= 2 and part:
      # Might be concatenated single-char directions
      for char in part:
        if char in dir_map:
          moves.append((char, dir_map[char]))

  return moves


gradedPaths = [None] * 4


def gradeAnswer(answer: str, subPass: int, aiEngineName: str):
  global gradedPaths

  moves = parse_path(answer)

  if not moves:
    return 0, "Could not parse any valid moves from the answer"

  x, y = start_pos
  path_taken = [(x, y)]
  worst_slope = 0
  total_steps = 0

  for dir_name, (dx, dy) in moves:
    nx, ny = x + dx, y + dy

    # Check bounds
    if not (0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE):
      gradedPaths[subPass] = (path_taken, worst_slope,
                              f"Path went out of bounds at step {total_steps+1}")
      return 0.1 * total_steps / len(optimal_path), f"Path went out of bounds at ({nx}, {ny})"

    # Calculate slope of this step
    step_slope = calculate_slope(heightmap, x, y, nx, ny)
    worst_slope = max(worst_slope, step_slope)

    x, y = nx, ny
    path_taken.append((x, y))
    total_steps += 1

    # Check if reached destination (within tolerance)
    dist_to_end = math.sqrt((x - end_pos[0])**2 + (y - end_pos[1])**2)
    if dist_to_end <= 2:
      gradedPaths[subPass] = (path_taken, worst_slope, "Reached destination!")

      # Score based on how close to optimal worst slope
      if worst_slope <= optimal_worst_slope * 1.1:
        score = 1.0  # Within 10% of optimal
      elif worst_slope <= optimal_worst_slope * 1.5:
        score = 0.8  # Within 50% of optimal
      elif worst_slope <= optimal_worst_slope * 2.0:
        score = 0.6  # Within 2x of optimal
      else:
        score = 0.4  # Reached but steep path

      return score, f"Reached destination! Your worst slope: {worst_slope:.3f}, Optimal: {optimal_worst_slope:.3f}"

  # Didn't reach destination
  dist_to_end = math.sqrt((x - end_pos[0])**2 + (y - end_pos[1])**2)
  progress = 1.0 - (dist_to_end / math.sqrt((start_pos[0] - end_pos[0])**2 +
                                            (start_pos[1] - end_pos[1])**2))

  gradedPaths[subPass] = (path_taken, worst_slope,
                          f"Did not reach destination, ended at ({x}, {y})")

  return max(0.0,
             progress * 0.3), f"Path ended at ({x}, {y}), {dist_to_end:.1f} units from destination"


def resultToNiceReport(answer, subPass, aiEngineName):
  if gradedPaths[subPass] is None:
    return "<p>No path data available</p>"

  path_taken, worst_slope, status = gradedPaths[subPass]

  html = f"<p><b>Status:</b> {status}</p>"
  html += f"<p><b>Worst slope encountered:</b> {worst_slope:.3f}</p>"
  html += f"<p><b>Optimal worst slope:</b> {optimal_worst_slope:.3f}</p>"
  html += f"<p><b>Steps taken:</b> {len(path_taken)-1}</p>"
  html += f"<p><b>Optimal path length:</b> {len(optimal_path)-1} steps</p>"

  return html


highLevelSummary = f"""
Can you plan a railway route that minimises vertical gradient? From photos?<br>

The AI must find a path from the red sphere (hilltop) to the blue sphere (distant hilltop)
across procedurally generated terrain. The goal is to minimize the WORST slope encountered,
not the path length.<br>

Eg It's better to spend a week descrending by spiraling around a mountain than jump off a cliff!<br>

The optimal path has a worst slope of {optimal_worst_slope:.3f} and takes {len(optimal_path)-1} steps.<br>

Some sample images (AI gets up to 50:)<br>
<div style="max-width:650px">
<img src="44_terrain_0.png" width="200px" style="float:left; padding:4px">
<img src="44_terrain_1.png" width="200px" style="float:left; padding:4px">
<img src="44_terrain_2.png" width="200px" style="float:left; padding:4px">
<img src="44_terrain_3.png" width="200px" style="float:left; padding:4px">
<img src="44_terrain_4.png" width="200px" style="float:left; padding:4px">
<img src="44_terrain_5.png" width="200px" style="float:left; padding:4px">
</div>

Just like 42 this has 2 ways to solve:
<ul>
<li> Solve each image individually - work out the best path(s) within each 
  photo, and then recognise sequences of left and right turns to stitch
  the images together. This is probably how you would approach this as a human.</li>
<li> Use feature detection to stich the entire playing field together,
and then work out a course using a known algorithm like dijiskstra.</li>
</ul>

"""

subpassParamSummary = [
  "Navigate with 50 aerial photos", "Navigate with 40 aerial photos",
  "Navigate with 30 aerial photos", "Navigate with 20 aerial photos"
]
promptChangeSummary = "Decreasing the number of aerial photos"
