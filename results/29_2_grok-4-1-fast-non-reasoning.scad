// Top layer with partial vertical stubs
module cage_layer_top()
{
  bar_thick = 10;
  gap = 80;
  layer_h = 50;
  top_stub_h = 30; // Partial height
  rod_hole = 6.2; // Bottom horizontal frame
  for(y = [-175, -85, 0, 85, 175])
  {
    translate([0, y * 2, -layer_h / 2]) cube([450, bar_thick, bar_thick], center = true);
  }
  for(x = [-225, -135, -45, 45, 135])
  {
    translate([x * 2, 0, -layer_h / 2]) cube([bar_thick, 450, bar_thick], center = true);
  }

  // Top horizontal frame
  for(y = [-175, -85, 0, 85, 175])
  {
    translate([0, y * 2, layer_h / 2]) cube([450, bar_thick, bar_thick], center = true);
  }
  for(x = [-225, -135, -45, 45, 135])
  {
    translate([x * 2, 0, layer_h / 2]) cube([bar_thick, 450, bar_thick], center = true);
  }

  // Vertical corner stubs (shorter, rod accessible from top)
  corners = [[-225, -175], [-225, 175], [225, -175], [225, 175]];
  for(c = corners)
  {
    translate([c[0] * 2, c[1] * 2, layer_h / 2 -top_stub_h / 2]) difference()
    {
      cube([bar_thick, bar_thick, top_stub_h], center = true);
      translate([0, 0, 0]) cube([rod_hole, rod_hole, top_stub_h + 0.1], center = true);
    }
  }
}

cage_layer_top();
