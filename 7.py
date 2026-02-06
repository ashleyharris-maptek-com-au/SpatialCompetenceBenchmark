import OpenScad as vc
from collections import deque
import hashlib
import json
import os
import tempfile
from LLMBenchCore.ResultPaths import result_path, report_relpath

# Cache for gradeAnswer results
_grade_cache_path = os.path.join(tempfile.gettempdir(), "grade_cache_7.json")
_grade_cache = None


def _load_grade_cache():
  global _grade_cache
  if _grade_cache is None:
    try:
      with open(_grade_cache_path, 'r') as f:
        _grade_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
      _grade_cache = {}
  return _grade_cache


def _save_grade_cache():
  if _grade_cache is not None:
    with open(_grade_cache_path, 'w') as f:
      json.dump(_grade_cache, f, indent=2)


title = "3D maze - solution requires jumping over gaps"

prompt = """

Here is a heightmap platform maze, in which A is located at height 5, and B is located at height 0. 
The maze represents a 3D space where movement is constrained by height differences. 
Characters can only move to adjacent cells if the height difference is at most 1, or jump over gaps.

A555
2B20
3015
4555

The character can move:
- 1 cell horizontally or vertically, so long as the height is within 1 unit.
- Can jump 2 cells horizontally or vertically, so long as:
  - source and destination heights are the same
  - the height of the cell between the source and destination is lower than the source height (jump over gaps, not through walls!)

In this case, the character:
- starts at A, which is at level 5
- walks flat for a bit, 
- jumps over a gap of height 0 to another level 5 block.
- walks flat for a bit
- descends until level 2, then jumps over B to level 2,
- and then continues down to level 0, reaching B.

The maze must use only 0-9, A & B to represent height, and must only have one solution.
A & B must appear in the grid once each.
The path must visit at least 20% of all cells.
No single elevation can occupy more than 30% of the grid.
"""

suffix = \
"""
Your output must be ONLY the maze's heightmap, nothing else.
Your output must be PARAM_A rows long, and every row must be PARAM_A characters long.
The maze must be your only output - Extra text above or below the maze itself corrupt your work.
"""

earlyFail = True

testParams = [
  {
    "size": 5,
    "a_height": 5,
    "b_height": 0,
    "required_jumps": 2,
    "summary": "Cover a 5x5 grid with A at level 5 and B at level 0, requiring at least 2 jumps",
  },
  {
    "size": 10,
    "a_height": 0,
    "b_height": 9,
    "required_jumps": 4,
    "summary": "Cover a 10x10 grid with A at level 0 and B at level 9, requiring at least 4 jumps",
  },
  {
    "size": 15,
    "a_height": 5,
    "b_height": 5,
    "required_jumps": 6,
    "summary": "Cover a 15x15 grid with A at level 5 and B at level 5, requiring at least 6 jumps",
  },
  {
    "size": 20,
    "a_height": 5,
    "b_height": 5,
    "required_jumps": 8,
    "summary": "Cover a 20x20 grid with A at level 5 and B at level 5, requiring at least 8 jumps",
  },
  {
    "size": 25,
    "a_height": 5,
    "b_height": 5,
    "required_jumps": 10,
    "summary": "Cover a 25x25 grid with A at level 5 and B at level 5, requiring at least 10 jumps",
  },
  {
    "size": 30,
    "a_height": 5,
    "b_height": 0,
    "required_jumps": 12,
    "summary": "Cover a 30x30 grid with A at level 5 and B at level 0, requiring at least 12 jumps",
  },
]

subpassParamSummary = [params["summary"] for params in testParams]

structure = None  # We just take a string here.


def prepareSubpassPrompt(index):
  #if index == 1: raise StopIteration # HACK while developing to save money.
  if index < 0 or index >= len(testParams):
    raise StopIteration
  params = testParams[index]
  size = params["size"]
  a_height = params["a_height"]
  b_height = params["b_height"]
  required_jumps = params["required_jumps"]
  description = (f"Create a maze of size {size}x{size} that has A at level {a_height} "
                 f"and B at level {b_height}, and at least {required_jumps} jumps.")
  return prompt + description + suffix.replace("PARAM_A", str(size))


def resultToNiceReport(result, subPass, aiEngineName, path=None, alt_path=None):
  if subPass < 0 or subPass >= len(testParams):
    raise StopIteration
  params = testParams[subPass]
  aHeight = params["a_height"]
  bHeight = params["b_height"]

  rows = result.split('\n')
  scad_content = "union() {\n"
  height_map = {}
  a_pos = None
  b_pos = None
  for j, row in enumerate(rows):
    for i, char in enumerate(row):
      if char.isdigit():
        height = int(char)
        height_map[(j, i)] = height
        if height > 0:
          scad_content += f'    translate([{j}, {i}, {height / 2}]) cube([1, 1, {height}], center=true);\n'
        else:
          scad_content += f'    translate([{j}, {i}, -0.5]) cube([1, 1, 1], center=true);\n'
      elif char == 'A':
        scad_content += f'    translate([{j}, {i}, {aHeight-0.5}]) color([1, 0, 0]) cube([1, 1, 1], center=true);\n'
        a_pos = (j, i)
        height_map[(j, i)] = aHeight
      elif char == 'B':
        scad_content += f'    translate([{j}, {i}, {bHeight-0.5}]) color([0, 0, 1]) cube([1, 1, 1], center=true);\n'
        b_pos = (j, i)
        height_map[(j, i)] = bHeight

  if path:
    print("New code running")
    path_radius = 0.12
    walk_color = "0.1, 0.9, 0.2"
    jump_color = "1.0, 0.6, 0.1"
    alt_color = "0.9, 0.1, 0.1"
    scad_content += "    // Path visualization\n"

    def draw_path(path_nodes, walk_col, jump_col):
      nonlocal scad_content
      if not path_nodes or len(path_nodes) < 2:
        return
      for idx in range(len(path_nodes) - 1):
        start = path_nodes[idx]
        end = path_nodes[idx + 1]
        start_z = height_map.get(start, 0) + 0.95
        end_z = height_map.get(end, 0) + 0.95
        manhattan = abs(start[0] - end[0]) + abs(start[1] - end[1])

        if manhattan == 2:
          arc_height = max(1.0, abs(start_z - end_z) * 0.5 + 0.8)
          segments = 8
          points = []
          for s in range(segments + 1):
            t = s / segments
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            z = (1 - t) * start_z + t * end_z + arc_height * 4 * t * (1 - t)
            points.append((x, y, z))

          for seg in range(len(points) - 1):
            x1, y1, z1 = points[seg]
            x2, y2, z2 = points[seg + 1]
            scad_content += (
              f'    color([{jump_col}]) hull() {{ '\
              f'translate([{x1:.3f}, {y1:.3f}, {z1:.3f}]) sphere(r={path_radius}); '\
              f'translate([{x2:.3f}, {y2:.3f}, {z2:.3f}]) sphere(r={path_radius}); }}\n'
            )
        else:
          scad_content += (
            f'    color([{walk_col}]) hull() {{ '\
            f'translate([{start[0]:.3f}, {start[1]:.3f}, {start_z:.3f}]) sphere(r={path_radius}); '\
            f'translate([{end[0]:.3f}, {end[1]:.3f}, {end_z:.3f}]) sphere(r={path_radius}); }}\n'
          )

    if alt_path:

      def common_prefix_len(first, second):
        limit = min(len(first), len(second))
        idx = 0
        while idx < limit and first[idx] == second[idx]:
          idx += 1
        return idx

      def common_suffix_len(first, second, prefix_len):
        idx1 = len(first) - 1
        idx2 = len(second) - 1
        count = 0
        while idx1 >= prefix_len and idx2 >= prefix_len and first[idx1] == second[idx2]:
          count += 1
          idx1 -= 1
          idx2 -= 1
        return count

      prefix_len = common_prefix_len(path, alt_path)
      suffix_len = common_suffix_len(path, alt_path, prefix_len)

      prefix_path = path[:prefix_len]
      suffix_path = path[len(path) - suffix_len:] if suffix_len > 0 else []

      mid_start = max(prefix_len - 1, 0)
      mid_end = len(path) - suffix_len
      alt_mid_end = len(alt_path) - suffix_len

      primary_mid = path[mid_start:mid_end + 1] if mid_end >= mid_start else []
      alt_mid = alt_path[mid_start:alt_mid_end + 1] if alt_mid_end >= mid_start else []

      draw_path(prefix_path, walk_color, jump_color)
      draw_path(suffix_path, walk_color, jump_color)
      draw_path(primary_mid, alt_color, alt_color)
      draw_path(alt_mid, alt_color, alt_color)
    else:
      draw_path(path, walk_color, jump_color)

  scad_content += "}\n"

  print("Drawing 3D maze of size " + str(len(rows)) + "x" + str(len(rows[0])))

  base_name = f"7_Visualization_{aiEngineName}_{len(rows)}_{subPass}"

  grid_size = len(rows)
  center_x = grid_size / 2
  center_y = grid_size / 2

  def build_camera_arg(eye_x, eye_y, eye_z, target_x=None, target_y=None, target_z=5):
    if target_x is None:
      target_x = center_x
    if target_y is None:
      target_y = center_y
    return (f"--camera={eye_x:.3f},{eye_y:.3f},{eye_z:.3f},"
            f"{target_x:.3f},{target_y:.3f},{target_z:.3f}")

  views = [("above", build_camera_arg(center_x, center_y, 50))]

  if a_pos and b_pos:
    dx = b_pos[0] - a_pos[0]
    dy = b_pos[1] - a_pos[1]
    cam_x = a_pos[0] - dx * 1.5
    cam_y = a_pos[1] - dy * 1.5
    cam_z = grid_size * 2 + 15
    views.append(("from_a", build_camera_arg(cam_x, cam_y, cam_z)))

  offset = grid_size * 2.0
  offsetClose = grid_size * 0.8
  side_height = grid_size * 1.8 + 25
  views.extend([
    ("north", build_camera_arg(center_x, center_y - offset, side_height)),
    ("south", build_camera_arg(center_x, center_y + offset, side_height)),
    ("west", build_camera_arg(center_x - offset, center_y, side_height)),
    ("east", build_camera_arg(center_x + offset, center_y, side_height)),
    ("northeast", build_camera_arg(center_x + offset * 0.7, center_y + offset * 0.7, side_height)),
    ("northwest", build_camera_arg(center_x - offset * 0.7, center_y + offset * 0.7, side_height)),
    ("southeast", build_camera_arg(center_x + offset * 0.7, center_y - offset * 0.7, side_height)),
    ("southwest", build_camera_arg(center_x - offset * 0.7, center_y - offset * 0.7, side_height)),
    ("northclose", build_camera_arg(center_x, center_y - offsetClose, side_height)),
    ("southclose", build_camera_arg(center_x, center_y + offsetClose, side_height)),
    ("westclose", build_camera_arg(center_x - offsetClose, center_y, side_height)),
    ("eastclose", build_camera_arg(center_x + offsetClose, center_y, side_height)),
    ("northeastclose",
     build_camera_arg(center_x + offsetClose * 0.7, center_y + offsetClose * 0.7, side_height)),
    ("northwestclose",
     build_camera_arg(center_x - offsetClose * 0.7, center_y + offsetClose * 0.7, side_height)),
    ("southeastclose",
     build_camera_arg(center_x + offsetClose * 0.7, center_y - offsetClose * 0.7, side_height)),
    ("southwestclose",
     build_camera_arg(center_x - offsetClose * 0.7, center_y - offsetClose * 0.7, side_height)),
  ])

  image_paths = []
  for view_name, camera_arg in views:
    filename = f"{base_name}_{view_name}.png"
    output_path = result_path(filename, aiEngineName)
    vc.render_scadText_to_png(scad_content, output_path, camera_arg, ["--no-autocenter"])
    image_paths.append(output_path)

  viewer_id = f"maze-viewer-{hashlib.md5(base_name.encode()).hexdigest()}"
  image_tags = []
  for idx, path in enumerate(image_paths):
    image_tags.append(f'<img src="{report_relpath(path, aiEngineName)}" class="maze-view view-{idx}" '
                      f'style="max-width: 100%;">')

  radio_name = f"{viewer_id}-view"
  radio_ids = [f"{viewer_id}-view-{idx}" for idx in range(len(image_paths))]
  inputs = []
  for idx, radio_id in enumerate(radio_ids):
    checked = " checked" if idx == 0 else ""
    inputs.append(f'<input type="radio" name="{radio_name}" id="{radio_id}"{checked}>')

  labels = []
  for idx in range(len(radio_ids)):
    prev_idx = (idx - 1) % len(radio_ids)
    next_idx = (idx + 1) % len(radio_ids)
    labels.append(
      f'<label class="maze-prev prev-{idx}" for="{radio_ids[prev_idx]}">&#8592;</label>')
    labels.append(
      f'<label class="maze-next next-{idx}" for="{radio_ids[next_idx]}">&#8594;</label>')

  style_lines = [
    f'#{viewer_id} {{ display:flex; align-items:center; gap:8px; }}',
    f'#{viewer_id} input[type="radio"] {{ display:none; }}',
    f'#{viewer_id} .maze-frame {{ flex:1; text-align:center; order:1; }}',
    f'#{viewer_id} .maze-prev {{ order:0; cursor:pointer; font-size:18px; display:none; }}',
    f'#{viewer_id} .maze-next {{ order:2; cursor:pointer; font-size:18px; display:none; }}',
    f'#{viewer_id} .maze-view {{ display:none; max-width:100%; }}',
  ]
  for idx, radio_id in enumerate(radio_ids):
    style_lines.append(f'#{radio_id}:checked ~ .maze-frame .view-{idx} {{ display:block; }}')
    style_lines.append(f'#{radio_id}:checked ~ .prev-{idx} {{ display:inline-flex; }}')
    style_lines.append(f'#{radio_id}:checked ~ .next-{idx} {{ display:inline-flex; }}')

  html = (f'<div id="{viewer_id}" class="maze-viewer">'
          f'<style>{" ".join(style_lines)}</style>'
          f'{"".join(inputs)}'
          f'{"".join(labels)}'
          f'<div class="maze-frame">'
          f'{"".join(image_tags)}'
          f'</div>'
          f'</div>')

  return html


def gradeAnswer(answer: str, subPass: int, aiEngineName: str):
  answer = answer.strip()

  # Check cache first
  cache_key = hashlib.md5((answer + str(subPass)).encode()).hexdigest()
  cache = _load_grade_cache()
  if cache_key in cache:
    print("Cache hit - " + _grade_cache_path + " : " + cache_key)
    return tuple(cache[cache_key])

  def _cache_and_return(result):
    cache[cache_key] = list(result)
    _save_grade_cache()
    return result

  if answer.count("A") != 1 or answer.count("B") != 1:
    return _cache_and_return((0, "Maze must have exactly one A and one B",
                              resultToNiceReport(answer, subPass, aiEngineName)))

  if subPass < 0 or subPass >= len(testParams):
    return _cache_and_return((0, "Invalid subpass", ""))

  params = testParams[subPass]
  size = params["size"]
  a_height = params["a_height"]
  b_height = params["b_height"]
  required_jumps = params["required_jumps"]

  rows = answer.split("\n")
  if len(rows) != size:
    return _cache_and_return(
      (0, f"Maze must have exactly {size} rows", resultToNiceReport(answer, subPass, aiEngineName)))

  if len(rows[0]) != size:
    return _cache_and_return((0, f"Maze must have exactly {size} columns",
                              resultToNiceReport(answer, subPass, aiEngineName)))

  for row in rows:
    if len(row) != len(rows[0]):
      return _cache_and_return((0, "Maze must have all rows the same width",
                                resultToNiceReport(answer, subPass, aiEngineName)))

  # Parse the maze and find A and B positions
  grid = []
  a_pos = None
  b_pos = None
  height_map = {}

  for i, row in enumerate(rows):
    grid_row = []
    for j, char in enumerate(row):
      if char == 'A':
        a_pos = (i, j)
        height_map[(i, j)] = a_height
      elif char == 'B':
        b_pos = (i, j)
        height_map[(i, j)] = b_height
      elif char.isdigit():
        height_map[(i, j)] = int(char)
      else:
        return _cache_and_return((0, f"Invalid character in maze: {char}", ""))
      grid_row.append(char)
    grid.append(grid_row)

  # Check that no elevation occupies more than 20% of the grid
  elevation_counts = {}
  for i in range(len(grid)):
    for j in range(len(grid[0])):
      height = height_map.get((i, j))
      if height is not None:
        elevation_counts[height] = elevation_counts.get(height, 0) + 1

  total_cells = len(grid) * len(grid[0])
  for height, count in elevation_counts.items():
    if count / total_cells > 0.3:
      return _cache_and_return((0, f"Elevation {height} occupies more than 30% of the grid",
                                resultToNiceReport(answer, subPass, aiEngineName)))

  print("Starting maze: " + cache_key)

  # Find all valid paths from A to B using DFS
  def get_height(pos):
    return height_map.get(pos, None)

  def get_neighbors(pos):
    """Get all valid moves from current position"""
    i, j = pos
    current_height = get_height(pos)
    neighbors = []

    # 4 directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for di, dj in directions:
      # Try 1-cell move (walk)
      ni, nj = i + di, j + dj
      if 0 <= ni < len(grid) and 0 <= nj < len(grid[0]):
        next_height = get_height((ni, nj))
        if next_height is not None and abs(current_height - next_height) <= 1:
          neighbors.append(((ni, nj), False))  # (position, is_jump)

      # Try 2-cell move (jump)
      ni2, nj2 = i + 2 * di, j + 2 * dj
      if 0 <= ni2 < len(grid) and 0 <= nj2 < len(grid[0]):
        dest_height = get_height((ni2, nj2))
        middle_height = get_height((ni, nj))

        # Jump rules: same height at source and dest, middle is lower.
        # Lower by more than 1 (otherwise it's walkable and jumpable and a false duplicate)
        if (dest_height is not None and middle_height is not None and current_height == dest_height
            and middle_height + 1 < current_height):
          neighbors.append(((ni2, nj2), True))  # (position, is_jump)

    return neighbors

  # Build adjacency list (undirected) for path checks
  graph = {}
  for i in range(len(grid)):
    for j in range(len(grid[0])):
      pos = (i, j)
      graph[pos] = get_neighbors(pos)

  def bfs_path(start, target, blocked_edges=None):
    queue = deque([start])
    parent = {start: (None, False)}  # node -> (prev, is_jump)

    while queue:
      current = queue.popleft()
      if current == target:
        break
      for neighbor, is_jump in graph[current]:
        if blocked_edges and tuple(sorted((current, neighbor))) in blocked_edges:
          continue
        if neighbor not in parent:
          parent[neighbor] = (current, is_jump)
          queue.append(neighbor)

    if target not in parent:
      return None, 0

    path_nodes = []
    jump_count = 0
    current = target
    while current is not None:
      path_nodes.append(current)
      prev, was_jump = parent[current]
      if prev is not None and was_jump:
        jump_count += 1
      current = prev
    path_nodes.reverse()
    return path_nodes, jump_count

  def bfs_farthest_path(start):
    queue = deque([start])
    parent = {start: None}
    distance = {start: 0}
    farthest = start

    while queue:
      current = queue.popleft()
      for neighbor, _ in graph[current]:
        if neighbor not in parent:
          parent[neighbor] = current
          distance[neighbor] = distance[current] + 1
          queue.append(neighbor)
          if distance[neighbor] > distance[farthest]:
            farthest = neighbor

    path_nodes = []
    current = farthest
    while current is not None:
      path_nodes.append(current)
      current = parent[current]
    path_nodes.reverse()
    return path_nodes

  def find_bridges(graph):
    bridges = set()
    disc = {}
    low = {}
    parent = {}
    time = 0

    def dfs(node):
      nonlocal time
      time += 1
      disc[node] = time
      low[node] = time

      for neighbor, _ in graph[node]:
        if neighbor not in disc:
          parent[neighbor] = node
          dfs(neighbor)
          low[node] = min(low[node], low[neighbor])
          if low[neighbor] > disc[node]:
            bridges.add(tuple(sorted((node, neighbor))))
        elif parent.get(node) != neighbor:
          low[node] = min(low[node], disc[neighbor])

    for node in graph:
      if node not in disc:
        parent[node] = None
        dfs(node)

    return bridges

  path, jump_count = bfs_path(a_pos, b_pos)
  if path is None:
    fallback_path = bfs_farthest_path(a_pos)
    return _cache_and_return(
      (0, "No valid path from A to B (showing longest reachable path from A)",
       resultToNiceReport(answer, subPass, aiEngineName, fallback_path)))

  bridges = find_bridges(graph)
  for idx in range(len(path) - 1):
    edge = tuple(sorted((path[idx], path[idx + 1])))
    if edge not in bridges:
      alt_path, _ = bfs_path(a_pos, b_pos, {edge})
      return _cache_and_return((0, "Multiple paths exist. Maze must have only one solution.",
                                resultToNiceReport(answer, subPass, aiEngineName, path, alt_path)))

  print("Finished maze: " + cache_key)

  # Check that path visits at least 20% of cells
  visited_cells = set(path)
  total_cells = len(grid) * len(grid[0])
  visited_percentage = len(visited_cells) / total_cells
  if visited_percentage < 0.2:
    return _cache_and_return(
      (0, f"Path visits only {visited_percentage:.2%} of cells (required: 20%)",
       resultToNiceReport(answer, subPass, aiEngineName, path)))

  if jump_count < required_jumps:
    return _cache_and_return(
      (0, f"Path has {jump_count} jumps, but at least {required_jumps} are required",
       resultToNiceReport(answer, subPass, aiEngineName, path)))

  return _cache_and_return((1, f"Valid maze with {jump_count} jumps (required: {required_jumps})",
                            resultToNiceReport(answer, subPass, aiEngineName, path)))


if __name__ == "__main__":
  resultToNiceReport(
    """
000000000B
0000000099
0000000090
0000000090
0000078086
0000202260
0000572400
0000060640
0000000640
A123450530
""".strip(), 1, "Placebo")

highLevelSummary = """
This is a maze creation that involves climbing "stairs" and jumping over gaps.
<br><br>
LLMs fail here for 3 main reasons:<ul>
<li>They make flat paths (which is banned in the rules)</li>
<li>They allow way too much jumping, creating loops.</li>
<li>They screw up the rows and colomn counts.</li>
</ul>
"""
