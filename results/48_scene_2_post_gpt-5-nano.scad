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
color([0.6, 0.4, 0.2]) translate([2.0001, -0.7998, 0.6000]) rotate([-0.00, -0.00, -0.04]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([4.0001, -0.8003, 0.6000]) rotate([-0.00, 0.00, 0.05]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.0001, 0.8004, 0.6000]) rotate([0.00, 0.00, -0.05]) cube([0.300, 0.300, 1.200], center=true);
color([0.6, 0.4, 0.2]) translate([4.0002, 0.8006, 0.6000]) rotate([0.00, -0.00, -0.04]) cube([0.300, 0.300, 1.200], center=true);
color([0.5, 0.5, 0.5]) translate([2.9996, 0.0008, 1.3000]) rotate([-0.00, -0.00, 0.04]) cube([2.400, 2.000, 0.200], center=true);
color([0.5, 0.5, 0.5]) translate([0.2046, -0.0001, 0.8499]) rotate([0.00, -40.13, -0.01]) cube([2.400, 2.000, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9993, -0.9002, 1.6000]) rotate([0.00, -0.00, -0.05]) cube([2.000, 0.100, 0.400], center=true);
color([0.6, 0.4, 0.2]) translate([3.0008, 0.8998, 1.6000]) rotate([-0.00, -0.00, -0.05]) cube([2.000, 0.100, 0.400], center=true);
color([0.6, 0.4, 0.2]) translate([1.0377, 0.0003, 0.5000]) rotate([-0.00, -0.00, -0.01]) cube([1.000, 1.000, 1.000], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([3.0000, -0.0000, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([2.5000, -0.0000, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.5000, -0.0000, 0.2000]) sphere(r=0.2);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.966, 0.000, 1.028]) sphere(r=0.08);
  translate([-7.630, 0.000, 1.299]) sphere(r=0.08);
  translate([-7.301, 0.000, 1.548]) sphere(r=0.08);
  translate([-6.977, 0.000, 1.775]) sphere(r=0.08);
  translate([-6.659, 0.000, 1.982]) sphere(r=0.08);
  translate([-6.346, 0.000, 2.169]) sphere(r=0.08);
  translate([-6.038, 0.000, 2.335]) sphere(r=0.08);
  translate([-5.735, 0.000, 2.482]) sphere(r=0.08);
  translate([-5.436, 0.000, 2.610]) sphere(r=0.08);
  translate([-5.142, 0.000, 2.719]) sphere(r=0.08);
  translate([-4.851, 0.000, 2.810]) sphere(r=0.08);
  translate([-4.565, 0.000, 2.883]) sphere(r=0.08);
  translate([-4.282, 0.000, 2.938]) sphere(r=0.08);
  translate([-4.003, 0.000, 2.975]) sphere(r=0.08);
  translate([-3.728, 0.000, 2.994]) sphere(r=0.08);
  translate([-3.456, 0.000, 2.997]) sphere(r=0.08);
  translate([-3.187, 0.000, 2.982]) sphere(r=0.08);
  translate([-2.922, 0.000, 2.951]) sphere(r=0.08);
  translate([-2.660, 0.000, 2.903]) sphere(r=0.08);
  translate([-2.401, 0.000, 2.839]) sphere(r=0.08);
  translate([-2.146, 0.000, 2.759]) sphere(r=0.08);
  translate([-1.893, 0.000, 2.663]) sphere(r=0.08);
  translate([-1.644, 0.000, 2.551]) sphere(r=0.08);
  translate([-1.398, 0.000, 2.423]) sphere(r=0.08);
  translate([-1.155, 0.000, 2.280]) sphere(r=0.08);
  translate([-0.915, 0.000, 2.122]) sphere(r=0.08);
  translate([-0.678, 0.000, 1.950]) sphere(r=0.08);
  translate([-0.445, 0.000, 1.762]) sphere(r=0.08);
  translate([-0.215, 0.000, 1.561]) sphere(r=0.08);
  translate([-0.008, -0.000, 1.369]) sphere(r=0.08);
  translate([0.013, -0.000, 1.378]) sphere(r=0.08);
  translate([0.027, 0.000, 1.379]) sphere(r=0.08);
  translate([0.033, 0.000, 1.376]) sphere(r=0.08);
  translate([0.029, 0.000, 1.370]) sphere(r=0.08);
  translate([0.017, 0.000, 1.360]) sphere(r=0.08);
  translate([-0.001, 0.000, 1.345]) sphere(r=0.08);
  translate([-0.025, 0.000, 1.325]) sphere(r=0.08);
  translate([-0.055, 0.000, 1.300]) sphere(r=0.08);
  translate([-0.090, 0.000, 1.269]) sphere(r=0.08);
  translate([-0.132, 0.000, 1.234]) sphere(r=0.08);
  translate([-0.179, 0.000, 1.194]) sphere(r=0.08);
  translate([-0.232, 0.000, 1.149]) sphere(r=0.08);
  translate([-0.290, 0.000, 1.099]) sphere(r=0.08);
  translate([-0.354, 0.000, 1.045]) sphere(r=0.08);
  translate([-0.424, 0.000, 0.986]) sphere(r=0.08);
  translate([-0.499, 0.000, 0.922]) sphere(r=0.08);
  translate([-0.579, 0.000, 0.854]) sphere(r=0.08);
  translate([-0.665, 0.000, 0.781]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.964, 0.000, 1.025]) sphere(r=0.08);
  translate([-7.603, 0.000, 1.267]) sphere(r=0.08);
  translate([-7.250, 0.000, 1.487]) sphere(r=0.08);
  translate([-6.902, 0.000, 1.686]) sphere(r=0.08);
  translate([-6.561, 0.000, 1.864]) sphere(r=0.08);
  translate([-6.225, 0.000, 2.023]) sphere(r=0.08);
  translate([-5.895, 0.000, 2.163]) sphere(r=0.08);
  translate([-5.570, 0.000, 2.283]) sphere(r=0.08);
  translate([-5.250, 0.000, 2.385]) sphere(r=0.08);
  translate([-4.935, 0.000, 2.468]) sphere(r=0.08);
  translate([-4.624, 0.000, 2.533]) sphere(r=0.08);
  translate([-4.318, 0.000, 2.580]) sphere(r=0.08);
  translate([-4.015, 0.000, 2.610]) sphere(r=0.08);
  translate([-3.717, 0.000, 2.622]) sphere(r=0.08);
  translate([-3.423, 0.000, 2.617]) sphere(r=0.08);
  translate([-3.133, 0.000, 2.595]) sphere(r=0.08);
  translate([-2.847, 0.000, 2.557]) sphere(r=0.08);
  translate([-2.565, 0.000, 2.502]) sphere(r=0.08);
  translate([-2.286, 0.000, 2.431]) sphere(r=0.08);
  translate([-2.011, 0.000, 2.344]) sphere(r=0.08);
  translate([-1.739, 0.000, 2.241]) sphere(r=0.08);
  translate([-1.471, 0.000, 2.123]) sphere(r=0.08);
  translate([-1.207, 0.000, 1.989]) sphere(r=0.08);
  translate([-0.946, 0.000, 1.841]) sphere(r=0.08);
  translate([-0.689, 0.000, 1.677]) sphere(r=0.08);
  translate([-0.435, 0.000, 1.499]) sphere(r=0.08);
  translate([-0.185, 0.000, 1.306]) sphere(r=0.08);
  translate([-0.080, 0.000, 1.257]) sphere(r=0.08);
  translate([-0.044, 0.000, 1.269]) sphere(r=0.08);
  translate([-0.017, 0.000, 1.278]) sphere(r=0.08);
  translate([0.000, 0.000, 1.284]) sphere(r=0.08);
  translate([0.007, 0.000, 1.288]) sphere(r=0.08);
  translate([0.006, 0.000, 1.287]) sphere(r=0.08);
  translate([-0.001, 0.000, 1.281]) sphere(r=0.08);
  translate([-0.013, 0.000, 1.270]) sphere(r=0.08);
  translate([-0.032, 0.000, 1.254]) sphere(r=0.08);
  translate([-0.057, 0.000, 1.233]) sphere(r=0.08);
  translate([-0.088, 0.000, 1.207]) sphere(r=0.08);
  translate([-0.124, 0.000, 1.176]) sphere(r=0.08);
  translate([-0.166, 0.000, 1.141]) sphere(r=0.08);
  translate([-0.214, 0.000, 1.100]) sphere(r=0.08);
  translate([-0.268, 0.000, 1.054]) sphere(r=0.08);
  translate([-0.327, 0.000, 1.004]) sphere(r=0.08);
  translate([-0.392, 0.000, 0.949]) sphere(r=0.08);
  translate([-0.462, 0.000, 0.889]) sphere(r=0.08);
  translate([-0.538, 0.000, 0.825]) sphere(r=0.08);
  translate([-0.619, 0.000, 0.756]) sphere(r=0.08);
  translate([-0.706, 0.000, 0.682]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.959, 0.000, 1.024]) sphere(r=0.08);
  translate([-7.552, 0.000, 1.248]) sphere(r=0.08);
  translate([-7.153, 0.000, 1.450]) sphere(r=0.08);
  translate([-6.762, 0.000, 1.632]) sphere(r=0.08);
  translate([-6.377, 0.000, 1.794]) sphere(r=0.08);
  translate([-6.000, 0.000, 1.936]) sphere(r=0.08);
  translate([-5.630, 0.000, 2.058]) sphere(r=0.08);
  translate([-5.265, 0.000, 2.162]) sphere(r=0.08);
  translate([-4.907, 0.000, 2.247]) sphere(r=0.08);
  translate([-4.554, 0.000, 2.313]) sphere(r=0.08);
  translate([-4.207, 0.000, 2.362]) sphere(r=0.08);
  translate([-3.866, 0.000, 2.393]) sphere(r=0.08);
  translate([-3.529, 0.000, 2.407]) sphere(r=0.08);
  translate([-3.198, 0.000, 2.403]) sphere(r=0.08);
  translate([-2.871, 0.000, 2.383]) sphere(r=0.08);
  translate([-2.550, 0.000, 2.346]) sphere(r=0.08);
  translate([-2.232, 0.000, 2.292]) sphere(r=0.08);
  translate([-1.920, 0.000, 2.223]) sphere(r=0.08);
  translate([-1.612, 0.000, 2.137]) sphere(r=0.08);
  translate([-1.308, 0.000, 2.036]) sphere(r=0.08);
  translate([-1.009, 0.000, 1.920]) sphere(r=0.08);
  translate([-0.714, 0.000, 1.788]) sphere(r=0.08);
  translate([-0.423, 0.000, 1.641]) sphere(r=0.08);
  translate([-0.137, 0.000, 1.479]) sphere(r=0.08);
  translate([0.102, -0.000, 1.348]) sphere(r=0.08);
  translate([0.165, -0.000, 1.383]) sphere(r=0.08);
  translate([0.221, -0.000, 1.412]) sphere(r=0.08);
  translate([0.266, -0.000, 1.437]) sphere(r=0.08);
  translate([0.302, -0.000, 1.459]) sphere(r=0.08);
  translate([0.328, -0.000, 1.478]) sphere(r=0.08);
  translate([0.346, -0.000, 1.493]) sphere(r=0.08);
  translate([0.358, -0.000, 1.503]) sphere(r=0.08);
  translate([0.363, -0.000, 1.508]) sphere(r=0.08);
  translate([0.363, -0.000, 1.507]) sphere(r=0.08);
  translate([0.356, -0.000, 1.502]) sphere(r=0.08);
  translate([0.344, -0.000, 1.491]) sphere(r=0.08);
  translate([0.326, -0.000, 1.475]) sphere(r=0.08);
  translate([0.301, -0.000, 1.455]) sphere(r=0.08);
  translate([0.271, -0.000, 1.429]) sphere(r=0.08);
  translate([0.235, -0.000, 1.399]) sphere(r=0.08);
  translate([0.194, -0.000, 1.364]) sphere(r=0.08);
  translate([0.146, -0.000, 1.324]) sphere(r=0.08);
  translate([0.093, -0.000, 1.279]) sphere(r=0.08);
  translate([0.034, -0.000, 1.230]) sphere(r=0.08);
  translate([-0.030, -0.000, 1.175]) sphere(r=0.08);
  translate([-0.100, -0.000, 1.116]) sphere(r=0.08);
  translate([-0.175, -0.000, 1.053]) sphere(r=0.08);
  translate([-0.256, -0.000, 0.985]) sphere(r=0.08);
}
