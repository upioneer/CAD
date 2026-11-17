// 8ft Maker Station: Multi-Tier 3D Printer and Soldering Workbench
// Parametric OpenSCAD Model
// Updated: Front & Rear Posts Oriented Short-Ways (3.5" in X, 1.5" in Y)
// Complete Zero-Collision Interlocking Geometry + Dual-Row Overhead Spools
// Units: Inches

$fn = 32;

// ==========================================
// PARAMETRIC CONFIGURATION
// ==========================================

total_width       = 96.0;   // 8 ft wide
total_depth       = 30.0;   // 30 in benchtop depth
desk_height       = 30.0;   // Finished top of main workbench

// True Dimensional Lumber (2x4) and Sheeting
lumber_t          = 1.5;    // 2x4 thickness (1-1/2 in) - Orienting depth-wise (Y)
lumber_w          = 3.5;    // 2x4 width (3-1/2 in) - Orienting width-wise (X)
plywood_t         = 0.75;   // 3/4 in Baltic birch / sanded plywood

// Vertical Elevations
frame_top_z       = desk_height - plywood_t;           // 29.25 in
frame_rail_bot_z  = frame_top_z - lumber_w;            // 25.75 in
bottom_rail_z     = 3.5;                               // 3.5 in off floor
bottom_slat_z     = bottom_rail_z + lumber_w;          // 7.0 in off floor

// Upper Shelf Elevations (78.0" frame, 78.75" finished top)
upper_shelf_depth = 18.0;                              // 18.0 in upper tier (Y: 12.0 to 30.0)
upper_shelf_top_z = 78.75;                             // Finished top of upper shelf
upper_shelf_frame = upper_shelf_top_z - plywood_t;     // 78.0 in (Uprights flush cut here)
upper_rail_bot_z  = upper_shelf_frame - lumber_w;      // 74.5 in

upright_height    = upper_shelf_frame;                 // 78.0 in

// Elegoo Neptune 3 Max Gantry Top: 59.5" from floor.
// Both Spool Rows strictly ABOVE Gantry:
spool_rod_dia     = 0.92;                              // 3/4" EMT Steel Conduit
spool_rod_y       = 21.0;                              // Aligned over top runout sensor
spool_z_row1      = 63.5;                              // Row 1: 4.0" ABOVE gantry top
spool_z_row2      = 71.0;                              // Row 2: 11.5" ABOVE gantry top

spool_rack_mode   = "left_dual";                       // "left_dual", "right_dual", "all_dual"

// Toggle Visuals
show_framing      = true;
show_slats        = true;
show_surfaces     = true;
show_printer      = true;
show_soldering    = true;
show_spool_rack   = true;
explode_gap       = 0.0;

// Color Palette
col_leg           = [0.82, 0.70, 0.50];
col_rail          = [0.88, 0.76, 0.56];
col_slat          = [0.78, 0.66, 0.46];
col_plywood       = [0.93, 0.86, 0.72];
col_conduit       = [0.72, 0.76, 0.82];
col_bracket       = [0.35, 0.35, 0.40];
col_printer       = [0.20, 0.22, 0.25, 0.80];
col_bed           = [0.85, 0.65, 0.15, 0.85];
col_spool_a       = [0.15, 0.55, 0.85];
col_spool_b       = [0.85, 0.30, 0.20];

// ==========================================
// 1. THREE LADDER BENTS (Short-Ways Orientation)
// Posts are 3.5" in X by 1.5" in Y
// X-Coordinates:
//   Left Bent:   [0.0, 3.5]
//   Center Bent: [46.25, 49.75]
//   Right Bent:  [92.5, 96.0]
// Y-Partitions (Total Depth = 30.0"):
//   Y [0.0, 1.5]   : Front 96" Rail
//   Y [1.5, 3.0]   : Front Leg (Z: 0 to 25.75)
//   Y [1.5, 27.0]  : Main Deck Depth Stringer (Z: 25.75 to 29.25, Length = 25.5")
//   Y [3.0, 27.0]  : Bottom Depth Stringer (Z: 3.5 to 7.0, Length = 24.0")
//   Y [27.0, 28.5] : Rear Upright Post (Z: 0 to 78.0)
//   Y [28.5, 30.0] : Rear 96" Rail
// ==========================================

bent_x_starts = [0.0, (total_width - lumber_w)/2, total_width - lumber_w];

module bent_assemblies() {
    for (i = [0 : len(bent_x_starts)-1]) {
        bx = bent_x_starts[i];

        // Rear Upright Post (Short-ways: 3.5" in X, 1.5" in Y, 78.0" tall)
        // X: [bx, bx + 3.5], Y: [27.0, 28.5], Z: [0, 78.0]
        color(col_leg)
        translate([bx, 27.0, 0])
            cube([lumber_w, lumber_t, upright_height]);

        // Front Leg (Short-ways: 3.5" in X, 1.5" in Y, 25.75" tall)
        // X: [bx, bx + 3.5], Y: [1.5, 3.0], Z: [0, 25.75]
        color(col_leg)
        translate([bx, lumber_t, 0])
            cube([lumber_w, lumber_t, frame_rail_bot_z]);

        // Main Deck Depth Stringer (Z: 25.75 to 29.25", Length: 25.5")
        // Sits directly on top of the front leg (Y: 1.5 to 3.0) and spans to rear post (Y=27.0)
        // X: [bx + 1.0, bx + 2.5] (centered on the 3.5" wide leg bent)
        color(col_rail)
        translate([bx + 1.0, lumber_t, frame_rail_bot_z])
            cube([lumber_t, 27.0 - lumber_t, lumber_w]);

        // Bottom Full-Depth Stringer (Z: 3.5 to 7.0", Length: 24.0")
        // Fits squarely between front leg (Y=3.0) and rear post (Y=27.0)
        color(col_rail)
        translate([bx + 1.0, 3.0, bottom_rail_z])
            cube([lumber_t, 27.0 - 3.0, lumber_w]);

        // Upper Shelf Cantilever Stringer (Z: 74.5 to 78.0", Length: 13.5")
        // Spans between Upper Front Rail (ends at Y=13.5) and Rear Post (starts at Y=27.0)
        color(col_rail)
        translate([bx + 1.0, total_depth - upper_shelf_depth + lumber_t, upper_rail_bot_z])
            cube([lumber_t, 27.0 - (total_depth - upper_shelf_depth + lumber_t), lumber_w]);

        // Dual Spool Pipe Cradle Brackets on Upright Posts (Row 1 & Row 2)
        for (cz = [spool_z_row1, spool_z_row2]) {
            color(col_bracket)
            translate([bx + 0.5, spool_rod_y - 0.75, cz - 1.25])
                cube([2.5, 27.0 - (spool_rod_y - 0.75), 2.5]);
        }
    }

    // Intermediate Deck Cross-Ribs (under main benchtop at X=24" and X=72")
    for (rib_x = [24.0, 72.0]) {
        color(col_rail)
        translate([rib_x - lumber_t/2, lumber_t, frame_rail_bot_z])
            cube([lumber_t, 27.0 - lumber_t, lumber_w]);
    }
}

// ==========================================
// 2. LONGITUDINAL 96" RAILS (Zero Collisions)
// ==========================================

module longitudinal_rails() {
    color(col_rail) {
        // Main Deck Front Rail (Z: 25.75 to 29.25, Y: 0.0 to 1.5)
        translate([0, 0, frame_rail_bot_z])
            cube([total_width, lumber_t, lumber_w]);

        // Main Deck Rear Rail (Z: 25.75 to 29.25, Y: 28.5 to 30.0)
        translate([0, 28.5, frame_rail_bot_z])
            cube([total_width, lumber_t, lumber_w]);

        // Lower Bottom Front Stretcher & Elevated Footrest (Z: 3.5 to 7.0, Y: 0.0 to 1.5)
        translate([0, 0, bottom_rail_z])
            cube([total_width, lumber_t, lumber_w]);

        // Lower Bottom Rear Stretcher (Z: 3.5 to 7.0, Y: 28.5 to 30.0)
        translate([0, 28.5, bottom_rail_z])
            cube([total_width, lumber_t, lumber_w]);

        // Upper Shelf Front Rail (Z: 74.5 to 78.0, Y: 12.0 to 13.5)
        translate([0, total_depth - upper_shelf_depth, upper_rail_bot_z])
            cube([total_width, lumber_t, lumber_w]);

        // Upper Shelf Rear Rail (Z: 74.5 to 78.0, Y: 28.5 to 30.0)
        translate([0, 28.5, upper_rail_bot_z])
            cube([total_width, lumber_t, lumber_w]);
    }
}

// ==========================================
// 3. BOTTOM SLAT DECK (APPROACH B)
// ==========================================

module bottom_slat_deck() {
    slat_y_positions = [23.5, 19.5, 15.5, 11.5];

    color(col_slat) {
        for (sy = slat_y_positions) {
            translate([0, sy, bottom_slat_z])
                cube([total_width, lumber_w, lumber_t]);
        }
    }
}

// ==========================================
// 4. PLYWOOD SURFACES (Flush Capped Design)
// ==========================================

module plywood_sheets() {
    color(col_plywood) {
        // Main Benchtop (30.0" x 96.0" x 0.75", Z: 29.25 to 30.0)
        translate([0, 0, frame_top_z + explode_gap])
            cube([total_width, total_depth, plywood_t]);

        // Upper Storage Shelf (18.0" x 96.0" x 0.75", Z: 78.0 to 78.75)
        // Caps cleanly over 78.0" rear upright posts and cantilever framing
        translate([0, total_depth - upper_shelf_depth, upper_shelf_frame + explode_gap * 1.5])
            cube([total_width, upper_shelf_depth, plywood_t]);
    }
}

// ==========================================
// 5. DUAL-TIER MODULAR 4FT SPOOL PIPES (Above Gantry)
// ==========================================

module single_spool_pipe(start_x, len_x, rod_z, spool_color) {
    color(col_conduit)
    translate([start_x, spool_rod_y, rod_z])
    rotate([0, 90, 0])
        cylinder(h=len_x, d=spool_rod_dia);

    for (s = [0:4]) {
        color(spool_color)
        translate([start_x + 6.0 + (s * 4.2), spool_rod_y, rod_z])
        rotate([0, 90, 0])
        difference() {
            cylinder(h=2.8, d=7.8, center=true);
            cylinder(h=3.0, d=2.2, center=true);
        }
    }
}

module dual_row_spool_system() {
    bay_w = total_width / 2;

    if (spool_rack_mode == "left_single" || spool_rack_mode == "left_dual" || spool_rack_mode == "all_dual") {
        single_spool_pipe(0.0, bay_w, spool_z_row1, col_spool_a);
    }

    if (spool_rack_mode == "left_dual" || spool_rack_mode == "all_dual") {
        single_spool_pipe(0.0, bay_w, spool_z_row2, col_spool_b);
    }

    if (spool_rack_mode == "right_single" || spool_rack_mode == "right_dual" || spool_rack_mode == "all_dual") {
        single_spool_pipe(bay_w, bay_w, spool_z_row1, col_spool_a);
    }

    if (spool_rack_mode == "right_dual" || spool_rack_mode == "all_dual") {
        single_spool_pipe(bay_w, bay_w, spool_z_row2, col_spool_b);
    }
}

// ==========================================
// 6. SPATIAL SIMULATION: ELEGOO NEPTUNE 3 MAX
// ==========================================

module neptune_3_max() {
    translate([8.0, 1.5, desk_height + explode_gap]) {
        color(col_printer)
        cube([28.0, 26.5, 3.5]);

        color(col_printer)
        translate([13.0, 0, 3.5])
            cube([2.0, 26.5, 26.0]);

        color(col_printer)
        translate([13.0, 0, 27.5])
            cube([2.0, 26.5, 2.0]);

        color(col_bed)
        translate([5.75, 5.0, 4.2])
            cube([16.5, 16.5, 0.4]);
    }
}

// Soldering Station Work Zone
module soldering_zone() {
    sx = total_width - 34.0;
    color([0.15, 0.45, 0.85])
    translate([sx, 4.0, desk_height + explode_gap])
        cube([22.0, 14.0, 0.15]);

    color([0.25, 0.25, 0.25])
    translate([sx + 1.0, 12.0, desk_height + 0.15 + explode_gap])
        cube([5.5, 5.0, 4.0]);

    color([0.15, 0.15, 0.15])
    translate([sx + 8.0, 11.0, desk_height + 0.15 + explode_gap])
        cube([7.0, 6.0, 8.5]);
}

// ==========================================
// ROOT SCENE ASSEMBLY
// ==========================================

module workstation() {
    if (show_framing) {
        bent_assemblies();
        longitudinal_rails();
    }

    if (show_slats) {
        bottom_slat_deck();
    }

    if (show_surfaces) {
        plywood_sheets();
    }

    if (show_spool_rack) {
        dual_row_spool_system();
    }

    if (show_printer) {
        neptune_3_max();
    }

    if (show_soldering) {
        soldering_zone();
    }
}

workstation();
