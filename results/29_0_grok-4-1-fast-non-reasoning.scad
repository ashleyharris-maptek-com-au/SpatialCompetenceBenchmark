// Bottom layer with full 50mm vertical stubs
module cage_layer_bottom()
{
  bar_thick = 10;
  gap = 80;
  layer_h = 50;
  rod_hole = 6.2; // Bottom frame horizontal bars
  // X direction bars at Y positions
  for(y = [-175, -85, 0, 85, 175])
  {
    translate([0, y * 2, 0]) cube([450, bar_thick, bar_thick], center = true);
  }

  // Y direction bars at X positions
  for(x = [-225, -135, -45, 45, 135])
  {
    translate([x * 2, 0, 0]) cube([bar_thick, 450, bar_thick], center = true);
  }

  // Vertical corner stubs with rod holes (only corners)
  corners = [[-225, -175], [-225, 175], [225, -175], [225, 175]];
  for(c = corners)
  {
    translate([c[0] * 2, c[1] * 2, layer_h / 2]) difference()
    {
      cube([bar_thick, bar_thick, layer_h], center = true);
      translate([0, 0, layer_h / 4]) cube([rod_hole, rod_hole, layer_h / 2 + 0.1], center = true);
    }
  }
}

cage_layer_bottom();
