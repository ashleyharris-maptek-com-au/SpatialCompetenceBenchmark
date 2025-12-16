
hull() {
    translate([1.1, 2.9000000000000004, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([2.9000000000000004, 1.1, 0]) cube([0.01, 0.01, 0.01], center=true);
}


hull() {
    translate([3.0, 1.4, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([3.0, 8.6, 0]) cube([0.01, 0.01, 0.01], center=true);
}


hull() {
    translate([3.3000000000000003, 8.7, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([8.7, 3.3000000000000003, 0]) cube([0.01, 0.01, 0.01], center=true);
}


translate([1, 3, 0]) linear_extrude(0.01) text("0",size=0.15, halign="center", valign="center");

translate([3, 1, 0]) linear_extrude(0.01) text("1",size=0.15, halign="center", valign="center");

translate([3, 9, 0]) linear_extrude(0.01) text("2",size=0.15, halign="center", valign="center");

translate([9, 3, 0]) linear_extrude(0.01) text("3",size=0.15, halign="center", valign="center");
