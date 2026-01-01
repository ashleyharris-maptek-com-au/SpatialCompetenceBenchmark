import math

title = "Hill Tetrahedron Packing in 3D"

prompt = """
Here is the points and faces of a tetrahedron
It has three edges of length 1 along the axes, and three edges of length sqrt(2) on the diagonals.

polyhedron(
    points = [
        [0, 0, 0],                               // 0 (origin corner)
        [1, 0, 0],                               // 1 (along X)
        [0, 1, 0],                               // 2 (along Y)
        [0, 0, 1]                                // 3 (along Z)
    ],
    faces = [
        [0, 2, 1],   // XY plane face (Z=0)
        [0, 1, 3],   // XZ plane face (Y=0)
        [0, 3, 2],   // YZ plane face (X=0)
        [1, 2, 3]    // slanted face (x+y+z=1)
    ],
    convexity = 4
);

We define an 8-part rigid transform of (x,y,z,q0,q1,q2,q3,m), where q0,q1,q2,q3 is a normalised quaternion, x, y, z are the translation, and m is an optional mirror flag.
If m is non-zero, the tetrahedron is mirrored along the X-axis before rotation. This allows both chiralities of the tetrahedron to be used.
Rotation is defined around the 0,0,0 point (Which is NOT THE CENTRE), and is performed before translation.

We create a scene with multiple tetrahedra, each with a different transform. Now we can pack them in as tightly as possible
in order to create a 3D shape, trying to maximize packing density and recreate the target shape.

Return the transform array of tetrahedra in order to create a:
"""

structure = {
  "type": "object",
  "properties": {
    "tetrahedra": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "x": {
            "type": "number"
          },
          "y": {
            "type": "number"
          },
          "z": {
            "type": "number"
          },
          "q0": {
            "type": "number"
          },
          "q1": {
            "type": "number"
          },
          "q2": {
            "type": "number"
          },
          "q3": {
            "type": "number"
          },
          "m": {
            "type":
            "number",
            "description":
            "Mirror flag. If non-zero, mirror along X-axis before rotation. Optional, defaults to 0."
          }
        },
        "additionalProperties": False,
        "required": ["x", "y", "z", "q0", "q1", "q2", "q3", "m"],
        "propertyOrdering": ["x", "y", "z", "q0", "q1", "q2", "q3", "m"]
      }
    }
  },
  "propertyOrdering": ["tetrahedra"],
  "required": ["tetrahedra"],
  "additionalProperties": False
}

earlyFail = True

subpassParamSummary = [
  "Create a unit cube",
  "Create a torus with major radius 8 and minor radius 2",
  "Create a set of dumbbells with spheres of radius 2 and a connecting cylinder of diameter 1",
  "Create an axially aligned square based pyramid with base side 4 and height 4, sitting on the Z=0 plane, centered at origin",
  "Create a cylinder with radius 3 and height 6, centered at origin and aligned along the Z-axis",
  "Create a cube of side length 4, centered at origin",
  "Create an octahedron with edge length 4, centered at origin, with faces on the x, y, and z plane",
  "Itself, but scaled up by a factor of 10 ",
  "Create a sphere of radius 4",
]

noMinkowski = True


def prepareSubpassPrompt(index: int) -> str:
  if index == 0:
    return prompt + "Unit cube (0,0,0) -> (1,1,1)"
  if index == 1:
    return prompt + "Torus of major radius 8, and minor radius 2, with the center at origin."
  if index == 2:
    return prompt + "Set of dumbbells. 2 spheres of radius 2, with centers x = +/-4, and a cylinder of diameter 1 connecting them."
  if index == 3:
    return prompt + "Axially aligned square based pyramid with base side 4 and height 4, sitting on the Z=0 plane, centered at origin."
  if index == 4:
    return prompt + "Cylinder of radius 3 and height 6, centered at origin and aligned along the Z-axis."
  if index == 5:
    return prompt + "Cube of side length 4, centered at origin."
  if index == 6:
    return prompt + "Octahedron with edge length 4, hieght 2, centered at origin, with faces on the x, y, and z plane."
  if index == 7:
    return prompt + "Tetrahedron of side length 10, with vertices at 0,0,0 and 10,0,0."
  if index == 8:
    return prompt + "Sphere of radius 4, with the center at origin."
  raise StopIteration


referenceScad = """
module reference(){
    translate([0,0,0.5]) cube([4,4,1], center=true);
}
"""


def prepareSubpassReferenceScad(index: int) -> str:
  if index == 0:
    return """
module reference(){
  cube(1);
}
        """

  if index == 1:
    return """
module reference(){
    rotate_extrude()
        translate([8, 0, 0])
            circle(r = 2, $fn = 16);
}
"""
  if index == 2:
    return """
module reference(){
  union() {
    translate([-4,0,0]) sphere(r=2);
    translate([ 4,0,0]) sphere(r=2);
    translate([0,0,0]) rotate([0,90,0]) cylinder(r=0.5, h=8, center=true, $fn=30);
  }
}
"""
  if index == 3:
    return """
module reference(){
    rotate([0,0,45]) cylinder(r1=2, r2=0,h=4, $fn=4);
}
"""

  if index == 4:
    return """
module reference(){
    cylinder(r=3, h=6, center=true, $fn=50);
}
"""

  if index == 5:
    return """
module reference(){
    cube([4,4,4], center=true);
}
"""

  if index == 6:
    return """
module reference(){
    cylinder(r=4, h=2, center=true, $fn=8);
}
"""

  if index == 7:
    return """
module reference(){
    scale([10,10,10]) tetrahedron();
}
"""
  if index == 8:
    return """
module reference(){
    sphere(r=4, $fn=20);
}
"""


def quaternionToPitchRollYawInDegrees(q0, q1, q2, q3):
  return [
    math.degrees(math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))),
    math.degrees(math.asin(2 * (q0 * q2 - q1 * q3))),
    math.degrees(math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3)))
  ]


scadModules = """
module tetrahedron(){
    // Hill tetrahedron (trirectangular) - 1/6 of a unit cube, tiles 3D space
    // CSG construction using hull of 4 vertices
    hull() {
        translate([0, 0, 0]) cube(0.001);
        translate([1, 0, 0]) cube(0.001);
        translate([0, 1, 0]) cube(0.001);
        translate([0, 0, 1]) cube(0.001);
    }
}
"""


def resultToScad(result, aiEngineName):
  scad = "module result(){ "
  #scad += "minkowski(){cube(0.001); union() { "
  tetras = []
  printedTetrahedra = 0
  for transform in result["tetrahedra"]:
    try:
      # if any nans or infinites, skip
      if any([math.isnan(x) or math.isinf(x) for x in transform.values()]):
        print("Dropping a tetrahedron that wasn't finite: " + str(transform))
        continue

      # If quaternion is not normalised, skip it.
      magnitude = abs(transform["q0"]**2 + transform["q1"]**2 + transform["q2"]**2 +
                      transform["q3"]**2)
      if magnitude - 1 > 0.001:
        print("Dropping a tetrahedron that wasn't normalised |q| = " + str(magnitude) + ": " +
              str(transform))
        continue

      mirror_str = "mirror([1,0,0]) " if transform.get("m", 0) != 0 else ""
      tetras.append("translate([" + str(transform["x"]) + "," + \
          str(transform["y"]) + "," + str(transform["z"]) + "]) rotate(" + \
          str(quaternionToPitchRollYawInDegrees(transform["q0"], transform["q1"], transform["q2"], transform["q3"])) + ") " + mirror_str + "tetrahedron();\n")
      printedTetrahedra += 1
    except Exception as e:
      print("Dropping a tetrahedron that wasn't valid: " + str(transform) + " " + str(e))

  if printedTetrahedra == 0:
    print("Test 19: No valid tetrahedra were provided by the LLM.")
    return ""

  def divideAndConquer(tetras: list) -> str:
    if len(tetras) < 50:
      return "union(){" + "\n".join(tetras) + "}"
    else:
      mid = len(tetras) // 2
      s = "union(){" + divideAndConquer(tetras[:mid]) + "\n}"
      s += "\n" + divideAndConquer(tetras[mid:])
      s += "}\n"
      return s

  scad += divideAndConquer(tetras)
  scad += "}\n\n"


highLevelSummary = """
Can the LLM create complex shapes out of Hill tetrahedra?
<br><br>
Hill tetrahedra (trirectangular tetrahedra) are special because they can tile 3D space
perfectly - 6 of them combine to form a cube. However, they are chiral (come in left and right-handed versions),
so both chiralities are needed for perfect tiling. The optional 'm' parameter allows mirroring.
<br><br>
The LLM needs to figure out the correct rotations and translations to pack these
tetrahedra into the target shapes without gaps or overlaps.
"""
