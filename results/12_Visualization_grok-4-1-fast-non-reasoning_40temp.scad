hull(){
    translate([20.0, 19.9]) sphere(0.01);
    translate([21.0, 19.9]) sphere(0.01);
}
hull(){
    translate([21.0, 20.0]) sphere(0.01);
    translate([20.1, 20.0]) sphere(0.01);
}
hull(){
    translate([20.1, 20.1]) sphere(0.01);
    translate([20.9, 20.1]) sphere(0.01);
}
hull(){
    translate([20.9, 19.9]) sphere(0.01);
    translate([22.0, 19.9]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([40,40,0.01]);