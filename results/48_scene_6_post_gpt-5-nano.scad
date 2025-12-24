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
color([0.5, 0.5, 0.55]) translate([2.1993, -0.9968, 0.4000]) rotate([0.00, 0.00, 0.60]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([3.1229, -0.0088, 0.4188]) rotate([0.00, 47.10, -11.93]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([2.1978, 0.9993, 0.4000]) rotate([0.00, 0.00, -0.27]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([3.7995, -0.9991, 0.4000]) rotate([0.00, 0.00, -0.28]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([3.9709, -0.0002, 0.4421]) rotate([0.00, 17.92, 1.16]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([3.7972, 0.9967, 0.4000]) rotate([0.00, 0.00, -0.31]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([3.0000, -1.2025, 0.4000]) rotate([0.00, 0.00, -0.04]) cube([0.400, 0.600, 0.800], center=true);
color([0.5, 0.5, 0.55]) translate([3.0000, 1.2006, 0.4000]) rotate([0.00, 0.00, -0.02]) cube([0.400, 0.600, 0.800], center=true);
color([0.45, 0.45, 0.5]) translate([4.2665, 0.0104, 0.8720]) rotate([0.01, 17.92, 1.19]) cube([1.800, 2.600, 0.200], center=true);
color([0.5, 0.5, 0.55]) translate([2.7751, -0.5442, 0.1200]) rotate([53.77, -90.00, 124.44]) cube([0.240, 0.500, 0.700], center=true);
color([0.5, 0.5, 0.55]) translate([5.0371, 0.4057, 0.2500]) rotate([-90.00, 0.01, 0.47]) cube([0.240, 0.500, 0.700], center=true);
color([0.5, 0.5, 0.55]) translate([2.7420, 0.6360, 0.2674]) rotate([90.00, -40.99, 78.92]) cube([0.240, 0.500, 0.700], center=true);
color([0.5, 0.5, 0.55]) translate([4.9295, -0.7622, 0.8938]) rotate([-1.81, -72.08, 1.16]) cube([0.240, 0.500, 0.700], center=true);
color([0.5, 0.5, 0.55]) translate([6.8178, 0.0111, 0.1200]) rotate([89.47, 90.00, 78.44]) cube([0.240, 0.500, 0.700], center=true);
color([0.5, 0.5, 0.55]) translate([4.9490, 0.8330, 0.8770]) rotate([-1.76, -72.08, 1.16]) cube([0.240, 0.500, 0.700], center=true);
color([0.5, 0.5, 0.55]) translate([4.1494, -0.8746, 1.1258]) rotate([-177.62, 72.08, -178.84]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([4.4467, -0.8564, 1.0295]) rotate([-1.81, -72.07, 1.16]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([0.7984, -0.2150, 0.1000]) rotate([100.80, -90.00, -176.40]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([4.9664, -0.2654, 0.1500]) rotate([90.00, 0.00, 86.31]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([1.3936, 0.4048, 0.1500]) rotate([-0.00, 0.00, 20.20]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([4.6581, 0.7378, 0.1500]) rotate([-0.00, -0.00, -158.80]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([4.1760, 0.8482, 1.1059]) rotate([-175.91, 72.08, -178.84]) cube([0.200, 0.300, 0.300], center=true);
color([0.5, 0.5, 0.55]) translate([4.4679, 0.9268, 1.0110]) rotate([-1.72, -72.08, 1.16]) cube([0.200, 0.300, 0.300], center=true);
color([0.55, 0.55, 0.6]) translate([5.9903, -0.1059, 0.3816]) rotate([13.43, 75.10, -11.02]) cube([0.500, 0.500, 1.000], center=true);
color([0.6, 0.4, 0.2]) translate([5.4665, 1.2590, 0.3000]) rotate([-90.00, -0.00, 74.29]) cube([0.600, 0.600, 0.160], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([-0.4325, 2.1913, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.4732, -0.0543, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([-18.1847, -0.0000, 0.2000]) sphere(r=0.2);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.942, 0.000, 1.023]) sphere(r=0.08);
  translate([-7.373, 0.000, 1.242]) sphere(r=0.08);
  translate([-6.817, 0.000, 1.439]) sphere(r=0.08);
  translate([-6.276, 0.000, 1.614]) sphere(r=0.08);
  translate([-5.747, 0.000, 1.768]) sphere(r=0.08);
  translate([-5.231, 0.000, 1.902]) sphere(r=0.08);
  translate([-4.726, 0.000, 2.016]) sphere(r=0.08);
  translate([-4.232, 0.000, 2.110]) sphere(r=0.08);
  translate([-3.749, 0.000, 2.186]) sphere(r=0.08);
  translate([-3.276, 0.000, 2.243]) sphere(r=0.08);
  translate([-2.812, 0.000, 2.282]) sphere(r=0.08);
  translate([-2.358, 0.000, 2.303]) sphere(r=0.08);
  translate([-1.913, 0.000, 2.307]) sphere(r=0.08);
  translate([-1.476, 0.000, 2.295]) sphere(r=0.08);
  translate([-1.047, 0.000, 2.265]) sphere(r=0.08);
  translate([-0.626, 0.000, 2.219]) sphere(r=0.08);
  translate([-0.213, 0.000, 2.157]) sphere(r=0.08);
  translate([0.192, 0.000, 2.080]) sphere(r=0.08);
  translate([0.590, 0.000, 1.986]) sphere(r=0.08);
  translate([0.981, 0.000, 1.878]) sphere(r=0.08);
  translate([1.366, 0.000, 1.755]) sphere(r=0.08);
  translate([1.743, 0.000, 1.617]) sphere(r=0.08);
  translate([2.096, 0.000, 1.475]) sphere(r=0.08);
  translate([2.289, 0.000, 1.419]) sphere(r=0.08);
  translate([2.472, 0.000, 1.349]) sphere(r=0.08);
  translate([2.626, 0.000, 1.300]) sphere(r=0.08);
  translate([2.745, 0.000, 1.300]) sphere(r=0.08);
  translate([2.856, 0.000, 1.300]) sphere(r=0.08);
  translate([2.960, 0.001, 1.300]) sphere(r=0.08);
  translate([3.056, 0.001, 1.300]) sphere(r=0.08);
  translate([3.143, 0.001, 1.300]) sphere(r=0.08);
  translate([3.226, 0.001, 1.300]) sphere(r=0.08);
  translate([3.306, 0.001, 1.300]) sphere(r=0.08);
  translate([3.383, 0.001, 1.300]) sphere(r=0.08);
  translate([3.456, 0.001, 1.300]) sphere(r=0.08);
  translate([3.524, 0.002, 1.300]) sphere(r=0.08);
  translate([3.589, 0.003, 1.300]) sphere(r=0.08);
  translate([3.655, 0.005, 1.300]) sphere(r=0.08);
  translate([3.722, 0.006, 1.300]) sphere(r=0.08);
  translate([3.788, 0.007, 1.300]) sphere(r=0.08);
  translate([3.853, 0.009, 1.300]) sphere(r=0.08);
  translate([3.918, 0.010, 1.299]) sphere(r=0.08);
  translate([3.983, 0.012, 1.288]) sphere(r=0.08);
  translate([4.047, 0.013, 1.261]) sphere(r=0.08);
  translate([4.111, 0.015, 1.217]) sphere(r=0.08);
  translate([4.175, 0.016, 1.157]) sphere(r=0.08);
  translate([4.238, 0.018, 1.080]) sphere(r=0.08);
  translate([4.301, 0.019, 0.986]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.940, 0.000, 1.028]) sphere(r=0.08);
  translate([-7.346, 0.000, 1.294]) sphere(r=0.08);
  translate([-6.769, 0.000, 1.535]) sphere(r=0.08);
  translate([-6.207, 0.000, 1.754]) sphere(r=0.08);
  translate([-5.659, 0.000, 1.950]) sphere(r=0.08);
  translate([-5.124, 0.000, 2.125]) sphere(r=0.08);
  translate([-4.601, 0.000, 2.279]) sphere(r=0.08);
  translate([-4.091, 0.000, 2.412]) sphere(r=0.08);
  translate([-3.592, 0.000, 2.525]) sphere(r=0.08);
  translate([-3.104, 0.000, 2.620]) sphere(r=0.08);
  translate([-2.626, 0.000, 2.695]) sphere(r=0.08);
  translate([-2.158, 0.000, 2.752]) sphere(r=0.08);
  translate([-1.700, 0.000, 2.791]) sphere(r=0.08);
  translate([-1.250, 0.000, 2.812]) sphere(r=0.08);
  translate([-0.809, 0.000, 2.816]) sphere(r=0.08);
  translate([-0.377, 0.000, 2.803]) sphere(r=0.08);
  translate([0.048, 0.000, 2.773]) sphere(r=0.08);
  translate([0.464, 0.000, 2.727]) sphere(r=0.08);
  translate([0.873, 0.000, 2.665]) sphere(r=0.08);
  translate([1.275, 0.000, 2.587]) sphere(r=0.08);
  translate([1.669, 0.000, 2.494]) sphere(r=0.08);
  translate([2.057, 0.000, 2.385]) sphere(r=0.08);
  translate([2.438, 0.000, 2.261]) sphere(r=0.08);
  translate([2.812, 0.000, 2.123]) sphere(r=0.08);
  translate([3.179, 0.000, 1.970]) sphere(r=0.08);
  translate([3.540, 0.000, 1.803]) sphere(r=0.08);
  translate([3.895, 0.000, 1.622]) sphere(r=0.08);
  translate([4.244, 0.000, 1.427]) sphere(r=0.08);
  translate([4.586, 0.000, 1.219]) sphere(r=0.08);
  translate([4.923, 0.000, 0.998]) sphere(r=0.08);
  translate([5.237, -0.002, 0.784]) sphere(r=0.08);
  translate([5.371, -0.003, 0.834]) sphere(r=0.08);
  translate([5.496, 0.001, 0.890]) sphere(r=0.08);
  translate([5.619, 0.006, 0.929]) sphere(r=0.08);
  translate([5.742, 0.010, 0.950]) sphere(r=0.08);
  translate([5.863, 0.014, 0.955]) sphere(r=0.08);
  translate([5.983, 0.018, 0.953]) sphere(r=0.08);
  translate([6.094, 0.024, 0.970]) sphere(r=0.08);
  translate([6.196, 0.032, 0.996]) sphere(r=0.08);
  translate([6.292, 0.041, 1.022]) sphere(r=0.08);
  translate([6.387, 0.050, 1.044]) sphere(r=0.08);
  translate([6.479, 0.058, 1.055]) sphere(r=0.08);
  translate([6.571, 0.066, 1.050]) sphere(r=0.08);
  translate([6.662, 0.074, 1.027]) sphere(r=0.08);
  translate([6.753, 0.082, 0.988]) sphere(r=0.08);
  translate([6.843, 0.090, 0.931]) sphere(r=0.08);
  translate([6.933, 0.097, 0.859]) sphere(r=0.08);
  translate([7.022, 0.105, 0.769]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.945, 0.000, 1.020]) sphere(r=0.08);
  translate([-7.406, 0.000, 1.205]) sphere(r=0.08);
  translate([-6.879, 0.000, 1.369]) sphere(r=0.08);
  translate([-6.365, 0.000, 1.513]) sphere(r=0.08);
  translate([-5.862, 0.000, 1.636]) sphere(r=0.08);
  translate([-5.370, 0.000, 1.740]) sphere(r=0.08);
  translate([-4.889, 0.000, 1.824]) sphere(r=0.08);
  translate([-4.418, 0.000, 1.890]) sphere(r=0.08);
  translate([-3.956, 0.000, 1.938]) sphere(r=0.08);
  translate([-3.504, 0.000, 1.968]) sphere(r=0.08);
  translate([-3.060, 0.000, 1.981]) sphere(r=0.08);
  translate([-2.625, 0.000, 1.976]) sphere(r=0.08);
  translate([-2.198, 0.000, 1.955]) sphere(r=0.08);
  translate([-1.778, 0.000, 1.917]) sphere(r=0.08);
  translate([-1.367, 0.000, 1.863]) sphere(r=0.08);
  translate([-0.963, 0.000, 1.793]) sphere(r=0.08);
  translate([-0.566, 0.000, 1.707]) sphere(r=0.08);
  translate([-0.176, 0.000, 1.606]) sphere(r=0.08);
  translate([0.207, 0.000, 1.490]) sphere(r=0.08);
  translate([0.583, 0.000, 1.359]) sphere(r=0.08);
  translate([0.953, 0.000, 1.214]) sphere(r=0.08);
  translate([1.316, 0.000, 1.054]) sphere(r=0.08);
  translate([1.673, 0.000, 0.879]) sphere(r=0.08);
  translate([1.846, 0.001, 0.777]) sphere(r=0.08);
  translate([1.958, 0.002, 0.670]) sphere(r=0.08);
  translate([2.034, 0.003, 0.569]) sphere(r=0.08);
  translate([2.071, 0.004, 0.487]) sphere(r=0.08);
  translate([2.100, 0.005, 0.397]) sphere(r=0.08);
  translate([2.129, 0.007, 0.290]) sphere(r=0.08);
  translate([2.106, 0.008, 0.296]) sphere(r=0.08);
  translate([2.079, 0.009, 0.298]) sphere(r=0.08);
  translate([2.052, 0.011, 0.299]) sphere(r=0.08);
  translate([2.025, 0.012, 0.300]) sphere(r=0.08);
  translate([1.998, 0.013, 0.300]) sphere(r=0.08);
  translate([1.971, 0.014, 0.300]) sphere(r=0.08);
  translate([1.944, 0.016, 0.300]) sphere(r=0.08);
  translate([1.917, 0.017, 0.300]) sphere(r=0.08);
  translate([1.891, 0.018, 0.300]) sphere(r=0.08);
  translate([1.864, 0.020, 0.300]) sphere(r=0.08);
  translate([1.837, 0.021, 0.300]) sphere(r=0.08);
  translate([1.813, 0.021, 0.300]) sphere(r=0.08);
  translate([1.789, 0.020, 0.300]) sphere(r=0.08);
  translate([1.766, 0.019, 0.300]) sphere(r=0.08);
  translate([1.743, 0.018, 0.300]) sphere(r=0.08);
  translate([1.721, 0.016, 0.300]) sphere(r=0.08);
  translate([1.699, 0.013, 0.300]) sphere(r=0.08);
  translate([1.678, 0.010, 0.300]) sphere(r=0.08);
  translate([1.657, 0.007, 0.300]) sphere(r=0.08);
}
