// face_band.scad
// A face band (350 x 360 x 10) with a rectangular grid of 10 mm square bars
// Model coordinates: X = 350 (width), Y = 360 (band height), Z = 10 (thickness). The part lies flat on Z=0.

width = 350;
band_h = 360; // half the full 720 height
thk = 10;

// horizontal full-face spacing is computed for the full 720 mm height (so that two bands align)
full_height = 720;
h_bar_count = 9; // number of horizontal bars across full height (bars = h_bar_count)
h_gap = (full_height - h_bar_count * thk) / (h_bar_count - 1); // 78.75 mm

// vertical spacing across the 350 mm internal width
v_gap_count = 4; // number of gaps
v_bars = v_gap_count + 1; // 5 bars
v_gap = (width - v_bars * thk) / v_gap_count; // 75 mm

$fn = 32;

module face_band(w=width, bh=band_h, t=thk) {
    union() {
        // bounding band box (we will place bars inside this)
        // vertical bars (along Y direction for the band)
        for (i = [0 : v_bars - 1]) {
            x = i * (t + v_gap);
            translate([x, 0, 0]) cube([t, bh, t]);
        }

        // horizontal bars: they are placed as if across full 720 height, then the band is the subset
        for (j = [0 : h_bar_count - 1]) {
            y_full = j * (t + h_gap); // This is the Y location along the full 720 height
            // include the portion of that bar that overlaps this band (band is from y=0..bh in local coordinates)
            // We'll compute overlap
            if (y_full < bh && (y_full + t) > 0) {
                // portion within this band's local Y span
                y_local = max(0, y_full);
                // For simplicity we place the bar limited to the band extents by intersection with a crop cube
                intersection() {
                    translate([0, y_full, 0]) cube([w, t, t]);
                    translate([0, 0, 0]) cube([w, bh, t]);
                }
            }
        }
    }
}

face_band();
