// Cage slice 12
// Internal cavity: 350 x 350 x 700 mm
// Bar thickness: 10 mm (square)
// Gap between bars: 70 mm (uniform)
// Slice index: 12, slice Z range: [600, 650] (local coordinates 0..50)
// This file places the slice with its bottom on Z=0; when assembling, translate in Z by 600 mm.
// Export to STL with OpenSCAD: Render -> Export as STL.

bar = 10;
gap = 70;
s = bar + gap;
$fn = 64;  // cylinder resolution

x_centers = [-160, -80, 0, 80, 160];
y_centers = [-160, -80, 0, 80, 160];
z_centers = [5, 85, 165, 245, 325, 405, 485, 565, 645];

slice_index = 12;
slice_h = 50;

front_y = 180;
back_y = -180;
left_x = -180;
right_x = 180;
panel_length = 370;

hole_diam = 6.6;

module slice() {
    union() {
        // vertical bars on front and back (along Z)
        for (x = x_centers) {
            translate([x, front_y, slice_h/2]) cube([bar, bar, slice_h], center=true);
            translate([x, back_y, slice_h/2])  cube([bar, bar, slice_h], center=true);
        }
        // vertical bars on left and right (along Z)
        for (y = y_centers) {
            translate([left_x, y, slice_h/2])  cube([bar, bar, slice_h], center=true);
            translate([right_x, y, slice_h/2]) cube([bar, bar, slice_h], center=true);
        }
        // explicit corner vertical bars (ensure 4 corners for M6 rods)
        translate([-180, 180, slice_h/2]) cube([bar, bar, slice_h], center=true);
        translate([180, 180, slice_h/2]) cube([bar, bar, slice_h], center=true);
        translate([-180, -180, slice_h/2]) cube([bar, bar, slice_h], center=true);
        translate([180, -180, slice_h/2]) cube([bar, bar, slice_h], center=true);

        // horizontal bars (10 mm thick in Z) that lie inside this slice
        for (zc = z_centers) {
            z_local = zc - slice_index*slice_h;
            // include this horizontal bar if its center lies within this slice and it fits entirely here
            if (z_local >= bar/2 && z_local <= slice_h - bar/2) {
                // front and back horizontal bars (run along X)
                translate([0, front_y, z_local]) cube([panel_length, bar, bar], center=true);
                translate([0, back_y,  z_local]) cube([panel_length, bar, bar], center=true);
                // left and right horizontal bars (run along Y)
                translate([left_x, 0, z_local]) cube([bar, panel_length, bar], center=true);
                translate([right_x,0, z_local]) cube([bar, panel_length, bar], center=true);
            }
        }
    }
}

difference() {
    slice();
    // four vertical holes for M6 rods through corner bars (slightly longer than slice to ensure clean subtraction)
    translate([-180, 180, slice_h/2]) rotate([0,0,0]) cylinder(h = slice_h*4, r = hole_diam/2, center=true);
    translate([180, 180, slice_h/2]) rotate([0,0,0]) cylinder(h = slice_h*4, r = hole_diam/2, center=true);
    translate([-180, -180, slice_h/2]) rotate([0,0,0]) cylinder(h = slice_h*4, r = hole_diam/2, center=true);
    translate([180, -180, slice_h/2]) rotate([0,0,0]) cylinder(h = slice_h*4, r = hole_diam/2, center=true);
}

slice();
