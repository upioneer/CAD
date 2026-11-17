// ==============================================================================
// 8ft Maker Station: Parametric 3D Printable Spool Bracket & Stopper Collar
// Parametric OpenSCAD Model for Modular 3/4" EMT Steel Conduit
// ==============================================================================
//
// Mounting: Designed for 2x4 posts oriented short-ways (3.5" wide front face).
// Support-Free DFM: Lay flat on side (print_orientation = "print") for 100%
// support-free printing and optimal tensile layer orientation.
//
// ==============================================================================

/* [Component Selection] */
// Select which part to preview / export
part_type = "center"; // [center: Center Pass-Through Bracket, end_left: Left End Bracket, end_right: Right End Bracket, collar: Conduit Stopper Collar, all: Complete Set]

// Orientation for 3D slicing vs workbench modeling
orientation = "print"; // [print: Laid flat on side for support-free printing, model: Upright as installed on workbench post]

/* [Conduit & Rod Specifications] */
// 3/4" EMT steel conduit nominal outer diameter (mm)
conduit_od = 23.42;

// Diametral clearance for smooth slip-fit (mm)
conduit_clearance = 0.78;

// Cantilever projection from post face to rod center (mm, 152.4mm = 6.0 inches)
cantilever_length = 152.4;

/* [Structural Bracket Dimensions] */
// Uniform bracket body width (mm) - sets print bed width when printed on side
bracket_width = 36.0;

// Base mounting flange thickness against 2x4 wood face (mm)
flange_thickness = 10.0;

// Upper mounting tab height above conduit center (mm)
mount_z_top = 30.0;

// Lower gusset anchor depth below conduit center (mm, total span 105mm)
mount_z_bot = -75.0;

// Solid wall thickness surrounding conduit bore (mm)
cradle_wall_thick = 6.0;

// Cradle top mouth height (mm)
cradle_head_top_z = 20.0;

// Cradle bottom reinforcement elevation (mm)
cradle_head_bot_z = -14.0;

// Include weight-saving / I-beam truss pocket
with_truss_pocket = true;

/* [Fasteners & Retaining Pin] */
// Wood screw clearance hole diameter (mm, #9/#10 / M5)
screw_hole_dia = 5.2;

// Screw counterbore diameter (mm)
screw_cbore_dia = 10.5;

// Screw counterbore depth (mm)
screw_cbore_depth = 5.0;

// Transverse retaining cross-bolt / linchpin hole diameter (mm)
pin_hole_dia = 5.2;

/* [Conduit Stopper Collar] */
collar_width = 16.0;
collar_od = 36.0;
collar_bolt_dia = 4.3; // M4 screw

/* [Rendering Precision] */
$fn = 64;

// ==============================================================================
// COMPUTED PARAMETERS
// ==============================================================================
conduit_r = (conduit_od + conduit_clearance) / 2.0; // 12.10 mm
cradle_y_min = cantilever_length - conduit_r - cradle_wall_thick;
cradle_y_max = cantilever_length + conduit_r + cradle_wall_thick;

// ==============================================================================
// MODULES
// ==============================================================================

module spool_bracket(type = "center") {
    difference() {
        // 1. Solid Extruded Profile
        translate([-bracket_width / 2, 0, 0])
            rotate([0, 90, 0])
            linear_extrude(height = bracket_width)
            polygon(points = [
                [z_bot_actual(), 0],
                [cradle_head_bot_z, cradle_y_min],
                [cradle_head_bot_z, cradle_y_max],
                [cradle_head_top_z, cradle_y_max],
                [cradle_head_top_z, cradle_y_min],
                [mount_z_top, flange_thickness],
                [mount_z_top, 0],
                [z_bot_actual(), 0]
            ]);

        // 2. Truss Weight-Saving Pocket
        if (with_truss_pocket) {
            translate([-bracket_width / 2 - 1, 0, 0])
                rotate([0, 90, 0])
                linear_extrude(height = bracket_width + 2)
                polygon(points = [
                    [z_bot_actual() + 20.0, flange_thickness + 10.0],
                    [cradle_head_bot_z + 8.0, cradle_y_min - 8.0],
                    [mount_z_top - 18.0, flange_thickness + 10.0]
                ]);
        }

        // 3. Conduit U-Channel Cradle Cutout
        cut_x_start = (type == "end_left") ? (-bracket_width / 2 + 4.0) : (-bracket_width / 2 - 2);
        cut_len = (type == "end_left" || type == "end_right") ? (bracket_width - 4.0 + 2.0) : (bracket_width + 4.0);

        translate([cut_x_start, cantilever_length, 0]) {
            // Circular bottom cradle
            rotate([0, 90, 0])
                cylinder(r = conduit_r, h = cut_len);

            // Upright vertical slot
            translate([0, -conduit_r, 0])
                cube([cut_len, 2 * conduit_r, cradle_head_top_z + 5]);

            // Flared lead-in chamfers at top opening
            translate([0, -conduit_r, cradle_head_top_z])
                rotate([45, 0, 0])
                cube([cut_len, 4, 4]);

            translate([0, conduit_r, cradle_head_top_z])
                rotate([45, 0, 0])
                cube([cut_len, 4, 4]);
        }

        // 4. Centerline Countersunk Mounting Screw Holes
        screw_z_positions = [16.0, -22.0, -60.0];
        for (hz = screw_z_positions) {
            translate([0, -1, hz]) {
                rotate([-90, 0, 0]) {
                    cylinder(d = screw_hole_dia, h = flange_thickness + 2);
                    translate([0, 0, flange_thickness - screw_cbore_depth + 1])
                        cylinder(d = screw_cbore_dia, h = screw_cbore_depth + 2);
                }
            }
        }

        // 5. Transverse Retaining Pin / Linchpin Hole
        translate([-bracket_width / 2 - 2, cantilever_length, 14.0])
            rotate([0, 90, 0])
            cylinder(d = pin_hole_dia, h = bracket_width + 4);
    }
}

function z_bot_actual() = mount_z_bot;

module stopper_collar() {
    r_in = (conduit_od + conduit_clearance) / 2.0;
    r_out = collar_od / 2.0;
    ear_w = 14.0;
    ear_len = 16.0;

    difference() {
        union() {
            cylinder(r = r_out, h = collar_width);
            translate([-ear_w / 2, r_out - 4.0, 0])
                cube([ear_w, ear_len, collar_width]);
        }

        // Central conduit bore
        translate([0, 0, -1])
            cylinder(r = r_in, h = collar_width + 2);

        // Clamping slit
        translate([-1.0, 0, -1])
            cube([2.0, ear_len + r_out, collar_width + 2]);

        // M4 Clamping bolt hole & counterbores
        translate([-ear_w / 2 - 2, r_out + 6.0, collar_width / 2])
            rotate([0, 90, 0]) {
                cylinder(d = collar_bolt_dia, h = ear_w + 4);
                // Bolt head pocket
                cylinder(d = 8.0, h = 4.0);
                // Nut trap pocket
                translate([0, 0, ear_w])
                    cylinder(d = 8.5, h = 4.0, $fn = 6);
            }
    }
}

// ==============================================================================
// DISPATCH / DISPLAY LOGIC
// ==============================================================================

module orient_bracket(type) {
    if (orientation == "print") {
        // Lay flat on side: X becomes Z (zero supports required)
        rotate([0, -90, 0])
            translate([bracket_width / 2, 0, 0])
            spool_bracket(type);
    } else {
        // Model orientation: upright mounted against post
        spool_bracket(type);
    }
}

if (part_type == "center") {
    color([0.2, 0.5, 0.8]) orient_bracket("center");
} else if (part_type == "end_left") {
    color([0.3, 0.7, 0.4]) orient_bracket("end_left");
} else if (part_type == "end_right") {
    color([0.3, 0.7, 0.4]) orient_bracket("end_right");
} else if (part_type == "collar") {
    color([0.8, 0.5, 0.2]) stopper_collar();
} else if (part_type == "all") {
    translate([-100, 0, 0]) color([0.3, 0.7, 0.4]) orient_bracket("end_left");
    translate([0, 0, 0])    color([0.2, 0.5, 0.8]) orient_bracket("center");
    translate([100, 0, 0])  color([0.3, 0.7, 0.4]) orient_bracket("end_right");
    translate([0, 200, 0])  color([0.8, 0.5, 0.2]) stopper_collar();
}
