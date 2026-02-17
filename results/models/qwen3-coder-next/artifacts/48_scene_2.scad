// Angry Birds Scene - Test 48
$fn = 24; // Colors
ground_color = [0.3, 0.5, 0.2];
wood_color = [0.6, 0.4, 0.2];
target_color = [0.1, 0.8, 0.1];
catapult_color = [0.4, 0.3, 0.25];
projectile_color = [0.8, 0.2, 0.2];
grid_color = [0.5, 0.5, 0.5, 0.3];
path_colors = [[1.0, 0.3, 0.3], [0.3, 0.3, 1.0], [1.0, 0.8, 0.2]]; // Red, Blue, Yellow for shots 1,2,3

// Ground
color(ground_color) translate([0, 0, -0.05]) cube([20.0, 20.0, 0.1], center = true); // Grid marks
color(grid_color)
{
  translate([-8, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([-6, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([-4, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([-2, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([0, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([2, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([4, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([6, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([8, 0, 0.01]) cube([0.05, 16, 0.02], center = true);
  translate([0, -8, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, -6, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, -4, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, -2, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, 0, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, 2, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, 4, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, 6, 0.01]) cube([16, 0.05, 0.02], center = true);
  translate([0, 8, 0.01]) cube([16, 0.05, 0.02], center = true);
}

// Catapult
color(catapult_color)
{
  translate([-8.0, 0.0, 0.15]) cube([0.8, 0.6, 0.3], center = true);
  translate([-8.2, -0.2, 0.5]) cube([0.1, 0.1, 0.7], center = true);
  translate([-8.2, 0.2, 0.5]) cube([0.1, 0.1, 0.7], center = true);
  translate([-8.2, 0.0, 0.85]) cube([0.1, 0.5, 0.1], center = true);
  translate([-7.7, 0.0, 0.75]) rotate([0, -30, 0]) cube([1.2, 0.08, 0.08], center = true);
  translate([-7.2, 0.0, 1.0]) sphere(r = 0.2);
}

// Structure blocks
color([0.6, 0.4, 0.2]) translate([2.0000, -0.8000, 0.6000]) rotate([-0.00, -0.00, -0.00])
  cube([0.300, 0.300, 1.200], center = true);
color([0.6, 0.4, 0.2]) translate([4.0000, -0.8000, 0.6000]) rotate([-0.00, 0.00, 0.00])
  cube([0.300, 0.300, 1.200], center = true);
color([0.6, 0.4, 0.2]) translate([2.0000, 0.8000, 0.6000]) rotate([0.00, 0.00, -0.00])
  cube([0.300, 0.300, 1.200], center = true);
color([0.6, 0.4, 0.2]) translate([4.0000, 0.8000, 0.6000]) rotate([0.00, 0.00, 0.00])
  cube([0.300, 0.300, 1.200], center = true);
color([0.5, 0.5, 0.5]) translate([3.0000, -0.0000, 1.3000]) rotate([0.00, 0.00, 0.00])
  cube([2.400, 2.000, 0.200], center = true);
color([0.5, 0.5, 0.5]) translate([-0.0273, 0.0003, 0.8531]) rotate([-0.00, -40.35, 0.00])
  cube([2.400, 2.000, 0.200], center = true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.9000, 1.6000]) rotate([0.00, -0.00, -0.00])
  cube([2.000, 0.100, 0.400], center = true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.9000, 1.6000]) rotate([0.00, 0.00, -0.00])
  cube([2.000, 0.100, 0.400], center = true);
color([0.6, 0.4, 0.2]) translate([0.8000, 0.0000, 0.5000]) rotate([0.00, -0.00, -0.00])
  cube([1.000, 1.000, 1.000], center = true); // Targets
color([0.0, 0.8, 0.0]) translate([3.0000, -0.0000, 0.2000]) sphere(r = 0.2);
color([0.0, 0.8, 0.0]) translate([2.5000, 0.0000, 0.2000]) sphere(r = 0.2);
color([0.0, 0.8, 0.0]) translate([3.5000, -0.0000, 0.2000]) sphere(r = 0.2);
