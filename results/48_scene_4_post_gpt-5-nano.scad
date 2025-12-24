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
color([0.6, 0.4, 0.2]) translate([2.8847, -1.8945, 0.6000]) rotate([-0.00, -0.00, -30.17]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.2477, -1.8634, 0.6000]) rotate([-0.00, -0.00, -4.18]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9532, -1.1925, 0.6000]) rotate([0.00, 0.00, -31.93]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.3181, -1.2725, 0.6000]) rotate([-0.00, -0.00, -21.02]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9387, -1.5090, 1.2800]) rotate([0.00, -0.00, 1.85]) cube([0.700, 0.700, 0.160], center=true);
color([0.6, 0.4, 0.2]) translate([2.9283, 1.2096, 0.6000]) rotate([-0.00, -0.00, 29.60]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.3158, 1.2446, 0.6000]) rotate([0.00, 0.00, 30.92]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.8961, 1.8926, 0.6000]) rotate([-0.00, -0.00, 34.80]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([3.2553, 1.8766, 0.6000]) rotate([-0.00, -0.00, 0.17]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9096, 1.4896, 1.2800]) rotate([-0.00, -0.00, -4.95]) cube([0.700, 0.700, 0.160], center=true);
color([0.6, 0.35, 0.2]) translate([2.8010, -0.7549, 0.1800]) rotate([-0.00, -0.00, -1.21]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([3.0839, -0.3199, 0.1800]) rotate([-0.00, -0.00, -48.81]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([3.0768, 0.3097, 0.1800]) rotate([-0.00, -0.00, 57.57]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.8025, 0.7615, 0.1800]) rotate([-0.00, 0.00, 2.91]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.8022, -0.7539, 0.5400]) rotate([-0.00, -0.00, -1.00]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([3.0808, -0.3180, 0.5400]) rotate([-0.00, -0.01, -47.80]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([3.0737, 0.3067, 0.5400]) rotate([-0.00, -0.00, 56.68]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.8062, 0.7629, 0.5400]) rotate([-0.00, 0.00, 3.64]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.8024, -0.7533, 0.9000]) rotate([-0.00, -0.00, -0.87]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.9585, -0.2681, 0.8999]) rotate([-0.00, -0.01, -29.71]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.9593, 0.2576, 0.8999]) rotate([-0.00, -0.00, 36.58]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.35, 0.2]) translate([2.8069, 0.7634, 0.9000]) rotate([-0.00, 0.00, 4.03]) cube([0.300, 0.440, 0.360], center=true);
color([0.6, 0.4, 0.2]) translate([2.9387, -1.5088, 1.4600]) rotate([0.00, -0.00, 1.75]) cube([0.800, 0.800, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9120, 1.4923, 1.4600]) rotate([-0.00, -0.00, -4.96]) cube([0.800, 0.800, 0.200], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([-7.0874, -4.0038, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([-3.0764, 2.3858, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.5000, -0.0000, 0.2000]) sphere(r=0.2);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.961, -0.006, 1.030]) sphere(r=0.08);
  translate([-7.571, -0.064, 1.316]) sphere(r=0.08);
  translate([-7.190, -0.121, 1.579]) sphere(r=0.08);
  translate([-6.816, -0.177, 1.820]) sphere(r=0.08);
  translate([-6.449, -0.232, 2.039]) sphere(r=0.08);
  translate([-6.089, -0.286, 2.237]) sphere(r=0.08);
  translate([-5.735, -0.338, 2.415]) sphere(r=0.08);
  translate([-5.388, -0.390, 2.574]) sphere(r=0.08);
  translate([-5.046, -0.441, 2.712]) sphere(r=0.08);
  translate([-4.710, -0.492, 2.831]) sphere(r=0.08);
  translate([-4.379, -0.541, 2.932]) sphere(r=0.08);
  translate([-4.054, -0.590, 3.014]) sphere(r=0.08);
  translate([-3.733, -0.638, 3.078]) sphere(r=0.08);
  translate([-3.417, -0.685, 3.124]) sphere(r=0.08);
  translate([-3.105, -0.732, 3.153]) sphere(r=0.08);
  translate([-2.798, -0.777, 3.164]) sphere(r=0.08);
  translate([-2.495, -0.823, 3.158]) sphere(r=0.08);
  translate([-2.196, -0.867, 3.135]) sphere(r=0.08);
  translate([-1.901, -0.911, 3.096]) sphere(r=0.08);
  translate([-1.611, -0.955, 3.040]) sphere(r=0.08);
  translate([-1.324, -0.998, 2.968]) sphere(r=0.08);
  translate([-1.041, -1.040, 2.881]) sphere(r=0.08);
  translate([-0.762, -1.082, 2.777]) sphere(r=0.08);
  translate([-0.487, -1.123, 2.658]) sphere(r=0.08);
  translate([-0.215, -1.163, 2.524]) sphere(r=0.08);
  translate([0.052, -1.203, 2.374]) sphere(r=0.08);
  translate([0.316, -1.243, 2.210]) sphere(r=0.08);
  translate([0.576, -1.282, 2.031]) sphere(r=0.08);
  translate([0.833, -1.320, 1.838]) sphere(r=0.08);
  translate([1.086, -1.358, 1.630]) sphere(r=0.08);
  translate([1.334, -1.395, 1.409]) sphere(r=0.08);
  translate([1.580, -1.432, 1.174]) sphere(r=0.08);
  translate([1.821, -1.468, 0.926]) sphere(r=0.08);
  translate([2.059, -1.503, 0.665]) sphere(r=0.08);
  translate([2.241, -1.530, 0.408]) sphere(r=0.08);
  translate([2.316, -1.551, 0.294]) sphere(r=0.08);
  translate([2.356, -1.565, 0.299]) sphere(r=0.08);
  translate([2.392, -1.578, 0.300]) sphere(r=0.08);
  translate([2.423, -1.587, 0.300]) sphere(r=0.08);
  translate([2.450, -1.594, 0.300]) sphere(r=0.08);
  translate([2.473, -1.598, 0.300]) sphere(r=0.08);
  translate([2.494, -1.601, 0.300]) sphere(r=0.08);
  translate([2.513, -1.603, 0.300]) sphere(r=0.08);
  translate([2.529, -1.603, 0.300]) sphere(r=0.08);
  translate([2.542, -1.601, 0.300]) sphere(r=0.08);
  translate([2.550, -1.596, 0.300]) sphere(r=0.08);
  translate([2.554, -1.589, 0.300]) sphere(r=0.08);
  translate([2.557, -1.583, 0.300]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.961, 0.006, 1.030]) sphere(r=0.08);
  translate([-7.571, 0.064, 1.316]) sphere(r=0.08);
  translate([-7.190, 0.121, 1.579]) sphere(r=0.08);
  translate([-6.816, 0.177, 1.820]) sphere(r=0.08);
  translate([-6.449, 0.232, 2.039]) sphere(r=0.08);
  translate([-6.089, 0.286, 2.237]) sphere(r=0.08);
  translate([-5.735, 0.338, 2.415]) sphere(r=0.08);
  translate([-5.388, 0.390, 2.574]) sphere(r=0.08);
  translate([-5.046, 0.441, 2.712]) sphere(r=0.08);
  translate([-4.710, 0.492, 2.831]) sphere(r=0.08);
  translate([-4.379, 0.541, 2.932]) sphere(r=0.08);
  translate([-4.054, 0.590, 3.014]) sphere(r=0.08);
  translate([-3.733, 0.638, 3.078]) sphere(r=0.08);
  translate([-3.417, 0.685, 3.124]) sphere(r=0.08);
  translate([-3.105, 0.732, 3.153]) sphere(r=0.08);
  translate([-2.798, 0.777, 3.164]) sphere(r=0.08);
  translate([-2.495, 0.823, 3.158]) sphere(r=0.08);
  translate([-2.196, 0.867, 3.135]) sphere(r=0.08);
  translate([-1.901, 0.911, 3.096]) sphere(r=0.08);
  translate([-1.611, 0.955, 3.040]) sphere(r=0.08);
  translate([-1.324, 0.998, 2.968]) sphere(r=0.08);
  translate([-1.041, 1.040, 2.881]) sphere(r=0.08);
  translate([-0.762, 1.082, 2.777]) sphere(r=0.08);
  translate([-0.487, 1.123, 2.658]) sphere(r=0.08);
  translate([-0.215, 1.163, 2.524]) sphere(r=0.08);
  translate([0.052, 1.203, 2.374]) sphere(r=0.08);
  translate([0.316, 1.243, 2.210]) sphere(r=0.08);
  translate([0.576, 1.282, 2.031]) sphere(r=0.08);
  translate([0.833, 1.320, 1.838]) sphere(r=0.08);
  translate([1.086, 1.358, 1.630]) sphere(r=0.08);
  translate([1.334, 1.395, 1.409]) sphere(r=0.08);
  translate([1.580, 1.432, 1.174]) sphere(r=0.08);
  translate([1.821, 1.468, 0.926]) sphere(r=0.08);
  translate([2.059, 1.503, 0.665]) sphere(r=0.08);
  translate([2.240, 1.530, 0.408]) sphere(r=0.08);
  translate([2.316, 1.551, 0.294]) sphere(r=0.08);
  translate([2.356, 1.565, 0.299]) sphere(r=0.08);
  translate([2.392, 1.577, 0.300]) sphere(r=0.08);
  translate([2.424, 1.586, 0.300]) sphere(r=0.08);
  translate([2.451, 1.593, 0.300]) sphere(r=0.08);
  translate([2.476, 1.598, 0.300]) sphere(r=0.08);
  translate([2.498, 1.602, 0.300]) sphere(r=0.08);
  translate([2.518, 1.605, 0.300]) sphere(r=0.08);
  translate([2.534, 1.604, 0.300]) sphere(r=0.08);
  translate([2.546, 1.601, 0.300]) sphere(r=0.08);
  translate([2.556, 1.596, 0.300]) sphere(r=0.08);
  translate([2.562, 1.590, 0.300]) sphere(r=0.08);
  translate([2.567, 1.583, 0.300]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.972, 0.000, 1.036]) sphere(r=0.08);
  translate([-7.693, 0.000, 1.381]) sphere(r=0.08);
  translate([-7.420, 0.000, 1.704]) sphere(r=0.08);
  translate([-7.152, 0.000, 2.003]) sphere(r=0.08);
  translate([-6.888, 0.000, 2.280]) sphere(r=0.08);
  translate([-6.628, 0.000, 2.536]) sphere(r=0.08);
  translate([-6.373, 0.000, 2.771]) sphere(r=0.08);
  translate([-6.122, 0.000, 2.986]) sphere(r=0.08);
  translate([-5.874, 0.000, 3.180]) sphere(r=0.08);
  translate([-5.629, 0.000, 3.355]) sphere(r=0.08);
  translate([-5.388, 0.000, 3.511]) sphere(r=0.08);
  translate([-5.150, 0.000, 3.647]) sphere(r=0.08);
  translate([-4.915, 0.000, 3.765]) sphere(r=0.08);
  translate([-4.683, 0.000, 3.865]) sphere(r=0.08);
  translate([-4.454, 0.000, 3.946]) sphere(r=0.08);
  translate([-4.227, 0.000, 4.010]) sphere(r=0.08);
  translate([-4.002, 0.000, 4.056]) sphere(r=0.08);
  translate([-3.780, 0.000, 4.085]) sphere(r=0.08);
  translate([-3.560, 0.000, 4.096]) sphere(r=0.08);
  translate([-3.343, 0.000, 4.090]) sphere(r=0.08);
  translate([-3.128, 0.000, 4.068]) sphere(r=0.08);
  translate([-2.914, 0.000, 4.028]) sphere(r=0.08);
  translate([-2.704, 0.000, 3.972]) sphere(r=0.08);
  translate([-2.495, 0.000, 3.900]) sphere(r=0.08);
  translate([-2.289, 0.000, 3.812]) sphere(r=0.08);
  translate([-2.084, 0.000, 3.707]) sphere(r=0.08);
  translate([-1.882, 0.000, 3.587]) sphere(r=0.08);
  translate([-1.682, 0.000, 3.451]) sphere(r=0.08);
  translate([-1.485, 0.000, 3.300]) sphere(r=0.08);
  translate([-1.290, 0.000, 3.133]) sphere(r=0.08);
  translate([-1.097, 0.000, 2.952]) sphere(r=0.08);
  translate([-0.906, 0.000, 2.756]) sphere(r=0.08);
  translate([-0.718, 0.000, 2.545]) sphere(r=0.08);
  translate([-0.533, 0.000, 2.321]) sphere(r=0.08);
  translate([-0.350, 0.000, 2.082]) sphere(r=0.08);
  translate([-0.169, 0.000, 1.830]) sphere(r=0.08);
  translate([0.009, 0.000, 1.564]) sphere(r=0.08);
  translate([0.184, 0.000, 1.286]) sphere(r=0.08);
  translate([0.357, 0.000, 0.994]) sphere(r=0.08);
  translate([0.527, 0.000, 0.690]) sphere(r=0.08);
  translate([0.695, 0.000, 0.374]) sphere(r=0.08);
  translate([0.827, -0.000, 0.293]) sphere(r=0.08);
  translate([0.944, -0.000, 0.302]) sphere(r=0.08);
  translate([1.060, -0.000, 0.300]) sphere(r=0.08);
  translate([1.175, -0.000, 0.300]) sphere(r=0.08);
  translate([1.288, -0.000, 0.300]) sphere(r=0.08);
  translate([1.401, -0.000, 0.300]) sphere(r=0.08);
  translate([1.512, -0.000, 0.300]) sphere(r=0.08);
}
