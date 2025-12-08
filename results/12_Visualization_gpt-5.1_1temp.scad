hull(){
    translate([0.05, 0.05]) sphere(0.01);
    translate([0.5, 0.9]) sphere(0.01);
}
hull(){
    translate([0.5, 0.9]) sphere(0.01);
    translate([0.95, 0.05]) sphere(0.01);
}
hull(){
    translate([0.95, 0.05]) sphere(0.01);
    translate([0.05, 0.05]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([1,1,0.01]);