// Slab: 350x350x50 mm lattice slab (OpenSCAD) - slab 5 identical
=t = 10; gap = 75; sizeX = 350; sizeY = 350; height = 50; holeR = 3.5; fn = 40;
difference() {
  translate([ -sizeX/2, -sizeY/2, 0 ])
  cube([ sizeX, sizeY, height ], center=false);
  for (i = [0 : 4]) {
    x0 = -sizeX/2 + i*(t + gap);
    translate([ x0, -sizeY/2, 0 ]) cube([ t, sizeY, height ], center=false);
  }
  for (j = [0 : 4]) {
    y0 = -sizeY/2 + j*(t + gap);
    translate([ -sizeX/2, y0, 0 ]) cube([ sizeX, t, height ], center=false);
  }
  translate([ -sizeX/2 + 0, -sizeY/2 + 0, 0 ]) cylinder(h = height, r = holeR, $fn = fn);
  translate([ -sizeX/2 + 0,  sizeY/2 - 0, 0 ]) cylinder(h = height, r = holeR, $fn = fn);
  translate([ sizeX/2 - 0, -sizeY/2 + 0, 0 ]) cylinder(h = height, r = holeR, $fn = fn);
  translate([ sizeX/2 - 0,  sizeY/2 - 0, 0 ]) cylinder(h = height, r = holeR, $fn = fn);
}
