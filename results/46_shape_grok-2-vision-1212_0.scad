// Auto-generated extrusion assembly
$fn = 20;

module extrusion_2020(length)
{
  // 20mm x 20mm extrusion, colored faces
  translate([0, 0, length / 2]) difference()
  {
    cube([0.02, 0.02, length], center = true); // Hollow out slightly for visual effect
    cube([0.016, 0.016, length + 0.001], center = true);
  }
}

module colored_extrusion(start, end, white_dir)
{
  // Calculate direction and length
  dir = end -start;
  len = norm(dir); // Calculate rotation to align Z with direction
  if(len > 0.001)
  {
    translate(start) multmatrix(m = look_at(dir, white_dir)) extrusion_2020(len);
  }
}

// Look-at matrix helper
function look_at(dir, up) = let(z = dir / norm(dir), x = cross(up, z) / norm(cross(up, z)), y = cross(z, x))
  [[x[0], y[0], z[0], 0], [x[1], y[1], z[1], 0], [x[2], y[2], z[2], 0], [0, 0, 0, 1]];

module connector(pos)
{
  translate(pos) color([0.3, 0.3, 0.3]) sphere(r = 0.015);
}

// Extrusion 1
translate([0.500000, 0.000000, 0.000000]) rotate([0, 90.00, 0.00]) color([0.7, 0.7, 0.8])
  cube([0.02, 0.02, 1.000000], center = true);

connector([0.000000, 0.000000, 0.000000]);
connector([1.000000, 0.000000, 0.000000]);
