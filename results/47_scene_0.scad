// Crime Scene Render - Test 47
$fn = 20;

// Colors
stair_color = [0.6, 0.5, 0.4];
body_color = [0.85, 0.65, 0.55];
head_color = [0.9, 0.75, 0.65];
floor_color = [0.35, 0.35, 0.38];

// Capsule module - hull of two spheres
module capsule(p1, p2, r) {
  hull() {
    translate(p1) sphere(r=r);
    translate(p2) sphere(r=r);
  }
}

// Stairs
color(stair_color) {
  translate([0.15, 0, 1.9]) cube([0.3, 2.0, 0.2], center=true);
  translate([0.44999999999999996, 0, 1.7]) cube([0.3, 2.0, 0.2], center=true);
  translate([0.75, 0, 1.5]) cube([0.3, 2.0, 0.2], center=true);
  translate([1.0499999999999998, 0, 1.2999999999999998]) cube([0.3, 2.0, 0.2], center=true);
  translate([1.3499999999999999, 0, 1.0999999999999999]) cube([0.3, 2.0, 0.2], center=true);
  translate([1.65, 0, 0.9]) cube([0.3, 2.0, 0.2], center=true);
  translate([1.9499999999999997, 0, 0.6999999999999998]) cube([0.3, 2.0, 0.2], center=true);
  translate([2.25, 0, 0.4999999999999999]) cube([0.3, 2.0, 0.2], center=true);
  translate([2.55, 0, 0.29999999999999993]) cube([0.3, 2.0, 0.2], center=true);
  translate([2.8499999999999996, 0, 0.09999999999999995]) cube([0.3, 2.0, 0.2], center=true);
}

// Floor
color(floor_color) translate([2.5, 0, -0.025]) cube([5, 3, 0.05], center=true);

// Ragdoll body (capsule-based)
color(body_color) {
  capsule([3.3588, 0.0138, 0.1217], [3.3771, 0.4117, 0.1432], 0.1); // base to chest
  capsule([3.1714, 0.4042, 0.1152], [3.1584, 0.1195, 0.0997], 0.05); // right_shoulder to right_elbow
  capsule([3.1584, 0.1195, 0.0997], [3.1512, -0.0357, 0.0912], 0.045); // right_elbow to right_wrist
  capsule([3.5812, 0.3853, 0.1153], [3.5681, 0.1007, 0.0997], 0.05); // left_shoulder to left_elbow
  capsule([3.5681, 0.1007, 0.0997], [3.5610, -0.0545, 0.0911], 0.045); // left_elbow to left_wrist
  capsule([3.3588, 0.0138, 0.1217], [3.2531, -0.2164, 0.1093], 0.065); // base to right_hip
  capsule([3.2531, -0.2164, 0.1093], [3.2320, -0.6763, 0.0851], 0.062); // right_hip to right_knee
  capsule([3.2320, -0.6763, 0.0851], [3.2199, -0.9385, 0.1218], 0.056); // right_knee to right_ankle
  capsule([3.3588, 0.0138, 0.1217], [3.4430, -0.2252, 0.1094], 0.065); // base to left_hip
  capsule([3.4430, -0.2252, 0.1094], [3.4218, -0.6850, 0.0851], 0.062); // left_hip to left_knee
  capsule([3.4218, -0.6850, 0.0851], [3.4097, -0.9472, 0.1218], 0.056); // left_knee to left_ankle
  capsule([3.1714, 0.4042, 0.1152], [3.5812, 0.3853, 0.1153], 0.07); // shoulders
  capsule([3.3771, 0.4117, 0.1432], [3.1714, 0.4042, 0.1152], 0.065); // chest to right shoulder
  capsule([3.3771, 0.4117, 0.1432], [3.5812, 0.3853, 0.1153], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([3.3771, 0.4117, 0.1432], [3.3914, 0.7233, 0.1601], 0.055); // neck
color(head_color) translate([3.3890, 0.6714, 0.1572]) sphere(r=0.15); // head

// Hands and feet
color(body_color) {
  translate([3.1512, -0.0357, 0.0912]) sphere(r=0.04);
  translate([3.5610, -0.0545, 0.0911]) sphere(r=0.04);
  translate([3.2199, -0.9385, 0.1218]) sphere(r=0.055);
  translate([3.4097, -0.9472, 0.1218]) sphere(r=0.055);
}
