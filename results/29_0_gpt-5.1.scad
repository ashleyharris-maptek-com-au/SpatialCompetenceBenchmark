// Cage with internal size 350 x 350 x 700 mm
// Bars: 10x10 mm square
// Approx-uniform grid: 75 mm gaps in X/Y, ~75 mm in Z (top cell 25 mm)
// 4 x M6 threaded rod clearance holes in corner vertical bars (6.5mm dia)

$fn = 64; // smooth rod holes

inner_x = 350;
inner_y = 350;
inner_z = 700;
bar = 10; // bar thickness (square)

// Internal cavity extents
ix_min = -inner_x / 2;
ix_max = inner_x / 2;
iy_min = -inner_y / 2;
iy_max = inner_y / 2;
iz_min = 0;
iz_max = inner_z; // Horizontal spacing (X,Y) chosen to make 4 equal gaps of 75 mm
Gxy = 75; // From earlier derivation: 5 bars per side
// X bar ranges:
// [-175,-165], [-90,-80], [-5,5], [80,90], [165,175]
xbars = [[ix_min, ix_min + bar], // -175 to -165
[ix_min + bar + Gxy, ix_min + bar + Gxy + bar], // -90 to -80
[ix_min + 2 * (bar + Gxy), ix_min + 2 * (bar + Gxy) + bar], // -5 to 5
[ix_min + 3 * (bar + Gxy), ix_min + 3 * (bar + Gxy) + bar], // 80 to 90
[ix_max -bar, ix_max] // 165 to 175
];

ybars = xbars; // symmetric in Y

// Vertical spacing for horizontal bar planes along Z
Gz = 75; // nominal
// Z levels where horizontal beams lie (bottom included at 0)
z_levels = [0:Gz:675]; // 0,75,...,675

rod_d = 6.5; // clearance for M6 rods
rod_r = rod_d / 2;

module vertical_bars()
{
  // Place vertical bars at every intersection of xbars and ybars
  for(xb = xbars) for(yb = ybars)
  {
    translate([(xb[0] + xb[1]) / 2, (yb[0] + yb[1]) / 2, (iz_min + iz_max) / 2])
      cube([bar, bar, inner_z], center = true);
  }
}

module horizontal_x_bars_at_z(z)
{
  // Bars running along X, positioned at each ybar
  for(yb = ybars)
  {
    translate([0, (yb[0] + yb[1]) / 2, z + bar / 2]) cube([inner_x, bar, bar], center = true);
  }
}

module horizontal_y_bars_at_z(z)
{
  // Bars running along Y, positioned at each xbar
  for(xb = xbars)
  {
    translate([(xb[0] + xb[1]) / 2, 0, z + bar / 2]) cube([bar, inner_y, bar], center = true);
  }
}

module horizontal_bars()
{
  // At each z level, add a full X and Y grid layer
  for(z = z_levels)
  {
    horizontal_x_bars_at_z(z);
    horizontal_y_bars_at_z(z);
  }
}

module rod_holes()
{
  // Corner bar centers:
  // corners at combinations of xbars[0], xbars[4], ybars[0], ybars[4]
  corner_x = [(xbars[0][0] + xbars[0][1]) / 2, (xbars[4][0] + xbars[4][1]) / 2];
  corner_y = [(ybars[0][0] + ybars[0][1]) / 2, (ybars[4][0] + ybars[4][1]) / 2];

  for(cx = corner_x) for(cy = corner_y)
  {
    translate([cx, cy, inner_z / 2]) cylinder(h = inner_z + 2 * bar, r = rod_r, center = true);
  }
}

module cage()
{
  difference()
  {
    union()
    {
      vertical_bars();
      horizontal_bars();
    }
    rod_holes();
  }
}

// Final object: cage centered in X/Y, sitting on z=0 plane
cage();
