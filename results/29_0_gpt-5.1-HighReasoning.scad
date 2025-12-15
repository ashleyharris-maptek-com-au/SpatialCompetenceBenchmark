/*
  Cage slice 01 of 15
  Internal target size ≈350 x 350 x 700 mm.
  Bars: 10 x 10 mm. Clear gap between repeating bars ≈60 mm.
  This file generates the lowest slice (including the floor grid).
*/

bar = 10;
half_inner = 175;
gap = 70;        // center-to-center spacing -> 60 mm clear gap
rod_d = 7;       // clearance for M6 threaded rod
half_outer = half_inner + bar;

function grid_pos(n) = -half_inner + n * gap;

module cage_full() {
  difference() {
    union() {
      // Floor grid at z = -10 .. 0
      for (j = [0:5]) {
        y = grid_pos(j);
        translate([-half_inner, y - bar/2, -bar])
          cube([2*half_inner, bar, bar], center=false);
      }
      for (i = [0:5]) {
        x = grid_pos(i);
        translate([x - bar/2, -half_inner, -bar])
          cube([bar, 2*half_inner, bar], center=false);
      }

      // Roof grid at z = 700 .. 710
      for (j = [0:5]) {
        y = grid_pos(j);
        translate([-half_inner, y - bar/2, 700])
          cube([2*half_inner, bar, bar], center=false);
      }
      for (i = [0:5]) {
        x = grid_pos(i);
        translate([x - bar/2, -half_inner, 700])
          cube([bar, 2*half_inner, bar], center=false);
      }

      // Side walls at x = ±175
      for (side = [-1, 1]) {
        sx = side * half_inner;
        x0 = (side == 1) ? sx : sx - bar;  // +175 or -185
        // Vertical bars on side walls
        for (j = [0:5]) {
          y = grid_pos(j);
          translate([x0, y - bar/2, 0])
            cube([bar, bar, 700], center=false);
        }
        // Horizontal bars on side walls
        for (k = [0:10]) {
          zc = 0 + k * gap;
          translate([x0, -half_inner, zc - bar/2])
            cube([bar, 2*half_inner, bar], center=false);
        }
      }

      // Front/back walls at y = ±175
      for (side = [-1, 1]) {
        sy = side * half_inner;
        y0 = (side == 1) ? sy : sy - bar;  // +175 or -185
        // Vertical bars on front/back walls
        for (i = [0:5]) {
          x = grid_pos(i);
          translate([x - bar/2, y0, 0])
            cube([bar, bar, 700], center=false);
        }
        // Horizontal bars on front/back walls
        for (k = [0:10]) {
          zc = 0 + k * gap;
          translate([-half_inner, y0, zc - bar/2])
            cube([2*half_inner, bar, bar], center=false);
        }
      }
    }

    // M6 threaded rod clearance holes in the four corner vertical bars
    for (sx = [-1, 1], sy = [-1, 1]) {
      translate([sx * (half_inner + bar/2),
                 sy * (half_inner + bar/2),
                 -20])
        cylinder(d = rod_d, h = 740, $fn = 64);
    }
  }
}

// Slice Z range in the cage_full() coordinate system
z_min = -10;
z_max = 40;   // height 50 mm

module slice() {
  intersection() {
    cage_full();
    translate([-half_outer - 5, -half_outer - 5, z_min])
      cube([2*(half_outer + 5), 2*(half_outer + 5), z_max - z_min], center=false);
  }
}

// Shift so this slice sits on z=0 for printing
translate([0, 0, -z_min])
  slice();
