import sys

# Bottom frame left - 3 interior bars at 70mm spacing
print('''union() {
  for(i=[1:3]) {
    translate([i*70, 0, 0]) cube([10, 10, 350]);
  }
}''')
