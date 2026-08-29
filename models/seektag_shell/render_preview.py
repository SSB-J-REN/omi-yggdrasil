#!/usr/bin/env python3
"""Dependency-free software renderer -> PNG preview of the shell.
Orthographic projection + z-buffer + flat diffuse shading. Uses only the
standard library (zlib for PNG compression)."""
import math
import struct
import zlib
import sys
import generate_shell as g

W = HGT = 720
BG = (238, 240, 243)
BASE_COL = (196, 120, 210)  # orchid-ish plastic


def rot(v, ax, ay):
    x, y, z = v
    # rotate about x then y
    cy, sy = math.cos(ay), math.sin(ay)
    cx, sx = math.cos(ax), math.sin(ax)
    y, z = y * cx - z * sx, y * sx + z * cx
    x, z = x * cy + z * sy, -x * sy + z * cy
    return (x, y, z)


def render(tris, ax, ay, path, light=(0.3, 0.4, 0.85)):
    lm = math.sqrt(sum(c * c for c in light))
    light = tuple(c / lm for c in light)
    # transform
    tv = [tuple(rot(v, ax, ay) for v in t) for t in tris]
    xs = [v[0] for t in tv for v in t]
    ys = [v[1] for t in tv for v in t]
    zs = [v[2] for t in tv for v in t]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    span = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.15
    scale = W / span

    def to_screen(v):
        sx = (v[0] - cx) * scale + W / 2
        sy = -(v[1] - cy) * scale + HGT / 2
        return sx, sy, v[2]

    zbuf = [-1e18] * (W * HGT)
    img = bytearray()
    for _ in range(W * HGT):
        img += bytes(BG)

    for t in tv:
        # shading from facet normal
        e1 = tuple(t[1][i] - t[0][i] for i in range(3))
        e2 = tuple(t[2][i] - t[0][i] for i in range(3))
        n = (e1[1] * e2[2] - e1[2] * e2[1],
             e1[2] * e2[0] - e1[0] * e2[2],
             e1[0] * e2[1] - e1[1] * e2[0])
        nm = math.sqrt(sum(c * c for c in n)) or 1.0
        n = tuple(c / nm for c in n)
        if n[2] < 0:  # back-facing after projection -> flip for shading
            n = tuple(-c for c in n)
        diff = max(0.0, sum(n[i] * light[i] for i in range(3)))
        shade = 0.35 + 0.65 * diff
        col = tuple(min(255, int(c * shade)) for c in BASE_COL)

        p = [to_screen(v) for v in t]
        minx = max(0, int(min(v[0] for v in p)))
        maxx = min(W - 1, int(max(v[0] for v in p)) + 1)
        miny = max(0, int(min(v[1] for v in p)))
        maxy = min(HGT - 1, int(max(v[1] for v in p)) + 1)
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = p
        denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(denom) < 1e-9:
            continue
        for py in range(miny, maxy + 1):
            for px in range(minx, maxx + 1):
                a = ((y1 - y2) * (px + 0.5 - x2) + (x2 - x1) * (py + 0.5 - y2)) / denom
                b = ((y2 - y0) * (px + 0.5 - x2) + (x0 - x2) * (py + 0.5 - y2)) / denom
                c = 1 - a - b
                if a < 0 or b < 0 or c < 0:
                    continue
                z = a * z0 + b * z1 + c * z2
                idx = py * W + px
                if z > zbuf[idx]:
                    zbuf[idx] = z
                    o = idx * 3
                    img[o], img[o + 1], img[o + 2] = col
    _write_png(img, path)


def _write_png(rgb, path):
    raw = bytearray()
    for y in range(HGT):
        raw.append(0)
        raw += rgb[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, HGT, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    tris = g.build()
    render(tris, math.radians(-58), math.radians(28), "preview_front.png")
    render(tris, math.radians(58), math.radians(28), "preview_back.png")
    print("wrote preview_front.png, preview_back.png")
