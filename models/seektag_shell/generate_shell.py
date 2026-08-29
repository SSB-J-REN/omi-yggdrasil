#!/usr/bin/env python3
"""
Decorative snap-in shell (case) for a round SeekTag / AirTag-style tracker.

The SeekTag TAG03NC is a round CR2032-powered tracker, ~40 mm diameter x ~8 mm
thick. This script generates a decorative front-facing case that the tracker
snaps into from the back, with:

  * a friction/snap retaining lip that holds the tracker in place
  * a raised flower / mandala relief on the decorative front face
  * a keyring loop at the top (12 o'clock)

No third-party libraries are required -- the mesh is written as an ASCII STL
built from watertight primitives (a solid of revolution for the body, plus
ellipsoids and a torus for the decoration and loop). Modern slicers (Cura,
PrusaSlicer, Bambu Studio, ...) automatically union the overlapping solids, so
the result prints as a single object.

Every dimension below is a parameter -- measure your tracker with calipers and
adjust TRACKER_DIA / TRACKER_THICK for a snug fit, then re-run.

Usage:
    python3 generate_shell.py [output.stl]
"""

import math
import sys

# ---------------------------------------------------------------------------
# Parameters  (all millimetres / degrees)
# ---------------------------------------------------------------------------

# --- Tracker being enclosed (SeekTag TAG03NC, round) -----------------------
TRACKER_DIA        = 40.0   # measured outer diameter of the tracker
TRACKER_THICK      = 8.0    # measured thickness of the tracker
FIT_CLEARANCE      = 0.4    # radial gap added around the tracker (per side)
DEPTH_CLEARANCE    = 0.5    # extra cavity depth so the tracker seats fully

# --- Shell walls -----------------------------------------------------------
SIDE_WALL          = 2.6    # wall thickness around the tracker
FRONT_WALL         = 2.5    # thickness of the decorative front face

# --- Snap-in retaining lip (protrudes inward at the open back) --------------
LIP                = 1.2    # how far the lip overhangs the cavity (radial)
LIP_HEIGHT         = 1.3    # axial thickness of the lip

# --- Front decoration style ------------------------------------------------
STYLE              = "flower"  # "flower" (mandala) or "monogram" (initials)
TEXT               = "AMP"     # initials for the monogram style (1-3 letters)
TEXT_HEIGHT        = 13.0      # cap height of the letters (mm)
TEXT_STROKE        = 2.4       # stroke thickness of the letters (mm)
TEXT_RISE          = 2.4       # how far the letters stand off the front face
TEXT_SPACING       = 0.14      # gap between letters (in glyph-height units)

# --- Decorative front relief (flower / mandala) ----------------------------
PETAL_COUNT        = 8      # number of flower petals
PETAL_LEN          = 12.0   # petal length (radial)
PETAL_WID          = 6.5    # petal width (tangential)
PETAL_RISE         = 3.0    # how far petals stand off the front face
PETAL_RING_R       = 11.0   # radius of the ring the petals are centred on
CENTER_BOSS_R      = 6.0    # central dome radius
CENTER_BOSS_RISE   = 3.4    # central dome height
DOT_COUNT          = 16     # small accent dots near the rim
DOT_R              = 1.6    # accent dot radius
DOT_RING_R         = 19.0   # radius of the accent-dot ring
DOT_RISE           = 1.1    # accent dot height
EMBED              = 0.8    # how far dome bases sink into the front face

# --- Keyring loop (top) ----------------------------------------------------
LOOP_MAJOR_R       = 5.0    # loop radius (centre of the ring)
LOOP_MINOR_R       = 2.0    # thickness of the ring stock
LOOP_NECK          = 3.0    # length of the neck bridging body -> loop

# --- Mesh resolution -------------------------------------------------------
REV_SEGMENTS       = 160    # angular facets for the revolved body
SPHERE_LAT         = 20     # latitude bands for ellipsoids
SPHERE_LON         = 28     # longitude bands for ellipsoids
TORUS_MAJOR_SEG    = 56     # segments around the loop
TORUS_MINOR_SEG    = 20     # segments around the ring stock

# ---------------------------------------------------------------------------
# Derived dimensions (read the module globals live, so a driver can override
# TRACKER_DIA / TEXT / STYLE and rebuild without re-importing).
# ---------------------------------------------------------------------------
def derived():
    r_track = TRACKER_DIA / 2.0 + FIT_CLEARANCE          # cavity radius
    r_out   = r_track + SIDE_WALL                        # outer shell radius
    r_lip   = r_track - LIP                              # inner edge of the lip
    h       = FRONT_WALL + TRACKER_THICK + DEPTH_CLEARANCE  # total height
    ceil    = h - FRONT_WALL                             # z of cavity ceiling
    return r_track, r_out, r_lip, h, ceil


R_TRACK, R_OUT, R_LIP, H, CAVITY_CEIL = derived()

Tri = tuple  # a triangle is (v0, v1, v2), each v a 3-tuple


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _norm(v):
    m = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if m < 1e-12:
        return (0.0, 0.0, 0.0)
    return (v[0] / m, v[1] / m, v[2] / m)


def _facet_normal(t):
    return _norm(_cross(_sub(t[1], t[0]), _sub(t[2], t[0])))


def _tri_area(t):
    return 0.5 * math.sqrt(sum(c * c for c in _cross(_sub(t[1], t[0]),
                                                     _sub(t[2], t[0]))))


def add_quad(tris, a, b, c, d):
    """Add a quad a-b-c-d as two triangles, dropping degenerate ones."""
    for t in ((a, b, c), (a, c, d)):
        if _tri_area(t) > 1e-9:
            tris.append(t)


# ---------------------------------------------------------------------------
# Primitives (each watertight on its own)
# ---------------------------------------------------------------------------
def revolve(profile, segments):
    """Revolve a closed (r, z) profile around the z axis -> closed solid."""
    tris = []
    n = len(profile)
    for j in range(segments):
        p0 = 2 * math.pi * j / segments
        p1 = 2 * math.pi * (j + 1) / segments
        c0, s0 = math.cos(p0), math.sin(p0)
        c1, s1 = math.cos(p1), math.sin(p1)
        for i in range(n):
            r0, z0 = profile[i]
            r1, z1 = profile[(i + 1) % n]
            a = (r0 * c0, r0 * s0, z0)
            b = (r1 * c0, r1 * s0, z1)
            cc = (r1 * c1, r1 * s1, z1)
            d = (r0 * c1, r0 * s1, z0)
            add_quad(tris, a, b, cc, d)
    return tris


def dome(cx, cy, base_z, rx, ry, height, rot_z=0.0,
         lat=SPHERE_LAT, lon=SPHERE_LON):
    """A raised half-ellipsoid (dome) with a flat closing base at `base_z`.

    Only the upper hemisphere is generated, so the solid never dips below
    `base_z`. Decorations use this so they rise off the front face without
    ever intruding into the tracker cavity behind it. `rot_z` spins the
    elliptical footprint so petals can point radially outward.
    """
    cr, sr = math.cos(rot_z), math.sin(rot_z)

    def pt(theta, phi):
        x = rx * math.sin(theta) * math.cos(phi)
        y = ry * math.sin(theta) * math.sin(phi)
        z = height * math.cos(theta)
        xr = x * cr - y * sr
        yr = x * sr + y * cr
        return (cx + xr, cy + yr, base_z + z)

    tris = []
    half = math.pi / 2.0
    for i in range(lat):
        t0 = half * i / lat
        t1 = half * (i + 1) / lat
        for k in range(lon):
            p0 = 2 * math.pi * k / lon
            p1 = 2 * math.pi * (k + 1) / lon
            add_quad(tris, pt(t0, p0), pt(t1, p0), pt(t1, p1), pt(t0, p1))
    # flat base cap (equator ring -> centre), wound for a downward normal
    center = (cx, cy, base_z)
    ring = [pt(half, 2 * math.pi * k / lon) for k in range(lon)]
    for k in range(lon):
        kn = (k + 1) % lon
        tris.append((center, ring[kn], ring[k]))
    return [t for t in tris if _tri_area(t) > 1e-9]


def torus(center, major_r, minor_r, axis="z",
          maj=TORUS_MAJOR_SEG, mnr=TORUS_MINOR_SEG):
    """Closed torus. `axis` is the direction of the hole through the ring."""
    cx, cy, cz = center
    tris = []

    def pt(u, v):
        # ring in local xy plane, hole along local z
        rr = major_r + minor_r * math.cos(v)
        lx = rr * math.cos(u)
        ly = rr * math.sin(u)
        lz = minor_r * math.sin(v)
        if axis == "z":
            x, y, z = lx, ly, lz
        elif axis == "y":
            x, y, z = lx, lz, ly
        else:  # "x"
            x, y, z = lz, lx, ly
        return (cx + x, cy + y, cz + z)

    for i in range(maj):
        u0 = 2 * math.pi * i / maj
        u1 = 2 * math.pi * (i + 1) / maj
        for k in range(mnr):
            v0 = 2 * math.pi * k / mnr
            v1 = 2 * math.pi * (k + 1) / mnr
            add_quad(tris, pt(u0, v0), pt(u1, v0), pt(u1, v1), pt(u0, v1))
    return tris


def capsule(p0, p1, r, z_bot, z_top, arc=8):
    """A raised, rounded bar (capsule footprint extruded in z) from a stroke
    p0->p1 of radius r. Used to draw monogram letters as raised strokes.
    The footprint is convex, so top/bottom caps are simple fans."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1e-9:
        ux, uy = 1.0, 0.0
        a_u = 0.0
    else:
        ux, uy = dx / L, dy / L
        a_u = math.atan2(uy, ux)

    poly = []
    # cap around p1: sweep a_u-90deg .. a_u+90deg (the half facing away p0)
    for i in range(arc + 1):
        a = a_u - math.pi / 2 + math.pi * i / arc
        poly.append((x1 + r * math.cos(a), y1 + r * math.sin(a)))
    # cap around p0: sweep a_u+90deg .. a_u+270deg (facing away p1)
    for i in range(arc + 1):
        a = a_u + math.pi / 2 + math.pi * i / arc
        poly.append((x0 + r * math.cos(a), y0 + r * math.sin(a)))

    n = len(poly)
    cx = sum(p[0] for p in poly) / n
    cy = sum(p[1] for p in poly) / n
    top_c = (cx, cy, z_top)
    bot_c = (cx, cy, z_bot)
    tris = []
    for i in range(n):
        j = (i + 1) % n
        ax, ay = poly[i]
        bx, by = poly[j]
        top_a = (ax, ay, z_top)
        top_b = (bx, by, z_top)
        bot_a = (ax, ay, z_bot)
        bot_b = (bx, by, z_bot)
        tris.append((top_c, top_a, top_b))      # top cap (up)
        tris.append((bot_c, bot_b, bot_a))      # bottom cap (down)
        add_quad(tris, bot_a, bot_b, top_b, top_a)  # side wall
    return [t for t in tris if _tri_area(t) > 1e-9]


# ---------------------------------------------------------------------------
# Stroke font: each glyph is a list of polylines in a unit box
# (x in [0, advance], y in [0, 1], baseline at 0). "advance" is the last item.
# ---------------------------------------------------------------------------
_FONT = {
    "A": ([(0.00, 0.0), (0.35, 1.0)], [(0.70, 0.0), (0.35, 1.0)],
          [(0.13, 0.42), (0.57, 0.42)], 0.70),
    "M": ([(0.00, 0.0), (0.00, 1.0), (0.42, 0.32), (0.84, 1.0),
           (0.84, 0.0)], 0.84),
    "P": ([(0.00, 0.0), (0.00, 1.0)],
          [(0.00, 1.0), (0.42, 0.98), (0.60, 0.83), (0.60, 0.68),
           (0.42, 0.53), (0.00, 0.51)], 0.62),
    "L": ([(0.00, 1.0), (0.00, 0.0), (0.52, 0.0)], 0.55),
    "D": ([(0.00, 0.0), (0.00, 1.0)],
          [(0.00, 1.0), (0.40, 0.96), (0.63, 0.74), (0.68, 0.50),
           (0.63, 0.26), (0.40, 0.04), (0.00, 0.0)], 0.70),
}


def monogram(text, cx, cy, cap_h, stroke, z_bot, z_top, spacing):
    """Raised initials centred at (cx, cy) on the front face."""
    glyphs = [g for g in text.upper() if g in _FONT]
    if not glyphs:
        return []
    advances = [_FONT[g][-1] for g in glyphs]
    total = sum(advances) + spacing * (len(glyphs) - 1)  # in glyph-h units
    r = stroke / 2.0
    tris = []
    x_cursor = -total / 2.0                      # left edge, glyph units
    for g, adv in zip(glyphs, advances):
        gx0 = x_cursor
        for stroke_poly in _FONT[g][:-1]:
            pts = [(cx + (gx0 + px) * cap_h, cy + (py - 0.5) * cap_h)
                   for (px, py) in stroke_poly]
            for i in range(len(pts) - 1):
                tris += capsule(pts[i], pts[i + 1], r, z_bot, z_top)
        x_cursor += adv + spacing
    return tris


# ---------------------------------------------------------------------------
# Build the model
# ---------------------------------------------------------------------------
def build():
    tris = []

    r_track, r_out, r_lip, h, ceil = derived()

    # --- Main body: solid of revolution ------------------------------------
    # Closed (r, z) profile. z = 0 is the open back; z = h is the front face.
    # Order traces the cross-section so the cavity + snap lip are carved out.
    profile = [
        (0.0,        h),               # front face centre
        (r_out,      h),               # front outer edge
        (r_out,      0.0),             # down the outer wall to the back
        (r_lip,      0.0),             # inward across the back rim (lip face)
        (r_lip,      LIP_HEIGHT),      # up the inner lip
        (r_track,    LIP_HEIGHT),      # out to the cavity wall
        (r_track,    ceil),            # up the cavity wall
        (0.0,        ceil),            # across the cavity ceiling to the axis
    ]
    tris += revolve(profile, REV_SEGMENTS)

    # Decorations are raised off the front face but never reach the cavity
    # ceiling behind the front wall (base_z stays well above `ceil`).
    base_z = h - EMBED
    dot_ring_r = min(DOT_RING_R, r_out - 3.0)

    if STYLE == "monogram":
        # --- Initials monogram in the centre -------------------------------
        tris += monogram(TEXT, 0.0, 0.0, TEXT_HEIGHT, TEXT_STROKE,
                         base_z, h + TEXT_RISE, TEXT_SPACING)
        # decorative dot-ring border
        for i in range(DOT_COUNT):
            ang = 2 * math.pi * (i + 0.5) / DOT_COUNT
            dx = dot_ring_r * math.cos(ang)
            dy = dot_ring_r * math.sin(ang)
            tris += dome(dx, dy, base_z, DOT_R, DOT_R, DOT_RISE + EMBED,
                         lat=10, lon=16)
    else:
        # --- Flower / mandala ----------------------------------------------
        tris += dome(0.0, 0.0, base_z, CENTER_BOSS_R, CENTER_BOSS_R,
                     CENTER_BOSS_RISE + EMBED)
        for i in range(PETAL_COUNT):
            ang = 2 * math.pi * i / PETAL_COUNT
            px = PETAL_RING_R * math.cos(ang)
            py = PETAL_RING_R * math.sin(ang)
            tris += dome(px, py, base_z, PETAL_LEN / 2.0, PETAL_WID / 2.0,
                         PETAL_RISE + EMBED, rot_z=ang)
        for i in range(DOT_COUNT):
            ang = 2 * math.pi * (i + 0.5) / DOT_COUNT
            dx = dot_ring_r * math.cos(ang)
            dy = dot_ring_r * math.sin(ang)
            tris += dome(dx, dy, base_z, DOT_R, DOT_R, DOT_RISE + EMBED,
                         lat=10, lon=16)

    # --- Keyring loop at the top (12 o'clock, +y) --------------------------
    loop_cy = r_out + LOOP_NECK + LOOP_MAJOR_R - LOOP_MINOR_R
    loop_cz = h / 2.0
    # neck: a stubby rounded block bridging the body rim to the loop
    tris += neck_block(r_out - 1.0, loop_cy, loop_cz)
    # the ring: hole faces front/back -> hole axis along z
    tris += torus((0.0, loop_cy, loop_cz), LOOP_MAJOR_R, LOOP_MINOR_R, axis="z")

    return tris


def neck_block(y0, y1, z):
    """A rounded neck bridging body rim (y0) to loop centre area (y1)."""
    half_w = LOOP_MINOR_R * 1.2
    half_h = LOOP_MINOR_R * 1.2
    verts = [
        (-half_w, y0, z - half_h), (half_w, y0, z - half_h),
        (half_w, y1, z - half_h), (-half_w, y1, z - half_h),
        (-half_w, y0, z + half_h), (half_w, y0, z + half_h),
        (half_w, y1, z + half_h), (-half_w, y1, z + half_h),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (2, 6, 7, 3), (1, 5, 6, 2), (0, 3, 7, 4),
    ]
    tris = []
    for a, b, c, d in faces:
        add_quad(tris, verts[a], verts[b], verts[c], verts[d])
    return tris


# ---------------------------------------------------------------------------
# STL output
# ---------------------------------------------------------------------------
def write_stl(tris, path, name="seektag_decorative_shell"):
    with open(path, "w") as f:
        f.write("solid %s\n" % name)
        for t in tris:
            nx, ny, nz = _facet_normal(t)
            f.write("  facet normal %.6e %.6e %.6e\n" % (nx, ny, nz))
            f.write("    outer loop\n")
            for v in t:
                f.write("      vertex %.6e %.6e %.6e\n" % (v[0], v[1], v[2]))
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid %s\n" % name)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "seektag_decorative_shell.stl"
    tris = build()
    write_stl(tris, out)
    xs = [v[0] for t in tris for v in t]
    ys = [v[1] for t in tris for v in t]
    zs = [v[2] for t in tris for v in t]
    print("Wrote %s" % out)
    print("  triangles : %d" % len(tris))
    print("  bounds    : X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f] mm"
          % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
    print("  case OD   : %.1f mm   height: %.1f mm" % (2 * R_OUT, H))
    print("  cavity    : %.1f mm dia x %.1f mm deep (holds %.0f x %.0f mm)"
          % (2 * R_TRACK, CAVITY_CEIL, TRACKER_DIA, TRACKER_THICK))


if __name__ == "__main__":
    main()
