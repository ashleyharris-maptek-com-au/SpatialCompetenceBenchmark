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
  capsule([3.3572, -0.1087, 0.2503], [3.3900, 0.2871, 0.2868], 0.1); // base to chest
  capsule([3.3370, 0.2548, 0.4849], [3.3136, -0.0284, 0.4590], 0.05); // right_shoulder to right_elbow
  capsule([3.3136, -0.0284, 0.4590], [3.3008, -0.1829, 0.4448], 0.045); // right_elbow to right_wrist
  capsule([3.3866, 0.2878, 0.0794], [3.4454, 0.0240, 0.0654], 0.05); // left_shoulder to left_elbow
  capsule([3.4454, 0.0240, 0.0654], [3.5280, -0.1079, 0.0648], 0.045); // left_elbow to left_wrist
  capsule([3.3572, -0.1087, 0.2503], [3.3264, -0.3499, 0.3225], 0.065); // base to right_hip
  capsule([3.3264, -0.3499, 0.3225], [3.1898, -0.7735, 0.2703], 0.062); // right_hip to right_knee
  capsule([3.1898, -0.7735, 0.2703], [3.0962, -1.0195, 0.2383], 0.056); // right_knee to right_ankle
  capsule([3.3572, -0.1087, 0.2503], [3.3495, -0.3344, 0.1345], 0.065); // base to left_hip
  capsule([3.3495, -0.3344, 0.1345], [3.3119, -0.7918, 0.0920], 0.062); // left_hip to left_knee
  capsule([3.3119, -0.7918, 0.0920], [3.3406, -1.0546, 0.0738], 0.056); // left_knee to left_ankle
  capsule([3.3370, 0.2548, 0.4849], [3.3866, 0.2878, 0.0794], 0.07); // shoulders
  capsule([3.3900, 0.2871, 0.2868], [3.3370, 0.2548, 0.4849], 0.065); // chest to right shoulder
  capsule([3.3900, 0.2871, 0.2868], [3.3866, 0.2878, 0.0794], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([3.3900, 0.2871, 0.2868], [3.4156, 0.5971, 0.3154], 0.055); // neck
color(head_color) translate([3.4113, 0.5455, 0.3106]) sphere(r=0.15); // head

// Hands and feet
color(body_color) {
  translate([3.3008, -0.1829, 0.4448]) sphere(r=0.04);
  translate([3.5280, -0.1079, 0.0648]) sphere(r=0.04);
  translate([3.0962, -1.0195, 0.2383]) sphere(r=0.055);
  translate([3.3406, -1.0546, 0.0738]) sphere(r=0.055);
}
