// Cage slice part (z0..z1). Units: mm.
// Print orientation: normal

bar=10;
inner=[350,350,700];
gap_xy=62;
gap_z=61;
hole_d=6.8;
$fn=64;

outer=[inner[0]+2*bar, inner[1]+2*bar, inner[2]+2*bar];
half=[outer[0]/2, outer[1]/2, outer[2]/2];

pitch_xy=bar+gap_xy;
pitch_z=bar+gap_z;

centers=[for(i=[0:5]) -(half[0]-bar/2) + i*pitch_xy];
z_levels=[for(i=[0:10]) i*pitch_z];

module vbar(xc,yc){ translate([xc-bar/2,yc-bar/2,0]) cube([bar,bar,outer[2]],center=false); }
module hbar_x(yc,z0){ translate([-half[0],yc-bar/2,z0]) cube([outer[0],bar,bar],center=false); }
module hbar_y(xc,z0){ translate([xc-bar/2,-half[1],z0]) cube([bar,outer[1],bar],center=false); }

module grid(z0){ union(){ for(yc=centers) hbar_x(yc,z0); for(xc=centers) hbar_y(xc,z0); } }

module side_verticals(){
  union(){
    for(xc=centers){ vbar(xc, half[1]-bar/2); vbar(xc,-half[1]+bar/2); }
    for(yc=centers){ vbar( half[0]-bar/2,yc); vbar(-half[0]+bar/2,yc); }
  }
}

module side_rings(){
  union(){
    for(z0=z_levels){
      hbar_x( half[1]-bar/2,z0); hbar_x(-half[1]+bar/2,z0);
      hbar_y( half[0]-bar/2,z0); hbar_y(-half[0]+bar/2,z0);
    }
  }
}

module rod_holes(){
  for(sx=[-1,1],sy=[-1,1]) translate([sx*(half[0]-bar/2), sy*(half[1]-bar/2), -1]) cylinder(d=hole_d,h=outer[2]+2,center=false);
}

module cage(){ difference(){ union(){ side_verticals(); side_rings(); grid(0); grid(outer[2]-bar); } rod_holes(); } }

module cage_slice(zmin,zmax){ intersection(){ cage(); translate([-1000,-1000,zmin]) cube([2000,2000,zmax-zmin],center=false); } }

z0=347; z1=397;
translate([0,0,-z0]) cage_slice(z0,z1);
