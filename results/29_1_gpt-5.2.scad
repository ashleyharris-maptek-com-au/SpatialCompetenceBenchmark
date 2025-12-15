// cage_side_xneg.scad
// Generates one 50mm-tall side band for the -X wall.
bar = 10;
inner = 350;
segH = 50;
holeD = 6.6;
gap = 80;
outer = inner + 2*bar;

module corner_block(){
    difference(){
        cube([bar, bar, segH], center=false);
        translate([bar/2, bar/2, 0]) cylinder(d=holeD, h=segH, $fn=40);
    }
}

module side_band_x(){
    union(){
        translate([0, 0, 0]) corner_block();
        translate([0, outer-bar, 0]) corner_block();
        translate([0, bar, 0]) cube([bar, outer-2*bar, bar], center=false);
        translate([0, bar, segH-bar]) cube([bar, outer-2*bar, bar], center=false);
        y0 = bar;
        maxY = outer - bar;
        L = inner;
        n = floor((L + gap) / (bar + gap));
        for (k=[0:n]){
            y = y0 + k*(bar+gap);
            if (y+bar <= maxY+1e-6){
                translate([0, y, 0]) cube([bar, bar, segH], center=false);
            }
        }
    }
}

side_band_x();
