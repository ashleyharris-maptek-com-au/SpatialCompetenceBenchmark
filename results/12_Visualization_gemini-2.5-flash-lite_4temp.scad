hull(){
    translate([30, 0]) sphere(0.01);
    translate([30, 1]) sphere(0.01);
}
hull(){
    translate([1, 30]) sphere(0.01);
    translate([0, 30]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([4,4,0.01]);