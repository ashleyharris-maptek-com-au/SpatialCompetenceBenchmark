difference()
{
  union()
  {
    // Vertical corner bars
    translate([-185, -185, 0]) cube([10, 10, 48]);
    translate([175, -185, 0]) cube([10, 10, 48]);
    translate([175, 175, 0]) cube([10, 10, 48]);
    translate([-185, 175, 0]) cube([10, 10, 48]); // Perimeter bars
    translate([-185, -185, 38]) cube([370, 10, 10]);
    translate([-185, 175, 38]) cube([370, 10, 10]);
    translate([-185, -185, 38]) cube([10, 370, 10]);
    translate([175, -185, 38]) cube([10, 370, 10]); // Intermediate grid bars
    translate([-185, -113, 38]) cube([370, 10, 10]);
    translate([-113, -185, 38]) cube([10, 370, 10]);
    translate([-185, -41, 38]) cube([370, 10, 10]);
    translate([-41, -185, 38]) cube([10, 370, 10]);
    translate([-185, 31, 38]) cube([370, 10, 10]);
    translate([31, -185, 38]) cube([10, 370, 10]);
    translate([-185, 103, 38]) cube([370, 10, 10]);
    translate([103, -185, 38]) cube([10, 370, 10]);
  }
  // Holes for M6 rods
  translate([-180, -180, -1]) cylinder(d = 7, h = 50, $fn = 30);
  translate([180, -180, -1]) cylinder(d = 7, h = 50, $fn = 30);
  translate([180, 180, -1]) cylinder(d = 7, h = 50, $fn = 30);
  translate([-180, 180, -1]) cylinder(d = 7, h = 50, $fn = 30);
}
