bar = 10;
gap = 62;
W = 370;
hole_d = 7;
$fn = 64;
difference()
{
  union()
  {
    for(i = [0:5]) let(x = -W / 2 + i * (bar + gap)) translate([x, -W / 2, 0]) cube([bar, W, bar]);
    for(i = [0:5]) let(y = -W / 2 + i * (bar + gap)) translate([-W / 2, y, 0]) cube([W, bar, bar]);
  }
  for(cx = [-W / 2 + bar / 2, W / 2 -bar / 2]) for(cy = [-W / 2 + bar / 2, W / 2 -bar / 2]) translate([cx, cy, -1])
    cylinder(h = bar + 2, d = hole_d);
}
