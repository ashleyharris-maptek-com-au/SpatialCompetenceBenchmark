// cage_slice.scad (slice 14 placeholder)
// Note: slice index 0..13 used to build height 0..700 mm. This is the final slice (i=13).
interior = 350; slice_h = 50; bar_thick = 10; hole_diam = 6.5; fn = 64;
centersX = [ -170, -85, 0, 85, 170 ]; centersY = [ -170, -85, 0, 85, 170 ]; cornerCenters = [ [-170,-170], [170,-170], [-170,170], [170,170] ];
module grid_slice(){ difference(){ union(){ for (xc in centersX){ translate([ xc - bar_thick/2, -interior/2, 0 ]) cube([ bar_thick, interior, slice_h ], center=false);} for (yc in centersY){ translate([ -interior/2, yc - bar_thick/2, 0 ]) cube([ interior, bar_thick, slice_h ], center=false);} for (cc in cornerCenters){ translate([ cc[0] - bar_thick/2, cc[1] - bar_thick/2, 0 ]) cube([ bar_thick, bar_thick, slice_h ], center=false);} } for (cc in cornerCenters){ translate([ cc[0], cc[1], slice_h/2 ]) cylinder(d=hole_diam, h=slice_h + 2, center=true, $fn=fn);} } }
grid_slice();
