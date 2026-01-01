module bar(length, width, height)
{
  translate([-width / 2, -width / 2, 0]) cube([width, width, length]);
}

module side_panel(width, height, bar_width, gap)
{
  difference()
  {
    union()
    {
      for(y = [0:gap + bar_width:height])
      {
        translate([0, y, 0]) bar(width, bar_width, bar_width);
      }
      for(x = [0:gap + bar_width:width])
      {
        translate([x, 0, 0]) bar(bar_width, height, bar_width);
      }
    }
    translate([-bar_width / 2, -bar_width / 2, -1]) cube([width + bar_width, height + bar_width, bar_width + 2]);
  }
}

module corner_post(length, width)
{
  difference()
  {
    bar(length, width, width);
    translate([-width / 2, -width / 2, width / 2]) rotate([0, 90, 0]) cylinder(h = width + 1, d = 6.2, $fn = 50);
  }
}

// Front and Back Panels
side_panel(350, 700, 10, 70); // Left and Right Panels
rotate([0, 0, 90]) side_panel(700, 350, 10, 70); // Corner Posts
translate([175, 0, 0]) corner_post(700, 10);
translate([-175, 0, 0]) corner_post(700, 10);
translate([175, 350, 0]) corner_post(700, 10);
translate([-175, 350, 0]) corner_post(700, 10);
