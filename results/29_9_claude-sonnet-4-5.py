import sys

# Bottom frame back - 5 bars at 60mm spacing
print('''union() {
  for(i=[0:4]) {
    translate([i*60, 0, 0]) cube([10, 10, 370]);
  }
}''')
