// face_band.scad reused for left upper band

width = 350;
band_h = 360;
thk = 10;
full_height = 720;
h_bar_count = 9;
h_gap = (full_height - h_bar_count * thk) / (h_bar_count - 1);
v_gap_count = 4;
v_bars = v_gap_count + 1;
v_gap = (width - v_bars * thk) / v_gap_count;
$fn = 32;

module face_band(w=width, bh=band_h, t=thk) {
    union() {
        for (i = [0 : v_bars - 1]) {
            x = i * (t + v_gap);
            translate([x, 0, 0]) cube([t, bh, t]);
        }
        for (j = [0 : h_bar_count - 1]) {
            y_full = j * (t + h_gap);
            if (y_full < bh && (y_full + t) > 0) {
                intersection() {
                    translate([0, y_full, 0]) cube([w, t, t]);
                    translate([0, 0, 0]) cube([w, bh, t]);
                }
            }
        }
    }
}

face_band();
