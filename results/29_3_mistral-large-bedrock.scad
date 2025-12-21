// OpenSCAD file
// Side of the cage
difference() {
  translate([175, 0, 0]) cube([700, 350, 10], center = true);
  for (i = [-2:2]) {
    translate([175, i * 50, 0]) cube([700, 10, 10], center = true);
    translate([i * 50, 0, 0]) cube([10, 350, 10], center = true);
  }
  translate([-175, 0, 5]) cylinder(h = 10, r = 3, $fn = 100);
  translate([175, 0, 5]) cylinder(h = 10, r = 3, $fn = 100);
}
