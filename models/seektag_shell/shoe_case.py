#!/usr/bin/env python3
"""
Lace-in shoe case for a round SeekTag / AirTag-style tracker.

Two parts, printed separately:

  * BASE -- a tracker cup raised on parallel ribs. The channels between the
            ribs are two enclosed lace tunnels: their roof is the sealed cup
            floor, their walls are the ribs, and their floor is the shoe
            itself. Thread a shoelace end through each tunnel and the case
            laces flat onto the shoe -- it can't come off without unlacing.
  * LID  -- a plain, low-profile cap that snaps onto the base and seals the
            tracker inside. Floor below + lid above = sealed on both sides.

Both parts are unions of individually watertight primitives (a solid of
revolution plus box ribs); slicers merge the overlapping solids of one part.

Prints with NO supports: the base sits on the rib bottoms, the tracker cavity
opens upward, and the sealed floor only has to bridge the ~13 mm tunnel gaps
between ribs. The lid prints flat.

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

STAND         = 4.8          # lace-tunnel height (rib height under the floor)
FLOOR_TH      = 1.8          # sealed floor thickness (tunnel roof)
SIDE_WALL     = 2.2          # outer wall thickness
LEDGE_W       = 1.6          # width of the shelf the lid rests on
LID_TH        = 2.2          # lid thickness
BEVEL         = 0.6          # lid edge bevel / snap lead-in chamfer

SNAP          = 0.5          # radial size of the retaining bead
CLEARANCE     = 0.25         # radial gap between lid edge and base bore

RIB_T         = 2.4          # rib thickness
RIB_X         = [-14.0, 0.0, 14.0]   # rib centre positions -> two tunnels
RIB_MARGIN    = 1.2          # keep rib ends inside the disc edge

# ---------------------------------------------------------------------------
# Derived
# ---------------------------------------------------------------------------
R_TRACK = TRACKER_DIA / 2.0 + FIT_CLEARANCE        # cavity radius
R_BORE  = R_TRACK + LEDGE_W                         # lid-bore radius
R_OUT   = R_BORE + SIDE_WALL                        # outer shell radius
R_BEAD  = R_BORE - SNAP                             # snap bead inner radius
R_LID   = R_BORE - CLEARANCE                        # lid disc radius

Z_FLOOR_BOT = STAND                                # floor underside (tunnel roof)
Z_FLOOR_TOP = STAND + FLOOR_TH                      # cavity floor
Z_LEDGE     = Z_FLOOR_TOP + TRACKER_THICK + 0.4    # top of cavity / lid shelf
Z_TOP       = Z_LEDGE + LID_TH                      # top of the base wall


# ---------------------------------------------------------------------------
# Box primitive (axis-aligned), watertight
# ---------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (2, 6, 7, 3), (1, 5, 6, 2), (0, 3, 7, 4),
    ]
    tris = []
    for a, b, c, d in faces:
        g.add_quad(tris, v[a], v[b], v[c], v[d])
    return tris


# ---------------------------------------------------------------------------
# Base part
# ---------------------------------------------------------------------------
def build_base():
    tris = []
    # Cup cross-section (r, z). The floor underside sits at Z_FLOOR_BOT; ribs
    # below carry it. A snap bead sits just inside the top rim.
    z_bead_hi, z_bead_mid, z_bead_lo = Z_TOP - 0.6, Z_TOP - 1.0, Z_TOP - 1.4
    profile = [
        (0.0,      Z_FLOOR_BOT),   # floor underside centre
        (R_OUT,    Z_FLOOR_BOT),   # floor underside outer edge
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
    tris += g.revolve(profile, g.REV_SEGMENTS)

    # Ribs under the floor -> the gaps between them are the lace tunnels.
    for c in RIB_X:
        x0, x1 = c - RIB_T / 2.0, c + RIB_T / 2.0
        edge = max(abs(x0), abs(x1))
        half_y = math.sqrt(max(0.0, R_OUT ** 2 - edge ** 2)) - RIB_MARGIN
        # rib bottom on the bed (z=0), top embedded slightly into the floor
        tris += box(x0, x1, -half_y, half_y, 0.0, Z_FLOOR_BOT + 0.5)
    return tris


# ---------------------------------------------------------------------------
# Lid part (plain, low-profile, bevelled edges as a snap lead-in)
# ---------------------------------------------------------------------------
def build_lid():
    profile = [
        (0.0,           0.0),
        (R_LID - BEVEL, 0.0),           # bottom face
        (R_LID,         BEVEL),         # lower lead-in chamfer
        (R_LID,         LID_TH - BEVEL),# straight side (snaps under the bead)
        (R_LID - BEVEL, LID_TH),        # upper chamfer
        (0.0,           LID_TH),        # top face
    ]
    return g.revolve(profile, g.REV_SEGMENTS)


def main():
    base = build_base()
    lid = build_lid()
    g.write_stl(base, "shoe_base.stl", name="seektag_shoe_base")
    g.write_stl(lid, "shoe_lid.stl", name="seektag_shoe_lid")

    tunnel_w = abs(RIB_X[1] - RIB_X[0]) - RIB_T
    print("Wrote shoe_base.stl (%d tris) and shoe_lid.stl (%d tris)"
          % (len(base), len(lid)))
    print("  case OD          : %.1f mm" % (2 * R_OUT))
    print("  assembled height : %.1f mm" % Z_TOP)
    print("  cavity           : %.1f mm dia x %.1f mm deep"
          % (2 * R_TRACK, Z_LEDGE - Z_FLOOR_TOP))
    print("  lace tunnels     : 2 x  ~%.1f mm wide x %.1f mm high"
          % (tunnel_w, STAND))


if __name__ == "__main__":
    main()
