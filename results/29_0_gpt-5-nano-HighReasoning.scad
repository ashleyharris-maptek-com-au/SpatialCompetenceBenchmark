// cage_slice.scad
// OpenSCAD model for one 50 mm-thick horizontal slice of a 350x350 cage interior
// 14 slices total will be stacked to reach 700 mm height.
// Grid: 5 bars along X (Y-oriented bars) and 5 bars along Y (X-oriented bars) with 10x10 mm cross section,
// resulting in 75 mm clear gaps between adjacent bars within the 350x350 interior.
// Corner vertical posts (4) are included at the slice corners; rods pass through middle of these posts.
// Holes for 4x M6 rods are drilled through the center of each corner post at mid-height of this slice.

// Global constants (adjust as needed)
interior = 350; // inner square dimension in mm
slice_h  = 50;  // slice thickness in mm (print height per piece)
bar_thick = 10; // bar cross-section thickness (square)
hole_diam = 6.5; // hole diameter for M6 clearance (mm)
fn = 64; // roundness for nicer holes

// Coordinates for grid centers
centersX = [ -170, -85, 0, 85, 170 ]; // centers of vertical bars (bars along Y)
centersY = [ -170, -85, 0, 85, 170 ]; // centers of horizontal bars (bars along X)

// Corner posts (centers)
cornerCenters = [ [-170,-170], [170,-170], [-170,170], [170,170] ];

module grid_slice(){
    // Base: 350x350x50 block served by the union of bars; holes will be subtracted via difference
    difference() {
        union() {
            // 5 bars along Y (oriented in Y), positioned at X centers
            for (xc in centersX) {
                translate([ xc - bar_thick/2, -interior/2, 0 ])
                    cube([ bar_thick, interior, slice_h ], center=false);
            }
            // 5 bars along X (oriented in X), positioned at Y centers
            for (yc in centersY) {
                translate([ -interior/2, yc - bar_thick/2, 0 ])
                    cube([ interior, bar_thick, slice_h ], center=false);
            }
            // 4 corner posts (vertical bars) at slice corners
            for (cc in cornerCenters) {
                translate([ cc[0] - bar_thick/2, cc[1] - bar_thick/2, 0 ])
                    cube([ bar_thick, bar_thick, slice_h ], center=false);
            }
        }
        // Holes for M6 rods through each corner post (mid-height of slice)
        for (cc in cornerCenters) {
            translate([ cc[0], cc[1], slice_h/2 ])
                rotate([0,0,0])
                    cylinder(d=hole_diam, h=slice_h + 2, center=true, $fn=fn);
        }
    }
}

// Render slice
grid_slice();
