difference() {
    cube([350, 10, 10]);
    translate([0, 5, 5])
        rotate([0, 90, 0])
            cylinder(h=350, r=3.3, $fn=32);
}