positions = [[-180,-180],[-180,-90],[-180,0],[-180,90],[-180,180],[180,-180],[180,-90],[180,0],[180,90],[180,180],[-90,-180],[0,-180],[90,-180],[-90,180],[0,180],[90,180]];
module vert(px,py){
translate([px,py,25])
difference(){
cube([10,10,50],center=true);
if (abs(px)==180 && abs(py)==180){
translate([5,5,0]) cylinder(r=3.25,h=55,$fn=32,center=true);
}
}
}
module hleft(zh){translate([-180,0,zh]) cube([10,370,10],center=true);}
module hright(zh){translate([180,0,zh]) cube([10,370,10],center=true);}
module hfront(zh){translate([0,-180,zh]) cube([370,10,10],center=true);}
module hback(zh){translate([0,180,zh]) cube([370,10,10],center=true);}
for(p=positions){
vert(p[0],p[1]);
}
hleft(5);
hright(5);
hfront(5);
hback(5);