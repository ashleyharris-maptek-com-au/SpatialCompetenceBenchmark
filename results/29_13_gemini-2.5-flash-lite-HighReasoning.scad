module bar(length, width, height) { cube([length, width, height]); }
module hollow_bar(length, width, height, hole_dia) { difference() { bar(length, width, height); translate([length/2, width/2, height/2]) cylinder(h=height + 0.2, d=hole_dia, center=true); }}

// Parameters
bar_thickness = 10.0;
gap_xy = 87.5;
num_bars_xy = 5;
outer_dim_xy = 400.0;
m6_hole_dia = 7.0;
total_cage_height = 790.0;
segment_height = 50.0;
num_segments = 16;

// Global cage parameters for positioning
x_bar_centers = [-195.0, -97.5, 0.0, 97.5, 195.0];
z_bar_centers = [5.0, 102.5, 200.0, 297.5, 395.0, 492.5, 590.0, 687.5, 785.0]; // Centerlines of horizontal bars

// Segment-specific parameters
segment_index = 13;
z_start_global = segment_index * segment_height;
z_end_global = min((segment_index + 1) * segment_height, total_cage_height);
current_segment_h_local = z_end_global - z_start_global;

// --- Geometry Generation for Segment 13 ---

module segment_geometry_13() {
    all_geometries = [];
    
    // Add vertical bar segments
    for (i = [0 : num_bars_xy-1]) {
        for (j = [0 : num_bars_xy-1]) {
            xc_global = x_bar_centers[i];
            yc_global = x_bar_centers[j];
            is_corner = (i == 0 || i == num_bars_xy - 1) && (j == 0 || j == num_bars_xy - 1);

            bar_height_in_segment = current_segment_h_local;

            if (is_corner) {
                bar_geo = hollow_bar(bar_thickness, bar_thickness, bar_height_in_segment, m6_hole_dia);
                all_geometries = concat(all_geometries, [translate([xc_global - bar_thickness/2.0, yc_global - bar_thickness/2.0, 0])(bar_geo)]);
            } else {
                bar_geo = bar(bar_thickness, bar_thickness, bar_height_in_segment);
                all_geometries = concat(all_geometries, [translate([xc_global - bar_thickness/2.0, yc_global - bar_thickness/2.0, 0])(bar_geo)]);
            }
        }
    }

    // Add horizontal bar segments
    for (zc_global = z_bar_centers) {
        bar_z_min_global = zc_global - bar_thickness / 2.0;
        bar_z_max_global = zc_global + bar_thickness / 2.0;

        // Calculate the intersection of the horizontal bar's Z range and the segment's Z range
        overlap_z_start_local = max(0, bar_z_min_global - z_start_global);
        overlap_z_end_local = min(current_segment_h_local, bar_z_max_global - z_start_global);

        if (overlap_z_start_local < overlap_z_end_local) {
            horizontal_bar_height_in_segment_local = overlap_z_end_local - overlap_z_start_local;

            // X-spanning bars
            for (i = [0 : num_bars_xy-1]) {
                yc_global = x_bar_centers[i];
                h_bar_x = bar(outer_dim_xy, bar_thickness, horizontal_bar_height_in_segment_local);
                all_geometries = concat(all_geometries, [translate([-outer_dim_xy/2.0, yc_global - bar_thickness/2.0, overlap_z_start_local])(h_bar_x)]);
            }
            
            // Y-spanning bars
            for (j = [0 : num_bars_xy-1]) {
                xc_global = x_bar_centers[j];
                h_bar_y = bar(bar_thickness, outer_dim_xy, horizontal_bar_height_in_segment_local);
                all_geometries = concat(all_geometries, [translate([xc_global - bar_thickness/2.0, -outer_dim_xy/2.0, overlap_z_start_local])(h_bar_y)]);
            }
        }
    }

    union()(all_geometries);
}

// Render the geometry for this segment
segment_geometry_13();
