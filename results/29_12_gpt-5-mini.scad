// square_panel.scad
// Top/bottom full square grid panel 370 x 370 x 10 (sits on Z=0 in the model). This is intended for top and bottom.

size = 370;
thk = 10;
bar = 10;
// attempt to space vertical bars at about 75 mm where possible; we repeat bar+gap until coverage and crop to size
v_gap = 75; // approximate spacing
$fn = 64;

module square_grid(sz=size, t=thk, b=bar, gap=v_gap) {
    union() {
        // vertical bars along Y
        x = 0;
        while (x < sz) {
            translate([x, 0, 0]) cube([b, sz, t]);
            x = x + b + gap;
        }
        // horizontal bars along X
        y = 0;
        while (y < sz) {
            translate([0, y, 0]) cube([sz, b, t]);
            y = y + b + gap;
        }
    }
}

square_grid();
