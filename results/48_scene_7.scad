// Angry Birds Scene - Test 48
$fn = 24;

// Colors
ground_color = [0.3, 0.5, 0.2];
wood_color = [0.6, 0.4, 0.2];
target_color = [0.1, 0.8, 0.1];
catapult_color = [0.4, 0.3, 0.25];
projectile_color = [0.8, 0.2, 0.2];
grid_color = [0.5, 0.5, 0.5, 0.3];
path_colors = [[1.0, 0.3, 0.3], [0.3, 0.3, 1.0], [1.0, 0.8, 0.2]];  // Red, Blue, Yellow for shots 1,2,3

// Ground
color(ground_color) translate([0, 0, -0.05]) cube([20.0, 20.0, 0.1], center=true);

// Grid marks
color(grid_color) {
  translate([-8, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([-6, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([-4, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([-2, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([0, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([2, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([4, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([6, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([8, 0, 0.01]) cube([0.05, 16, 0.02], center=true);
  translate([0, -8, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, -6, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, -4, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, -2, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, 0, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, 2, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, 4, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, 6, 0.01]) cube([16, 0.05, 0.02], center=true);
  translate([0, 8, 0.01]) cube([16, 0.05, 0.02], center=true);
}

// Catapult
color(catapult_color) {
  translate([-8.0, 0.0, 0.15]) cube([0.8, 0.6, 0.3], center=true);
  translate([-8.2, -0.2, 0.5]) cube([0.1, 0.1, 0.7], center=true);
  translate([-8.2, 0.2, 0.5]) cube([0.1, 0.1, 0.7], center=true);
  translate([-8.2, 0.0, 0.85]) cube([0.1, 0.5, 0.1], center=true);
  translate([-7.7, 0.0, 0.75]) rotate([0, -30, 0]) cube([1.2, 0.08, 0.08], center=true);
  translate([-7.2, 0.0, 1.0]) sphere(r=0.2);
}

// Structure blocks
color([0.6, 0.4, 0.2]) translate([2.2051, -0.9979, 1.2000]) rotate([0.00, 0.00, -1.05]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([2.2031, 1.0011, 1.2000]) rotate([-0.00, 0.03, -0.12]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([3.8078, -0.9939, 1.2000]) rotate([0.01, 0.00, -4.34]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([3.8057, 1.0046, 1.2000]) rotate([-0.01, 0.00, 1.22]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([2.2807, 0.0244, 2.5000]) rotate([-0.00, 0.03, -0.04]) cube([0.200, 2.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.8870, 0.0301, 2.5000]) rotate([-0.00, 0.00, 0.09]) cube([0.200, 2.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.1702, -0.9510, 2.7000]) rotate([-0.00, 0.00, 0.14]) cube([1.800, 0.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.1709, 1.0156, 2.7000]) rotate([-0.00, -0.00, 1.23]) cube([1.800, 0.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9999, -0.5001, 0.4000]) rotate([0.00, 0.00, 0.02]) cube([0.120, 0.120, 0.800], center=true);
color([0.6, 0.4, 0.2]) translate([2.9997, -0.5001, 0.8300]) rotate([0.00, 0.00, 0.00]) cube([0.240, 0.240, 0.060], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.4999, 0.7000]) rotate([0.00, 0.00, 0.02]) cube([0.120, 0.120, 1.400], center=true);
color([0.6, 0.4, 0.2]) translate([2.9997, 0.4997, 1.4300]) rotate([0.00, 0.00, 0.01]) cube([0.240, 0.240, 0.060], center=true);
color([0.6, 0.4, 0.2]) translate([2.6000, -0.0000, 1.0000]) rotate([-0.00, 0.00, 0.01]) cube([0.120, 0.120, 2.000], center=true);
color([0.6, 0.4, 0.2]) translate([2.5998, -0.0002, 2.0300]) rotate([-0.00, 0.00, -0.00]) cube([0.240, 0.240, 0.060], center=true);
color([0.6, 0.4, 0.2]) translate([3.4000, -0.0001, 0.5500]) rotate([0.00, 0.00, 0.02]) cube([0.120, 0.120, 1.100], center=true);
color([0.6, 0.4, 0.2]) translate([3.3997, -0.0003, 1.1300]) rotate([0.00, 0.00, 0.01]) cube([0.240, 0.240, 0.060], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([3.0009, -0.5005, 1.0100]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([3.0013, 0.4999, 1.6100]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([2.6013, -0.0001, 2.2100]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([3.4013, -0.0002, 1.3100]) sphere(r=0.15);
