// OpenSCAD: One 50 mm-thick slice (370 x 370 x 50) of a 3D printed cage grid
// Grid: 5 bars along X (width 370, cross-section 10x10), 5 bars along Y (length 370), plus 4 corner vertical bars (Z-direction) with M6 clearance holes
// Parameters
t = 10;           // bar thickness (mm), square cross-section 10x10
g = 80;            // gap between adjacent bars (mm)
size = 370;         // outer footprint (X and Y) in mm
height_slice = 50;  // slice thickness along Z (mm)
hole_d = 6.5;     // through-hole diameter for M6 clearance (mm)
hole_r = hole_d/2;

module corner_bar_with_hole(cx, cy){
    // Corner bar: 10x10x50 with through-hole centered in the bar
    difference(){
        translate([cx, cy, 0]) cube([t, t, height_slice]);
        translate([cx + t/2, cy + t/2, 0]) cylinder(h=height_slice, r=hole_r, center=false);
    }
}

module grid_slice(){
    // Bars along Y (vertical strands in X direction)
    for(i=[0,1,2,3,4]){
        x = i*(t + g);
        translate([x, 0, 0]) cube([t, size, height_slice]);
    }
    // Bars along X (horizontal strands in Y direction)
    for(j=[0,1,2,3,4]){
        y = j*(t + g);
        translate([0, y, 0]) cube([size, t, height_slice]);
    }
    // Corner vertical bars with through-holes (Z-direction)
    corner_bar_with_hole(0, 0);           // bottom-left
    corner_bar_with_hole(size - t, 0);    // bottom-right (x=360)
    corner_bar_with_hole(0, size - t);    // top-left (y=360)
    corner_bar_with_hole(size - t, size - t); // top-right (x=360, y=360)
}

// Render one slice at its local origin (0,0,0)
grid_slice();
