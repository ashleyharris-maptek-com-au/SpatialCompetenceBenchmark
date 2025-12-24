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
  capsule([5.1243, -0.0594, 0.0953], [5.0102, 0.3218, 0.1232], 0.1); // base to chest
  capsule([5.2111, 0.3599, 0.1595], [5.2922, 0.0961, 0.1007], 0.05); // right_shoulder to right_elbow
  capsule([5.2922, 0.0961, 0.1007], [5.3361, -0.0423, 0.0448], 0.045); // right_elbow to right_wrist
  capsule([4.8183, 0.2440, 0.1380], [4.8269, 0.2238, 0.0892], 0.05); // left_shoulder to left_elbow
  capsule([4.8269, 0.2238, 0.0892], [4.7869, 0.3675, 0.0448], 0.045); // left_elbow to left_wrist
  capsule([5.1243, -0.0594, 0.0953], [5.2825, -0.2573, 0.0837], 0.065); // base to right_hip
  capsule([5.2825, -0.2573, 0.0837], [5.4104, -0.6956, 0.1077], 0.062); // right_hip to right_knee
  capsule([5.4104, -0.6956, 0.1077], [5.4854, -0.9499, 0.1056], 0.056); // right_knee to right_ankle
  capsule([5.1243, -0.0594, 0.0953], [5.1004, -0.3110, 0.0735], 0.065); // base to left_hip
  capsule([5.1004, -0.3110, 0.0735], [5.1045, -0.3347, 0.1274], 0.062); // left_hip to left_knee
  capsule([5.1045, -0.3347, 0.1274], [5.0325, -0.1152, 0.2574], 0.056); // left_knee to left_ankle
  capsule([5.2111, 0.3599, 0.1595], [4.8183, 0.2440, 0.1380], 0.07); // shoulders
  capsule([5.0102, 0.3218, 0.1232], [5.2111, 0.3599, 0.1595], 0.065); // chest to right shoulder
  capsule([5.0102, 0.3218, 0.1232], [4.8183, 0.2440, 0.1380], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([5.0102, 0.3218, 0.1232], [4.9209, 0.6203, 0.1451], 0.055); // neck
color(head_color) translate([4.9358, 0.5706, 0.1415]) sphere(r=0.15); // head

// Hands and feet
color(body_color) {
  translate([5.3361, -0.0423, 0.0448]) sphere(r=0.04);
  translate([4.7869, 0.3675, 0.0448]) sphere(r=0.04);
  translate([5.4854, -0.9499, 0.1056]) sphere(r=0.055);
  translate([5.0325, -0.1152, 0.2574]) sphere(r=0.055);
}
