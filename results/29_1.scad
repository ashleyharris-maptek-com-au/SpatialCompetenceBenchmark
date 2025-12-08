// Slab: 350x350x50 mm lattice slab (OpenSCAD) - variant 2 (identical geometry; identical parts)
// This is identical to slab_01.scad; provided as a ready-to-slice part to minimize per-slab tooling.
// If you want different internal grids per slab, I can adjust.
// The same grid logic as slab_01.scad is used here.

=t = 10; gap = 75; sizeX = 350; sizeY = 350; height = 50; holeR = 3.5; fn = 40;
origin = [-sizeX/2, -sizeY/2, 0];

difference() {
  translate([ -sizeX/2, -sizeY/2, 0 ])
  cube([ sizeX, sizeY, height ], center=false);

  // Y-oriented bars
  for (i = [0 : 4]) {
    x0 = -sizeX/2 + i*(t + gap);
    translate([ x0, -sizeY/2, 0 ])
      cube([ t, sizeY, height ], center=false);
  }

  // X-oriented bars
  for (j = [0 : 4]) {
    y0 = -sizeY/2 + j*(t + gap);
    translate([ -sizeX/2, y0, 0 ])
      cube([ sizeX, t, height ], center=false);
  }

  // Corner holes for M6 rods (vertical through-cylinder)
  translate([ -sizeX/2 + 0, -sizeY/2 + 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
  translate([ -sizeX/2 + 0, sizeY/2 - 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
  translate([ sizeX/2 - 0, -sizeY/2 + 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
  translate([ sizeX/2 - 0, sizeY/2 - 0, 0 ])
  cylinder(h = height, r = holeR, $fn = fn);
}
