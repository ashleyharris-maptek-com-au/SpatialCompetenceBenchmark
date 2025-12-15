// ring_17.scad - ring index 17 (z bottom = 170 mm)
$fn = 64; bar = 10; half_b = bar/2; outer = 370; half_outer = outer/2;
front_y = 180; back_y = -180; left_x = -180; right_x = 180;
x_centers = [-170, -100, -30, 40, 110, 180];
z_centers = [5, 85, 155, 225, 295, 365, 435, 505, 575, 645, 715]; ring_z = 170;
module place_box(cx, cy, sx, sy) { translate([cx - sx/2, cy - sy/2, 0]) cube([sx, sy, bar]); }

difference() { union() {
    for (x = x_centers) { place_box(x, front_y, bar, bar); place_box(x, back_y, bar, bar); }
    for (y = x_centers) { place_box(left_x, y, bar, bar); place_box(right_x, y, bar, bar); }
    for (zc = z_centers) if ((zc - half_b < ring_z + bar) && (zc + half_b > ring_z)) {
        translate([-half_outer, front_y - half_b, 0]) cube([outer, bar, bar]);
        translate([-half_outer, back_y - half_b, 0])  cube([outer, bar, bar]);
        translate([left_x - half_b, -half_outer, 0])  cube([bar, outer, bar]);
        translate([right_x - half_b, -half_outer, 0]) cube([bar, outer, bar]);
    }
  }
  for (cx = [-180, 180]) for (cy = [-180, 180]) translate([cx, cy, 0]) cylinder(h = bar, r = 3.5, $fn = 64);
}
