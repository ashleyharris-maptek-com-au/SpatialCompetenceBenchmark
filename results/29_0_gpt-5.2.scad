// cage_side_xpos.scad
// Generates one 50mm-tall side band for the +X wall.
// Print orientation: lies flat on z=0, thickness in +Z.
// Parameters
bar = 10; // bar thickness (square)
inner = 350; // internal span in Y for this wall
segH = 50; // segment height
holeD = 6.6; // clearance for M6 threaded rod
// grid parameters (uniform)
gap = 80; // uniform gap between vertical bars (50-100 ok)
// Derived
outer = inner + 2 * bar; // total length including corner bars

module corner_block()
{
  // 10x10 corner post section for this 50mm band, with rod hole
  difference()
  {
    cube([bar, bar, segH], center = false);
    translate([bar / 2, bar / 2, 0]) cylinder(d = holeD, h = segH, $fn = 40);
  }
}

module side_band_x()
{
  // Local coordinates:
  // X thickness is bar (0..bar)
  // Y runs along wall length (0..outer)
  // Z height (0..segH)

  union()
  {
    // corner blocks at both ends
    translate([0, 0, 0]) corner_block();
    translate([0, outer -bar, 0]) corner_block()
      ; // horizontal bars (bottom and top of this band) across between corner blocks
    // bottom
    translate([0, bar, 0]) cube([bar, outer -2 * bar, bar], center = false); // top
    translate([0, bar, segH -bar]) cube([bar, outer -2 * bar, bar], center = false)
      ; // vertical grid bars in this band (including those adjacent to corners already accounted by corner blocks)
    // Place vertical bars of 10mm width along Y with uniform gaps = gap.
    // Clear internal span is inner (between inside faces of corner posts).
    // Along Y from bar to outer-bar.
    // We start with a bar at y=bar, then gap, etc.
    y0 = bar;
    maxY = outer -bar; // compute how many bars fit with gap
    // pattern: bar, gap, bar, gap, ... , bar
    // available length L = maxY - y0 = inner
    L = inner;
    n = floor((L + gap) / (bar + gap))
      ; // Recompute to distribute uniformly: keep requested gap if exact fit; here chosen to fit nicely.
    for(k = [0:n])
    {
      y = y0 + k * (bar + gap);
      if(y + bar <= maxY + 1e-6)
      {
        translate([0, y, 0]) cube([bar, bar, segH], center = false);
      }
    }
  }
}

side_band_x();
