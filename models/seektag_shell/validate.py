#!/usr/bin/env python3
"""Per-primitive watertightness check: every edge must be shared by exactly
two triangles within a closed manifold. We check each primitive on its own,
because the final model is a *union* of overlapping solids (globally that is
intentionally non-manifold, which slicers resolve)."""
import generate_shell as g
from collections import defaultdict


def check(tris, label):
    quant = lambda v: tuple(round(c, 4) for c in v)
    edges = defaultdict(int)
    for t in tris:
        vs = [quant(v) for v in t]
        for i in range(3):
            a, b = vs[i], vs[(i + 1) % 3]
            edges[frozenset((a, b))] += 1
    bad = {e: n for e, n in edges.items() if n != 2}
    status = "OK (watertight)" if not bad else "NOT closed: %d bad edges" % len(bad)
    print("  %-22s %6d tris  %s" % (label, len(tris), status))
    return not bad


print("Per-primitive watertightness:")
ok = True
prof = [
    (0.0, g.H), (g.R_OUT, g.H), (g.R_OUT, 0.0), (g.R_LIP, 0.0),
    (g.R_LIP, g.LIP_HEIGHT), (g.R_TRACK, g.LIP_HEIGHT),
    (g.R_TRACK, g.CAVITY_CEIL), (0.0, g.CAVITY_CEIL),
]
ok &= check(g.revolve(prof, g.REV_SEGMENTS), "body (revolve)")
ok &= check(g.dome(0, 0, 0, 6, 4, 3, rot_z=0.5), "dome (petal)")
ok &= check(g.capsule((0, 0), (5, 3), 1.2, 0.0, 2.4), "capsule (letter stroke)")
ok &= check(g.torus((0, 0, 0), g.LOOP_MAJOR_R, g.LOOP_MINOR_R), "keyring torus")
ok &= check(g.neck_block(g.R_OUT - 1.0, 30.0, g.H / 2.0), "neck block")
print("\nALL WATERTIGHT" if ok else "\nSOME PRIMITIVES NOT CLOSED")

# Decorations must never reach the cavity ceiling (the front wall must stay
# solid). Lowest dome point is base_z = H - EMBED.
gap = (g.H - g.EMBED) - g.CAVITY_CEIL
print("\nFront-wall clearance below decorations: %.2f mm (must be > 0)" % gap)
assert gap > 0, "decorations intrude into the cavity!"
