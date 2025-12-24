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
color([0.6, 0.4, 0.2]) translate([3.0067, -1.0016, 0.1500]) rotate([0.00, -0.01, 0.50]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([0.9995, -1.0012, 0.1500]) rotate([0.00, 0.00, 0.23]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0025, -0.5008, 0.1500]) rotate([-0.00, 0.01, 0.25]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([0.9988, -0.5011, 0.1500]) rotate([0.00, 0.00, 0.27]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0019, -0.0003, 0.1500]) rotate([-0.01, 0.01, 0.09]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([0.9964, -0.0001, 0.1500]) rotate([-0.00, -0.00, -0.03]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0038, 0.5011, 0.1500]) rotate([0.01, -0.01, 0.50]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([0.9995, 0.5002, 0.1500]) rotate([0.00, -0.00, -0.12]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([2.9996, 1.0029, 0.1500]) rotate([-0.00, 0.00, -0.06]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0002, 1.0002, 0.1500]) rotate([-0.00, 0.00, -0.08]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0134, -0.7738, 0.4499]) rotate([0.00, 0.00, -4.60]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0241, -0.8184, 0.4500]) rotate([-0.00, 0.00, -19.74]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.2462, -0.2882, 0.4499]) rotate([0.00, 0.01, -11.58]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.5946, -0.4664, 0.4499]) rotate([0.01, 0.01, -75.55]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0266, 0.2450, 0.4499]) rotate([-0.01, 0.01, 2.93]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.7301, 0.6951, 0.2000]) rotate([-0.53, 90.00, 83.09]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0024, 0.7552, 0.4500]) rotate([-0.00, 0.00, 1.57]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.0288, 0.8377, 0.4500]) rotate([-0.00, 0.00, 21.21]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0450, -0.5303, 0.7499]) rotate([0.00, -0.00, -6.50]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.3033, -0.6639, 0.7499]) rotate([-0.00, 0.01, -47.83]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.1286, 0.0098, 0.7499]) rotate([-0.00, 0.01, 8.58]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([2.6585, 0.0340, 0.4927]) rotate([-179.40, 80.63, -178.47]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0138, 0.5146, 0.7500]) rotate([0.00, 0.01, 5.92]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.4756, 1.0205, 0.2000]) rotate([9.32, 90.00, 104.26]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.6629, -0.3103, 0.2500]) rotate([-90.00, 0.00, -116.99]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.6581, -0.2519, 0.1500]) rotate([180.00, 0.00, 174.91]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([4.6636, 0.6159, 0.2500]) rotate([90.00, 0.00, -165.39]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([1.5915, 0.2568, 0.1500]) rotate([-180.00, -0.00, 175.09]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([4.9741, -0.1523, 0.1500]) rotate([-0.00, 0.00, 147.32]) cube([0.400, 0.500, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([2.4000, -0.0211, 0.1499]) rotate([-179.99, 0.00, -178.51]) cube([0.400, 0.500, 0.300], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([3.3727, 8.1755, 0.1500]) sphere(r=0.15);
color([0.0, 0.8, 0.0]) translate([7.4800, -8.6537, 0.1500]) sphere(r=0.15);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.958, 0.000, 1.029]) sphere(r=0.08);
  translate([-7.548, 0.004, 1.305]) sphere(r=0.08);
  translate([-7.146, 0.007, 1.559]) sphere(r=0.08);
  translate([-6.752, 0.011, 1.791]) sphere(r=0.08);
  translate([-6.366, 0.014, 2.002]) sphere(r=0.08);
  translate([-5.987, 0.018, 2.191]) sphere(r=0.08);
  translate([-5.615, 0.021, 2.360]) sphere(r=0.08);
  translate([-5.249, 0.024, 2.510]) sphere(r=0.08);
  translate([-4.890, 0.027, 2.640]) sphere(r=0.08);
  translate([-4.537, 0.030, 2.751]) sphere(r=0.08);
  translate([-4.189, 0.033, 2.843]) sphere(r=0.08);
  translate([-3.847, 0.036, 2.916]) sphere(r=0.08);
  translate([-3.511, 0.039, 2.972]) sphere(r=0.08);
  translate([-3.179, 0.042, 3.010]) sphere(r=0.08);
  translate([-2.852, 0.045, 3.031]) sphere(r=0.08);
  translate([-2.530, 0.048, 3.034]) sphere(r=0.08);
  translate([-2.212, 0.051, 3.020]) sphere(r=0.08);
  translate([-1.900, 0.053, 2.990]) sphere(r=0.08);
  translate([-1.591, 0.056, 2.943]) sphere(r=0.08);
  translate([-1.287, 0.059, 2.880]) sphere(r=0.08);
  translate([-0.987, 0.061, 2.801]) sphere(r=0.08);
  translate([-0.691, 0.064, 2.706]) sphere(r=0.08);
  translate([-0.400, 0.066, 2.595]) sphere(r=0.08);
  translate([-0.112, 0.069, 2.469]) sphere(r=0.08);
  translate([0.171, 0.071, 2.328]) sphere(r=0.08);
  translate([0.450, 0.074, 2.172]) sphere(r=0.08);
  translate([0.726, 0.076, 2.001]) sphere(r=0.08);
  translate([0.997, 0.079, 1.816]) sphere(r=0.08);
  translate([1.212, 0.080, 1.799]) sphere(r=0.08);
  translate([1.419, 0.082, 1.788]) sphere(r=0.08);
  translate([1.623, 0.084, 1.761]) sphere(r=0.08);
  translate([1.825, 0.086, 1.718]) sphere(r=0.08);
  translate([2.025, 0.088, 1.658]) sphere(r=0.08);
  translate([2.223, 0.090, 1.581]) sphere(r=0.08);
  translate([2.419, 0.091, 1.488]) sphere(r=0.08);
  translate([2.586, 0.094, 1.395]) sphere(r=0.08);
  translate([2.663, 0.101, 1.395]) sphere(r=0.08);
  translate([2.729, 0.111, 1.385]) sphere(r=0.08);
  translate([2.791, 0.123, 1.365]) sphere(r=0.08);
  translate([2.849, 0.138, 1.331]) sphere(r=0.08);
  translate([2.907, 0.152, 1.280]) sphere(r=0.08);
  translate([2.964, 0.167, 1.212]) sphere(r=0.08);
  translate([3.006, 0.183, 1.200]) sphere(r=0.08);
  translate([3.043, 0.200, 1.200]) sphere(r=0.08);
  translate([3.081, 0.218, 1.200]) sphere(r=0.08);
  translate([3.118, 0.235, 1.200]) sphere(r=0.08);
  translate([3.155, 0.252, 1.200]) sphere(r=0.08);
  translate([3.191, 0.269, 1.200]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.958, -0.000, 1.029]) sphere(r=0.08);
  translate([-7.548, -0.004, 1.305]) sphere(r=0.08);
  translate([-7.146, -0.007, 1.559]) sphere(r=0.08);
  translate([-6.752, -0.011, 1.791]) sphere(r=0.08);
  translate([-6.366, -0.014, 2.002]) sphere(r=0.08);
  translate([-5.987, -0.018, 2.191]) sphere(r=0.08);
  translate([-5.615, -0.021, 2.360]) sphere(r=0.08);
  translate([-5.249, -0.024, 2.510]) sphere(r=0.08);
  translate([-4.890, -0.027, 2.640]) sphere(r=0.08);
  translate([-4.537, -0.030, 2.751]) sphere(r=0.08);
  translate([-4.189, -0.033, 2.843]) sphere(r=0.08);
  translate([-3.847, -0.036, 2.916]) sphere(r=0.08);
  translate([-3.511, -0.039, 2.972]) sphere(r=0.08);
  translate([-3.179, -0.042, 3.010]) sphere(r=0.08);
  translate([-2.852, -0.045, 3.031]) sphere(r=0.08);
  translate([-2.530, -0.048, 3.034]) sphere(r=0.08);
  translate([-2.212, -0.051, 3.020]) sphere(r=0.08);
  translate([-1.900, -0.053, 2.990]) sphere(r=0.08);
  translate([-1.591, -0.056, 2.943]) sphere(r=0.08);
  translate([-1.287, -0.059, 2.880]) sphere(r=0.08);
  translate([-0.987, -0.061, 2.801]) sphere(r=0.08);
  translate([-0.691, -0.064, 2.706]) sphere(r=0.08);
  translate([-0.400, -0.066, 2.595]) sphere(r=0.08);
  translate([-0.112, -0.069, 2.469]) sphere(r=0.08);
  translate([0.171, -0.071, 2.328]) sphere(r=0.08);
  translate([0.450, -0.074, 2.172]) sphere(r=0.08);
  translate([0.726, -0.076, 2.001]) sphere(r=0.08);
  translate([0.997, -0.079, 1.816]) sphere(r=0.08);
  translate([1.202, -0.081, 1.810]) sphere(r=0.08);
  translate([1.398, -0.083, 1.808]) sphere(r=0.08);
  translate([1.592, -0.085, 1.790]) sphere(r=0.08);
  translate([1.784, -0.087, 1.755]) sphere(r=0.08);
  translate([1.975, -0.089, 1.704]) sphere(r=0.08);
  translate([2.164, -0.091, 1.636]) sphere(r=0.08);
  translate([2.350, -0.093, 1.551]) sphere(r=0.08);
  translate([2.535, -0.095, 1.451]) sphere(r=0.08);
  translate([2.718, -0.097, 1.335]) sphere(r=0.08);
  translate([2.899, -0.099, 1.202]) sphere(r=0.08);
  translate([3.055, -0.101, 1.200]) sphere(r=0.08);
  translate([3.209, -0.102, 1.200]) sphere(r=0.08);
  translate([3.361, -0.104, 1.190]) sphere(r=0.08);
  translate([3.512, -0.105, 1.164]) sphere(r=0.08);
  translate([3.661, -0.106, 1.121]) sphere(r=0.08);
  translate([3.810, -0.108, 1.061]) sphere(r=0.08);
  translate([3.957, -0.109, 0.985]) sphere(r=0.08);
  translate([4.104, -0.110, 0.893]) sphere(r=0.08);
  translate([4.248, -0.112, 0.784]) sphere(r=0.08);
  translate([4.392, -0.113, 0.659]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.955, 0.000, 1.021]) sphere(r=0.08);
  translate([-7.508, 0.000, 1.218]) sphere(r=0.08);
  translate([-7.070, 0.000, 1.395]) sphere(r=0.08);
  translate([-6.641, 0.000, 1.551]) sphere(r=0.08);
  translate([-6.221, 0.000, 1.687]) sphere(r=0.08);
  translate([-5.808, 0.000, 1.803]) sphere(r=0.08);
  translate([-5.403, 0.000, 1.901]) sphere(r=0.08);
  translate([-5.006, 0.000, 1.980]) sphere(r=0.08);
  translate([-4.615, 0.000, 2.041]) sphere(r=0.08);
  translate([-4.231, 0.000, 2.083]) sphere(r=0.08);
  translate([-3.854, 0.000, 2.108]) sphere(r=0.08);
  translate([-3.483, 0.000, 2.116]) sphere(r=0.08);
  translate([-3.117, 0.000, 2.107]) sphere(r=0.08);
  translate([-2.758, 0.000, 2.081]) sphere(r=0.08);
  translate([-2.404, 0.000, 2.038]) sphere(r=0.08);
  translate([-2.056, 0.000, 1.980]) sphere(r=0.08);
  translate([-1.714, 0.000, 1.905]) sphere(r=0.08);
  translate([-1.377, 0.000, 1.814]) sphere(r=0.08);
  translate([-1.044, 0.000, 1.708]) sphere(r=0.08);
  translate([-0.718, 0.000, 1.587]) sphere(r=0.08);
  translate([-0.396, 0.000, 1.451]) sphere(r=0.08);
  translate([-0.079, 0.000, 1.300]) sphere(r=0.08);
  translate([0.233, 0.000, 1.134]) sphere(r=0.08);
  translate([0.540, 0.000, 0.954]) sphere(r=0.08);
  translate([0.717, 0.002, 0.853]) sphere(r=0.08);
  translate([0.804, 0.009, 0.845]) sphere(r=0.08);
  translate([0.882, 0.011, 0.829]) sphere(r=0.08);
  translate([0.956, 0.015, 0.806]) sphere(r=0.08);
  translate([1.023, 0.019, 0.775]) sphere(r=0.08);
  translate([1.085, 0.023, 0.733]) sphere(r=0.08);
  translate([1.144, 0.025, 0.679]) sphere(r=0.08);
  translate([1.202, 0.027, 0.608]) sphere(r=0.08);
  translate([1.244, 0.029, 0.599]) sphere(r=0.08);
  translate([1.285, 0.030, 0.596]) sphere(r=0.08);
  translate([1.320, 0.032, 0.595]) sphere(r=0.08);
  translate([1.349, 0.034, 0.599]) sphere(r=0.08);
  translate([1.377, 0.036, 0.600]) sphere(r=0.08);
  translate([1.405, 0.039, 0.600]) sphere(r=0.08);
  translate([1.433, 0.041, 0.600]) sphere(r=0.08);
  translate([1.460, 0.043, 0.600]) sphere(r=0.08);
  translate([1.488, 0.045, 0.600]) sphere(r=0.08);
  translate([1.516, 0.047, 0.600]) sphere(r=0.08);
  translate([1.543, 0.049, 0.600]) sphere(r=0.08);
  translate([1.570, 0.052, 0.600]) sphere(r=0.08);
  translate([1.597, 0.054, 0.600]) sphere(r=0.08);
  translate([1.623, 0.058, 0.600]) sphere(r=0.08);
  translate([1.649, 0.063, 0.600]) sphere(r=0.08);
  translate([1.674, 0.068, 0.600]) sphere(r=0.08);
}
