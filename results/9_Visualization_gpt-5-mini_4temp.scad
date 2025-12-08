
hull() {
    translate([1.0, 1.05, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([1.0, 1.9500000000000002, 0]) cube([0.01, 0.01, 0.01], center=true);
}


hull() {
    translate([1.0, 2.05, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([1.0, 2.95, 0]) cube([0.01, 0.01, 0.01], center=true);
}


hull() {
    translate([1.0, 3.0500000000000003, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([1.0, 3.95, 0]) cube([0.01, 0.01, 0.01], center=true);
}


translate([1, 1, 0]) linear_extrude(0.01) text("0",size=0.15, halign="center", valign="center");

translate([1, 2, 0]) linear_extrude(0.01) text("1",size=0.15, halign="center", valign="center");

translate([1, 3, 0]) linear_extrude(0.01) text("2",size=0.15, halign="center", valign="center");

translate([1, 4, 0]) linear_extrude(0.01) text("3",size=0.15, halign="center", valign="center");
