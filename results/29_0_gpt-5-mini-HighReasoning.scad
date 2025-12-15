// ring_00.scad - ring index 0 (z bottom = 0 mm)
// Layer is 10 mm tall; bars are 10 mm square.
$fn = 64;
bar = 10; // 10 mm thickness in Z for each layer
half_b = bar/2;
outer = 370; half_outer = outer/2;
front_y = 180; back_y = -180; left_x = -180; right_x = 180;
x_centers = [-170, -100, -30, 40, 110, 180];
// Horizontal bar centers (Z centers) where bars exist on face planes; these are the 11 grid levels
z_centers = [5, 85, 155, 225, 295, 365, 435, 505, 575, 645, 715];
ring_z = 0; // this layer bottom (global Z)

module place_box(cx, cy, sx, sy) {
  translate([cx - sx/2, cy - sy/2, 0])
    cube([sx, sy, bar]);
}

difference() {
  union() {
    // vertical bars on front and back faces (present every layer)
    for (x = x_centers) {
      place_box(x, front_y, bar, bar);
      place_box(x, back_y, bar, bar);
    }
    // vertical bars on left and right faces
    for (y = x_centers) {
      place_box(left_x, y, bar, bar);
      place_box(right_x, y, bar, bar);
    }

    // horizontal bars (X-direction on front/back, Y-direction on left/right) appear only in layers that intersect their Z extents
    for (zc = z_centers) {
      if ((zc - half_b < ring_z + bar) && (zc + half_b > ring_z)) {
        // front/back horizontal (X across full width)
        translate([-half_outer, front_y - half_b, 0]) cube([outer, bar, bar]);
        translate([-half_outer, back_y - half_b, 0])  cube([outer, bar, bar]);
        // left/right horizontal (Y across full depth)
        translate([left_x - half_b, -half_outer, 0])  cube([bar, outer, bar]);
        translate([right_x - half_b, -half_outer, 0]) cube([bar, outer, bar]);
      }
    }
  }
  // Subtract the 4 rod holes (7 mm diameter) at corners for the M6 rods (clearance)
  for (cx = [-180, 180])
    for (cy = [-180, 180])
      translate([cx, cy, 0])
        cylinder(h = bar, r = 3.5, $fn = 64);
}
