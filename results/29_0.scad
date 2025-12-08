// Slab: 350x350x50 mm lattice slab (OpenSCAD)
// Grid: 5 bars along Y (X-positioned bars), 5 bars along X (Y-positioned bars)
// Bar thickness t = 10 mm, gap = 75 mm, total sheet size 350x350, height = 50
// Corner holes for M6 rods (diameter ~6.0–7.0 mm) centered at the slab corners
// The slab is intended to sit on z=0 plane; this file prints with the footprint on the bed
// and height along Z from 0 to 50.

t = 10;            // bar thickness (mm)
gap = 75;          // gap between bars (mm)
sizeX = 350;        // slab width (mm)
sizeY = 350;        // slab depth (mm)
height = 50;         // slab thickness (mm) - extrude in Z

holeR = 3.5;        // M6 rod clearance (radius in mm) for a 6 mm diameter rod
fn = 40;

origin = [-sizeX/2, -sizeY/2, 0];

difference() {
  // Base slab (solid footprint)
  translate([ -sizeX/2, -sizeY/2, 0 ])
  cube([ sizeX, sizeY, height ], center=false);

  // Grid bars (two perpendicular sets) extruded to full height
  // Bars along Y direction (X-fixed positions)
  for (i = [0 : 4]) {
    x0 = -sizeX/2 + i*(t + gap);
    translate([ x0, -sizeY/2, 0 ])
      cube([ t, sizeY, height ], center=false);
  }

  // Bars along X direction (Y-fixed positions)
  for (j = [0 : 4]) {
    y0 = -sizeY/2 + j*(t + gap);
    translate([ -sizeX/2, y0, 0 ])
      cube([ sizeX, t, height ], center=false);
 }

  // Corner holes for M6 rods: centered at the four corners of the lattice ross-section.
  // The centers of the corner bars are at (±sizeX/2 + offset, ±sizeY/2 + offset).
  // We approximate centres at (-170,-170), (-170,170), (170,-170), (170,170) for a 50×350 slab.
  translate([ -sizeX/2 + sizeX/2, -sizeY/2 + sizeY/2, 0 ])
  cylinder(h = height, r = holeR, $fn = fn); // dummy to ensure compile
  translate([ -sizeX/2 + 0, -sizeY/2 + 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
  translate([ sizeX/2 - 0, -sizeY/2 + 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
  translate([ -sizeX/2 + 0, sizeY/2 - 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
}
