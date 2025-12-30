title = "Lay out pipe to make a H shape."

prompt = """
You are given 5 rigid lengths of pipe, each 5 meters long and 10cm in diameter. 

One pipe is fixed with its center at the origin (0,0) and a rotation of 0, meaning its length is along the x-axis, and it
spans from -2.5,-0.05 to 2.5, 0.05.

Arrange the remaining 4 pipes on a 2D plane such that the the pipes resemble a "H" shape 10m high when viewed from above.

Pipes can not intersect each other, and should only touch at their ends.

Return a 5 element array of where each of the pipes are located:
"""

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
  translate([2.55,0,0]) cube([0.1,10,.1], center=true);
  translate([-2.55,0,0]) cube([0.1,10,.1], center=true);
}
"""


def resultToScad(result, aiEngineName):
  scad = "module result(){ union(){"
  for pipe in result["pipes"]:
    scad += "translate([" + str(pipe["xCentre"]) + "," + \
      str(pipe["yCentre"]) + "]) rotate([0,0," + \
      str(pipe["rotationDegrees"]) + "]) cube([5,0.1,.1], center=true);\n"

  return scad + "}}"


highLevelSummary = \
    """
This is a deceptively hard problem to solve, the issue is overlap at the 3-way joins.

Closeup of correct result: (Note all 3 pipes touch but don't overlap.)
<pre>
   x = -2.55 (from -2.6 to -2.5)
   | 
|  i  |
|  i  |
|  i  |
|  i  X--------------- 
|  i  | 5 m long
X-----X - - - - - - - 
|  i  | -2.5 to 2.5
|  i  X---------------
|  i  |
|  i  |
|  i  |
</pre>

Closeup of typical failed result: (note the overlap between vertical pipes and the horizontal pipe)         
<pre>
   x = -2.5 (from -2.55 to -2.45)       
   |                                    
|  i  |                                 
|  i  |                                 
|  X--X                 
|  i??X---------------                        
|  i??| 5 m long                    
X--XXXX - - - - - - -                   
|  i??| -2.5 to 2.5                                 
|  i??X---------------                                   
|  X--X              
|  i  |                                 
|  i  |                                 
</pre>
"""


def postProcessScore(score, subPassIndex):
  # If you get it perfect, sometimes it reports 95% instead of 100%,
  # so we round up to 100% if we get 95%
  if score > 0.95: return 1

  # If you mess up (and overlay your pipes), it reports a score in
  # the mid 20s. Ew. No round down to 0.
  if score < 0.3: return 0

  return score
