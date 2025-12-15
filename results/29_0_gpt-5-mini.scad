// column_half.scad
// A single corner vertical segment, printed lying flat
// Model coordinates: X=length (360), Y=thickness (10), Z=thickness (10)
// The part sits on Z=0 (no height below Z=0). Hole runs along X-axis centered in Y/Z.

length = 360;
thk = 10;
hole_d = 7; // clearance for M6
$fn = 64;

module column_segment(len=length, t=thk, hd=hole_d) {
    difference() {
        // block
        translate([0,0,0]) cube([len, t, t]);
        // hole along X (rotate cylinder to X-axis)
        translate([len/2, t/2, t/2]) rotate([0,90,0]) cylinder(r=hd/2, h=len + 20, $fn=$fn);
    }
}

column_segment();
