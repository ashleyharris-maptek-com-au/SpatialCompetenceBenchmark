// Cage slice - index 9
bar = 10;
outer = 350;
half = outer / 2;
height = 700;

N_xy = 6;
N_z  = 11;

x_spacing = (outer - bar) / (N_xy - 1);
z_spacing = (height - bar) / (N_z  - 1);

xs = [ for (i = [0 : N_xy - 1]) (-half + bar/2 + i * x_spacing) ];
ys = xs;

zs = [ for (k = [0 : N_z - 1]) (bar/2 + k * z_spacing) ];

$fn = 64;

module cage_bars() {
    union() {
        // Vertical bars on front and back faces
        for (xv = xs) {
            translate([xv, -half + bar/2, height/2])
                cube([bar, bar, height], center = true);
            translate([xv,  half - bar/2, height/2])
                cube([bar, bar, height], center = true);
        }

        // Vertical bars on left and right faces
        for (yv = ys) {
            translate([-half + bar/2, yv, height/2])
                cube([bar, bar, height], center = true);
            translate([ half - bar/2, yv, height/2])
                cube([bar, bar, height], center = true);
        }

        // Horizontal x-bars on front and back faces
        for (zv = zs) {
            translate([0, -half + bar/2, zv])
                cube([outer, bar, bar], center = true);
            translate([0,  half - bar/2, zv])
                cube([outer, bar, bar], center = true);
        }

        // Horizontal y-bars on left and right faces
        for (zv = zs) {
            translate([-half + bar/2, 0, zv])
                cube([bar, outer, bar], center = true);
            translate([ half - bar/2, 0, zv])
                cube([bar, outer, bar], center = true);
        }

        // Floor and ceiling extra x-bars at all y positions
        z_floor = bar/2;
        z_ceil  = height - bar/2;
        for (yv = ys) {
            translate([0, yv, z_floor])
                cube([outer, bar, bar], center = true);
            translate([0, yv, z_ceil])
                cube([outer, bar, bar], center = true);
        }

        // Floor and ceiling extra y-bars at all x positions
        for (xv = xs) {
            translate([xv, 0, z_floor])
                cube([bar, outer, bar], center = true);
            translate([xv, 0, z_ceil])
                cube([bar, outer, bar], center = true);
        }
    }
}

module corner_holes() {
    hole_d = 7;
    for (sx = [-1, 1])
        for (sy = [-1, 1])
            translate([sx * (half - bar/2), sy * (half - bar/2), height/2])
                cylinder(h = height + 2, d = hole_d, center = true);
}

module cage_full() {
    difference() {
        cage_bars();
        corner_holes();
    }
}

slice_index = 9;
slice_height = 50;

module cage_slice() {
    translate([0, 0, -slice_index * slice_height]) {
        intersection() {
            cage_full();
            translate([0, 0, slice_index * slice_height + slice_height/2])
                cube([outer + 20, outer + 20, slice_height], center = true);
        }
    }
}

cage_slice();
