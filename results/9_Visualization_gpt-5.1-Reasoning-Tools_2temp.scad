
hull() {
    translate([1.0, 1.0, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([1.0, 1.0, 0]) cube([0.01, 0.01, 0.01], center=true);
}


translate([1, 1, 0]) linear_extrude(0.01) text("0",size=0.15, halign="center", valign="center");

translate([1, 1, 0]) linear_extrude(0.01) text("1",size=0.15, halign="center", valign="center");
