/*
  Cage slice 06 of 15
*/

bar = 10;
half_inner = 175;
gap = 70;
rod_d = 7;
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
        x0 = (side == 1) ? sx : sx - bar;
        for (j = [0:5]) {
          y = grid_pos(j);
          translate([x0, y - bar/2, 0])
            cube([bar, bar, 700], center=false);
        }
        for (k = [0:10]) {
          zc = 0 + k * gap;
          translate([x0, -half_inner, zc - bar/2])
            cube([bar, 2*half_inner, bar], center=false);
        }
      }

      // Front/back walls at y = ±175
      for (side = [-1, 1]) {
        sy = side * half_inner;
        y0 = (side == 1) ? sy : sy - bar;
        for (i = [0:5]) {
          x = grid_pos(i);
          translate([x - bar/2, y0, 0])
            cube([bar, bar, 700], center=false);
        }
        for (k = [0:10]) {
          zc = 0 + k * gap;
          translate([-half_inner, y0, zc - bar/2])
            cube([2*half_inner, bar, bar], center=false);
        }
      }
    }

    for (sx = [-1, 1], sy = [-1, 1]) {
      translate([sx * (half_inner + bar/2),
                 sy * (half_inner + bar/2),
                 -20])
        cylinder(d = rod_d, h = 740, $fn = 64);
    }
  }
}

z_min = 240;
z_max = 290;  // height 50 mm

module slice() {
  intersection() {
    cage_full();
    translate([-half_outer - 5, -half_outer - 5, z_min])
      cube([2*(half_outer + 5), 2*(half_outer + 5), z_max - z_min], center=false);
  }
}

translate([0, 0, -z_min])
  slice();
