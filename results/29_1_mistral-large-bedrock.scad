// OpenSCAD file
// Top of the cage
difference() {
  translate([0, 0, 690]) cube([350, 350, 10], center = true);
  for (i = [-2:2]) {
    translate([i * 50, 0, 690]) cube([10, 350, 10], center = true);
    translate([0, i * 50, 690]) cube([350, 10, 10], center = true);
  }
  translate([0, 0, 695]) cylinder(h = 10, r = 3, $fn = 100);
}
