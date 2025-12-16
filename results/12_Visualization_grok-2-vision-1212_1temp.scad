hull(){
    translate([0.5, 0.0]) sphere(0.01);
    translate([1.0, 0.5]) sphere(0.01);
}
hull(){
    translate([1.0, 0.5]) sphere(0.01);
    translate([0.5, 1.0]) sphere(0.01);
}
hull(){
    translate([0.5, 1.0]) sphere(0.01);
    translate([0.5, 0.0]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([1,1,0.01]);