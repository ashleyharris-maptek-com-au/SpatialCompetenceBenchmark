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
  capsule([3.0927, 1.2276, 0.0977], [2.7206, 1.3691, 0.1232], 0.1); // base to chest
  capsule([2.8118, 1.5557, 0.1278], [3.0732, 1.4535, 0.0842], 0.05); // right_shoulder to right_elbow
  capsule([3.0732, 1.4535, 0.0842], [3.2128, 1.3972, 0.0448], 0.045); // right_elbow to right_wrist
  capsule([2.6693, 1.1736, 0.1698], [2.9275, 1.0720, 0.1159], 0.05); // left_shoulder to left_elbow
  capsule([2.9275, 1.0720, 0.1159], [3.0633, 1.0160, 0.0646], 0.045); // left_elbow to left_wrist
  capsule([3.0927, 1.2276, 0.0977], [3.3450, 1.2325, 0.0729], 0.065); // base to right_hip
  capsule([3.3450, 1.2325, 0.0729], [3.7719, 1.0768, 0.1091], 0.062); // right_hip to right_knee
  capsule([3.7719, 1.0768, 0.1091], [4.0205, 0.9850, 0.1200], 0.056); // right_knee to right_ankle
  capsule([3.0927, 1.2276, 0.0977], [3.2790, 1.0554, 0.0924], 0.065); // base to left_hip
  capsule([3.2790, 1.0554, 0.0924], [3.7069, 0.8988, 0.1233], 0.062); // left_hip to left_knee
  capsule([3.7069, 0.8988, 0.1233], [3.9553, 0.8066, 0.1279], 0.056); // left_knee to left_ankle
  capsule([2.8118, 1.5557, 0.1278], [2.6693, 1.1736, 0.1698], 0.07); // shoulders
  capsule([2.7206, 1.3691, 0.1232], [2.8118, 1.5557, 0.1278], 0.065); // chest to right shoulder
  capsule([2.7206, 1.3691, 0.1232], [2.6693, 1.1736, 0.1698], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([2.7206, 1.3691, 0.1232], [2.4293, 1.4799, 0.1431], 0.055); // neck
color(head_color) translate([2.4779, 1.4614, 0.1398]) sphere(r=0.15); // head

// Hands and feet
color(body_color) {
  translate([3.2128, 1.3972, 0.0448]) sphere(r=0.04);
  translate([3.0633, 1.0160, 0.0646]) sphere(r=0.04);
  translate([4.0205, 0.9850, 0.1200]) sphere(r=0.055);
  translate([3.9553, 0.8066, 0.1279]) sphere(r=0.055);
}
