#!/usr/bin/env python3
"""
Build STEP (B-rep CAD) versions of every model, using CadQuery / OpenCASCADE.

Unlike the STL files (triangle meshes), STEP files are true parametric solids
with exact curved surfaces -- editable in Fusion 360, SolidWorks, FreeCAD,
Onshape, etc. This rebuilds the same designs as the .py mesh generators, using
real boolean operations (so, e.g., the shoe tunnels are genuine cut holes and
the monogram uses a real extruded font).

Outputs (next to this file):
    seektag_decorative_shell.step        (flower / mandala pendant)
    seektag_AMP_40mm.step  seektag_AMP_42mm.step
    seektag_LDP_40mm.step  seektag_LDP_42mm.step
    shoe_base.step  shoe_lid.step

    python3 build_step.py
"""

import math
import cadquery as cq

import generate_shell as P   # pendant parameters
import shoe_case as S        # shoe-case parameters

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def dome(cx, cy, base_z, rx, ry, rise, rot_deg=0.0):
    """A raised half-ellipsoid sitting flat on z=base_z (clipped lower half)."""
    s = cq.Solid.makeSphere(1.0, angleDegrees1=-90, angleDegrees2=90,
                            angleDegrees3=360)
    m = cq.Matrix([[rx, 0, 0, 0], [0, ry, 0, 0], [0, 0, rise, 0]])
    s = s.transformGeometry(m)
    if rot_deg:
        s = s.rotate((0, 0, 0), (0, 0, 1), rot_deg)
    s = s.translate((cx, cy, base_z))
    clip = cq.Solid.makeBox(200, 200, rise + 1.0, cq.Vector(cx - 100, cy - 100, base_z))
    return s.intersect(clip)


def pendant_body():
    """Shared pendant body: disc + tracker cavity + snap lip + keyring loop."""
    R_OUT, R_TRACK, R_LIP = P.R_OUT, P.R_TRACK, P.R_LIP
    H, CEIL, LIPH = P.H, P.CAVITY_CEIL, P.LIP_HEIGHT

    body = cq.Workplane("XY").circle(R_OUT).extrude(H)
    # cavity void: narrow lip opening then full-width pocket
    lip = cq.Solid.makeCylinder(R_LIP, LIPH, cq.Vector(0, 0, 0))
    pocket = cq.Solid.makeCylinder(R_TRACK, CEIL - LIPH, cq.Vector(0, 0, LIPH))
    body = body.cut(lip).cut(pocket)

    # keyring loop + neck at +Y
    loop_cy = R_OUT + P.LOOP_NECK + P.LOOP_MAJOR_R - P.LOOP_MINOR_R
    torus = cq.Solid.makeTorus(P.LOOP_MAJOR_R, P.LOOP_MINOR_R,
                               cq.Vector(0, loop_cy, H / 2), cq.Vector(0, 0, 1))
    hw = P.LOOP_MINOR_R * 1.2
    neck = cq.Solid.makeBox(2 * hw, loop_cy - (R_OUT - 1.0) + 1, 2 * hw,
                            cq.Vector(-hw, R_OUT - 1.0, H / 2 - hw))
    return body.union(torus).union(neck), (R_OUT, H, CEIL)


def add_dot_ring(body, H):
    base_z = H - P.EMBED
    r = min(P.DOT_RING_R, P.R_OUT - 3.0)
    for i in range(P.DOT_COUNT):
        ang = 2 * math.pi * (i + 0.5) / P.DOT_COUNT
        body = body.union(dome(r * math.cos(ang), r * math.sin(ang), base_z,
                               P.DOT_R, P.DOT_R, P.DOT_RISE))
    return body


def build_flower():
    body, (R_OUT, H, CEIL) = pendant_body()
    base_z = H - P.EMBED
    body = body.union(dome(0, 0, base_z, P.CENTER_BOSS_R, P.CENTER_BOSS_R,
                           P.CENTER_BOSS_RISE))
    for i in range(P.PETAL_COUNT):
        ang = 2 * math.pi * i / P.PETAL_COUNT
        body = body.union(dome(P.PETAL_RING_R * math.cos(ang),
                               P.PETAL_RING_R * math.sin(ang), base_z,
                               P.PETAL_LEN / 2, P.PETAL_WID / 2, P.PETAL_RISE,
                               rot_deg=math.degrees(ang)))
    body = add_dot_ring(body, H)
    return body


def build_monogram(text, tracker_dia):
    P.TRACKER_DIA = tracker_dia
    P.R_TRACK, P.R_OUT, P.R_LIP, P.H, P.CAVITY_CEIL = P.derived()
    body, (R_OUT, H, CEIL) = pendant_body()
    base_z = H - P.EMBED
    letters = (cq.Workplane("XY").workplane(offset=base_z)
               .text(text, 15.0, P.TEXT_RISE + P.EMBED, fontPath=FONT_PATH,
                     halign="center", valign="center", kind="bold"))
    body = body.union(letters)
    body = add_dot_ring(body, H)
    return body


def build_shoe_base():
    R_OUT, R_TRACK, R_BORE = S.R_OUT, S.R_TRACK, S.R_BORE
    body = cq.Workplane("XY").circle(R_OUT).extrude(S.Z_TOP)
    # cavity: lid bore + shelf step + tracker pocket
    bore = cq.Solid.makeCylinder(R_BORE, S.Z_TOP - S.Z_LEDGE, cq.Vector(0, 0, S.Z_LEDGE))
    pocket = cq.Solid.makeCylinder(R_TRACK, S.Z_LEDGE - S.Z_FLOOR_TOP,
                                   cq.Vector(0, 0, S.Z_FLOOR_TOP))
    body = body.cut(bore).cut(pocket)
    # two lace tunnels (real through holes)
    for sgn in (-1, 1):
        cx = sgn * (S.DIVIDER_HALF + S.TUNNEL_HALF)
        tun = cq.Solid.makeBox(2 * S.TUNNEL_HALF, 4 * R_OUT, S.TUNNEL_H,
                               cq.Vector(cx - S.TUNNEL_HALF, -2 * R_OUT, S.Z_SLAB))
        body = body.cut(tun)
    # snap bead: inward ring near the top rim
    bead = cq.Solid.makeTorus(R_BORE, S.SNAP, cq.Vector(0, 0, S.Z_TOP - 1.0),
                              cq.Vector(0, 0, 1))
    body = body.union(bead)
    return body


def build_shoe_lid():
    lid = cq.Workplane("XY").circle(S.R_LID).extrude(S.LID_TH)
    return lid.edges("%CIRCLE").chamfer(S.BEVEL)


def export(obj, name):
    if hasattr(obj, "val"):
        obj = obj.val()
    cq.exporters.export(obj, name)
    print("  wrote", name)


def main():
    print("Building STEP files...")
    export(build_flower(), "seektag_decorative_shell.step")
    for dia, label in ((40.0, "40mm"), (42.0, "42mm")):
        export(build_monogram("AMP", dia), "seektag_AMP_%s.step" % label)
        export(build_monogram("LDP", dia), "seektag_LDP_%s.step" % label)
    export(build_shoe_base(), "shoe_base.step")
    export(build_shoe_lid(), "shoe_lid.step")
    print("Done.")


if __name__ == "__main__":
    main()
