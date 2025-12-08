hull(){
    translate([0, 0]) sphere(0.01);
    translate([1, 0]) sphere(0.01);
}
hull(){
    translate([1, 0]) sphere(0.01);
    translate([2, 0]) sphere(0.01);
}
hull(){
    translate([2, 0]) sphere(0.01);
    translate([3, 0]) sphere(0.01);
}
hull(){
    translate([3, 0]) sphere(0.01);
    translate([4, 0]) sphere(0.01);
}
hull(){
    translate([4, 0]) sphere(0.01);
    translate([5, 0]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([40,40,0.01]);