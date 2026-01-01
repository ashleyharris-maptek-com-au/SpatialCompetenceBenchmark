module pyramid_pin()
{
  rotate([0, 0, 45]) cylinder(h = 3, d1 = 5.4, d2 = 0, $fn = 4);
}

module hemi_male()
{
  bar_h = 39.375;
  union()
  {
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
            translate([pos[0], pos[1], 5 + bar_h / 2]) cube([10, 10, bar_h], center = true); // Male Pins
            translate([pos[0], pos[1], 5 + bar_h]) pyramid_pin();
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
    }
  }
}

hemi_male();
