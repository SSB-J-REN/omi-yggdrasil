#!/usr/bin/env python3
"""Generate the monogram shell variants: initials x tracker sizes.

Produces one STL per (initials, size) combination. All variants share the
decorative dot-ring border and keyring loop; only the centre initials and the
cavity size change.

    python3 generate_variants.py
"""
import generate_shell as g

# (label, tracker diameter mm, tracker thickness mm)
SIZES = [
    ("40mm", 40.0, 8.0),   # standard round SeekTag / AirTag-style tracker
    ("42mm", 42.0, 8.0),   # roomier option if yours measures larger
]
INITIALS = ["AMP", "LDP"]


def main():
    g.STYLE = "monogram"
    made = []
    for label, dia, thick in SIZES:
        g.TRACKER_DIA = dia
        g.TRACKER_THICK = thick
        for text in INITIALS:
            g.TEXT = text
            tris = g.build()
            r_track, r_out, _, h, ceil = g.derived()
            fname = "seektag_%s_%s.stl" % (text, label)
            g.write_stl(tris, fname, name="seektag_%s_%s" % (text, label))
            made.append((fname, len(tris), 2 * r_out, h, 2 * r_track, ceil))

    print("Generated %d variants:\n" % len(made))
    print("  %-26s %7s  %-9s %-8s %s"
          % ("file", "tris", "case OD", "height", "cavity (dia x deep)"))
    for fname, n, od, h, cav, ceil in made:
        print("  %-26s %7d  %6.1fmm  %6.1fmm  %.1f x %.1f mm"
              % (fname, n, od, h, cav, ceil))


if __name__ == "__main__":
    main()
