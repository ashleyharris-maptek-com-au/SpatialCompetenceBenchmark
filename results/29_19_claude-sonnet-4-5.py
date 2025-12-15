import sys

# Middle horizontal frame right section - 3 interior bars
print('''union() {
  for(i=[1:3]) {
    translate([i*70, 0, 0]) cube([10, 10, 350]);
  }
}''')
