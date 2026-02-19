difference()
{
  union()
  {
    // Perimeter bars
    translate([-185, -185, 0]) cube([370, 10, 10]);
    translate([-185, 175, 0]) cube([370, 10, 10]);
    translate([-185, -185, 0]) cube([10, 370, 10]);
    translate([175, -185, 0]) cube([10, 370, 10]); // Intermediate grid bars
    translate([-185, -113, 0]) cube([370, 10, 10]);
    translate([-113, -185, 0]) cube([10, 370, 10]);
    translate([-185, -41, 0]) cube([370, 10, 10]);
    translate([-41, -185, 0]) cube([10, 370, 10]);
    translate([-185, 31, 0]) cube([370, 10, 10]);
    translate([31, -185, 0]) cube([10, 370, 10]);
    translate([-185, 103, 0]) cube([370, 10, 10]);
    translate([103, -185, 0]) cube([10, 370, 10]); // Vertical corner bars
    translate([-185, -185, 0]) cube([10, 10, 48]);
    translate([175, -185, 0]) cube([10, 10, 48]);
    translate([175, 175, 0]) cube([10, 10, 48]);
    translate([-185, 175, 0]) cube([10, 10, 48]);
  }
  // Holes for M6 rods
  translate([-180, -180, -1]) cylinder(d = 7, h = 50, $fn = 30);
  translate([180, -180, -1]) cylinder(d = 7, h = 50, $fn = 30);
  translate([180, 180, -1]) cylinder(d = 7, h = 50, $fn = 30);
  translate([-180, 180, -1]) cylinder(d = 7, h = 50, $fn = 30);
}
