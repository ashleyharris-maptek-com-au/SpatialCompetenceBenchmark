
hull() {
    translate([1.1, 2.9000000000000004, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([2.9000000000000004, 1.1, 0]) cube([0.01, 0.01, 0.01], center=true);
}


hull() {
    translate([3.2, 1.3, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([6.8, 6.7, 0]) cube([0.01, 0.01, 0.01], center=true);
}


hull() {
    translate([7.3, 7.3, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([12.700000000000001, 12.700000000000001, 0]) cube([0.01, 0.01, 0.01], center=true);
}


translate([1, 3, 0]) linear_extrude(0.01) text("0",size=0.15, halign="center", valign="center");

translate([3, 1, 0]) linear_extrude(0.01) text("1",size=0.15, halign="center", valign="center");

translate([7, 7, 0]) linear_extrude(0.01) text("2",size=0.15, halign="center", valign="center");

translate([13, 13, 0]) linear_extrude(0.01) text("3",size=0.15, halign="center", valign="center");
