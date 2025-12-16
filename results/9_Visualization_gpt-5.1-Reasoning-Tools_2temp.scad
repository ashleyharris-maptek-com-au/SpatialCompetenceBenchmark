
hull() {
    translate([0.0, 0.0, 0]) cube([0.01, 0.01, 0.01], center=true);
    translate([0.0, 0.0, 0]) cube([0.01, 0.01, 0.01], center=true);
}


translate([0, 0, 0]) linear_extrude(0.01) text("0",size=0.15, halign="center", valign="center");

translate([0, 0, 0]) linear_extrude(0.01) text("1",size=0.15, halign="center", valign="center");
