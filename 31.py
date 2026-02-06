skip = True

import OpenScad as vc
import math
from LLMBenchCore.ResultPaths import result_path

title = "Prove a convex solid can fit throught itself"
skip = True

# See https://en.wikipedia.org/wiki/Prince_Rupert%27s_cube

# Credit to Matt Parker for the idea.

prompt = """

Here is a 3d object, specifically the '{PROMPT_A}', orientated such that its largest face is parallel
to the z=0 plane and centred at the origin.

I conject that this solid can fit through it's own projection if both carefully rotated.

Prove this conjecture by crafting two orientations:
- An orientation which when projected on Z creates a large shadow, being the 'hole'.
- An orientation which when projected on Z creates a small shadow, being the 'solid'.

The solid should be small enough to fit through the hole with a non-zero margin.

Provide each orientation as a 4 element quaternion.

If a solution is not possible using rotations around the origin, provide a 7 element transform:
4 element quaternion and a 3 element offset vector (in that order), the translation is applied in 3D after 
rotation but before projection.

"""

structure = {
  "type": "object",
  "properties": {
    "hole": {
      "type": "object",
      "properties": {
        "transform": {
          "type": "array",
          "items": {
            "type": "number"
          }
        },
      },
      "required": ["transform"],
      "additionalProperties": False,
      "propertyOrdering": ["transform"]
    },
    "solid": {
      "type": "object",
      "properties": {
        "transform": {
          "type": "array",
          "items": {
            "type": "number"
          }
        }
      },
      "required": ["transform"],
      "additionalProperties": False,
      "propertyOrdering": ["transform"]
    }
  },
  "required": ["hole", "solid"],
  "additionalProperties": False,
  "propertyOrdering": ["hole", "solid"]
}

solidNames = [
  "unit cube", "rectangular prism (6,5,4)",
  "letter G in Arial, 5 units high, linearly extruded 0.2 units, wrapped in a convex hull"
]

subpassParamSummary = ["Unit cube", "Rectangular prism", "Hull of Letter G"]


def prepareSubpassPrompt(index: int) -> str:
  if index == 0:
    return prompt.format(PROMPT_A=solidNames[0])
  if index == 1:
    return prompt.format(PROMPT_A=solidNames[1])
  if index == 2:
    return prompt.format(PROMPT_A=solidNames[2])
  raise StopIteration


def gradeAnswer(answer: dict, subPass: int, aiEngineName: str):
  openScadShape = ""
  if subPass == 0:
    openScadShape = "cube([1,1,1], center=True);"
  elif subPass == 1:
    openScadShape = "cube([6,5,4], center=True);"
  elif subPass == 2:
    openScadShape = 'hull() linear_extrude(height=0.2) text("G", font="Arial", size=5, halign="center", valign="center");'

  if "solid" not in answer or "hole" not in answer:
    return 0, "Answer must contain both solid and hole"

  if "transform" not in answer["solid"] or "transform" not in answer["hole"]:
    return 0, "Answer must contain both solid and hole transforms"

  solidTransform = answer["solid"]["transform"]
  holeTransform = answer["hole"]["transform"]

  if len(solidTransform) != 4 and len(solidTransform) != 7:
    return 0, "Solid transform must be 4 or 7 elements"

  if len(holeTransform) != 4 and len(holeTransform) != 7:
    return 0, "Hole transform must be 4 or 7 elements"

  if holeTransform == solidTransform:
    return 0, "Hole and solid transforms must be different"

  holeTransformMagnitude = math.sqrt(holeTransform[0]**2 + holeTransform[1]**2 +
                                     holeTransform[2]**2 + holeTransform[3]**2)
  if holeTransformMagnitude - 1 > 0.01:
    return 0, "Hole transform must be normalised"

  solidTransformMagnitude = math.sqrt(solidTransform[0]**2 + solidTransform[1]**2 +
                                      solidTransform[2]**2 + solidTransform[3]**2)
  if solidTransformMagnitude - 1 > 0.01:
    return 0, "Solid transform must be normalised"

  solidRotation = quaternion_to_euler_angles(solidTransform[0:4])
  solidPrefix = "rotate([" + ",".join([str(x) for x in solidRotation]) + "]) "

  holeRotation = quaternion_to_euler_angles(holeTransform[0:4])
  holePrefix = "rotate([" + ",".join([str(x) for x in holeRotation]) + "]) "

  if len(solidTransform) == 7:
    solidPrefix = "translate([" + ",".join([str(x)
                                            for x in solidTransform[4:]]) + "]) " + solidPrefix
  if len(holeTransform) == 7:
    holePrefix = "translate([" + ",".join([str(x) for x in holeTransform[4:]]) + "]) " + holePrefix

  solidPrefix = "color([0,1,0]) projection() " + solidPrefix
  holePrefix = " color([1,0,0]) projection() " + holePrefix

  solid_path = result_path("31_solid_" + aiEngineName + "_" + str(subPass) + ".png", aiEngineName)
  hole_path = result_path("31_hole_" + aiEngineName + "_" + str(subPass) + ".png", aiEngineName)
  vc.render_scadText_to_png("$fn=90;" + solidPrefix + openScadShape, solid_path,
                            "--camera=0,0,50,0,0,0")
  vc.render_scadText_to_png("$fn=90;" + holePrefix + openScadShape, hole_path,
                            "--camera=0,0,50,0,0,0")

  import PIL

  solidImage = PIL.Image.open(solid_path)
  holeImage = PIL.Image.open(hole_path)

  overlay = PIL.Image.new("RGB", solidImage.size, (0, 0, 0))

  solidP = solidImage.load()
  holeP = holeImage.load()

  solidInHole = 0
  solidMissedHole = 0

  countSolidPixels = 0
  countHolePixels = 0

  for x in range(solidImage.width):
    for y in range(solidImage.height):
      sp = solidP[x, y]
      hp = holeP[x, y]

      solidPixel = sp[1] > 50 and sp[0] < 50 and sp[2] < 50
      holePixel = hp[1] < 50 and hp[0] > 50 and hp[2] < 50

      if solidPixel: countSolidPixels += 1
      if holePixel: countHolePixels += 1

      if solidPixel and not holePixel:
        solidMissedHole += 1
        overlay.putpixel((x, y), (255, 0, 0))
      elif holePixel and solidPixel:
        solidInHole += 1
        overlay.putpixel((x, y), (0, 255, 0))
      elif holePixel:
        overlay.putpixel((x, y), (0, 0, 255))

  overlay_path = result_path("31_overlay_" + aiEngineName + "_" + str(subPass) + ".png",
                             aiEngineName)
  overlay.save(overlay_path)

  if countSolidPixels < 200:
    return 0.0, "Solid transformed away from origin and out of field of view."

  if countHolePixels < 200:
    return 0.0, "Hole transformed away from origin and out of field of view."

  if solidMissedHole == 0:
    return 1.0, "Solid fits through the hole!"

  if solidMissedHole < 100:
    return 1.0 - solidMissedHole / 100, "Solid is VERY close to fitting through the hole, was off with a margin of " + str(
      solidMissedHole) + " pixels"

  return 0.0, "Solid is too far from fitting through the hole, was off by " + str(
    solidMissedHole) + " pixels"


def quaternion_to_euler_angles(quaternion):
  x, y, z, w = quaternion
  t0 = +2.0 * (w * x + y * z)
  t1 = +1.0 - 2.0 * (x * x + y * y)
  X = math.atan2(t0, t1)

  t2 = +2.0 * (w * y - z * x)
  t2 = +1.0 if t2 > +1.0 else t2
  t2 = -1.0 if t2 < -1.0 else t2
  Y = math.asin(t2)

  t3 = +2.0 * (w * z + x * y)
  t4 = +1.0 - 2.0 * (y * y + z * z)
  Z = math.atan2(t3, t4)

  return math.degrees(X), math.degrees(Y), math.degrees(Z)


def resultToNiceReport(result: dict, subPass: int, aiEngineName: str):
  return """
Green = solid and hole lining up<br>
Red = Excess object not fitting through the hole<br>
Blue = Unused hole.<br>
    
    <img src='artifacts/31_overlay_""" + aiEngineName + "_" + str(subPass) + ".png'/>"


highLevelSummary = """
Can a dice fit through another dice, if they're both rotated optimally? This problem
was famously unsolved for decades.
<br><br>
This is now known and proven. Most convex solids can fit through themselves with room
to spare even, but calculate the orientations is non-trivial.

"""
