hull(){
    translate([0.0170370869, 0.0170370869]) sphere(0.01);
    translate([0.9829629131, 0.275856132]) sphere(0.01);
}
hull(){
    translate([0.9829629131, 0.275856132]) sphere(0.01);
    translate([0.275856132, 0.9829629131]) sphere(0.01);
}
hull(){
    translate([0.275856132, 0.9829629131]) sphere(0.01);
    translate([0.0170370869, 0.0170370869]) sphere(0.01);
}
translate([0,0,-0.01]) color([0.1,0.1,0.1]) cube([1,1,0.01]);