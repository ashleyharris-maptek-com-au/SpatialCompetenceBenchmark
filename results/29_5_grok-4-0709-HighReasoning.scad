difference() {
union() {
translate([67,0,0]) cube([10,350,10]);
translate([139,0,0]) cube([10,350,10]);
translate([211,0,0]) cube([10,350,10]);
translate([283,0,0]) cube([10,350,10]);
h = [36,108,180,252,324];
for (c = h) {
translate([0, c-5,0]) cube([360,10,10]);
}
translate([0,0,0]) cube([5,350,10]);
translate([355,0,0]) cube([5,350,10]);
}
intersection() {
translate([0,175,5]) rotate([90,0,0]) cylinder(h=352, r=3.5, $fn=50, center=true);
translate([0,0,0]) cube([10,350,10]);
}
intersection() {
translate([360,175,5]) rotate([90,0,0]) cylinder(h=352, r=3.5, $fn=50, center=true);
translate([350,0,0]) cube([10,350,10]);
}
}