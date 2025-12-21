// OpenSCAD file
// Base of the cage
difference() {
  cube([350, 350, 10], center = true);
  for (i = [-2:2]) {
    translate([i * 50, 0, 0]) cube([10, 350, 10], center = true);
    translate([0, i * 50, 0]) cube([350, 10, 10], center = true);
  }
  translate([0, 0, 5]) cylinder(h = 10, r = 3, $fn = 100);
}
