rotate([0, 0, 90]) translate([0, 0, 5]) difference()
{
  union()
  {
    for(x = [-370 / 2 + 5:72:220])
    {
      translate([x, 0, 0]) cube([10, 370, 10], center = true);
    }

    for(y = [-370 / 2 + 5:72:220])
    {
      translate([0, y, 0]) cube([370, 10, 10], center = true);
    }
  }

  translate([364, 0, 0]) cube([380, 380, 20], center = true);

  translate([0, 220, 0]) cube([80, 100, 20], center = true);
  translate([0, -220, 0]) cube([80, 100, 20], center = true);

  translate([0, 180, 0]) rotate([0, 90, 0]) cylinder(h = 1000, d = 6.1, center = true);
  translate([0, -180, 0]) rotate([0, 90, 0]) cylinder(h = 1000, d = 6.1, center = true);
}
