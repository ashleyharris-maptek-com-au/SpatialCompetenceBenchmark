module pyramid_pin()
{
  rotate([0, 0, 45]) cylinder(h = 3, d1 = 5.4, d2 = 0, $fn = 4);
}

module shim_body()
{
  difference()
  {
    translate([0, 0, 2.5]) cube([370, 370, 5], center = true);
    translate([0, 0, 2.5]) cube([350, 350, 6], center = true); // Corner holes
    for(x = [-180, 180])
    {
      for(y = [-180, 180])
      {
        translate([x, y, -1]) cylinder(h = 10, d = 7, $fn = 20);
      }
    }
  }
}

shim_body();
