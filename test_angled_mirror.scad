// Room visualization
color([0.8, 0.8, 0.8, 0.3]) translate([0, 0, -0.05]) cube([10, 8, 0.05]);
// Angled Mirror
color([0.3, 0.5, 1.0, 0.5]) translate([5, 0, 1.5]) rotate([0, 0, -45.0]) cube([0.05, 10, 3], center=true);
// Vase
color([0.6, 0.6, 0.6]) translate([2, 2, 0.7]) cylinder(r1=0.15, r2=0.25, h=0.6, $fn=24);
color([1, 0, 0]) translate([2, 2, 1.5]) linear_extrude(0.01) text("Vase", size=0.3, halign="center");
// Clock
color([0.6, 0.6, 0.6]) translate([8, 1, 2]) cylinder(r=0.3, h=0.05, $fn=24);
color([1, 0, 0]) translate([8, 1, 2.5]) linear_extrude(0.01) text("Clock", size=0.3, halign="center");
// Viewer
color([0.9, 0.7, 0.5]) translate([3, 6, 0]) cylinder(r=0.15, h=1.2, $fn=16);
color([0.9, 0.7, 0.5]) translate([3, 6, 1.4]) sphere(r=0.2, $fn=16);
color([1, 0, 0]) translate([3, 6, 1.7]) linear_extrude(0.01) text("YOU", size=0.4, halign="center");
