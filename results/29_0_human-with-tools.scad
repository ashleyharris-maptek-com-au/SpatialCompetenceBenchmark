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

  // Bottom and top part are identical.
  for(x = [360 / 2, -360 / 2]) for(y = [360 / 2, -360 / 2])
  {
    translate([x, y, 0]) cylinder(h = 100, d = 6.1, center = true);
  }
}
