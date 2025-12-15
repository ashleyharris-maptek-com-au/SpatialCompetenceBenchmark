$fn=60;
module spacer_layer() {
    h = 39.375;
    difference() {
        union() {
            for (x = [-180, 180]) for (y = [-180, 180]) translate([x - 5, y - 5, 0]) cube([10, 10, h]);
        }
        for (x = [-180, 180]) for (y = [-180, 180]) translate([x, y, -1]) cylinder(d=7, h=h + 2);
    }
}
spacer_layer();