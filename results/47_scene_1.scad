// Crime Scene Render - Test 47
$fn = 20; // Colors
stair_color = [0.6, 0.5, 0.4];
body_color = [0.85, 0.65, 0.55];
head_color = [0.9, 0.75, 0.65];
floor_color = [0.35, 0.35, 0.38]; // Capsule module - hull of two spheres
module capsule(p1, p2, r)
{
  hull()
  {
    translate(p1) sphere(r = r);
    translate(p2) sphere(r = r);
  }
}

// Stairs
color(stair_color)
{
  translate([0.15, 0, 1.9]) cube([0.3, 2.0, 0.2], center = true);
  translate([0.44999999999999996, 0, 1.7]) cube([0.3, 2.0, 0.2], center = true);
  translate([0.75, 0, 1.5]) cube([0.3, 2.0, 0.2], center = true);
  translate([1.0499999999999998, 0, 1.2999999999999998]) cube([0.3, 2.0, 0.2], center = true);
  translate([1.3499999999999999, 0, 1.0999999999999999]) cube([0.3, 2.0, 0.2], center = true);
  translate([1.65, 0, 0.9]) cube([0.3, 2.0, 0.2], center = true);
  translate([1.9499999999999997, 0, 0.6999999999999998]) cube([0.3, 2.0, 0.2], center = true);
  translate([2.25, 0, 0.4999999999999999]) cube([0.3, 2.0, 0.2], center = true);
  translate([2.55, 0, 0.29999999999999993]) cube([0.3, 2.0, 0.2], center = true);
  translate([2.8499999999999996, 0, 0.09999999999999995]) cube([0.3, 2.0, 0.2], center = true);
}

// Floor
color(floor_color) translate([2.5, 0, -0.025]) cube([5, 3, 0.05], center = true); // Ragdoll body (capsule-based)
color(body_color)
{
  capsule([2.7862, -0.4577, 0.6800], [2.6202, -0.8188, 0.6452], 0.1); // base to chest
  capsule([2.8086, -0.8789, 0.5819], [2.9303, -0.6337, 0.6480], 0.05); // right_shoulder to right_elbow
  capsule([2.9303, -0.6337, 0.6480], [2.9984, -0.5080, 0.7095], 0.045); // right_elbow to right_wrist
  capsule([2.4399, -0.7169, 0.6593], [2.5586, -0.4586, 0.6845], 0.05); // left_shoulder to left_elbow
  capsule([2.5586, -0.4586, 0.6845], [2.6234, -0.3178, 0.6984], 0.045); // left_elbow to left_wrist
  capsule([2.7862, -0.4577, 0.6800], [2.9698, -0.2826, 0.6832], 0.065); // base to right_hip
  capsule([2.9698, -0.2826, 0.6832], [3.0459, -0.0203, 0.4868], 0.062); // right_hip to right_knee
  capsule([3.0459, -0.0203, 0.4868], [3.0407, 0.0804, 0.2416], 0.056); // right_knee to right_ankle
  capsule([2.7862, -0.4577, 0.6800], [2.7986, -0.2073, 0.7183], 0.065); // base to left_hip
  capsule([2.7986, -0.2073, 0.7183], [2.8490, -0.0005, 0.5202], 0.062); // left_hip to left_knee
  capsule([2.8490, -0.0005, 0.5202], [2.8122, 0.0368, 0.2604], 0.056); // left_knee to left_ankle
  capsule([2.8086, -0.8789, 0.5819], [2.4399, -0.7169, 0.6593], 0.07); // shoulders
  capsule([2.6202, -0.8188, 0.6452], [2.8086, -0.8789, 0.5819], 0.065); // chest to right shoulder
  capsule([2.6202, -0.8188, 0.6452], [2.4399, -0.7169, 0.6593], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([2.6202, -0.8188, 0.6452], [2.4903, -1.1015, 0.6180], 0.055); // neck
color(head_color) translate([2.5119, -1.0544, 0.6226]) sphere(r = 0.15); // head

// Hands and feet
color(body_color)
{
  translate([2.9984, -0.5080, 0.7095]) sphere(r = 0.04);
  translate([2.6234, -0.3178, 0.6984]) sphere(r = 0.04);
  translate([3.0407, 0.0804, 0.2416]) sphere(r = 0.055);
  translate([2.8122, 0.0368, 0.2604]) sphere(r = 0.055);
}
