import sys

# Corner post top section - position 4
print('''$fn=30;
difference() {
  cube([10, 10, 360]);
  translate([5, 5, -1]) cylinder(d=6.5, h=362);
}''')
