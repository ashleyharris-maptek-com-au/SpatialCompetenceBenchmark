import math

tags = ["2D", "Constructive", "Packing"]

title = "Lay out pipe to make letter shapes."

promptTemplate = """
You are given PIPE_COUNT rigid lengths of pipe, each 5 meters long and 10cm in diameter. 

One pipe is fixed with its center at the origin (0,0) and a rotation of 0, meaning its length is along the x-axis, and it
spans from -2.5,-0.05 to 2.5, 0.05.

Arrange the remaining pipes on a 2D plane such that SHAPE_DESCRIPTION

Importantly:
- Pipes can NOT intersect each other, and this must be buildable in real life. 
- Corners and joins should not have gaps in them.
- When rendered in a 3D preview with each pipe a different colour there must be ZERO Z-Fighting.

Return a PIPE_COUNT element array of where each of the pipes are located:
"""

# (pipe_count, shape_description, reference_scad_body, summary)
testParams = [
  (2, "the pipes resemble a \"T\" shape 5m tall when viewed from above. "
   "The given horizontal pipe is the top bar of the T, and a single vertical pipe "
   "descends from the center of that bar.", """
   color("red") cube([5,0.1,.1], center=true);
   translate([0,-2.55,0]) cube([0.1,5,.1], center=true);
   """, "T shape (2 pipes)"),
  (2, "the pipes resemble an \"L\" shape when viewed from above. "
   "The given horizontal pipe is the entire bottom of the L. A vertical pipe "
   "rises upward from the left end of that bar, making the corner of the L at the left.", """
   color("red") cube([5,0.1,.1], center=true);
   translate([-2.45,2.55,0]) cube([0.1,5,.1], center=true);
   """, "L shape (2 pipes)"),
  (3, "the pipes resemble a \"U\" shape when viewed from above. "
   "The given horizontal pipe is the entire bottom of the U. Two vertical pipes rise upward "
   "from each end of the bottom bar, one on the left and one on the right.", """
   color("red") cube([5,0.1,.1], center=true);
   translate([2.45,2.55,0]) cube([0.1,5,.1], center=true);
   translate([-2.45,2.55,0]) cube([0.1,5,.1], center=true);
   """, "U shape (3 pipes)"),
  (4, "the pipes resemble a capital \"F\" shape when viewed from above. "
   "The given horizontal pipe is the middle bar of the F. A vertical pipe forms the left "
   "upright, touching the left end of the given pipe and extending upward. "
   "A second horizontal pipe at the top connects to the top of the vertical upright, "
   "extending to the right.", """
color("blue") translate([0,0]) rotate([0,0,0]) cube([5,0.1,.1], center=true);
translate([-2.55,2.5]) rotate([0,0,90]) cube([5,0.1,.1], center=true);
color("red") translate([-2.55,-2.5]) rotate([0,0,90]) cube([5,0.1,.1], center=true);
color("green") translate([0,4.95]) rotate([0,0,0]) cube([5,0.1,.1], center=true);
   """, "F shape (4 pipes)"),
  (5, "the pipes resemble a \"H\" shape 10m high when viewed from above. "
   "The given horizontal pipe is the crossbar of the H. Two vertical pipes on each side "
   "form the uprights, extending above and below the crossbar.", """
   color("red") cube([5,0.1,.1], center=true);
   translate([2.55,2.5,0]) cube([0.1,5,.1], center=true);
   translate([-2.55,2.5,0]) cube([0.1,5,.1], center=true);
   translate([2.55,-2.5,0]) cube([0.1,5,.1], center=true);
   translate([-2.55,-2.5,0]) cube([0.1,5,.1], center=true);
   """, "H shape (5 pipes)"),
  (4, "the pipes resemble a capital \"I\" shape (with serifs) 10m tall when viewed from above. "
   "The given horizontal pipe is the bottom serif. Two vertical pipes rise from the center "
   "of the bottom bar (stacked end to end) to reach 10m height, "
   "then a horizontal pipe sits on top as the top serif.", """
   color("red") translate([0,0]) rotate([0,0,0]) cube([5,0.1,.1], center=true);
translate([0,2.55]) rotate([0,0,90]) cube([5,0.1,.1], center=true);
translate([0,7.55]) rotate([0,0,90]) cube([5,0.1,.1], center=true);
translate([0,10.1]) rotate([0,0,0]) cube([5,0.1,.1], center=true);
   """, "Capital I with serifs (4 pipes)"),
  (4, "the pipes resemble a square shape when viewed from above."
   "The given horizontal pipe is the entire bottom bar. A vertical pipe rises from each end of "
   "the bottom bar. A horizontal pipe spans the top, resting on the tops of both verticals. "
   "The frame should be ~5m wide and ~5m tall, with no gaps in the corners.", """
   color("red") cube([5,0.1,.1], center=true);
   translate([2.45,2.55]) rotate([0,0,90.0]) cube([5,0.1,.1], center=true);
   translate([0.0,5.1]) rotate([0,0,0.0]) cube([5,0.1,.1], center=true);
   translate([-2.45,2.55]) rotate([0,0,90.0]) cube([5,0.1,.1], center=true);
   """, "Square shape (4 pipes)"),
]

subpassParamSummary = [tp[3] for tp in testParams]
promptChangeSummary = "Different letter shapes with varying pipe counts and spatial complexity"

structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "pipes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "xCentre": {
            "type": "number"
          },
          "yCentre": {
            "type": "number"
          },
          "rotationDegrees": {
            "type": "number"
          }
        },
        "propertyOrdering": ["xCentre", "yCentre", "rotationDegrees"],
        "required": ["xCentre", "yCentre", "rotationDegrees"],
        "additionalProperties": False,
      }
    }
  },
  "propertyOrdering": ["reasoning", "pipes"],
  "required": ["reasoning", "pipes"],
  "additionalProperties": False,
}

referenceScad = """
module reference()
{
  color("red") cube([5,0.1,.1], center=true);
  translate([0,-2.55,0]) cube([0.1,5,.1], center=true);
}
"""


def prepareSubpassPrompt(index):
  if index >= len(testParams):
    raise StopIteration
  pipeCount, description, _, _ = testParams[index]
  return promptTemplate.replace("PIPE_COUNT", str(pipeCount)).replace("SHAPE_DESCRIPTION",
                                                                      description)


def prepareSubpassReferenceScad(index):
  if index >= len(testParams):
    raise StopIteration
  _, _, scad, _ = testParams[index]
  return "module reference(){\n" + scad + "\n}"


def resultToScad(result, aiEngineName):
  scad = "module result(){ union(){"
  for pipe in result["pipes"]:
    scad += "translate([" + str(pipe["xCentre"]) + "," + \
      str(pipe["yCentre"]) + "]) rotate([0,0," + \
      str(pipe["rotationDegrees"]) + "]) cube([5,0.1,.1], center=true);\n"

  return scad + "}}"


highLevelSummary = """
Tests arranging rigid pipes into letter shapes. The core challenge is handling the 10cm pipe 
diameter at joins — pipes must touch at their ends without overlapping.

<br><br>

Simpler shapes (T, L, J) test basic spatial reasoning. The H, I, and frame shapes require careful 
placement of 4-5 pipes with correct offsets at 3-way joins.

<br><br>

Closeup of correct 3-way join (e.g. H shape): pipes touch but don't overlap.
<pre>
   x = -2.55 (from -2.6 to -2.5)
   | 
|  i  |
|  i  X--------------- 
|  i  | 5 m long
X-----X - - - - - - - 
|  i  | -2.5 to 2.5
|  i  X---------------
|  i  |
</pre>

Common failure: pipes overlap at joins (x = -2.5 instead of -2.55).
"""

PIPE_LENGTH = 5.0
PIPE_WIDTH = 0.1
OVERLAP_TOLERANCE = 0.02  # Allow 2cm tolerance for touching joins


def _pipe_corners(pipe):
  cx = pipe["xCentre"]
  cy = pipe["yCentre"]
  angle = math.radians(pipe["rotationDegrees"])
  cos_a = math.cos(angle)
  sin_a = math.sin(angle)
  hw = PIPE_LENGTH / 2
  hh = PIPE_WIDTH / 2
  corners = []
  for dx, dy in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
    corners.append((cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a))
  return corners


def _sat_axes(corners):
  axes = []
  for i in range(2):
    j = i + 1
    ex = corners[j][0] - corners[i][0]
    ey = corners[j][1] - corners[i][1]
    length = math.hypot(ex, ey)
    if length > 0:
      axes.append((-ey / length, ex / length))
  return axes


def _project(corners, axis):
  dots = [c[0] * axis[0] + c[1] * axis[1] for c in corners]
  return min(dots), max(dots)


def _pipes_intersect(corners1, corners2):
  for axis in _sat_axes(corners1) + _sat_axes(corners2):
    min1, max1 = _project(corners1, axis)
    min2, max2 = _project(corners2, axis)
    overlap = min(max1 - min2, max2 - min1)
    if overlap <= OVERLAP_TOLERANCE:
      return False
  return True


def lateFailTest(result, subPass):
  pipes = result.get("pipes", [])
  if len(pipes) < 2:
    return None

  all_corners = [_pipe_corners(p) for p in pipes]

  for i in range(len(pipes)):
    for j in range(i + 1, len(pipes)):
      if _pipes_intersect(all_corners[i], all_corners[j]):
        return (f"Pipe {i} and pipe {j} intersect. "
                f"Pipe {i}: center=({pipes[i]['xCentre']}, {pipes[i]['yCentre']}), "
                f"rotation={pipes[i]['rotationDegrees']}deg. "
                f"Pipe {j}: center=({pipes[j]['xCentre']}, {pipes[j]['yCentre']}), "
                f"rotation={pipes[j]['rotationDegrees']}deg.")

  return None


def postProcessScore(score, subPassIndex):
  # If you get it perfect, sometimes it reports 95% instead of 100%,
  # so we round up to 100% if we get 95%
  if score > 0.95: return 1

  # If you mess up (and overlay your pipes), it reports a score in
  # the mid 20s. Ew. No round down to 0.
  if score < 0.3: return 0

  return score
