hull(){
    translate([2.5, 0]) sphere(0.01);
    translate([3, 0.5]) sphere(0.01);
}
hull(){
    translate([3, 2.5]) sphere(0.01);
    translate([2.5, 3]) sphere(0.01);
}
hull(){
    translate([0.5, 3]) sphere(0.01);
    translate([0, 2.5]) sphere(0.01);
}
hull(){
    translate([2.5, 0.5]) sphere(0.01);
    translate([1.5, 0.5]) sphere(0.01);
}
hull(){
    translate([1, 1]) sphere(0.01);
    translate([0.5, 0]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([3,3,0.01]);