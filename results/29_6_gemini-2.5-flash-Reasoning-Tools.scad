// Part Name: Cage_Layer_6_H50mm
// This part represents a horizontal slice of the cage.
// It is designed to be 3D printed on its base.

// Parameters for the cage
bar_t = 10;
gap_xy = 80;
hole_d = 7;
cage_ext_xy = 370;

// Calculate bar center positions relative to the overall cage center
bar_centers_xy = [for (j = [0:4]) (-cage_ext_xy/2 + bar_t/2 + j * (bar_t + gap_xy))];

// Module to generate a single layer segment
module cage_layer_segment(height) {
    // Offset for printing on z=0 plane. The module itself is centered on XY=0, so this Z offset moves its base to Z=0.
    translate([0, 0, height/2]) {
        union() {
            // Horizontal bars (along X)
            for (y_center = bar_centers_xy) {
                translate([0, y_center, 0])
                cube([cage_ext_xy, bar_t, height], center = true);
            }

            // Vertical bars (along Y)
            for (x_center = bar_centers_xy) {
                translate([x_center, 0, 0])
                cube([bar_t, cage_ext_xy, height], center = true);
            }

            // Subtract holes for M6 rods at the 4 corners
            corner_offsets_xy = [bar_centers_xy[0], bar_centers_xy[4]];

            for (x_offset = corner_offsets_xy) {
                for (y_offset = corner_offsets_xy) {
                    // Hole through the center of the corner bar
                    translate([x_offset, y_offset, 0])
                    cylinder(h = height + 0.1, d = hole_d, center = true, $fn=32); // +0.1 for clean cut
                }
            }
        }
    }
}

// Render the segment
cage_layer_segment(50);