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
  capsule([4.3155, 0.5705, 0.1395], [3.9966, 0.8098, 0.1502], 0.1); // base to chest
  capsule([4.1188, 0.9462, 0.0525], [4.3477, 0.7758, 0.0472], 0.05); // right_shoulder to right_elbow
  capsule([4.3477, 0.7758, 0.0472], [4.4726, 0.6831, 0.0447], 0.045); // right_elbow to right_wrist
  capsule([3.9260, 0.6774, 0.2948], [3.9750, 0.5434, 0.1863], 0.05); // left_shoulder to left_elbow
  capsule([3.9750, 0.5434, 0.1863], [3.8919, 0.4928, 0.0648], 0.045); // left_elbow to left_wrist
  capsule([4.3155, 0.5705, 0.1395], [4.5468, 0.4898, 0.0719], 0.065); // base to right_hip
  capsule([4.5468, 0.4898, 0.0719], [4.9300, 0.2449, 0.1033], 0.062); // right_hip to right_knee
  capsule([4.9300, 0.2449, 0.1033], [5.1499, 0.0973, 0.1134], 0.056); // right_knee to right_ankle
  capsule([4.3155, 0.5705, 0.1395], [4.4571, 0.3654, 0.1849], 0.065); // base to left_hip
  capsule([4.4571, 0.3654, 0.1849], [4.8225, 0.0852, 0.1637], 0.062); // left_hip to left_knee
  capsule([4.8225, 0.0852, 0.1637], [5.0091, -0.0955, 0.1112], 0.056); // left_knee to left_ankle
  capsule([4.1188, 0.9462, 0.0525], [3.9260, 0.6774, 0.2948], 0.07); // shoulders
  capsule([3.9966, 0.8098, 0.1502], [4.1188, 0.9462, 0.0525], 0.065); // chest to right shoulder
  capsule([3.9966, 0.8098, 0.1502], [3.9260, 0.6774, 0.2948], 0.065); // chest to left shoulder
}

// Head and neck
color(body_color) capsule([3.9966, 0.8098, 0.1502], [3.7480, 0.9986, 0.1620], 0.055); // neck
color(head_color) translate([3.7894, 0.9672, 0.1601]) sphere(r = 0.15); // head

// Hands and feet
color(body_color)
{
  translate([4.4726, 0.6831, 0.0447]) sphere(r = 0.04);
  translate([3.8919, 0.4928, 0.0648]) sphere(r = 0.04);
  translate([5.1499, 0.0973, 0.1134]) sphere(r = 0.055);
  translate([5.0091, -0.0955, 0.1112]) sphere(r = 0.055);
}
