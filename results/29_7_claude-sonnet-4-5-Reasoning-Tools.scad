union() {
    for (x = [0, 90, 180, 270, 340]) {
        translate([x, 0, 0])
            cube([10, 360, 10]);
    }
    for (y = [0, 90, 180, 270]) {
        translate([0, y, 0])
            cube([350, 10, 10]);
    }
}