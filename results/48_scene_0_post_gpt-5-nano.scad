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
color([0.6, 0.4, 0.2]) translate([3.0043, -0.4257, 0.1500]) rotate([-0.00, 0.00, -0.43]) cube([1.000, 0.300, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([3.0026, 0.4232, 0.1500]) rotate([0.00, 0.00, 0.25]) cube([1.000, 0.300, 0.300], center=true);
color([0.6, 0.4, 0.2]) translate([2.6514, -0.4068, 0.8012]) rotate([-0.74, 0.03, -1.55]) cube([0.200, 0.200, 1.000], center=true);
color([0.6, 0.4, 0.2]) translate([3.3536, -0.4265, 0.8000]) rotate([-0.00, 0.00, -0.06]) cube([0.200, 0.200, 1.000], center=true);
color([0.6, 0.4, 0.2]) translate([2.6488, 0.4192, 0.8000]) rotate([0.02, 0.01, -0.89]) cube([0.200, 0.200, 1.000], center=true);
color([0.6, 0.4, 0.2]) translate([3.3516, 0.4218, 0.7999]) rotate([0.02, -0.01, 0.13]) cube([0.200, 0.200, 1.000], center=true);
color([0.6, 0.4, 0.2]) translate([3.0021, -0.4110, 1.4012]) rotate([-0.74, -0.01, -1.93]) cube([1.000, 0.300, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9974, 0.4182, 1.3999]) rotate([0.02, 0.01, 0.16]) cube([1.000, 0.300, 0.200], center=true);
color([0.6, 0.4, 0.2]) translate([2.9965, 0.0131, 1.5810]) rotate([-0.13, 0.02, 0.31]) cube([1.200, 1.000, 0.160], center=true);
color([0.6, 0.4, 0.2]) translate([2.9959, -0.2687, 2.0626]) rotate([0.58, 0.01, 0.96]) cube([0.160, 0.160, 0.800], center=true);
color([0.6, 0.4, 0.2]) translate([2.9940, 0.2994, 2.0624]) rotate([-1.69, 0.01, -0.19]) cube([0.160, 0.160, 0.800], center=true);
color([0.6, 0.4, 0.2]) translate([2.9941, 0.0195, 2.5240]) rotate([0.17, 0.01, 0.42]) cube([0.600, 0.800, 0.120], center=true);
color([0.6, 0.4, 0.2]) translate([1.4763, 0.0008, 0.2404]) rotate([0.00, 81.87, 0.01]) cube([0.200, 1.200, 2.000], center=true);
color([0.6, 0.4, 0.2]) translate([2.0011, 0.0002, 0.1000]) rotate([0.00, -0.00, -0.08]) cube([0.200, 0.200, 0.200], center=true);

// Targets
color([0.0, 0.8, 0.0]) translate([13.6983, -0.9660, 0.2000]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([2.9917, 0.0133, 1.8610]) sphere(r=0.2);
color([0.0, 0.8, 0.0]) translate([3.0989, -5.4706, 0.2000]) sphere(r=0.2);

// Projectile trajectories
// Shot 1 trajectory
color(path_colors[0]) {
  translate([-7.969, 0.000, 1.031]) sphere(r=0.08);
  translate([-7.660, 0.000, 1.328]) sphere(r=0.08);
  translate([-7.358, 0.000, 1.604]) sphere(r=0.08);
  translate([-7.060, 0.000, 1.857]) sphere(r=0.08);
  translate([-6.768, 0.000, 2.089]) sphere(r=0.08);
  translate([-6.480, 0.000, 2.301]) sphere(r=0.08);
  translate([-6.197, 0.000, 2.492]) sphere(r=0.08);
  translate([-5.918, 0.000, 2.664]) sphere(r=0.08);
  translate([-5.643, 0.000, 2.816]) sphere(r=0.08);
  translate([-5.371, 0.000, 2.949]) sphere(r=0.08);
  translate([-5.104, 0.000, 3.063]) sphere(r=0.08);
  translate([-4.840, 0.000, 3.159]) sphere(r=0.08);
  translate([-4.579, 0.000, 3.237]) sphere(r=0.08);
  translate([-4.322, 0.000, 3.297]) sphere(r=0.08);
  translate([-4.067, 0.000, 3.339]) sphere(r=0.08);
  translate([-3.816, 0.000, 3.364]) sphere(r=0.08);
  translate([-3.568, 0.000, 3.372]) sphere(r=0.08);
  translate([-3.322, 0.000, 3.362]) sphere(r=0.08);
  translate([-3.079, 0.000, 3.336]) sphere(r=0.08);
  translate([-2.839, 0.000, 3.293]) sphere(r=0.08);
  translate([-2.602, 0.000, 3.234]) sphere(r=0.08);
  translate([-2.367, 0.000, 3.158]) sphere(r=0.08);
  translate([-2.135, 0.000, 3.066]) sphere(r=0.08);
  translate([-1.906, 0.000, 2.959]) sphere(r=0.08);
  translate([-1.680, 0.000, 2.836]) sphere(r=0.08);
  translate([-1.456, 0.000, 2.697]) sphere(r=0.08);
  translate([-1.235, 0.000, 2.543]) sphere(r=0.08);
  translate([-1.017, 0.000, 2.374]) sphere(r=0.08);
  translate([-0.801, 0.000, 2.190]) sphere(r=0.08);
  translate([-0.589, 0.000, 1.992]) sphere(r=0.08);
  translate([-0.389, -0.000, 1.782]) sphere(r=0.08);
  translate([-0.285, -0.000, 1.587]) sphere(r=0.08);
  translate([-0.198, -0.000, 1.382]) sphere(r=0.08);
  translate([-0.134, -0.000, 1.173]) sphere(r=0.08);
  translate([-0.096, -0.000, 0.965]) sphere(r=0.08);
  translate([-0.090, -0.000, 0.764]) sphere(r=0.08);
  translate([-0.118, -0.000, 0.580]) sphere(r=0.08);
  translate([-0.182, -0.000, 0.416]) sphere(r=0.08);
  translate([-0.280, -0.000, 0.287]) sphere(r=0.08);
  translate([-0.412, -0.000, 0.295]) sphere(r=0.08);
  translate([-0.543, -0.000, 0.298]) sphere(r=0.08);
  translate([-0.672, -0.000, 0.299]) sphere(r=0.08);
  translate([-0.800, -0.000, 0.300]) sphere(r=0.08);
  translate([-0.926, -0.000, 0.300]) sphere(r=0.08);
  translate([-1.052, -0.000, 0.300]) sphere(r=0.08);
  translate([-1.176, -0.000, 0.300]) sphere(r=0.08);
  translate([-1.299, -0.000, 0.300]) sphere(r=0.08);
  translate([-1.421, -0.000, 0.300]) sphere(r=0.08);
}
// Shot 2 trajectory
color(path_colors[1]) {
  translate([-7.966, 0.000, 1.033]) sphere(r=0.08);
  translate([-7.635, 0.000, 1.354]) sphere(r=0.08);
  translate([-7.310, 0.000, 1.651]) sphere(r=0.08);
  translate([-6.991, 0.000, 1.926]) sphere(r=0.08);
  translate([-6.678, 0.000, 2.179]) sphere(r=0.08);
  translate([-6.370, 0.000, 2.411]) sphere(r=0.08);
  translate([-6.068, 0.000, 2.622]) sphere(r=0.08);
  translate([-5.770, 0.000, 2.812]) sphere(r=0.08);
  translate([-5.477, 0.000, 2.983]) sphere(r=0.08);
  translate([-5.188, 0.000, 3.134]) sphere(r=0.08);
  translate([-4.904, 0.000, 3.267]) sphere(r=0.08);
  translate([-4.623, 0.000, 3.380]) sphere(r=0.08);
  translate([-4.346, 0.000, 3.475]) sphere(r=0.08);
  translate([-4.073, 0.000, 3.552]) sphere(r=0.08);
  translate([-3.803, 0.000, 3.611]) sphere(r=0.08);
  translate([-3.537, 0.000, 3.652]) sphere(r=0.08);
  translate([-3.274, 0.000, 3.676]) sphere(r=0.08);
  translate([-3.014, 0.000, 3.682]) sphere(r=0.08);
  translate([-2.757, 0.000, 3.672]) sphere(r=0.08);
  translate([-2.503, 0.000, 3.645]) sphere(r=0.08);
  translate([-2.253, 0.000, 3.601]) sphere(r=0.08);
  translate([-2.005, 0.000, 3.541]) sphere(r=0.08);
  translate([-1.760, 0.000, 3.464]) sphere(r=0.08);
  translate([-1.518, 0.000, 3.371]) sphere(r=0.08);
  translate([-1.279, 0.000, 3.263]) sphere(r=0.08);
  translate([-1.043, 0.000, 3.139]) sphere(r=0.08);
  translate([-0.810, 0.000, 3.000]) sphere(r=0.08);
  translate([-0.579, 0.000, 2.845]) sphere(r=0.08);
  translate([-0.352, 0.000, 2.675]) sphere(r=0.08);
  translate([-0.128, 0.000, 2.491]) sphere(r=0.08);
  translate([0.094, 0.000, 2.292]) sphere(r=0.08);
  translate([0.312, 0.000, 2.080]) sphere(r=0.08);
  translate([0.528, 0.000, 1.853]) sphere(r=0.08);
  translate([0.740, 0.000, 1.612]) sphere(r=0.08);
  translate([0.949, 0.000, 1.358]) sphere(r=0.08);
  translate([1.155, 0.000, 1.091]) sphere(r=0.08);
  translate([1.358, 0.000, 0.811]) sphere(r=0.08);
  translate([1.521, 0.000, 0.646]) sphere(r=0.08);
  translate([1.628, 0.000, 0.664]) sphere(r=0.08);
  translate([1.733, 0.000, 0.680]) sphere(r=0.08);
  translate([1.835, 0.000, 0.695]) sphere(r=0.08);
  translate([1.935, 0.000, 0.710]) sphere(r=0.08);
  translate([2.032, 0.000, 0.724]) sphere(r=0.08);
  translate([2.126, 0.000, 0.738]) sphere(r=0.08);
  translate([2.218, 0.000, 0.751]) sphere(r=0.08);
  translate([2.308, 0.000, 0.764]) sphere(r=0.08);
  translate([2.395, 0.000, 0.777]) sphere(r=0.08);
  translate([2.480, 0.000, 0.785]) sphere(r=0.08);
}
// Shot 3 trajectory
color(path_colors[2]) {
  translate([-7.965, 0.000, 1.035]) sphere(r=0.08);
  translate([-7.616, 0.000, 1.373]) sphere(r=0.08);
  translate([-7.275, 0.000, 1.687]) sphere(r=0.08);
  translate([-6.940, 0.000, 1.978]) sphere(r=0.08);
  translate([-6.611, 0.000, 2.246]) sphere(r=0.08);
  translate([-6.289, 0.000, 2.493]) sphere(r=0.08);
  translate([-5.972, 0.000, 2.718]) sphere(r=0.08);
  translate([-5.660, 0.000, 2.923]) sphere(r=0.08);
  translate([-5.354, 0.000, 3.107]) sphere(r=0.08);
  translate([-5.052, 0.000, 3.272]) sphere(r=0.08);
  translate([-4.755, 0.000, 3.418]) sphere(r=0.08);
  translate([-4.462, 0.000, 3.544]) sphere(r=0.08);
  translate([-4.173, 0.000, 3.652]) sphere(r=0.08);
  translate([-3.888, 0.000, 3.741]) sphere(r=0.08);
  translate([-3.608, 0.000, 3.812]) sphere(r=0.08);
  translate([-3.330, 0.000, 3.865]) sphere(r=0.08);
  translate([-3.057, 0.000, 3.901]) sphere(r=0.08);
  translate([-2.786, 0.000, 3.919]) sphere(r=0.08);
  translate([-2.519, 0.000, 3.920]) sphere(r=0.08);
  translate([-2.256, 0.000, 3.904]) sphere(r=0.08);
  translate([-1.995, 0.000, 3.871]) sphere(r=0.08);
  translate([-1.738, 0.000, 3.822]) sphere(r=0.08);
  translate([-1.484, 0.000, 3.757]) sphere(r=0.08);
  translate([-1.232, 0.000, 3.675]) sphere(r=0.08);
  translate([-0.984, 0.000, 3.577]) sphere(r=0.08);
  translate([-0.739, 0.000, 3.464]) sphere(r=0.08);
  translate([-0.497, 0.000, 3.335]) sphere(r=0.08);
  translate([-0.258, 0.000, 3.191]) sphere(r=0.08);
  translate([-0.023, 0.000, 3.032]) sphere(r=0.08);
  translate([0.210, 0.000, 2.858]) sphere(r=0.08);
  translate([0.440, 0.000, 2.669]) sphere(r=0.08);
  translate([0.666, 0.000, 2.466]) sphere(r=0.08);
  translate([0.890, 0.000, 2.249]) sphere(r=0.08);
  translate([1.110, 0.000, 2.018]) sphere(r=0.08);
  translate([1.327, 0.000, 1.773]) sphere(r=0.08);
  translate([1.541, 0.000, 1.515]) sphere(r=0.08);
  translate([1.752, 0.000, 1.245]) sphere(r=0.08);
  translate([1.959, 0.000, 0.961]) sphere(r=0.08);
  translate([2.146, 0.000, 0.726]) sphere(r=0.08);
  translate([2.265, 0.001, 0.718]) sphere(r=0.08);
  translate([2.383, 0.002, 0.693]) sphere(r=0.08);
  translate([2.495, 0.002, 0.672]) sphere(r=0.08);
  translate([2.606, 0.001, 0.645]) sphere(r=0.08);
  translate([2.716, -0.001, 0.603]) sphere(r=0.08);
  translate([2.824, -0.001, 0.544]) sphere(r=0.08);
  translate([2.932, -0.000, 0.469]) sphere(r=0.08);
  translate([3.015, -0.000, 0.441]) sphere(r=0.08);
  translate([3.082, 0.000, 0.428]) sphere(r=0.08);
}
