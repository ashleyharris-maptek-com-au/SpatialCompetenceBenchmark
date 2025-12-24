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
color([0.5, 0.3, 0.1]) translate([2.0000, -1.5000, 0.4000]) rotate([0.00, 0.00, 0.00]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([2.1818, -1.2272, 0.4000]) rotate([0.00, 0.00, 0.08]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([2.3536, -0.9528, 0.4000]) rotate([-0.00, 0.00, 2.76]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([2.5066, -0.6938, 0.4000]) rotate([0.00, 0.00, 10.39]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([2.6411, -0.4554, 0.4000]) rotate([0.00, 0.00, 26.83]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([2.6302, -0.1218, 0.4000]) rotate([0.00, 0.00, 62.15]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([3.3695, 0.1263, 0.4000]) rotate([0.00, -0.01, 63.04]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([3.3592, 0.4579, 0.4000]) rotate([0.00, -0.00, 27.30]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([3.4943, 0.6937, 0.4000]) rotate([0.00, -0.00, 10.67]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([3.6447, 0.9531, 0.4000]) rotate([-0.00, -0.00, 2.42]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([4.5539, 0.6511, 0.0800]) rotate([-149.88, 90.00, 126.68]) cube([0.160, 0.500, 0.800], center=true);
color([0.5, 0.3, 0.1]) translate([6.3724, 1.2312, 0.0800]) rotate([-107.68, 90.00, -143.45]) cube([0.160, 0.500, 0.800], center=true);
color([0.6, 0.4, 0.2]) translate([0.8001, 0.0003, 0.5000]) rotate([0.00, -0.00, -0.01]) cube([1.000, 1.000, 1.000], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([19.4338, -2.0335, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.0224, -0.0130, 0.2000]) sphere(r=0.2);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.940, 0.000, 1.017]) sphere(r=0.08);
  translate([-7.350, 0.000, 1.175]) sphere(r=0.08);
  translate([-6.774, 0.000, 1.313]) sphere(r=0.08);
  translate([-6.213, 0.000, 1.430]) sphere(r=0.08);
  translate([-5.665, 0.000, 1.528]) sphere(r=0.08);
  translate([-5.130, 0.000, 1.606]) sphere(r=0.08);
  translate([-4.607, 0.000, 1.666]) sphere(r=0.08);
  translate([-4.096, 0.000, 1.708]) sphere(r=0.08);
  translate([-3.596, 0.000, 1.731]) sphere(r=0.08);
  translate([-3.106, 0.000, 1.738]) sphere(r=0.08);
  translate([-2.627, 0.000, 1.727]) sphere(r=0.08);
  translate([-2.158, 0.000, 1.700]) sphere(r=0.08);
  translate([-1.698, 0.000, 1.657]) sphere(r=0.08);
  translate([-1.247, 0.000, 1.597]) sphere(r=0.08);
  translate([-0.805, 0.000, 1.522]) sphere(r=0.08);
  translate([-0.372, 0.000, 1.431]) sphere(r=0.08);
  translate([0.054, 0.000, 1.325]) sphere(r=0.08);
  translate([0.390, 0.000, 1.331]) sphere(r=0.08);
  translate([0.668, 0.000, 1.404]) sphere(r=0.08);
  translate([0.943, 0.000, 1.459]) sphere(r=0.08);
  translate([1.214, 0.000, 1.496]) sphere(r=0.08);
  translate([1.482, 0.000, 1.516]) sphere(r=0.08);
  translate([1.746, 0.000, 1.519]) sphere(r=0.08);
  translate([2.007, 0.000, 1.505]) sphere(r=0.08);
  translate([2.265, 0.000, 1.474]) sphere(r=0.08);
  translate([2.520, 0.000, 1.426]) sphere(r=0.08);
  translate([2.772, 0.000, 1.362]) sphere(r=0.08);
  translate([3.021, 0.000, 1.282]) sphere(r=0.08);
  translate([3.267, 0.000, 1.186]) sphere(r=0.08);
  translate([3.505, -0.001, 1.099]) sphere(r=0.08);
  translate([3.721, -0.008, 1.097]) sphere(r=0.08);
  translate([3.934, -0.014, 1.079]) sphere(r=0.08);
  translate([4.145, -0.020, 1.044]) sphere(r=0.08);
  translate([4.354, -0.025, 0.992]) sphere(r=0.08);
  translate([4.561, -0.031, 0.924]) sphere(r=0.08);
  translate([4.766, -0.037, 0.840]) sphere(r=0.08);
  translate([4.968, -0.043, 0.740]) sphere(r=0.08);
  translate([5.169, -0.048, 0.624]) sphere(r=0.08);
  translate([5.367, -0.054, 0.492]) sphere(r=0.08);
  translate([5.563, -0.060, 0.345]) sphere(r=0.08);
  translate([5.748, -0.062, 0.299]) sphere(r=0.08);
  translate([5.928, -0.062, 0.300]) sphere(r=0.08);
  translate([6.105, -0.063, 0.300]) sphere(r=0.08);
  translate([6.279, -0.063, 0.300]) sphere(r=0.08);
  translate([6.452, -0.064, 0.300]) sphere(r=0.08);
  translate([6.622, -0.064, 0.300]) sphere(r=0.08);
  translate([6.790, -0.065, 0.300]) sphere(r=0.08);
  translate([6.956, -0.066, 0.300]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.941, 0.008, 1.019]) sphere(r=0.08);
  translate([-7.363, 0.090, 1.198]) sphere(r=0.08);
  translate([-6.799, 0.169, 1.355]) sphere(r=0.08);
  translate([-6.249, 0.246, 1.492]) sphere(r=0.08);
  translate([-5.712, 0.322, 1.609]) sphere(r=0.08);
  translate([-5.188, 0.395, 1.706]) sphere(r=0.08);
  translate([-4.675, 0.467, 1.784]) sphere(r=0.08);
  translate([-4.174, 0.538, 1.843]) sphere(r=0.08);
  translate([-3.684, 0.607, 1.885]) sphere(r=0.08);
  translate([-3.204, 0.674, 1.908]) sphere(r=0.08);
  translate([-2.734, 0.740, 1.914]) sphere(r=0.08);
  translate([-2.274, 0.805, 1.903]) sphere(r=0.08);
  translate([-1.823, 0.868, 1.876]) sphere(r=0.08);
  translate([-1.380, 0.930, 1.832]) sphere(r=0.08);
  translate([-0.946, 0.991, 1.772]) sphere(r=0.08);
  translate([-0.521, 1.051, 1.697]) sphere(r=0.08);
  translate([-0.103, 1.110, 1.606]) sphere(r=0.08);
  translate([0.307, 1.167, 1.499]) sphere(r=0.08);
  translate([0.709, 1.224, 1.378]) sphere(r=0.08);
  translate([1.103, 1.279, 1.242]) sphere(r=0.08);
  translate([1.491, 1.334, 1.092]) sphere(r=0.08);
  translate([1.871, 1.387, 0.928]) sphere(r=0.08);
  translate([2.245, 1.440, 0.749]) sphere(r=0.08);
  translate([2.612, 1.491, 0.557]) sphere(r=0.08);
  translate([2.972, 1.542, 0.352]) sphere(r=0.08);
  translate([3.261, 1.583, 0.296]) sphere(r=0.08);
  translate([3.512, 1.621, 0.299]) sphere(r=0.08);
  translate([3.732, 1.667, 0.300]) sphere(r=0.08);
  translate([3.943, 1.711, 0.300]) sphere(r=0.08);
  translate([4.151, 1.754, 0.300]) sphere(r=0.08);
  translate([4.355, 1.797, 0.300]) sphere(r=0.08);
  translate([4.557, 1.838, 0.300]) sphere(r=0.08);
  translate([4.755, 1.880, 0.300]) sphere(r=0.08);
  translate([4.950, 1.920, 0.300]) sphere(r=0.08);
  translate([5.142, 1.960, 0.300]) sphere(r=0.08);
  translate([5.332, 2.000, 0.300]) sphere(r=0.08);
  translate([5.519, 2.038, 0.300]) sphere(r=0.08);
  translate([5.703, 2.077, 0.300]) sphere(r=0.08);
  translate([5.884, 2.114, 0.300]) sphere(r=0.08);
  translate([6.063, 2.152, 0.300]) sphere(r=0.08);
  translate([6.240, 2.188, 0.300]) sphere(r=0.08);
  translate([6.414, 2.225, 0.300]) sphere(r=0.08);
  translate([6.579, 2.263, 0.301]) sphere(r=0.08);
  translate([6.736, 2.304, 0.300]) sphere(r=0.08);
  translate([6.891, 2.345, 0.300]) sphere(r=0.08);
  translate([7.044, 2.385, 0.300]) sphere(r=0.08);
  translate([7.195, 2.424, 0.300]) sphere(r=0.08);
  translate([7.345, 2.463, 0.300]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.938, 0.009, 1.023]) sphere(r=0.08);
  translate([-7.329, 0.094, 1.236]) sphere(r=0.08);
  translate([-6.736, 0.178, 1.426]) sphere(r=0.08);
  translate([-6.159, 0.259, 1.594]) sphere(r=0.08);
  translate([-5.596, 0.338, 1.742]) sphere(r=0.08);
  translate([-5.047, 0.415, 1.869]) sphere(r=0.08);
  translate([-4.512, 0.490, 1.976]) sphere(r=0.08);
  translate([-3.988, 0.564, 2.064]) sphere(r=0.08);
  translate([-3.477, 0.636, 2.133]) sphere(r=0.08);
  translate([-2.976, 0.706, 2.183]) sphere(r=0.08);
  translate([-2.487, 0.775, 2.216]) sphere(r=0.08);
  translate([-2.008, 0.842, 2.231]) sphere(r=0.08);
  translate([-1.538, 0.908, 2.229]) sphere(r=0.08);
  translate([-1.079, 0.973, 2.210]) sphere(r=0.08);
  translate([-0.628, 1.036, 2.174]) sphere(r=0.08);
  translate([-0.186, 1.098, 2.123]) sphere(r=0.08);
  translate([0.247, 1.159, 2.055]) sphere(r=0.08);
  translate([0.672, 1.219, 1.972]) sphere(r=0.08);
  translate([1.089, 1.277, 1.874]) sphere(r=0.08);
  translate([1.498, 1.335, 1.760]) sphere(r=0.08);
  translate([1.899, 1.391, 1.632]) sphere(r=0.08);
  translate([2.293, 1.447, 1.489]) sphere(r=0.08);
  translate([2.680, 1.501, 1.332]) sphere(r=0.08);
  translate([3.060, 1.554, 1.161]) sphere(r=0.08);
  translate([3.433, 1.607, 0.976]) sphere(r=0.08);
  translate([3.799, 1.658, 0.778]) sphere(r=0.08);
  translate([4.158, 1.709, 0.566]) sphere(r=0.08);
  translate([4.511, 1.758, 0.342]) sphere(r=0.08);
  translate([4.780, 1.796, 0.299]) sphere(r=0.08);
  translate([5.024, 1.830, 0.300]) sphere(r=0.08);
  translate([5.262, 1.864, 0.300]) sphere(r=0.08);
  translate([5.497, 1.897, 0.300]) sphere(r=0.08);
  translate([5.727, 1.929, 0.300]) sphere(r=0.08);
  translate([5.954, 1.961, 0.300]) sphere(r=0.08);
  translate([6.176, 1.992, 0.300]) sphere(r=0.08);
  translate([6.395, 2.023, 0.300]) sphere(r=0.08);
  translate([6.611, 2.053, 0.300]) sphere(r=0.08);
  translate([6.823, 2.083, 0.300]) sphere(r=0.08);
  translate([7.032, 2.113, 0.300]) sphere(r=0.08);
  translate([7.237, 2.141, 0.300]) sphere(r=0.08);
  translate([7.440, 2.170, 0.300]) sphere(r=0.08);
  translate([7.639, 2.198, 0.300]) sphere(r=0.08);
  translate([7.835, 2.226, 0.300]) sphere(r=0.08);
  translate([8.029, 2.253, 0.300]) sphere(r=0.08);
  translate([8.220, 2.280, 0.300]) sphere(r=0.08);
  translate([8.408, 2.306, 0.300]) sphere(r=0.08);
  translate([8.593, 2.332, 0.300]) sphere(r=0.08);
  translate([8.775, 2.358, 0.300]) sphere(r=0.08);
}
