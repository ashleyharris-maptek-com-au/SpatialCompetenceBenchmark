import math

title = "Laser beam art"
earlyFail = True
skip = True

prompt = """
You are an artist in charge of creating a laser beam art piece.

You have a workspace of 100x100 meters, and a laser emitter at the center (50,50), facing -y.

You have an unlimited budget for mirrors and beamsplitters. These are both 20cm wide and neglicably
thin. Mirrors are essentially perfect, reflecting 100% of the beam energy. Beamsplitters are
essentially perfect, splitting the beam energy 50/50, 50% continues on it's existing path,
50% is reflected as if it was a mirror.

You should aim to fill your entire workspace with the art if possible, and you're free to choose the
optimal viewing angle for the audience to see your work.

The artwork you have been asked to create is:
"""


def prepareSubpassPrompt(index: int) -> str:
  if index == 0:
    return prompt + "\n\n" + "A regular pentagram, with a line connecting each vertex to the center dividing the space into 5 identical triangles."
  if index == 1:
    return prompt + "\n\nA 5 sided star, with each point connected to the centre and both opposite points."
  if index == 2:
    return prompt + "\n\n The 'cool S' (https://en.wikipedia.org/wiki/Cool_S)"
  if index == 3:
    return prompt + "\n\n The coastline and state boundaries of the continental United States"
  raise StopIteration


def prepareSubpassReferenceScad(index):

  if index == 0:
    center = [50.0, 50.0]
    radius = 50.0
    pts = []
    for i in range(5):
      a = -math.pi / 2 + i * (2 * math.pi / 5)
      pts.append([center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)])
    body = "w = 0.6;\n"
    body += "module seg(a,b,w){ hull(){ translate([a[0],a[1],0]) circle(d=w,$fn=24); translate([b[0],b[1],0]) circle(d=w,$fn=24); } }\n"
    body += "linear_extrude(height=0.1) union(){\n"
    for a, b in zip(pts, pts[1:] + pts[:1]):
      body += f"  seg([{a[0]:.6f},{a[1]:.6f}],[{b[0]:.6f},{b[1]:.6f}],w);\n"
      body += f"  seg([{a[0]:.6f},{a[1]:.6f}],[{center[0]:.6f},{center[1]:.6f}],w);\n"

    body += "}\n"
    return "module reference()\n{\n" + body + "\n}\n"

  if index == 1:
    center = [50.0, 50.0]
    radius = 50.0
    pts = []
    for i in range(5):
      a = -math.pi / 2 + i * (2 * math.pi / 5)
      pts.append([center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)])

    segs = []
    for i in range(5):
      segs.append((pts[i], pts[(i + 2) % 5]))
    for i in range(5):
      segs.append((pts[i], center))

    body = ""
    body += "w = 0.6;\n"
    body += "module seg(a,b,w){ hull(){ translate([a[0],a[1],0]) circle(d=w,$fn=24); translate([b[0],b[1],0]) circle(d=w,$fn=24); } }\n"
    body += "linear_extrude(height=0.1) union(){\n"
    for a, b in segs:
      body += f"  seg([{a[0]:.6f},{a[1]:.6f}],[{b[0]:.6f},{b[1]:.6f}],w);\n"
    body += "}\n"
    return "module reference()\n{\n" + body + "\n}\n"
  if index == 2:
    x0, x1, x2, x3 = 30.0, 42.0, 58.0, 70.0
    y0, y1, y2, y3, y4 = 20.0, 35.0, 50.0, 65.0, 80.0
    segs = [
      ([x1, y4], [x2, y4]),
      ([x1, y4], [x0, y3]),
      ([x2, y4], [x3, y3]),
      ([x0, y3], [x3, y3]),
      ([x0, y3], [x1, y2]),
      ([x3, y3], [x2, y2]),
      ([x1, y2], [x2, y2]),
      ([x1, y2], [x0, y1]),
      ([x2, y2], [x3, y1]),
      ([x0, y1], [x3, y1]),
      ([x1, y0], [x2, y0]),
      ([x0, y1], [x1, y0]),
      ([x3, y1], [x2, y0]),
      ([50.0, y0], [50.0, 50.0]),
    ]

    body = ""
    body += "w = 0.8;\n"
    body += "module seg(a,b,w){ hull(){ translate([a[0],a[1],0]) circle(d=w,$fn=24); translate([b[0],b[1],0]) circle(d=w,$fn=24); } }\n"
    body += "linear_extrude(height=0.1) union(){\n"
    for a, b in segs:
      body += f"  seg([{a[0]:.6f},{a[1]:.6f}],[{b[0]:.6f},{b[1]:.6f}],w);\n"
    body += "}\n"
    return "module reference()\n{\n" + body + "\n}\n"
  if index == 3:
    body = ""
    body += "linear_extrude(height=0.1)\n"
    body += "projection(cut=true)\n"
    body += "intersection(){\n"
    body += "  scale([100/512,100/512,10]) surface(file=\"images/41_ref.png\", center=false, invert=true, convexity=10);\n"
    body += "  translate([0,0,2]) cube([100,100,20], center=false);\n"
    body += "}\n"
    return "module reference()\n{\n" + body + "\n}\n"
  raise StopIteration


structure = {
  "type": "object",
  "properties": {
    "reasoning": {
      "type": "string"
    },
    "beamSplitters": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "position": {
            "type": "array",
            "items": {
              "type": "number"
            }
          },
          "normal": {
            "type": "array",
            "items": {
              "type": "number"
            }
          }
        },
        "additionalProperties": False,
        "required": ["position", "normal"],
        "propertyOrdering": ["position", "normal"],
        "description": "2D positions and 2D normal vectors of beam splitters"
      }
    },
    "mirrors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "position": {
            "type": "array",
            "items": {
              "type": "number"
            }
          },
          "normal": {
            "type": "array",
            "items": {
              "type": "number"
            }
          }
        },
        "additionalProperties": False,
        "required": ["position", "normal"],
        "propertyOrdering": ["position", "normal"]
      },
      "description": "2D positions and 2D normal vectors of mirrors"
    },
    "observerLocation": {
      "type":
      "array",
      "items": {
        "type": "number"
      },
      "description":
      "The 2D location on the edge of the workspace, that the audience should enter the exhibit from, in order to recognise the art"
    },
  },
  "additionalProperties": False,
  "required": ["reasoning", "beamSplitters", "mirrors", "observerLocation"],
  "propertyOrdering": ["reasoning", "beamSplitters", "mirrors", "observerLocation"]
}


def normalize(v):
  """Normalize a 2D vector."""
  length = math.sqrt(v[0]**2 + v[1]**2)
  if length < 1e-10:
    return [0, 0]
  return [v[0] / length, v[1] / length]


def dot(v1, v2):
  """Dot product of two 2D vectors."""
  return v1[0] * v2[0] + v1[1] * v2[1]


def reflect(direction, normal):
  """Reflect a direction vector about a normal."""
  d = dot(direction, normal)
  return [direction[0] - 2 * d * normal[0], direction[1] - 2 * d * normal[1]]


def ray_line_intersection(ray_origin, ray_dir, line_pos, line_normal, object_half_size=0.1):
  """
    Find intersection between a ray and a finite line segment (mirror/splitter).
    The line is perpendicular to the normal, centered at line_pos, with given half-size.
    Returns (t, intersection_point) or (None, None) if no intersection.
    """
  # Line tangent is perpendicular to normal
  tangent = [-line_normal[1], line_normal[0]]

  # Line segment endpoints
  p1 = [line_pos[0] - tangent[0] * object_half_size, line_pos[1] - tangent[1] * object_half_size]
  p2 = [line_pos[0] + tangent[0] * object_half_size, line_pos[1] + tangent[1] * object_half_size]

  # Ray-segment intersection using parametric form
  dx = p2[0] - p1[0]
  dy = p2[1] - p1[1]

  denom = ray_dir[0] * dy - ray_dir[1] * dx
  if abs(denom) < 1e-10:
    return None, None  # Parallel

  t = ((p1[0] - ray_origin[0]) * dy - (p1[1] - ray_origin[1]) * dx) / denom
  s = ((p1[0] - ray_origin[0]) * ray_dir[1] - (p1[1] - ray_origin[1]) * ray_dir[0]) / denom

  if t > 1e-6 and 0 <= s <= 1:  # t > small epsilon to avoid self-intersection
    intersection = [ray_origin[0] + t * ray_dir[0], ray_origin[1] + t * ray_dir[1]]
    return t, intersection

  return None, None


def ray_boundary_intersection(ray_origin, ray_dir, world_size):
  """Find where ray exits the world boundary."""
  min_t = float('inf')

  # Check all 4 boundaries: x=0, x=world_size[0], y=0, y=world_size[1]
  boundaries = [
    (0, 0, 0),  # x = 0 (left)
    (0, world_size[0], 0),  # x = world_size[0] (right)
    (1, 0, 1),  # y = 0 (bottom)
    (1, world_size[1], 1),  # y = world_size[1] (top)
  ]

  for axis, value, _ in boundaries:
    if abs(ray_dir[axis]) > 1e-10:
      t = (value - ray_origin[axis]) / ray_dir[axis]
      if t > 1e-6 and t < min_t:
        # Check if intersection is within world bounds on other axis
        other_axis = 1 - axis
        other_val = ray_origin[other_axis] + t * ray_dir[other_axis]
        if -1e-6 <= other_val <= world_size[other_axis] + 1e-6:
          min_t = t

  if min_t < float('inf'):
    return [ray_origin[0] + min_t * ray_dir[0], ray_origin[1] + min_t * ray_dir[1]]
  return None


def propagate_laser(origin, direction, mirrors, beam_splitters, world_size, max_bounces=100):
  """
    Propagate a laser beam, handling reflections and splits.
    Returns list of line segments [[start, end], ...]
    """
  segments = []

  # Active beams: list of (origin, direction, bounces_remaining)
  active_beams = [(origin, normalize(direction), max_bounces)]

  # Track visited beam states to prevent duplicates: (rounded_pos, rounded_dir)
  # Use 4 decimal places (~0.1mm precision) to identify duplicate beams
  visited = set()

  def beam_key(pos, dir):
    return (round(pos[0], 4), round(pos[1], 4), round(dir[0], 4), round(dir[1], 4))

  while active_beams:
    if len(active_beams) > 100000:
      print("WARNING: " + str(len(active_beams)) + " beams left to trace.")
    if len(active_beams) > 200000:
      print("ERROR: " + str(len(active_beams)) + " beams. Basically infinite beams.")
      break

    ray_origin, ray_dir, bounces_left = active_beams.pop(0)

    if bounces_left <= 0:
      continue

    # Skip if we've already processed a beam from this position in this direction
    key = beam_key(ray_origin, ray_dir)
    if key in visited:
      continue
    visited.add(key)

    # Find closest intersection with any mirror or beam splitter
    closest_t = float('inf')
    closest_point = None
    closest_obj = None
    closest_type = None

    for mirror in mirrors:
      pos = mirror.get("position", [0, 0])
      normal = normalize(mirror.get("normal", [0, 1]))
      t, point = ray_line_intersection(ray_origin, ray_dir, pos, normal)
      if t is not None and t < closest_t:
        closest_t = t
        closest_point = point
        closest_obj = {"position": pos, "normal": normal}
        closest_type = "mirror"

    for splitter in beam_splitters:
      pos = splitter.get("position", [0, 0])
      normal = normalize(splitter.get("normal", [0, 1]))
      t, point = ray_line_intersection(ray_origin, ray_dir, pos, normal)
      if t is not None and t < closest_t:
        closest_t = t
        closest_point = point
        closest_obj = {"position": pos, "normal": normal}
        closest_type = "splitter"

    if closest_point is not None:
      # Add segment to closest object
      segments.append([list(ray_origin), list(closest_point)])

      normal = closest_obj["normal"]
      # Ensure normal faces the incoming ray
      if dot(ray_dir, normal) > 0:
        normal = [-normal[0], -normal[1]]

      if closest_type == "mirror":
        # Reflect beam
        reflected_dir = reflect(ray_dir, normal)
        active_beams.append((closest_point, reflected_dir, bounces_left - 1))
      else:
        # Beam splitter: create both reflected and transmitted beams
        reflected_dir = reflect(ray_dir, normal)
        active_beams.append((closest_point, reflected_dir, bounces_left - 1))
        active_beams.append(
          (closest_point, ray_dir, bounces_left - 1))  # Transmitted continues same direction
    else:
      # No object hit, trace to world boundary
      boundary_point = ray_boundary_intersection(ray_origin, ray_dir, world_size)
      if boundary_point:
        segments.append([list(ray_origin), boundary_point])

  return segments


def resultToScad(answer: dict, aiEngineName) -> str:
  beamSplitters = answer.get("beamSplitters", [])
  mirrors = answer.get("mirrors", [])

  worldSize = [100, 100]
  laserEmitterPos = [50, 50]
  laserEmitterDir = [0, -1]

  # Calculate the path(s) of the laser beam
  laserPathSegments = propagate_laser(laserEmitterPos, laserEmitterDir, mirrors, beamSplitters,
                                      worldSize)

  scad = ""
  for segment in laserPathSegments:
    scad += f"""
color([1,0,0]) hull()
{{
    translate({segment[0]})
    cube([0.6,0.6,0.1],center=true);
    translate({segment[1]})
    cube([0.6,0.6,0.1],center=true);
}}
        """

  for beamSplitter in beamSplitters:
    normal = beamSplitter["normal"]
    rotation = math.degrees(math.atan2(normal[1], normal[0]))
    scad += f"""
        color([0,1,0])
        translate({beamSplitter["position"]})
        rotate([0,0,{rotation}])
        cube([0.2,0.5,0.2],center=true);
        """

  for mirror in mirrors:
    normal = mirror["normal"]
    rotation = math.degrees(math.atan2(normal[1], normal[0]))
    scad += f"""
        color([0,1,1])
        translate({mirror["position"]})
        rotate([0,0,{rotation}])
        cube([0.2,0.5,0.2],center=true);
        """

  referenceObserverLocation = [50, 100]
  actualObserverLocation = answer.get("observerLocation", [50, 100])
  rotation = math.atan2(actualObserverLocation[1] - referenceObserverLocation[1],
                        actualObserverLocation[0] - referenceObserverLocation[0])
  scad = f"""
    translate([50,50,0]) rotate([0,0,{rotation}]) translate([-50,-50,0]) {{ 
    """ + scad + "}"
  return scad


if __name__ == "__main__":
  print(
    resultToScad({
      'reasoning':
      'I designed a center-origin laser network that traces a pentagram (the five star diagonals) and the five radii from the center to the pentagon vertices. The five pentagon vertices sit on a circle of radius 40 m around the center (50,50), giving a symmetric regular pentagram contained in the 100x100 workspace. Each of the five vertices hosts a thin, 50/50 beam-splitter that reflects half of the arriving center-to-vertex beam along the corresponding pentagram edge to the next vertex, while the other half continues outward along the radius, making the radius line visible up to the vertex. The star lines are then completed by mirrors placed along the five star edges, tiling each edge with a small sequence of 20 cm wide mirrors to ensure the reflected beam follows the straight star segment from vertex to vertex. The combination yields the pentagram plus the five lines from center to vertices that divide the space into five identical triangles. I chose an audience viewing point on a wall edge where the five lines and the star are most legible from a single vantage: the left edge midpoint (0,50). This maximizes visibility of both the internal pentagram and the radii when viewed from the edge. ',
      'beamSplitters': [{
        'position': [50.0, 10.0],
        'normal': [-0.157, -0.987]
      }, {
        'position': [88.0424, 37.6392],
        'normal': [0.987, 0.156]
      }, {
        'position': [73.5114, 82.3607],
        'normal': [-0.987, -0.157]
      }, {
        'position': [26.4886, 82.3607],
        'normal': [0.891, -0.454]
      }, {
        'position': [11.9577, 37.6393],
        'normal': [-0.454, 0.892]
      }],
      'mirrors': [{
        'position': [55.878, 28.09],
        'normal': [-0.951, 0.309]
      }, {
        'position': [61.756, 46.18],
        'normal': [-0.951, 0.309]
      }, {
        'position': [67.634, 64.27],
        'normal': [-0.951, 0.309]
      }, {
        'position': [58.123, 71.18],
        'normal': [0.598, -0.801]
      }, {
        'position': [42.734, 60.0],
        'normal': [0.598, -0.801]
      }, {
        'position': [27.344, 48.82],
        'normal': [0.598, -0.801]
      }, {
        'position': [30.978, 37.64],
        'normal': [0.0, -1.0]
      }, {
        'position': [50.0, 37.64],
        'normal': [0.0, -1.0]
      }, {
        'position': [69.022, 37.64],
        'normal': [0.0, -1.0]
      }, {
        'position': [72.655, 48.82],
        'normal': [-0.587, -0.809]
      }, {
        'position': [57.266, 60.0],
        'normal': [-0.587, -0.809]
      }, {
        'position': [41.876, 71.18],
        'normal': [-0.587, -0.809]
      }, {
        'position': [32.366, 64.27],
        'normal': [0.951, 0.309]
      }, {
        'position': [38.244, 46.18],
        'normal': [0.951, 0.309]
      }, {
        'position': [44.122, 28.09],
        'normal': [0.951, 0.309]
      }],
      'observerLocation': [0, 50]
    }), 0, "")

highLevelSummary = """
Using only mirrors and beam-splitters, can you create art work?

The art increases in complexity, from a pentagram, to a star, to 'that cool S', to eventually
the borders of the USA.

The LLM is forced to consider the audience and it's appearence, as the laser source is fixed
in the center of the room facding Y+, but the 'entrance door' is selectable to maximise the 
recognoition of the artwork.

"""
