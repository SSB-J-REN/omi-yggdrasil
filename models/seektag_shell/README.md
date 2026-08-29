# SeekTag Decorative Shell

A decorative snap-in case for a round **SeekTag / AirTag-style tracker**
(SeekTag `TAG03NC`, CR2032-powered, ~40 mm dia × ~8 mm thick). The tracker
snaps into the back; the front shows a raised flower / mandala relief, and a
keyring loop at the top lets you hang it from keys, a bag, or a zipper.

![front](preview_front.png)
![cavity](preview_cavity.png)

| | |
|---|---|
| Case outer diameter | **46 mm** |
| Case height | **11 mm** (up to ~14.4 mm at the flower peak) |
| Cavity | **40.8 mm dia × 8.5 mm deep** |
| Fits tracker | 40 mm dia × 8 mm (with 0.4 mm radial + 0.5 mm depth clearance) |
| Retaining lip | 1.2 mm overhang — snaps over the tracker edge |
| Keyring loop | 10 mm OD ring, 4 mm hole |

## Files

- `generate_shell.py` — parametric generator (pure Python, **no dependencies**).
- `seektag_decorative_shell.stl` — the ready-to-print model (ASCII STL).
- `validate.py` — checks each primitive is watertight and that the decorations
  don't intrude into the tracker cavity.
- `render_preview.py` — dependency-free software renderer for the preview PNGs.

## Regenerating / resizing

Everything is parametric. **Measure your tracker with calipers** and edit the
values at the top of `generate_shell.py` — most importantly:

```python
TRACKER_DIA   = 40.0   # your tracker's diameter
TRACKER_THICK = 8.0    # your tracker's thickness
FIT_CLEARANCE = 0.4    # loosen (0.5) if too tight, tighten (0.3) if too loose
```

Then:

```bash
python3 generate_shell.py seektag_decorative_shell.stl   # rebuild the STL
python3 validate.py                                      # sanity-check it
python3 render_preview.py                                # refresh previews
```

You can also restyle the front: `PETAL_COUNT`, `PETAL_LEN`, `PETAL_RISE`,
`DOT_COUNT`, `CENTER_BOSS_R`, etc.

## Printing notes

- **Orientation:** print with the **open cavity facing down** (decorative
  front up). No supports needed; the keyring loop bridges fine at this size.
- **Material:** PLA or PETG. PETG gives the snap lip a bit more springiness.
- **Settings:** 0.2 mm layers, 3 walls, 15–20% infill.
- **Fit:** the tracker snaps past the 1.2 mm lip and is held by it. If your
  slicer/printer runs tight, bump `FIT_CLEARANCE` to 0.5 and reprint. The mesh
  is a union of individually watertight solids, so slicers merge it into one
  solid body automatically.

## How it's built

The model is a union of watertight primitives (a slicer merges overlapping
solids into one object):

- **Body** — a solid of revolution whose cross-section carves out the cavity
  and the inward snap lip.
- **Decorations** — flat-based domes (half-ellipsoids) for the petals, centre
  boss, and accent dots. Being flat-based, they rise off the front face but
  never dip into the cavity behind the front wall.
- **Keyring loop** — a torus plus a short neck bridging it to the body rim.
