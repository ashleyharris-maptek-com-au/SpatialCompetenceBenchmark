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
color([0.5, 0.5, 0.55]) translate([2.2005, -0.9979, 0.4000]) rotate([0.00, 0.00, 0.28])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([2.2014, 0.0010, 0.4000]) rotate([0.00, -0.00, -0.47])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([2.1991, 0.9998, 0.4000]) rotate([-0.00, 0.00, -0.02])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([3.7997, -0.9993, 0.4000]) rotate([0.00, -0.00, -0.23])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([3.7992, -0.0007, 0.4000]) rotate([-0.00, 0.00, -0.26])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([3.7979, 0.9972, 0.4000]) rotate([-0.00, 0.00, -0.25])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([3.0000, -1.2020, 0.4000]) rotate([-0.00, -0.00, -0.06])
  cube([0.400, 0.600, 0.800], center = true);
color([0.5, 0.5, 0.55]) translate([3.0000, 1.2004, 0.4000]) rotate([0.00, 0.00, -0.02])
  cube([0.400, 0.600, 0.800], center = true);
color([0.45, 0.45, 0.5]) translate([2.9997, -0.0001, 0.9000]) rotate([0.00, 0.00, 0.00])
  cube([1.800, 2.600, 0.200], center = true);
color([0.5, 0.5, 0.55]) translate([2.2991, -0.8011, 1.3500]) rotate([0.00, 0.00, 0.02])
  cube([0.240, 0.500, 0.700], center = true);
color([0.5, 0.5, 0.55]) translate([2.4859, -0.0004, 1.3643]) rotate([-0.00, 28.97, -0.03])
  cube([0.240, 0.500, 0.700], center = true);
color([0.5, 0.5, 0.55]) translate([2.2997, 0.8004, 1.3500]) rotate([0.00, 0.00, -0.09])
  cube([0.240, 0.500, 0.700], center = true);
color([0.5, 0.5, 0.55]) translate([3.6998, -0.8000, 1.3500]) rotate([0.00, 0.00, -0.07])
  cube([0.240, 0.500, 0.700], center = true);
color([0.5, 0.5, 0.55]) translate([3.7006, -0.0001, 1.3499]) rotate([0.00, -0.00, 0.12])
  cube([0.240, 0.500, 0.700], center = true);
color([0.5, 0.5, 0.55]) translate([3.7000, 0.7999, 1.3500]) rotate([0.00, 0.01, -0.04])
  cube([0.240, 0.500, 0.700], center = true);
color([0.5, 0.5, 0.55]) translate([2.2984, -0.9009, 1.8499]) rotate([0.00, 0.00, 0.08])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([3.6983, -0.8995, 1.8499]) rotate([0.00, 0.01, -0.02])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([0.9797, -0.1688, 0.1000]) rotate([151.90, -90.00, 146.12])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([3.7007, -0.3955, 1.7628]) rotate([48.09, 0.04, -0.04])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([1.4677, 0.3278, 0.1500]) rotate([-0.00, 0.00, 19.02])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([3.6993, 0.3953, 1.7627]) rotate([-48.11, -0.03, 0.00])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([2.2997, 0.9002, 1.8500]) rotate([0.00, 0.00, -0.05])
  cube([0.200, 0.300, 0.300], center = true);
color([0.5, 0.5, 0.55]) translate([3.7000, 0.8998, 1.8499]) rotate([0.00, 0.00, 0.01])
  cube([0.200, 0.300, 0.300], center = true);
color([0.55, 0.55, 0.6]) translate([3.0104, -0.0000, 1.5000]) rotate([0.00, 0.00, -0.03])
  cube([0.500, 0.500, 1.000], center = true);
color([0.6, 0.4, 0.2]) translate([3.0075, -0.0001, 2.0799]) rotate([0.00, 0.00, -0.06])
  cube([0.600, 0.600, 0.160], center = true); // Targets
color([0.0, 0.8, 0.0]) translate([3.0078, -0.0038, 2.3599]) sphere(r = 0.2);
color([0.0, 0.8, 0.0]) translate([3.0000, -0.0000, 0.2000]) sphere(r = 0.2);
color([0.0, 0.8, 0.0]) translate([-10.8643, -0.0000, 0.2000]) sphere(r = 0.2);
