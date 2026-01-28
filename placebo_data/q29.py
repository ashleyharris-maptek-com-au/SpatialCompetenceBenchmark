import math
from textwrap import dedent


def get_response(subPass: int):
  """Get the placebo response for this question."""
  if subPass == 0:
    corePart = dedent("""
                        union()
                        {
                                for (x = [-370/2+5:72:220])
                                {
                                        translate([x,0,0]) cube([10, 370, 10],center=true);
                                }

                                for (y = [-370/2+5:72:220])
                                {
                                        translate([0,y,0]) cube([370, 10, 10],center=true);
                                }
                        }
                                        """)

    def corePartMinus(s: str):
      return "rotate([0,0,90]) translate([0,0,5]) difference(){" + corePart + s + "}"

    bottomAndTopPart = corePartMinus("""
                                // Bottom and top part are identical.
                                for (x = [360/2, -360/2])
                                for (y = [360/2, -360/2])
                                {
                                        translate([x,y,0]) cylinder(h=100, d=6.1, center=true);
                                }
                                """)

    northAndSouthLower = corePartMinus("""
                        translate([364,0,0]) cube([380,380,20], center=true);

                        translate([0,220,0]) cube([80,100,20], center=true);
                        translate([0,-220,0]) cube([80,100,20], center=true);

                        translate([0,180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                        translate([0,-180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                """)

    northAndSouthUpper = corePartMinus("""
                        translate([364,0,0]) cube([380,380,20], center=true);
                        translate([-364,0,0]) cube([380,380,20], center=true);

                        translate([0,220,0]) cube([80,100,20], center=true);
                        translate([0,-220,0]) cube([80,100,20], center=true);

                        translate([0,180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                        translate([0,-180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                """)

    eastAndWestLower = corePartMinus("""
                        translate([364,0,0]) cube([380,380,20], center=true);

                        translate([-140,220,0]) cube([200,100,20], center=true);
                        translate([-140,-220,0]) cube([200,100,20], center=true);
                        translate([140,-220,0]) cube([200,100,20], center=true);
                        translate([140,220,0]) cube([200,100,20], center=true);

                        translate([0,180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                        translate([0,-180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                """)

    eastAndWestUpper = corePartMinus("""
                        translate([364,0,0]) cube([380,380,20], center=true);
                        translate([-364,0,0]) cube([380,380,20], center=true);

                        translate([-140,220,0]) cube([200,100,20], center=true);
                        translate([-140,-220,0]) cube([200,100,20], center=true);
                        translate([140,-220,0]) cube([200,100,20], center=true);
                        translate([140,220,0]) cube([200,100,20], center=true);

                        translate([0,180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                        translate([0,-180,0]) rotate([0,90,0]) cylinder(h=1000, d=6.1, center=true);
                """)

    return {
      "parts": [
        {
          "fileContents": bottomAndTopPart,
          "fileType": "OpenScad",
          "transform": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": bottomAndTopPart,
          "fileType": "OpenScad",
          "transform": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 720, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": northAndSouthLower,
          "fileType": "OpenScad",
          "transform": [1, 0, 0, 0, 0, 0, -1, 185, 0, 1, 0, 545, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": northAndSouthLower,
          "fileType": "OpenScad",
          "transform": [1, 0, 0, 0, 0, 0, -1, -175, 0, 1, 0, 545, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": northAndSouthUpper,
          "fileType": "OpenScad",
          "transform": [-1, 0, 0, 0, 0, 0, 1, -185, 0, 1, 0, 185, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": northAndSouthUpper,
          "fileType": "OpenScad",
          "transform": [-1, 0, 0, 0, 0, 0, 1, 175, 0, 1, 0, 185, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": eastAndWestLower,
          "fileType": "OpenScad",
          "transform": [0, 0, 1, 175, 1, 0, 0, 0, 0, 1, 0, 545, 0, 0, 0, 1]  # Done
        },
        {
          "fileContents": eastAndWestLower,
          "fileType": "OpenScad",
          "transform": [0, 0, 1, -185, 1, 0, 0, 0, 0, 1, 0, 545, 0, 0, 0, 1]
        },
        {
          "fileContents": eastAndWestUpper,
          "fileType": "OpenScad",
          "transform": [0, 0, -1, -175, -1, 0, 0, 0, 0, 1, 0, 185, 0, 0, 0, 1]
        },
        {
          "fileContents": eastAndWestUpper,
          "fileType": "OpenScad",
          "transform": [0, 0, -1, 185, -1, 0, 0, 0, 0, 1, 0, 185, 0, 0, 0, 1]
        },
      ],
      "reasoning":
      "Ash spent an hour messing about in OpenSCAD and created it. Yes I 3D printed it. It used $50 worth of PLA."
    }, "(sound of actual 3D printer printing...)"

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  part = {
    "fileContents": "cube([10,10,10]);",
    "fileType": "OpenScad",
    "transform": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
  }
  return {"reasoning": "Random guess", "parts": [part]}, "Random guess"
