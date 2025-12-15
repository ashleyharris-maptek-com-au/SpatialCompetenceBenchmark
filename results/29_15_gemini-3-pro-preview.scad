$fn=60;
module grid_frame() {
    difference() {
        union() {
            for (y = [-180 : 90 : 180]) translate([-185, y - 5, 0]) cube([370, 10, 10]);
            for (x = [-180 : 90 : 180]) translate([x - 5, -185, 0]) cube([10, 370, 10]);
        }
        for (hx = [-180, 180]) for (hy = [-180, 180]) translate([hx, hy, -1]) cylinder(d=7, h=12);
    }
}
grid_frame();