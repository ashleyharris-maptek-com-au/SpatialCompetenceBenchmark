module cage_panel()
{
  // Dimensions
  width = 370;
  height = 360;
  thick = 10;
  bar_size = 10;
  hole_rad = 3.25; // 6.5mm diameter clearance for M6

  // Y-positions of horizontal bars (Centers)
  // Calculated to be uniform: 5, 93.75, 182.5, 271.25, 360
  // Bar 0: Y=0..10 (Full bar)
  // Bar 4: Y=355..360 (Half bar at top)
  bar_centers = [5, 93.75, 182.5, 271.25, 360]; // X-positions of vertical bars (Centers)
  // -180 (Left Col), -90, 0, 90, 180 (Right Col)
  // Inner bars at -90, 0, 90
  vert_centers = [-90, 0, 90];

  difference()
  {
    union()
    {
      // 1. Left Column (Mitered)
      // Extrudes along Y. Profile in XZ.
      // Outer corner at X=-185. Inner corner at X=-175.
      // Miter slope: At Z=0 (Outer), X=-185. At Z=10 (Inner), X=-175.
      translate([0, height / 2, 0]) rotate([90, 0, 0]) linear_extrude(height, center = true)
        polygon(points = [[-185, 0], [-175, 0], [-175, 10], [-185, 0]]); // 2. Right Column (Mitered)
      translate([0, height / 2, 0]) rotate([90, 0, 0]) linear_extrude(height, center = true)
        polygon(points = [[185, 0], [175, 0], [175, 10], [185, 0]]); // 3. Horizontal Bars
      for(i = [0:4])
      {
        y_c = bar_centers[i]; // Determine bar height and offset based on position
        // Bottom bar (i=0): Full 10mm, Center 5. Range 0..10
        // Top bar (i=4): Half 5mm, Center 360? No, Range 355..360.
        // Others: Full 10mm.

        b_h = (i == 4) ? 5 : 10;
        y_pos = (i == 4) ? 357.5 : y_c; // Bar spans between columns (-175 to 175)
        translate([0, y_pos, thick / 2]) cube([350, b_h, thick], center = true);
      }

      // 4. Intermediate Vertical Bars
      for(x_c = vert_centers)
      {
        translate([x_c, height / 2, thick / 2]) cube([bar_size, height, thick], center = true);
      }
    }

    // Subtract Holes for Threaded Rods
    // Located at the center of the corner bars (-180, 5) and (180, 5)
    // Running along Y axis
    translate([-180, height / 2, 5]) rotate([90, 0, 0]) cylinder(r = hole_rad, h = height + 1, center = true, $fn = 32);

    translate([180, height / 2, 5]) rotate([90, 0, 0]) cylinder(r = hole_rad, h = height + 1, center = true, $fn = 32);
  }
}

cage_panel();
