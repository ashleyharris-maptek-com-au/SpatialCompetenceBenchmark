import random
import os
import OpenScad as vc

title = "Reconstruct a 3D voxel grid from photos"
earlyFail = True
skip = True

# Define colors for voxels - distinct, easily distinguishable colors
COLORS = [
  ([1, 0, 0], "red"),
  ([0, 1, 0], "green"),
  ([0, 0, 1], "blue"),
  ([1, 1, 0], "yellow"),
  ([1, 0, 1], "magenta"),
  ([0, 1, 1], "cyan"),
  ([1, 0.5, 0], "orange"),
  ([0.5, 0, 1], "purple"),
]

# Subpass configurations: (grid_size, num_voxels, num_colors, seed)
SUBPASS_CONFIG = [
  (4, 10, 3, 43001),  # 4x4x4 grid, 10 voxels, 3 colors
  (5, 20, 4, 43002),  # 5x5x5 grid, 20 voxels, 4 colors
  (6, 35, 5, 43003),  # 6x6x6 grid, 35 voxels, 5 colors
  (7, 50, 5, 43004),  # 7x7x7 grid, 50 voxels, 5 colors
  (8, 70, 6, 43005),  # 8x8x8 grid, 70 voxels, 6 colors
  (10, 100, 6, 43006),  # 10x10x10 grid, 100 voxels, 6 colors
]

# Store generated voxel data for each subpass
_generated_voxels = {}


def generate_voxels(subpass):
  """Generate random voxels for a given subpass configuration."""
  if subpass in _generated_voxels:
    return _generated_voxels[subpass]

  grid_size, num_voxels, num_colors, seed = SUBPASS_CONFIG[subpass]
  random.seed(seed)

  # Generate unique random positions
  all_positions = [(x, y, z) for x in range(grid_size) for y in range(grid_size)
                   for z in range(grid_size)]
  random.shuffle(all_positions)
  positions = all_positions[:num_voxels]

  # Assign colors to voxels
  voxels = []
  for i, pos in enumerate(positions):
    color_idx = i % num_colors
    voxels.append({"xyz": list(pos), "color": COLORS[color_idx][1], "rgb": COLORS[color_idx][0]})

  _generated_voxels[subpass] = voxels
  return voxels


def render_voxels_to_scad(voxels, grid_size):
  """Convert voxels to OpenSCAD code."""
  scad = ""
  for v in voxels:
    x, y, z = v["xyz"]
    r, g, b = v["rgb"]
    scad += f"color([{r},{g},{b}]) translate([{x},{y},{z}]) cube([0.9,0.9,0.9]);\n"

  # Add axis labels
  scad += f'color([0.3,0.3,0.3]) translate([{grid_size/2},-1.5,0]) linear_extrude(0.01) text("+X", size=0.8, halign="center");\n'
  scad += f'color([0.3,0.3,0.3]) translate([-1.5,{grid_size/2},0]) linear_extrude(0.01) text("+Y", size=0.8, halign="center");\n'
  scad += f'color([0.3,0.3,0.3]) translate([-1.5,0,{grid_size/2}]) rotate([90,0,0]) linear_extrude(0.01) text("+Z", size=0.8, halign="center");\n'

  scad += "color([1,1,1]) sphere(d=0.1, $fn=20);"

  return scad


def render_images_for_subpass(subpass):
  """Render 8 corner views of the voxel grid."""
  voxels = generate_voxels(subpass)
  grid_size = SUBPASS_CONFIG[subpass][0]
  scad = render_voxels_to_scad(voxels, grid_size)

  os.makedirs("results", exist_ok=True)

  # Camera positions at 8 corners of a cube surrounding the grid
  center = grid_size / 2
  dist = grid_size * 2.5

  corners = [
    (center - dist, center - dist, center + dist),  # front-left-top
    (center + dist, center - dist, center + dist),  # front-right-top
    (center - dist, center + dist, center + dist),  # back-left-top
    (center + dist, center + dist, center + dist),  # back-right-top
    (center - dist, center - dist, center - dist + grid_size),  # front-left-bottom (elevated)
    (center + dist, center - dist, center - dist + grid_size),  # front-right-bottom
    (center - dist, center + dist, center - dist + grid_size),  # back-left-bottom
    (center + dist, center + dist, center - dist + grid_size),  # back-right-bottom
  ]

  for i, (cx, cy, cz) in enumerate(corners):
    camera_arg = f"--camera={cx:.2f},{cy:.2f},{cz:.2f},{center:.2f},{center:.2f},{center:.2f}"
    output_path = f"results/43_voxels_{subpass}_{i}.png"
    vc.render_scadText_to_png(scad,
                              output_path,
                              cameraArg=camera_arg,
                              extraScadArgs=["--projection=p"])


def ensure_images_exist(subpass):
  """Ensure images exist for a subpass, render if not."""
  if not os.path.exists(f"results/43_voxels_{subpass}_0.png"):
    render_images_for_subpass(subpass)


prompt = """
You are given 8 photographs of a 3D voxel grid taken from the 8 corners of the viewing cube.
Your task is to reconstruct the exact positions and colors of all voxels in the grid.

The grid is GRID_SIZExGRID_SIZExGRID_SIZE, with coordinates from (0,0,0) to (MAX_COORD,MAX_COORD,MAX_COORD).
There are NUM_VOXELS voxels in total.

Available colors: COLORS_LIST

For each voxel, provide its xyz coordinates and color name.

Coordinate system:
- X increases to the right (labeled +X)
- Y increases going back (labeled +Y)  
- Z increases going up (labeled +Z)
- (0,0,0) is at the front-left-bottom corner
- the white sphere is at the front-left-bottom corner of the 0,0,0 voxel.
"""

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string",
      "description": "Your reasoning process for reconstructing the voxels"
    },
    "voxels": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "xyz": {
            "type": "array",
            "items": {
              "type": "integer"
            },
            "description": "The x, y, z coordinates of the voxel"
          },
          "color": {
            "type": "string",
            "description": "The color name of the voxel",
            "enum": ["red", "green", "blue", "yellow", "magenta", "cyan", "orange", "purple"]
          }
        },
        "required": ["xyz", "color"],
        "additionalProperties": False
      }
    }
  },
  "required": ["reasoning", "voxels"],
  "additionalProperties": False
}

subpassParamSummary = [
  "4x4x4 grid with 10 voxels (3 colors)",
  "5x5x5 grid with 20 voxels (4 colors)",
  "6x6x6 grid with 35 voxels (5 colors)",
  "7x7x7 grid with 50 voxels (5 colors)",
  "8x8x8 grid with 70 voxels (6 colors)",
  "10x10x10 grid with 100 voxels (6 colors)",
]

promptChangeSummary = "Increasing grid size and voxel count"


def prepareSubpassPrompt(index: int) -> str:
  if index >= len(SUBPASS_CONFIG):
    raise StopIteration

  ensure_images_exist(index)

  grid_size, num_voxels, num_colors, _ = SUBPASS_CONFIG[index]
  color_names = [c[1] for c in COLORS[:num_colors]]

  p = prompt.replace("GRID_SIZE", str(grid_size))
  p = p.replace("MAX_COORD", str(grid_size - 1))
  p = p.replace("NUM_VOXELS", str(num_voxels))
  p = p.replace("COLORS_LIST", ", ".join(color_names))

  # Add image references
  images = "".join([f"[[image:results/43_voxels_{index}_{i}.png]]" for i in range(8)])

  return p + "\n\n" + images


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  if subPass >= len(SUBPASS_CONFIG):
    return 0, "Invalid subpass"

  grid_size, num_voxels, num_colors, _ = SUBPASS_CONFIG[subPass]
  expected_voxels = generate_voxels(subPass)

  submitted = answer.get("voxels", [])
  if not isinstance(submitted, list):
    return 0, "voxels must be a list"

  # Build expected set: {(x,y,z): color}
  expected_set = {}
  for v in expected_voxels:
    pos = tuple(v["xyz"])
    expected_set[pos] = v["color"]

  # Parse submitted voxels
  submitted_set = {}
  valid_colors = {c[1] for c in COLORS[:num_colors]}

  for i, v in enumerate(submitted):
    if not isinstance(v, dict):
      return 0, f"Voxel {i} is not an object"

    xyz = v.get("xyz")
    if not isinstance(xyz, (list, tuple)) or len(xyz) != 3:
      return 0, f"Voxel {i} has invalid xyz format"

    try:
      x, y, z = int(xyz[0]), int(xyz[1]), int(xyz[2])
    except (ValueError, TypeError):
      return 0, f"Voxel {i} has non-integer coordinates"

    if not (0 <= x < grid_size and 0 <= y < grid_size and 0 <= z < grid_size):
      return 0, f"Voxel {i} at ({x},{y},{z}) is outside grid bounds [0,{grid_size-1}]"

    color = v.get("color", "").lower().strip()
    if color not in valid_colors:
      return 0, f"Voxel {i} has invalid color '{color}'. Valid colors: {valid_colors}"

    pos = (x, y, z)
    if pos in submitted_set:
      return 0, f"Duplicate voxel at position ({x},{y},{z})"

    submitted_set[pos] = color

  # Score: count correct positions and correct position+color matches
  correct_positions = 0
  correct_colors = 0

  for pos, color in submitted_set.items():
    if pos in expected_set:
      correct_positions += 1
      if expected_set[pos] == color:
        correct_colors += 1

  # Missing and extra voxels
  missing = len(expected_set) - correct_positions
  extra = len(submitted_set) - correct_positions
  wrong_color = correct_positions - correct_colors

  # Scoring:
  # - 70% weight on position accuracy
  # - 30% weight on color accuracy (of correctly positioned voxels)
  position_score = correct_positions / num_voxels if num_voxels > 0 else 0
  color_score = correct_colors / num_voxels if num_voxels > 0 else 0

  # Penalty for extra voxels
  extra_penalty = min(0.2, extra * 0.02)

  final_score = max(0, 0.7 * position_score + 0.3 * color_score - extra_penalty)

  details = (f"Positions correct: {correct_positions}/{num_voxels}, "
             f"Colors correct: {correct_colors}/{num_voxels}, "
             f"Missing: {missing}, Extra: {extra}, Wrong color: {wrong_color}")

  if final_score >= 0.99:
    return 1, "Perfect reconstruction! " + details
  elif final_score >= 0.8:
    return final_score, "Good reconstruction. " + details
  elif final_score >= 0.5:
    return final_score, "Partial reconstruction. " + details
  else:
    return final_score, "Poor reconstruction. " + details


def resultToNiceReport(answer, subPass, aiEngineName):
  """Generate visualization comparing expected vs submitted voxels."""
  if subPass >= len(SUBPASS_CONFIG):
    return "<p>Invalid subpass</p>"

  grid_size = SUBPASS_CONFIG[subPass][0]
  expected_voxels = generate_voxels(subPass)
  submitted = answer.get("voxels", [])

  # Build expected set
  expected_set = {tuple(v["xyz"]): v for v in expected_voxels}

  # Build submitted set
  submitted_set = {}
  for v in submitted:
    if isinstance(v, dict) and "xyz" in v:
      xyz = v.get("xyz", [])
      if isinstance(xyz, (list, tuple)) and len(xyz) == 3:
        try:
          pos = (int(xyz[0]), int(xyz[1]), int(xyz[2]))
          submitted_set[pos] = v
        except:
          pass

  # Generate comparison SCAD
  scadExpected = "// Expected voxels (wireframe)\n"
  for v in expected_voxels:
    x, y, z = v["xyz"]
    r, g, b = v["rgb"]
    scadExpected += f"color([{r},{g},{b},0.3]) translate([{x},{y},{z}]) cube([0.7,0.7,0.7]);\n"

  scadSubmitted = "\n// Submitted voxels (solid, offset slightly)\n"
  for pos, v in submitted_set.items():
    x, y, z = pos
    color_name = v.get("color", "red").lower()
    rgb = [1, 0, 0]  # default red
    for c in COLORS:
      if c[1] == color_name:
        rgb = c[0]
        break
    r, g, b = rgb
    scadSubmitted += f"color([{r},{g},{b}], 0.3) translate([{x+0.1},{y+0.1},{z+0.1}]) cube([0.7,0.7,0.7]);\n"

  # Render comparison
  os.makedirs("results", exist_ok=True)
  submitted_path = f"results/43_{subPass}_{aiEngineName}_submitted.png"
  expected_path = f"results/43_{subPass}_{aiEngineName}_expected.png"
  center = grid_size / 2
  dist = grid_size * 2.5
  camera_arg = f"--camera={center+dist},{center-dist},{center+dist},{center},{center},{center}"
  vc.render_scadText_to_png(scadSubmitted,
                            submitted_path,
                            cameraArg=camera_arg,
                            extraScadArgs=["--projection=p", "--no-autocenter"])
  vc.render_scadText_to_png(scadExpected,
                            expected_path,
                            cameraArg=camera_arg,
                            extraScadArgs=["--projection=p", "--no-autocenter"])

  return f'<td>AI guess:<br><img src="{os.path.basename(submitted_path)}" alt="Voxel Comparison" style="max-width:100%;"></td><td>' + \
         f'Actual result:<br><img src="{os.path.basename(expected_path)}" alt="Voxel Comparison" style="max-width:100%;"></td>'


highLevelSummary = """
Can you reconstruct a 3D voxel grid from photos only?<br><br>

Given 8 photographs of a coloured voxel grid taken from the corners of a viewing cube,
reconstruct the exact positions and colors of all voxels.<br><br>

This tests spatial reasoning, 3D reconstruction from 2D images, and color recognition.
"""

if __name__ == "__main__":
  # Test rendering for subpass 0
  print("Generating test images for subpass 0...")
  render_images_for_subpass(0)
  print("Done. Check results/43_voxels_0_*.png")

  # Print expected voxels
  voxels = generate_voxels(0)
  print(f"\nExpected voxels for subpass 0 ({len(voxels)} voxels):")
  for v in voxels:
    print(f"  {v['xyz']} - {v['color']}")
