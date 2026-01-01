module pyramid_socket()
{
  // Inverted pyramid for subtraction, slightly larger for clearance
  rotate([0, 0, 45]) cylinder(h = 3.2, d1 = 0, d2 = 6.0, $fn = 4);
}

module hemi_female()
{
  bar_h = 39.375;
  difference()
  {
    union()
    {
      // Base Ring
      translate([0, 0, 2.5]) difference()
      {
        cube([370, 370, 5], center = true);
        cube([350, 350, 5.1], center = true);
      }
      // Bars
      // Corners
      for(x = [-180, 180])
      {
        for(y = [-180, 180])
        {
          translate([x, y, 5 + bar_h / 2]) cube([10, 10, bar_h], center = true);
        }
      }
      // Intermediates
      for(i = [-90, 0, 90])
      {
        for(pos = [[i, -180], [i, 180], [-180, i], [180, i]])
        {
          translate([pos[0], pos[1], 5 + bar_h / 2]) cube([10, 10, bar_h], center = true);
        }
      }
    }
    // Corner Holes
    for(x = [-180, 180])
    {
      for(y = [-180, 180])
      {
        translate([x, y, -1]) cylinder(h = 100, d = 7, $fn = 20);
      }
    }
    // Female Sockets
    for(i = [-90, 0, 90])
    {
      for(pos = [[i, -180], [i, 180], [-180, i], [180, i]])
      {
        translate([pos[0], pos[1], 5 + bar_h -3.2]) pyramid_socket();
      }
    }
  }
}

hemi_female();
