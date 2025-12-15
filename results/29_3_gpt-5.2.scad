// cage_side_yneg.scad
// Generates one 50mm-tall side band for the -Y wall.
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

module side_band_y(){
    union(){
        translate([0, 0, 0]) corner_block();
        translate([outer-bar, 0, 0]) corner_block();
        translate([bar, 0, 0]) cube([outer-2*bar, bar, bar], center=false);
        translate([bar, 0, segH-bar]) cube([outer-2*bar, bar, bar], center=false);
        x0 = bar;
        maxX = outer - bar;
        L = inner;
        n = floor((L + gap) / (bar + gap));
        for (k=[0:n]){
            x = x0 + k*(bar+gap);
            if (x+bar <= maxX+1e-6){
                translate([x, 0, 0]) cube([bar, bar, segH], center=false);
            }
        }
    }
}

side_band_y();
