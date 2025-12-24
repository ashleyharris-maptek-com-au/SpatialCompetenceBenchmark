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
color([0.6, 0.4, 0.2]) translate([2.2060, -0.9976, 1.2000]) rotate([0.00, 0.00, -1.21]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([0.8319, 0.9975, 0.1200]) rotate([-90.41, -90.00, 90.62]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([5.4216, -1.0335, 0.1200]) rotate([86.59, 90.00, 90.00]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([5.2504, 1.0367, 0.1200]) rotate([-90.51, 90.00, -89.09]) cube([0.240, 0.240, 2.400], center=true);
color([0.6, 0.4, 0.2]) translate([3.9668, -0.0633, 0.2020]) rotate([90.33, -84.66, -82.02]) cube([0.200, 2.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([7.5004, 0.1776, 0.1000]) rotate([-0.05, -90.00, 45.14]) cube([0.200, 2.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.4279, -1.8131, 0.1000]) rotate([-180.00, -0.00, -118.09]) cube([1.800, 0.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.1467, 1.0058, 0.3145]) rotate([-179.96, -13.98, -179.95]) cube([1.800, 0.200, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.9125, -0.8559, 0.0600]) rotate([82.33, 90.00, 0.00]) cube([0.120, 0.120, 0.800], center=true);
color([0.6, 0.4, 0.2]) translate([8.4904, -1.5933, 0.0300]) rotate([180.00, -0.00, -124.07]) cube([0.240, 0.240, 0.060], center=true);
color([0.6, 0.4, 0.2]) translate([4.0450, 0.4869, 0.0600]) rotate([89.20, 90.00, 94.80]) cube([0.120, 0.120, 1.400], center=true);
color([0.6, 0.4, 0.2]) translate([8.2043, 0.8971, 0.0300]) rotate([0.00, -0.00, -94.71]) cube([0.240, 0.240, 0.060], center=true);
color([0.6, 0.4, 0.2]) translate([4.5144, 0.2732, 0.0600]) rotate([90.35, 89.99, 98.33]) cube([0.120, 0.120, 2.000], center=true);
color([0.6, 0.4, 0.2]) translate([8.3152, 0.0049, 0.0300]) rotate([0.00, -0.00, -0.30]) cube([0.240, 0.240, 0.060], center=true);
color([0.6, 0.4, 0.2]) translate([4.8448, -0.0605, 0.0600]) rotate([88.83, 90.00, 94.66]) cube([0.120, 0.120, 1.100], center=true);
color([0.6, 0.4, 0.2]) translate([7.3251, -0.2795, 0.0300]) rotate([-180.00, 0.00, 16.43]) cube([0.240, 0.240, 0.060], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([10.1299, -2.7992, 0.1500]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([18.3642, -2.0660, 0.1500]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([19.6640, 0.8796, 0.1500]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([25.4424, 0.6015, 0.1500]) sphere(r=0.15);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.943, 0.003, 1.025]) sphere(r=0.08);
  translate([-7.380, 0.028, 1.259]) sphere(r=0.08);
  translate([-6.831, 0.053, 1.470]) sphere(r=0.08);
  translate([-6.296, 0.077, 1.659]) sphere(r=0.08);
  translate([-5.774, 0.101, 1.827]) sphere(r=0.08);
  translate([-5.264, 0.124, 1.974]) sphere(r=0.08);
  translate([-4.765, 0.147, 2.101]) sphere(r=0.08);
  translate([-4.277, 0.169, 2.208]) sphere(r=0.08);
  translate([-3.799, 0.191, 2.297]) sphere(r=0.08);
  translate([-3.331, 0.212, 2.366]) sphere(r=0.08);
  translate([-2.873, 0.233, 2.417]) sphere(r=0.08);
  translate([-2.424, 0.253, 2.451]) sphere(r=0.08);
  translate([-1.983, 0.273, 2.466]) sphere(r=0.08);
  translate([-1.551, 0.293, 2.465]) sphere(r=0.08);
  translate([-1.127, 0.312, 2.447]) sphere(r=0.08);
  translate([-0.711, 0.331, 2.412]) sphere(r=0.08);
  translate([-0.302, 0.350, 2.361]) sphere(r=0.08);
  translate([0.100, 0.368, 2.294]) sphere(r=0.08);
  translate([0.494, 0.386, 2.211]) sphere(r=0.08);
  translate([0.881, 0.403, 2.113]) sphere(r=0.08);
  translate([1.262, 0.421, 1.999]) sphere(r=0.08);
  translate([1.636, 0.438, 1.871]) sphere(r=0.08);
  translate([2.003, 0.454, 1.728]) sphere(r=0.08);
  translate([2.365, 0.471, 1.571]) sphere(r=0.08);
  translate([2.699, 0.486, 1.402]) sphere(r=0.08);
  translate([2.986, 0.498, 1.227]) sphere(r=0.08);
  translate([3.262, 0.511, 1.044]) sphere(r=0.08);
  translate([3.525, 0.522, 0.855]) sphere(r=0.08);
  translate([3.780, 0.534, 0.665]) sphere(r=0.08);
  translate([4.032, 0.547, 0.480]) sphere(r=0.08);
  translate([4.243, 0.567, 0.411]) sphere(r=0.08);
  translate([4.423, 0.591, 0.416]) sphere(r=0.08);
  translate([4.598, 0.615, 0.418]) sphere(r=0.08);
  translate([4.767, 0.639, 0.418]) sphere(r=0.08);
  translate([4.933, 0.663, 0.406]) sphere(r=0.08);
  translate([5.097, 0.687, 0.378]) sphere(r=0.08);
  translate([5.260, 0.711, 0.333]) sphere(r=0.08);
  translate([5.418, 0.734, 0.299]) sphere(r=0.08);
  translate([5.570, 0.755, 0.300]) sphere(r=0.08);
  translate([5.720, 0.776, 0.300]) sphere(r=0.08);
  translate([5.868, 0.797, 0.300]) sphere(r=0.08);
  translate([6.015, 0.818, 0.300]) sphere(r=0.08);
  translate([6.160, 0.839, 0.300]) sphere(r=0.08);
  translate([6.303, 0.859, 0.300]) sphere(r=0.08);
  translate([6.445, 0.879, 0.300]) sphere(r=0.08);
  translate([6.585, 0.899, 0.300]) sphere(r=0.08);
  translate([6.724, 0.919, 0.300]) sphere(r=0.08);
  translate([6.861, 0.938, 0.300]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.944, 0.000, 1.028]) sphere(r=0.08);
  translate([-7.395, 0.000, 1.293]) sphere(r=0.08);
  translate([-6.860, 0.000, 1.534]) sphere(r=0.08);
  translate([-6.339, 0.000, 1.753]) sphere(r=0.08);
  translate([-5.829, 0.000, 1.950]) sphere(r=0.08);
  translate([-5.331, 0.000, 2.125]) sphere(r=0.08);
  translate([-4.845, 0.000, 2.280]) sphere(r=0.08);
  translate([-4.368, 0.000, 2.414]) sphere(r=0.08);
  translate([-3.902, 0.000, 2.529]) sphere(r=0.08);
  translate([-3.445, 0.000, 2.625]) sphere(r=0.08);
  translate([-2.998, 0.000, 2.701]) sphere(r=0.08);
  translate([-2.559, 0.000, 2.760]) sphere(r=0.08);
  translate([-2.128, 0.000, 2.800]) sphere(r=0.08);
  translate([-1.706, 0.000, 2.823]) sphere(r=0.08);
  translate([-1.291, 0.000, 2.828]) sphere(r=0.08);
  translate([-0.884, 0.000, 2.816]) sphere(r=0.08);
  translate([-0.483, 0.000, 2.788]) sphere(r=0.08);
  translate([-0.090, 0.000, 2.743]) sphere(r=0.08);
  translate([0.296, 0.000, 2.683]) sphere(r=0.08);
  translate([0.676, 0.000, 2.606]) sphere(r=0.08);
  translate([1.049, 0.000, 2.514]) sphere(r=0.08);
  translate([1.416, 0.000, 2.406]) sphere(r=0.08);
  translate([1.777, 0.000, 2.283]) sphere(r=0.08);
  translate([2.105, -0.000, 2.135]) sphere(r=0.08);
  translate([2.368, -0.000, 1.967]) sphere(r=0.08);
  translate([2.607, -0.000, 1.790]) sphere(r=0.08);
  translate([2.840, -0.001, 1.600]) sphere(r=0.08);
  translate([3.029, -0.003, 1.432]) sphere(r=0.08);
  translate([3.182, -0.004, 1.281]) sphere(r=0.08);
  translate([3.326, -0.004, 1.124]) sphere(r=0.08);
  translate([3.463, -0.004, 0.957]) sphere(r=0.08);
  translate([3.597, -0.005, 0.779]) sphere(r=0.08);
  translate([3.715, -0.006, 0.610]) sphere(r=0.08);
  translate([3.802, -0.006, 0.528]) sphere(r=0.08);
  translate([3.846, -0.007, 0.588]) sphere(r=0.08);
  translate([3.889, -0.008, 0.633]) sphere(r=0.08);
  translate([3.932, -0.008, 0.660]) sphere(r=0.08);
  translate([3.975, -0.009, 0.671]) sphere(r=0.08);
  translate([4.018, -0.009, 0.664]) sphere(r=0.08);
  translate([4.060, -0.010, 0.640]) sphere(r=0.08);
  translate([4.103, -0.010, 0.600]) sphere(r=0.08);
  translate([4.145, -0.011, 0.543]) sphere(r=0.08);
  translate([4.184, -0.014, 0.485]) sphere(r=0.08);
  translate([4.221, -0.017, 0.420]) sphere(r=0.08);
  translate([4.236, -0.014, 0.420]) sphere(r=0.08);
  translate([4.251, -0.010, 0.420]) sphere(r=0.08);
  translate([4.266, -0.007, 0.420]) sphere(r=0.08);
  translate([4.281, -0.003, 0.420]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.942, -0.003, 1.022]) sphere(r=0.08);
  translate([-7.367, -0.029, 1.227]) sphere(r=0.08);
  translate([-6.807, -0.054, 1.410]) sphere(r=0.08);
  translate([-6.261, -0.079, 1.572]) sphere(r=0.08);
  translate([-5.728, -0.103, 1.713]) sphere(r=0.08);
  translate([-5.207, -0.127, 1.834]) sphere(r=0.08);
  translate([-4.698, -0.150, 1.935]) sphere(r=0.08);
  translate([-4.201, -0.173, 2.018]) sphere(r=0.08);
  translate([-3.713, -0.195, 2.081]) sphere(r=0.08);
  translate([-3.237, -0.216, 2.127]) sphere(r=0.08);
  translate([-2.769, -0.238, 2.154]) sphere(r=0.08);
  translate([-2.312, -0.258, 2.164]) sphere(r=0.08);
  translate([-1.863, -0.279, 2.158]) sphere(r=0.08);
  translate([-1.423, -0.299, 2.134]) sphere(r=0.08);
  translate([-0.991, -0.318, 2.094]) sphere(r=0.08);
  translate([-0.567, -0.338, 2.038]) sphere(r=0.08);
  translate([-0.151, -0.356, 1.966]) sphere(r=0.08);
  translate([0.257, -0.375, 1.878]) sphere(r=0.08);
  translate([0.658, -0.393, 1.775]) sphere(r=0.08);
  translate([1.051, -0.411, 1.657]) sphere(r=0.08);
  translate([1.438, -0.429, 1.524]) sphere(r=0.08);
  translate([1.817, -0.446, 1.377]) sphere(r=0.08);
  translate([2.190, -0.463, 1.216]) sphere(r=0.08);
  translate([2.556, -0.479, 1.040]) sphere(r=0.08);
  translate([2.842, -0.476, 0.890]) sphere(r=0.08);
  translate([3.106, -0.471, 0.739]) sphere(r=0.08);
  translate([3.346, -0.467, 0.603]) sphere(r=0.08);
  translate([3.502, -0.468, 0.583]) sphere(r=0.08);
  translate([3.627, -0.463, 0.587]) sphere(r=0.08);
  translate([3.742, -0.456, 0.583]) sphere(r=0.08);
  translate([3.856, -0.448, 0.569]) sphere(r=0.08);
  translate([3.960, -0.438, 0.569]) sphere(r=0.08);
  translate([4.060, -0.427, 0.569]) sphere(r=0.08);
  translate([4.156, -0.415, 0.566]) sphere(r=0.08);
  translate([4.250, -0.404, 0.549]) sphere(r=0.08);
  translate([4.344, -0.393, 0.514]) sphere(r=0.08);
  translate([4.438, -0.381, 0.463]) sphere(r=0.08);
  translate([4.522, -0.379, 0.398]) sphere(r=0.08);
  translate([4.594, -0.389, 0.321]) sphere(r=0.08);
  translate([4.664, -0.397, 0.297]) sphere(r=0.08);
  translate([4.734, -0.405, 0.299]) sphere(r=0.08);
  translate([4.803, -0.413, 0.299]) sphere(r=0.08);
  translate([4.869, -0.424, 0.300]) sphere(r=0.08);
  translate([4.935, -0.436, 0.300]) sphere(r=0.08);
  translate([5.000, -0.448, 0.300]) sphere(r=0.08);
  translate([5.064, -0.461, 0.300]) sphere(r=0.08);
  translate([5.128, -0.473, 0.300]) sphere(r=0.08);
  translate([5.192, -0.485, 0.300]) sphere(r=0.08);
}
