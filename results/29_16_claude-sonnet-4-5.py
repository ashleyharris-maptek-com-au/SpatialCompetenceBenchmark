import sys

# Middle horizontal frame front section - 5 bars
print('''union() {
  for(i=[0:4]) {
    translate([i*60, 0, 0]) cube([10, 10, 370]);
  }
}''')
