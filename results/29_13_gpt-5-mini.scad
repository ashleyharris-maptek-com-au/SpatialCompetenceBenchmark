// square_panel.scad reused for bottom panel

size = 370;
thk = 10;
bar = 10;
v_gap = 75;
$fn = 64;

module square_grid(sz=size, t=thk, b=bar, gap=v_gap) {
    union() {
        x = 0;
        while (x < sz) {
            translate([x, 0, 0]) cube([b, sz, t]);
            x = x + b + gap;
        }
        y = 0;
        while (y < sz) {
            translate([0, y, 0]) cube([sz, b, t]);
            y = y + b + gap;
        }
    }
}

square_grid();
