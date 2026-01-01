module cage_panel_section(height, bar_thickness, gap_size)
{
  total_width = bar_thickness + gap_size;
  num_bars = floor(350 / total_width);
  remaining_space = 350 -(num_bars * total_width);
  final_gap = remaining_space / (num_bars + 1);

  difference()
  {
    union()
    {
      for(i = [0:num_bars])
      {
        translate([i * total_width + i * gap_size, 0, 0]) cube([bar_thickness, 350, height]);
      }
      translate([num_bars * total_width + num_bars * gap_size, 0, 0]) cube([bar_thickness, 350, height]);
    }
    union()
    {
      for(i = [0:num_bars -1])
      {
        translate([i * total_width + i * gap_size + bar_thickness, 0, 0]) cube([gap_size, 350, height]);
      }
      translate([num_bars * total_width + num_bars * gap_size + bar_thickness, 0, 0])
        cube([350 -(num_bars * total_width + num_bars * gap_size), 350, height]);
    }
  }
}

module create_cage_section(height, bar_thickness, gap_size, length)
{
  total_width = bar_thickness + gap_size;
  num_bars = floor(length / total_width);
  remaining_space = length -(num_bars * total_width);
  final_gap = remaining_space / (num_bars + 1);

  difference()
  {
    union()
    {
      for(i = [0:num_bars])
      {
        translate([0, i * total_width + i * gap_size, 0]) cube([length, bar_thickness, height]);
      }
      translate([0, num_bars * total_width + num_bars * gap_size, 0]) cube([length, bar_thickness, height]);
    }
    union()
    {
      for(i = [0:num_bars -1])
      {
        translate([0, i * total_width + i * gap_size + bar_thickness, 0]) cube([length, gap_size, height]);
      }
      translate([0, num_bars * total_width + num_bars * gap_size + bar_thickness, 0])
        cube([length, length -(num_bars * total_width + num_bars * gap_size), height]);
    }
  }
}

module cage_panel(height, bar_thickness, gap_size, panel_length)
{
  union()
  {
    cage_panel_section(height, bar_thickness, gap_size);
    translate([0, panel_length, 0]) rotate([0, 0, 90]) cage_panel_section(height, bar_thickness, gap_size);
  }
}

module cage_frame(height, bar_thickness, gap_size, cage_width, cage_depth)
{
  union()
  {
    // Side panels (along width)
    for(y = [0, cage_depth -bar_thickness])
    {
      translate([0, y, 0]) cage_panel(height, bar_thickness, gap_size, cage_width);
    }
    // Front/Back panels (along depth)
    for(x = [bar_thickness, cage_width -bar_thickness])
    {
      translate([x, 0, 0]) rotate([0, 0, 90]) cage_panel(height, bar_thickness, gap_size, cage_depth);
    }
  }
}

// Constants
bar_thickness = 10;
gap = 60; // Avg of 50-100mm, ensures uniform gap.
cage_internal_width = 350;
cage_internal_depth = 350;
cage_internal_height = 700; // Calculate actual panel dimensions
cage_width = cage_internal_width + 2 * bar_thickness;
cage_depth = cage_internal_depth + 2 * bar_thickness;
cage_height = cage_internal_height + 2 *
  bar_thickness; // M6 rod diameter is 6mm, so hole diameter should be slightly larger for clearance. 6.5mm.
rod_hole_diameter = 6.5;

module create_cage_part(panel_type, height, bar_thickness, gap_size, panel_length, is_corner = false)
{
  part_length = panel_length;
  part_height = height;
  part_width = part_length;

  if(panel_type == "horizontal")
  {
    create_cage_section(part_height, bar_thickness, gap_size, part_width);
  }
  else
  {
    // vertical
    rotate([0, 0, 90]) create_cage_section(part_height, bar_thickness, gap_size, part_width);
  }
}

// Determine number of bars and gap for the specified dimensions
num_horizontal_bars = floor(350 / (bar_thickness + gap)) + 1;
actual_gap_horizontal = (350 -(num_horizontal_bars -1) * bar_thickness) / num_horizontal_bars;

num_vertical_bars = floor(350 / (bar_thickness + gap)) + 1;
actual_gap_vertical = (350 -(num_vertical_bars -1) * bar_thickness) /
  num_vertical_bars; // Ensure the gap is within the desired range
if(actual_gap_horizontal < 50 || actual_gap_horizontal > 100)
{
  echo("Warning: Horizontal gap is out of range.");
}
if(actual_gap_vertical < 50 || actual_gap_vertical > 100)
{
  echo("Warning: Vertical gap is out of range.");
}

// Define the effective gap for panel generation
final_gap = actual_gap_horizontal; // Split the cage into printable parts, considering the 50mm height limit.
section_height = 50;
num_sections = ceil(cage_height / section_height); // Each part will be a section of the cage frame.
// We need 4 vertical corner posts and the connecting horizontal and vertical bars.

// Corner post part
module corner_post(height, bar_thickness, rod_hole_diameter)
{
  difference()
  {
    cube([bar_thickness, bar_thickness, height]);
    translate([bar_thickness / 2, bar_thickness / 2, 0]) cylinder(h = height, r = rod_hole_diameter / 2, $fn = 32);
  }
}

// Generate sections of the corner posts
for(i = [0:num_sections -1])
{
  start_z = i * section_height;
  current_section_height = min(section_height, cage_height -start_z); // Bottom corners
  if(i == 0)
  {
    translate([-cage_width / 2, -cage_depth / 2, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
    translate([cage_width / 2 -bar_thickness, -cage_depth / 2, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
    translate([-cage_width / 2, cage_depth / 2 -bar_thickness, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
    translate([cage_width / 2 -bar_thickness, cage_depth / 2 -bar_thickness, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
  }
  else
  {
    // Mid and top sections of corner posts
    translate([-cage_width / 2, -cage_depth / 2, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
    translate([cage_width / 2 -bar_thickness, -cage_depth / 2, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
    translate([-cage_width / 2, cage_depth / 2 -bar_thickness, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
    translate([cage_width / 2 -bar_thickness, cage_depth / 2 -bar_thickness, start_z])
      corner_post(current_section_height, bar_thickness, rod_hole_diameter);
  }
}

// Generate the horizontal and vertical bars for each section
for(i = [0:num_sections -1])
{
  start_z = i * section_height;
  current_section_height = min(section_height, cage_height -start_z); // Horizontal bars (along the width)
  for(y = [bar_thickness:bar_thickness + final_gap:cage_depth -bar_thickness -bar_thickness])
  {
    translate([-cage_width / 2, y, start_z])
      create_cage_part("horizontal", current_section_height, bar_thickness, final_gap, cage_width);
  }

  // Vertical bars (along the depth)
  for(x = [bar_thickness:bar_thickness + final_gap:cage_width -bar_thickness -bar_thickness])
  {
    translate([x -cage_width / 2, -cage_depth / 2, start_z])
      create_cage_part("vertical", current_section_height, bar_thickness, final_gap, cage_depth);
  }
}
