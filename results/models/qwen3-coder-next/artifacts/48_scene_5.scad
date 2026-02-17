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
color([0.5, 0.3, 0.1]) translate([2.0000, -1.5000, 0.4000]) rotate([0.00, 0.00, 0.00])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([2.1818, -1.2272, 0.4000]) rotate([0.00, 0.00, 0.08])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([2.3536, -0.9528, 0.4000]) rotate([-0.00, 0.00, 2.76])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([2.5066, -0.6938, 0.4000]) rotate([0.00, 0.00, 10.39])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([2.6411, -0.4554, 0.4000]) rotate([0.00, 0.00, 26.83])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([2.6302, -0.1218, 0.4000]) rotate([0.00, 0.00, 62.16])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([3.3697, 0.1220, 0.4000]) rotate([-0.00, -0.00, 62.03])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([3.3588, 0.4555, 0.4000]) rotate([0.00, -0.00, 26.85])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([3.4942, 0.6937, 0.4000]) rotate([-0.00, -0.00, 10.63])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([3.6448, 0.9530, 0.4000]) rotate([-0.00, -0.00, 2.24])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([3.8158, 1.2278, 0.4000]) rotate([0.00, 0.00, 0.57])
  cube([0.160, 0.500, 0.800], center = true);
color([0.5, 0.3, 0.1]) translate([3.9732, 1.4947, 0.4000]) rotate([0.00, 0.00, 7.78])
  cube([0.160, 0.500, 0.800], center = true);
color([0.6, 0.4, 0.2]) translate([0.8000, 0.0001, 0.5000]) rotate([0.00, -0.00, -0.00])
  cube([1.000, 1.000, 1.000], center = true); // Targets
color([0.0, 0.8, 0.0]) translate([6.2905, 1.9474, 0.2000]) sphere(r = 0.2);
color([0.0, 0.8, 0.0]) translate([2.9992, -0.0013, 0.2000]) sphere(r = 0.2);
