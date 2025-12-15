import sys

# Corner post bottom section (360mm tall to fit in 400x400x50 when laid flat)
print('''$fn=30;
difference() {
  cube([10, 10, 360]);
  translate([5, 5, -1]) cylinder(d=6.5, h=362);
}''')
