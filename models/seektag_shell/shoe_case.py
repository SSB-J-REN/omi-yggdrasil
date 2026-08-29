#!/usr/bin/env python3
"""
Lace-in shoe case for a round SeekTag / AirTag-style tracker.

Two parts, printed separately:

  * BASE -- holds the tracker and has TWO real, fully-enclosed lace tunnels
            running straight through the lower body (open only at the two
            edges). You thread a shoelace end through each tunnel like
            threading a bead, so the case laces flat onto the shoe and can't
            come off without unlacing.
  * LID  -- a plain, low-profile cap that snaps onto the base and seals the
            tracker inside. Floor below + lid above = sealed on both sides.

The tunnels are genuine holes (walls above, below, and on both sides), built
without boolean CSG by assembling the body from watertight solids that leave
the tunnel voids between them:

    - a full-disc bottom slab (the tunnel floor),
    - the tracker cup on top (its floor is the tunnel roof),
    - two curved outer-wall arcs (partial revolves) that support the rim but
      leave the tunnel mouths open at the top/bottom edges,
    - a centre divider wall between the two tunnels.

Prints flat with NO supports: the base sits on the slab, the cavity opens up,
and the cup floor only bridges the ~10 mm tunnel width.

The snap is a light interference bead; FDM snap fits vary, so tune
SNAP / CLEARANCE if the lid is too tight or too loose.

Usage:
    python3 shoe_case.py           # writes shoe_base.stl and shoe_lid.stl
"""

import math

import generate_shell as g  # reuse revolve / write_stl / helpers

# ---------------------------------------------------------------------------
# Parameters (mm)
# ---------------------------------------------------------------------------
TRACKER_DIA   = 40.0
TRACKER_THICK = 8.0
FIT_CLEARANCE = 0.4          # radial gap around the tracker

SLAB_TH       = 1.2          # tunnel floor thickness (bottom slab)
TUNNEL_H      = 3.4          # tunnel height
FLOOR_TH      = 1.8          # sealed floor thickness (tunnel roof)
SIDE_WALL     = 2.2          # outer wall thickness
LEDGE_W       = 1.6          # width of the shelf the lid rests on
LID_TH        = 2.2          # lid thickness
BEVEL         = 0.6          # lid edge bevel / snap lead-in chamfer

SNAP          = 0.5          # radial size of the retaining bead
CLEARANCE     = 0.25         # radial gap between lid edge and base bore

TUNNEL_HALF   = 5.0          # half-width of each tunnel (tunnels are 10mm wide)
DIVIDER_HALF  = 2.0          # half-width of the centre wall between tunnels

# ---------------------------------------------------------------------------
# Derived
# ---------------------------------------------------------------------------
R_TRACK = TRACKER_DIA / 2.0 + FIT_CLEARANCE        # cavity radius
R_BORE  = R_TRACK + LEDGE_W                         # lid-bore radius
R_OUT   = R_BORE + SIDE_WALL                        # outer shell radius
R_BEAD  = R_BORE - SNAP                             # snap bead inner radius
R_LID   = R_BORE - CLEARANCE                        # lid disc radius

R_TUN   = DIVIDER_HALF + 2 * TUNNEL_HALF            # tunnel outer x -> wall arc inner radius

Z_SLAB      = SLAB_TH                               # top of the bottom slab (tunnel floor)
Z_ROOF      = Z_SLAB + TUNNEL_H                     # tunnel roof / cup floor underside
Z_FLOOR_TOP = Z_ROOF + FLOOR_TH                     # cavity floor
Z_LEDGE     = Z_FLOOR_TOP + TRACKER_THICK + 0.4     # top of cavity / lid shelf
Z_TOP       = Z_LEDGE + LID_TH                       # top of the base wall

# angular half-span of each tunnel mouth at the wall (where the arcs are absent)
_MOUTH = math.asin(min(1.0, R_TUN / R_OUT))         # to x=+/-R_TUN on the rim


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (2, 6, 7, 3), (1, 5, 6, 2), (0, 3, 7, 4)]
    tris = []
    for a, b, c, d in faces:
        g.add_quad(tris, v[a], v[b], v[c], v[d])
    return tris


def partial_revolve(profile, a0, a1, segments):
    """Revolve a closed (r, z) profile over the angular range [a0, a1] and cap
    the two open ends. `profile` must be convex (capped with a centroid fan)."""
    tris = []
    n = len(profile)
    for j in range(segments):
        p0 = a0 + (a1 - a0) * j / segments
        p1 = a0 + (a1 - a0) * (j + 1) / segments
        c0, s0 = math.cos(p0), math.sin(p0)
        c1, s1 = math.cos(p1), math.sin(p1)
        for i in range(n):
            r0, z0 = profile[i]
            r1, z1 = profile[(i + 1) % n]
            A = (r0 * c0, r0 * s0, z0)
            B = (r1 * c0, r1 * s0, z1)
            C = (r1 * c1, r1 * s1, z1)
            D = (r0 * c1, r0 * s1, z0)
            g.add_quad(tris, A, B, C, D)
    for ang, flip in ((a0, False), (a1, True)):
        c, s = math.cos(ang), math.sin(ang)
        pts = [(r * c, r * s, z) for (r, z) in profile]
        cen = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n,
               sum(p[2] for p in pts) / n)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            tris.append((cen, b, a) if flip else (cen, a, b))
    return [t for t in tris if g._tri_area(t) > 1e-9]


# ---------------------------------------------------------------------------
# Base part
# ---------------------------------------------------------------------------
def build_base():
    tris = []

    # 1) bottom slab (tunnel floor) -- full disc
    tris += g.revolve([(0.0, 0.0), (R_OUT, 0.0), (R_OUT, Z_SLAB),
                       (0.0, Z_SLAB)], g.REV_SEGMENTS)

    # 2) tracker cup on top; its floor is the tunnel roof
    z_bead_hi, z_bead_mid, z_bead_lo = Z_TOP - 0.6, Z_TOP - 1.0, Z_TOP - 1.4
    cup = [
        (0.0,      Z_ROOF),        # roof underside centre
        (R_OUT,    Z_ROOF),        # roof underside outer edge
        (R_OUT,    Z_TOP),         # up the outer wall
        (R_BORE,   Z_TOP),         # inward across the top rim
        (R_BORE,   z_bead_hi),     # down the bore to the bead
        (R_BEAD,   z_bead_mid),    # bead tip (overhangs the lid edge)
        (R_BORE,   z_bead_lo),     # back out below the bead
        (R_BORE,   Z_LEDGE),       # down to the shelf
        (R_TRACK,  Z_LEDGE),       # inward across the shelf (lid rests here)
        (R_TRACK,  Z_FLOOR_TOP),   # down the cavity wall
        (0.0,      Z_FLOOR_TOP),   # across the cavity floor to the axis
    ]
    tris += g.revolve(cup, g.REV_SEGMENTS)

    # 3) two outer-wall arcs that support the rim but leave the tunnel mouths
    #    open at the top (+Y) and bottom (-Y) edges. Ring rect in (r, z),
    #    overlapping the slab and cup floor so the union merges cleanly.
    ring = [(R_TUN, Z_SLAB - 0.2), (R_OUT, Z_SLAB - 0.2),
            (R_OUT, Z_ROOF + 0.2), (R_TUN, Z_ROOF + 0.2)]
    seg = max(8, g.REV_SEGMENTS // 4)
    right = (-(math.pi / 2 - _MOUTH), (math.pi / 2 - _MOUTH))   # around 0 deg
    left = (math.pi / 2 + _MOUTH, 3 * math.pi / 2 - _MOUTH)     # around 180 deg
    tris += partial_revolve(ring, right[0], right[1], seg)
    tris += partial_revolve(ring, left[0], left[1], seg)

    # 4) centre divider wall between the two tunnels (runs the full length)
    ymax = math.sqrt(max(0.0, R_OUT ** 2 - DIVIDER_HALF ** 2)) - 0.6
    tris += box(-DIVIDER_HALF, DIVIDER_HALF, -ymax, ymax,
                Z_SLAB - 0.2, Z_ROOF + 0.2)
    return tris


# ---------------------------------------------------------------------------
# Lid part (plain, low-profile, bevelled edges as a snap lead-in)
# ---------------------------------------------------------------------------
def build_lid():
    profile = [
        (0.0,           0.0),
        (R_LID - BEVEL, 0.0),
        (R_LID,         BEVEL),
        (R_LID,         LID_TH - BEVEL),
        (R_LID - BEVEL, LID_TH),
        (0.0,           LID_TH),
    ]
    return g.revolve(profile, g.REV_SEGMENTS)


def main():
    base = build_base()
    lid = build_lid()
    g.write_stl(base, "shoe_base.stl", name="seektag_shoe_base")
    g.write_stl(lid, "shoe_lid.stl", name="seektag_shoe_lid")
    print("Wrote shoe_base.stl (%d tris) and shoe_lid.stl (%d tris)"
          % (len(base), len(lid)))
    print("  case OD          : %.1f mm" % (2 * R_OUT))
    print("  assembled height : %.1f mm" % Z_TOP)
    print("  cavity           : %.1f mm dia x %.1f mm deep"
          % (2 * R_TRACK, Z_LEDGE - Z_FLOOR_TOP))
    print("  lace tunnels     : 2 x  %.1f mm wide x %.1f mm high (through holes)"
          % (2 * TUNNEL_HALF, TUNNEL_H))


if __name__ == "__main__":
    main()
