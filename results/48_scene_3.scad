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
color([0.6, 0.4, 0.2]) translate([3.0000, -1.0000, 0.1500]) rotate([0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -1.0000, 0.1500]) rotate([-0.00, 0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.5000, 0.1500]) rotate([0.00, 0.00, -0.01]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -0.5000, 0.1500]) rotate([0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.0000, 0.1500]) rotate([-0.00, -0.01, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.0000, 0.1500]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.5000, 0.1500]) rotate([0.00, 0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.5000, 0.1500]) rotate([-0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 1.0000, 0.1500]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 1.0000, 0.1500]) rotate([-0.00, 0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.7500, 0.4500]) rotate([-0.00, -0.00, 0.01]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -0.7500, 0.4500]) rotate([-0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.2500, 0.4500]) rotate([-0.01, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -0.2500, 0.4500]) rotate([0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.2500, 0.4500]) rotate([0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.2500, 0.4500]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.7500, 0.4500]) rotate([0.00, 0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.7500, 0.4500]) rotate([-0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.5000, 0.7499]) rotate([-0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -0.5000, 0.7500]) rotate([-0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.0000, 0.7499]) rotate([-0.00, 0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.0000, 0.7500]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.5000, 0.7499]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.5000, 0.7500]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, -0.2500, 1.0499]) rotate([-0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -0.2500, 1.0499]) rotate([-0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.2500, 1.0499]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, 0.2500, 1.0499]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0000, 0.0000, 1.3499]) rotate([0.00, -0.00, 0.00]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0000, -0.0000, 1.3499]) rotate([0.00, -0.00, -0.00]) cube([0.400, 0.500, 0.300], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([3.0000, -0.1500, 1.6499]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([3.0000, 0.1500, 1.6499]) sphere(r=0.15);
