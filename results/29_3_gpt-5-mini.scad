// column_half.scad (corner: -x, -y, upper)

length = 360;
thk = 10;
hole_d = 7; // clearance for M6
$fn = 64;

module column_segment(len=length, t=thk, hd=hole_d) {
    difference() {
        translate([0,0,0]) cube([len, t, t]);
        translate([len/2, t/2, t/2]) rotate([0,90,0]) cylinder(r=hd/2, h=len + 20, $fn=$fn);
    }
}

column_segment();
