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
color([0.7, 0.3, 0.2]) translate([2.4995, -0.9999, 0.1500]) rotate([0.00, -0.00, 0.10]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5002, -0.4997, 0.1500]) rotate([-0.00, -0.00, -0.17]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5014, 0.0015, 0.1500]) rotate([-0.00, -0.01, 0.40]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4979, 0.5013, 0.1500]) rotate([0.01, 0.00, 0.34]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5006, 1.0004, 0.1500]) rotate([-0.00, -0.00, -0.49]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4999, -0.7497, 0.4500]) rotate([0.00, -0.01, -0.57]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5010, -0.2499, 0.4499]) rotate([-0.01, 0.00, -0.28]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4997, 0.2515, 0.4499]) rotate([0.00, -0.00, 0.52]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4981, 0.7541, 0.4500]) rotate([0.00, -0.01, -1.01]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4975, -0.9995, 0.7499]) rotate([0.00, -0.01, -0.53]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5005, -0.5007, 0.7499]) rotate([-0.00, -0.01, -0.17]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5014, -0.0017, 0.7499]) rotate([-0.00, -0.01, -0.31]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4985, 0.5042, 0.7499]) rotate([0.00, -0.01, 0.61]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4998, 1.0057, 0.7499]) rotate([0.00, -0.01, -0.27]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5004, -0.7496, 1.0499]) rotate([-0.00, -0.01, -0.65]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.5010, -0.2499, 1.0499]) rotate([-0.00, -0.01, 0.03]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4999, 0.2542, 1.0499]) rotate([0.00, -0.01, 0.71]) cube([0.400, 0.440, 0.300], center=true);
color([0.7, 0.3, 0.2]) translate([2.4990, 0.7561, 1.0499]) rotate([0.00, -0.01, -0.01]) cube([0.400, 0.440, 0.300], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([3.5000, -0.5000, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.5000, 0.5000, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.5000, -0.0000, 0.2000]) sphere(r=0.2);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.954, -0.003, 1.036]) sphere(r=0.08);
  translate([-7.503, -0.035, 1.378]) sphere(r=0.08);
  translate([-7.062, -0.066, 1.696]) sphere(r=0.08);
  translate([-6.632, -0.096, 1.989]) sphere(r=0.08);
  translate([-6.211, -0.125, 2.259]) sphere(r=0.08);
  translate([-5.799, -0.154, 2.507]) sphere(r=0.08);
  translate([-5.395, -0.182, 2.732]) sphere(r=0.08);
  translate([-4.999, -0.210, 2.936]) sphere(r=0.08);
  translate([-4.611, -0.237, 3.120]) sphere(r=0.08);
  translate([-4.230, -0.264, 3.283]) sphere(r=0.08);
  translate([-3.855, -0.290, 3.426]) sphere(r=0.08);
  translate([-3.488, -0.316, 3.550]) sphere(r=0.08);
  translate([-3.126, -0.341, 3.655]) sphere(r=0.08);
  translate([-2.770, -0.366, 3.742]) sphere(r=0.08);
  translate([-2.421, -0.390, 3.810]) sphere(r=0.08);
  translate([-2.076, -0.414, 3.860]) sphere(r=0.08);
  translate([-1.737, -0.438, 3.892]) sphere(r=0.08);
  translate([-1.403, -0.461, 3.907]) sphere(r=0.08);
  translate([-1.074, -0.484, 3.905]) sphere(r=0.08);
  translate([-0.750, -0.507, 3.886]) sphere(r=0.08);
  translate([-0.430, -0.529, 3.850]) sphere(r=0.08);
  translate([-0.115, -0.551, 3.798]) sphere(r=0.08);
  translate([0.195, -0.573, 3.730]) sphere(r=0.08);
  translate([0.501, -0.594, 3.646]) sphere(r=0.08);
  translate([0.803, -0.616, 3.546]) sphere(r=0.08);
  translate([1.100, -0.636, 3.431]) sphere(r=0.08);
  translate([1.393, -0.657, 3.300]) sphere(r=0.08);
  translate([1.681, -0.677, 3.154]) sphere(r=0.08);
  translate([1.966, -0.697, 2.994]) sphere(r=0.08);
  translate([2.246, -0.716, 2.819]) sphere(r=0.08);
  translate([2.522, -0.736, 2.629]) sphere(r=0.08);
  translate([2.794, -0.755, 2.426]) sphere(r=0.08);
  translate([3.062, -0.774, 2.209]) sphere(r=0.08);
  translate([3.326, -0.792, 1.978]) sphere(r=0.08);
  translate([3.585, -0.810, 1.734]) sphere(r=0.08);
  translate([3.841, -0.828, 1.477]) sphere(r=0.08);
  translate([4.092, -0.846, 1.207]) sphere(r=0.08);
  translate([4.339, -0.863, 0.925]) sphere(r=0.08);
  translate([4.582, -0.880, 0.630]) sphere(r=0.08);
  translate([4.821, -0.897, 0.324]) sphere(r=0.08);
  translate([4.996, -0.909, 0.300]) sphere(r=0.08);
  translate([5.162, -0.920, 0.300]) sphere(r=0.08);
  translate([5.326, -0.932, 0.300]) sphere(r=0.08);
  translate([5.488, -0.943, 0.300]) sphere(r=0.08);
  translate([5.648, -0.954, 0.300]) sphere(r=0.08);
  translate([5.805, -0.965, 0.300]) sphere(r=0.08);
  translate([5.961, -0.976, 0.300]) sphere(r=0.08);
  translate([6.115, -0.987, 0.300]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.954, 0.000, 1.042]) sphere(r=0.08);
  translate([-7.497, 0.000, 1.442]) sphere(r=0.08);
  translate([-7.052, 0.000, 1.815]) sphere(r=0.08);
  translate([-6.618, 0.000, 2.162]) sphere(r=0.08);
  translate([-6.193, 0.000, 2.485]) sphere(r=0.08);
  translate([-5.779, 0.000, 2.783]) sphere(r=0.08);
  translate([-5.373, 0.000, 3.058]) sphere(r=0.08);
  translate([-4.975, 0.000, 3.311]) sphere(r=0.08);
  translate([-4.586, 0.000, 3.541]) sphere(r=0.08);
  translate([-4.204, 0.000, 3.750]) sphere(r=0.08);
  translate([-3.829, 0.000, 3.939]) sphere(r=0.08);
  translate([-3.461, 0.000, 4.107]) sphere(r=0.08);
  translate([-3.099, 0.000, 4.255]) sphere(r=0.08);
  translate([-2.744, 0.000, 4.384]) sphere(r=0.08);
  translate([-2.394, 0.000, 4.494]) sphere(r=0.08);
  translate([-2.050, 0.000, 4.585]) sphere(r=0.08);
  translate([-1.711, 0.000, 4.658]) sphere(r=0.08);
  translate([-1.378, 0.000, 4.713]) sphere(r=0.08);
  translate([-1.049, 0.000, 4.750]) sphere(r=0.08);
  translate([-0.726, 0.000, 4.770]) sphere(r=0.08);
  translate([-0.407, 0.000, 4.772]) sphere(r=0.08);
  translate([-0.092, 0.000, 4.758]) sphere(r=0.08);
  translate([0.218, 0.000, 4.726]) sphere(r=0.08);
  translate([0.524, 0.000, 4.679]) sphere(r=0.08);
  translate([0.825, 0.000, 4.615]) sphere(r=0.08);
  translate([1.122, 0.000, 4.535]) sphere(r=0.08);
  translate([1.415, 0.000, 4.439]) sphere(r=0.08);
  translate([1.705, 0.000, 4.327]) sphere(r=0.08);
  translate([1.990, 0.000, 4.201]) sphere(r=0.08);
  translate([2.270, 0.000, 4.059]) sphere(r=0.08);
  translate([2.547, 0.000, 3.902]) sphere(r=0.08);
  translate([2.820, 0.000, 3.730]) sphere(r=0.08);
  translate([3.090, 0.000, 3.545]) sphere(r=0.08);
  translate([3.355, 0.000, 3.344]) sphere(r=0.08);
  translate([3.616, 0.000, 3.130]) sphere(r=0.08);
  translate([3.873, 0.000, 2.903]) sphere(r=0.08);
  translate([4.126, 0.000, 2.662]) sphere(r=0.08);
  translate([4.375, 0.000, 2.407]) sphere(r=0.08);
  translate([4.620, 0.000, 2.140]) sphere(r=0.08);
  translate([4.862, 0.000, 1.861]) sphere(r=0.08);
  translate([5.099, 0.000, 1.569]) sphere(r=0.08);
  translate([5.332, 0.000, 1.265]) sphere(r=0.08);
  translate([5.562, 0.000, 0.949]) sphere(r=0.08);
  translate([5.787, 0.000, 0.622]) sphere(r=0.08);
  translate([6.009, 0.000, 0.283]) sphere(r=0.08);
  translate([6.165, 0.000, 0.299]) sphere(r=0.08);
  translate([6.319, 0.000, 0.300]) sphere(r=0.08);
  translate([6.471, 0.000, 0.300]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.952, 0.003, 1.032]) sphere(r=0.08);
  translate([-7.477, 0.037, 1.342]) sphere(r=0.08);
  translate([-7.014, 0.069, 1.628]) sphere(r=0.08);
  translate([-6.561, 0.101, 1.891]) sphere(r=0.08);
  translate([-6.118, 0.132, 2.130]) sphere(r=0.08);
  translate([-5.684, 0.162, 2.348]) sphere(r=0.08);
  translate([-5.260, 0.192, 2.545]) sphere(r=0.08);
  translate([-4.844, 0.221, 2.720]) sphere(r=0.08);
  translate([-4.436, 0.249, 2.876]) sphere(r=0.08);
  translate([-4.035, 0.277, 3.011]) sphere(r=0.08);
  translate([-3.642, 0.305, 3.127]) sphere(r=0.08);
  translate([-3.256, 0.332, 3.225]) sphere(r=0.08);
  translate([-2.877, 0.358, 3.303]) sphere(r=0.08);
  translate([-2.504, 0.384, 3.364]) sphere(r=0.08);
  translate([-2.137, 0.410, 3.406]) sphere(r=0.08);
  translate([-1.776, 0.435, 3.431]) sphere(r=0.08);
  translate([-1.421, 0.460, 3.439]) sphere(r=0.08);
  translate([-1.071, 0.485, 3.429]) sphere(r=0.08);
  translate([-0.727, 0.509, 3.403]) sphere(r=0.08);
  translate([-0.388, 0.532, 3.360]) sphere(r=0.08);
  translate([-0.055, 0.556, 3.302]) sphere(r=0.08);
  translate([0.274, 0.579, 3.227]) sphere(r=0.08);
  translate([0.598, 0.601, 3.136]) sphere(r=0.08);
  translate([0.917, 0.624, 3.029]) sphere(r=0.08);
  translate([1.231, 0.645, 2.908]) sphere(r=0.08);
  translate([1.540, 0.667, 2.771]) sphere(r=0.08);
  translate([1.845, 0.688, 2.620]) sphere(r=0.08);
  translate([2.145, 0.709, 2.453]) sphere(r=0.08);
  translate([2.440, 0.730, 2.273]) sphere(r=0.08);
  translate([2.731, 0.750, 2.078]) sphere(r=0.08);
  translate([3.017, 0.770, 1.870]) sphere(r=0.08);
  translate([3.299, 0.790, 1.648]) sphere(r=0.08);
  translate([3.576, 0.809, 1.412]) sphere(r=0.08);
  translate([3.849, 0.829, 1.164]) sphere(r=0.08);
  translate([4.117, 0.847, 0.902]) sphere(r=0.08);
  translate([4.381, 0.866, 0.628]) sphere(r=0.08);
  translate([4.640, 0.884, 0.342]) sphere(r=0.08);
  translate([4.837, 0.898, 0.296]) sphere(r=0.08);
  translate([5.018, 0.910, 0.299]) sphere(r=0.08);
  translate([5.195, 0.923, 0.300]) sphere(r=0.08);
  translate([5.370, 0.935, 0.300]) sphere(r=0.08);
  translate([5.542, 0.947, 0.300]) sphere(r=0.08);
  translate([5.713, 0.959, 0.300]) sphere(r=0.08);
  translate([5.881, 0.971, 0.300]) sphere(r=0.08);
  translate([6.047, 0.982, 0.300]) sphere(r=0.08);
  translate([6.211, 0.994, 0.300]) sphere(r=0.08);
  translate([6.373, 1.005, 0.300]) sphere(r=0.08);
  translate([6.533, 1.016, 0.300]) sphere(r=0.08);
}
