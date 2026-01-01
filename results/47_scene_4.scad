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
  capsule([3.6105, 0.2867, 0.1153], [3.8092, -0.0580, 0.1432], 0.1); // base to chest
  capsule([3.6207, -0.1441, 0.1570], [3.6123, -0.1240, 0.1086], 0.05); // right_shoulder to right_elbow
  capsule([3.6123, -0.1240, 0.1086], [3.6895, -0.2518, 0.0648], 0.045); // right_elbow to right_wrist
  capsule([3.9747, 0.0617, 0.1805], [3.8390, 0.3019, 0.1212], 0.05); // left_shoulder to left_elbow
  capsule([3.8390, 0.3019, 0.1212], [3.7689, 0.4288, 0.0648], 0.045); // left_elbow to left_wrist
  capsule([3.6105, 0.2867, 0.1153], [3.4114, 0.4423, 0.0934], 0.065); // base to right_hip
  capsule([3.4114, 0.4423, 0.0934], [3.3967, 0.4613, 0.1473], 0.062); // right_hip to right_knee
  capsule([3.3967, 0.4613, 0.1473], [3.5064, 0.2578, 0.2770], 0.056); // right_knee to right_ankle
  capsule([3.6105, 0.2867, 0.1153], [3.5755, 0.5377, 0.1043], 0.065); // base to left_hip
  capsule([3.5755, 0.5377, 0.1043], [3.3444, 0.9334, 0.1188], 0.062); // left_hip to left_knee
  capsule([3.3444, 0.9334, 0.1188], [3.2120, 1.1626, 0.1051], 0.056); // left_knee to left_ankle
  capsule([3.6207, -0.1441, 0.1570], [3.9747, 0.0617, 0.1805], 0.07); // shoulders
  capsule([3.8092, -0.0580, 0.1432], [3.6207, -0.1441, 0.1570], 0.065); // chest to right shoulder
  capsule([3.8092, -0.0580, 0.1432], [3.9747, 0.0617, 0.1805], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([3.8092, -0.0580, 0.1432], [3.9648, -0.3280, 0.1650], 0.055); // neck
color(head_color) translate([3.9389, -0.2830, 0.1614]) sphere(r = 0.15); // head

// Hands and feet
color(body_color)
{
  translate([3.6895, -0.2518, 0.0648]) sphere(r = 0.04);
  translate([3.7689, 0.4288, 0.0648]) sphere(r = 0.04);
  translate([3.5064, 0.2578, 0.2770]) sphere(r = 0.055);
  translate([3.2120, 1.1626, 0.1051]) sphere(r = 0.055);
}
