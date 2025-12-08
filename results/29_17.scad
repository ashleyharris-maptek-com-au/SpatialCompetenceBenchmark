// Part 18: Corner post segment (SE, UPPER)
// Same geometry as generic corner post segment.
bar = 10;
len = 350;
rod_d = 6.5;

module corner_post_segment_350() {
    difference() {
        cube([len, bar, bar], center=false);
        translate([0, bar/2, bar/2])
            rotate([0,90,0])
                cylinder(d=rod_d, h=len, $fn=64);
    }
}

corner_post_segment_350();
