# Sim Cockpit Frame — 3D Model Specification

> **Purpose:** Machine-parseable build specification for generating a 3D model of a DIY sim
> cockpit built from **1-5/8" Unistrut P1000 steel channel**, per blueprint **SC-001…SC-003**
> (`cockpit_blueprint.pdf`, sheets 1–3). Every structural member, prop, material, light, and
> camera is defined numerically. Generate the model directly from the tables below — no
> dimension should need to be guessed.
>
> **Rig loadout (from blueprint):** WINWING Orion 2 HOTAS · Samsung 49" G93SC QD-OLED
> (44" wide, 1800R curve, 27 lb) · HUANUO ultrawide monitor arm · racing seat on slider rails.

---

## 0. Deviation Note (read first)

The blueprint's side elevation and top plan draw the monitor mast (uprights + crossbar) at the
**rear** of the frame, which would put the screen behind the seated driver. This spec models the
mast at the **front** of the main frame (Y ≈ 47", at the pedal-deck junction) so the monitor
faces the driver — matching the front elevation, where the wheel hub sits between the uprights
and the monitor floats above the crossbar. The diagonal braces and optional center drop are
repositioned with the mast; the PC shelf stays at the rear as drawn. To revert to the literal
as-drawn layout, mirror the mast group (UP, CB, CD, AD, MA, MN, WS, AS, DB members) about Y = 24.

---

## 1. Global Conventions

| Property | Value |
|---|---|
| Units | **inches** (per blueprint; multiply by 25.4 for mm — export at real-world scale) |
| Coordinate origin | Rear-left corner of the base frame, at floor level |
| +X axis | Left → Right (width) |
| +Y axis | Rear → Front (toward pedals) |
| +Z axis | Floor → Up (height) |
| Member coordinates | Centerline start → end points unless noted as a plate/prop |
| Plates & props | Center point + W(X)×D(Y)×H(Z) extents + rotation |
| Rotation convention | Degrees, right-hand rule about the named axis |
| Overall envelope | X −13…41 (crossbar span) × Y 0–72 (total depth) × Z 0–62.2 |

**Strut stock:** all framing is **Unistrut P1000, 1.625" × 1.625"** square channel, 12-gauge,
pre-galvanized. Slotted open face (9/16" slots) **faces inward** toward the rig centerline
(blueprint note 1); on horizontal members the open face points up unless noted.
**Fasteners:** 3/8-16 spring nut + hex bolt at every strut-to-strut joint (blueprint note 2).
**Sheet stock:** 3/4" plywood.

---

## 2. Assembly Hierarchy

```
CockpitRig (root)
├── BaseFrame          CR-R, CR-F, SR-L, SR-R, FT-01…04
├── PedalDeck          PR-L, PR-R, PP-01
├── MonitorMast
│   ├── Uprights       UP-L, UP-R
│   ├── Crossbar       CB-01
│   ├── CenterDrop     CD-01 [OPTIONAL]
│   ├── Braces         DB-L, DB-R
│   ├── ArmAdapter     AD-01
│   └── WheelStubs     WS-L, WS-R, WH-01, WH-02 [OPTIONAL]
├── PCShelf            PS-C1, PS-C2, PC-P1, PC-01
├── SeatAssembly       SB-01, SL-L, SL-R, ST-01, ST-02
├── HOTASTables
│   ├── Left throttle  HL-L, HA-L, HT-PL, TH-01
│   └── Right stick    HL-R, HA-R, HT-PR, JS-01, JS-02
├── ArmrestShelves     AS-L, AS-R
└── MonitorAssembly    MA-01, MA-02, MN-01
```

---

## 3. Structural Members (Unistrut P1000, 1.625" square section)

Section extents are the centerline ± 0.8125" in both perpendicular axes.

| ID | BOM item | Component | Start (x, y, z) | End (x, y, z) | Cut length | Notes |
|---|---|---|---|---|---|---|
| CR-R | 4 | Rear base cross rail | (0, 0.8125, 1.3125) | (28, 0.8125, 1.3125) | 28" | On leveling feet; Z 0.5–2.125 |
| CR-F | 4 | Front base cross rail | (0, 47.1875, 1.3125) | (28, 47.1875, 1.3125) | 28" | On leveling feet; Z 0.5–2.125 |
| SR-L | 3 | Left base side rail | (0.8125, 0, 2.9375) | (0.8125, 48, 2.9375) | 48" | On top of cross rails; Z 2.125–3.75; P1325 flat corners |
| SR-R | 3 | Right base side rail | (27.1875, 0, 2.9375) | (27.1875, 48, 2.9375) | 48" | Mirror of SR-L |
| PR-L | 5 | Left pedal deck rail | (0.8125, 48, 2.9375) | (0.8125, 72, 2.9375) | 24" | Splices to SR-L end, same layer |
| PR-R | 5 | Right pedal deck rail | (27.1875, 48, 2.9375) | (27.1875, 72, 2.9375) | 24" | Mirror of PR-L |
| UP-L | 1 | Left upright | (−0.8125, 47.1875, 0) | (−0.8125, 47.1875, 60) | 60" | Outboard of SR-L; P2751 90° fittings to side + cross rail |
| UP-R | 1 | Right upright | (28.8125, 47.1875, 0) | (28.8125, 47.1875, 60) | 60" | Mirror of UP-L |
| CB-01 | 2 | Monitor crossbar | (−13, 45.5625, 59.1875) | (41, 45.5625, 59.1875) | 54" | Bolted to rear (−Y) faces of uprights; top flush at Z=60; centered X=14 |
| CD-01 | 8 | Center support drop **[OPTIONAL]** | (14, 45.5625, 0) | (14, 45.5625, 58.375) | 58.375" (from 60" stock) | Floor to crossbar underside; P2058 clamps; blueprint note 3 — add only if crossbar flexes; passes between pedal foot paths, omit if it interferes |
| WS-L | 7 | Left steering/yoke stub **[OPTIONAL]** | (11.1875, 47.1875, 2.125) | (11.1875, 47.1875, 16.125) | 14" | Vertical on CR-F top; HOTAS-only config may omit |
| WS-R | 7 | Right steering/yoke stub **[OPTIONAL]** | (16.8125, 47.1875, 2.125) | (16.8125, 47.1875, 16.125) | 14" | Mirror of WS-L |
| PS-C1 | 6 | PC shelf cross support (rear) | (0, 4, 4.5625) | (28, 4, 4.5625) | 28" | On top of side rails; Z 3.75–5.375 |
| PS-C2 | 6 | PC shelf cross support (front) | (0, 14, 4.5625) | (28, 14, 4.5625) | 28" | Same layer as PS-C1 |
| HL-L | 10 | Left HOTAS table leg | (0.8125, 22, 3.75) | (0.8125, 22, 19.75) | 16" | Vertical, on SR-L top |
| HL-R | 10 | Right HOTAS table leg | (27.1875, 22, 3.75) | (27.1875, 22, 19.75) | 16" | Mirror of HL-L |
| HA-L | 10 | Left HOTAS table arm | (−13, 22, 20.5625) | (3, 22, 20.5625) | 16" | Horizontal on HL-L top, cantilevers outboard; Z 19.75–21.375 |
| HA-R | 10 | Right HOTAS table arm | (25, 22, 20.5625) | (41, 22, 20.5625) | 16" | Mirror of HA-L |
| AS-L | 9 | Left armrest/controller shelf stub | (0.8125, 32.375, 28.8125) | (0.8125, 46.375, 28.8125) | 14" | Bolted to inboard face (X=0) of UP-L, cantilevers rearward; shelf height 28" per blueprint |
| AS-R | 9 | Right armrest/controller shelf stub | (27.1875, 32.375, 28.8125) | (27.1875, 46.375, 28.8125) | 14" | Mirror of AS-L |
| DB-L | 18 | Left rear diagonal brace | (0, 46.375, 26) | (0.8125, 26, 3.9) | ~33" (36" flat bar stock) | 1.5" × 1/8" steel flat bar, upright inboard face → SR-L top; slight X-skew, bar twists |
| DB-R | 18 | Right rear diagonal brace | (28, 46.375, 26) | (27.1875, 26, 3.9) | ~33" | Mirror of DB-L |

Fitting hardware (model as simple prop geometry at the named joints):
**P2751 90° fittings** (item 11, ×8) at upright-to-base corners; **P1325 flat corner brackets**
(item 12, ×4) at base inside corners; **P2058 strut clamps** (item 13, ×6) on braces + center
drop; 3/8" hex-bolt heads + spring nuts at every joint (items 14–16) — optional detail level.

---

## 4. Plates & Shelves (3/4" plywood unless noted)

| ID | BOM item | Component | Center (x, y, z) | Extents W(X) × D(Y) × T | Rotation | Notes |
|---|---|---|---|---|---|---|
| PP-01 | 19 | Pedal deck surface | (14, 60.1, 7.2) | 24 × 24 × 0.75 | **+15° about X** | Heel edge (14, 48.5, 4.1) rising to toe edge (14, 71.7, 10.3); blueprint 15° callout |
| PC-P1 | 20 | PC shelf deck | (14, 9, 5.75) | 20 × 16 × 0.75 | 0 | On PS-C1/C2; X 4–24, Y 1–17, top Z=6.125 |
| HT-PL | 21 | Left HOTAS table top (throttle) | (−6.5, 22, 21.75) | 12 × 10 × 0.75 | 0 | On HA-L; top Z=22.125; extends 12" outboard of frame |
| HT-PR | 21 | Right HOTAS table top (joystick) | (34.5, 22, 21.75) | 12 × 10 × 0.75 | 0 | Mirror of HT-PL |
| AD-01 | 22 | HUANUO wall-plate adapter | (14, 44.625, 59.1875) | 6 × 0.25 × 6 | 0 | 1/4" steel plate on rear (−Y) face of CB-01 center; 4× M6×20 bolts (item 23); Z 56.19–62.19 |

---

## 5. Props (equipment & non-structural, simplified shapes)

| ID | BOM item | Component | Center (x, y, z) | Extents / size | Rotation | Notes |
|---|---|---|---|---|---|---|
| FT-01…04 | 24 | Rubber leveling feet | (2, 0.8125, 0.25), (26, 0.8125, 0.25), (2, 47.1875, 0.25), (26, 47.1875, 0.25) | Ø2 × 0.5 pucks | 0 | Under cross-rail corners; frame base starts at Z=0.5 |
| PC-01 | — | SFF PC case | (14, 8, 9.625) | 15 × 12 × 7.5 | 0 | On PC-P1, under/behind seat between base rails; front face carries LED strip |
| SB-01 | — | Seat base pedestal (simplified) | — | 4 legs 1.5" sq from floor Z=0 to Z=11.5 at (8, 17), (20, 17), (8, 31), (20, 31) | 0 | Generic support connecting sliders to floor/frame |
| SL-L / SL-R | 17 | Seat slider rails | (8, 24, 12) / (20, 24, 12) | 1 × 20 × 1 each | 0 | Along Y 14–34, under cushion |
| ST-01 | — | Seat cushion | (14, 24, 14.25) | 20 × 18 × 3.5 | 0 | Top Z=16 (blueprint 16" callout); side bolsters +2 |
| ST-02 | — | Seat backrest + headrest | (14, 13.2, 28.5) | 20 × 4 × 26 | **−15° about X** | Base hinge (14, 16.5, 16); top ≈ (14, 9.8, 41.1); headrest to Z≈43 |
| TH-01 | 27 | WINWING Orion 2 throttle | (−6.5, 22, 24.4) | 9 × 11 × 4.5 + twin levers | 0 | On HT-PL; levers angled −20° about X |
| JS-01 | 27 | WINWING Orion 2 stick base | (34.5, 22, 23.6) | 8 × 8 × 3 | 0 | On HT-PR |
| JS-02 | 27 | Flight stick + grip | (34.5, 22, 29.1) | Ø2 × 8 tall + grip | +8° about Y | Top ≈ Z=34 |
| WH-01 | — | Wheel hub **[OPTIONAL]** | (14, 45, 16.5) | Ø4 × 3 cylinder, axis −Y | 0 | On plate spanning WS-L/WS-R tops (plate 10 × 0.25 × 5, center (14, 46.3, 16.1)) |
| WH-02 | — | Steering wheel rim **[OPTIONAL]** | (14, 43.2, 16.5) | Ø12 torus, tube Ø1.1 | −15° about X | Faces seat; omit WH/WS group for HOTAS-only config |
| MA-01 | 26 | HUANUO arm, upper link | (12, 43.5, 54.5) | Ø1.4 × ~7 long | — | From wall plate at (14, 44.5, 57) to elbow (10, 42.5, 52) |
| MA-02 | 26 | HUANUO arm, forearm link | (12, 41.75, 50) | Ø1.4 × ~6 long | — | Elbow to VESA point (14, 41, 48) |
| MN-01 | 28 | Samsung 49" G93SC monitor | (14, 40, 48) | 44 (chord) × 13.2 × ~4 | Curved, faces −Y | **1800R curve** (R≈70.9"), concave toward seat; edges pull to Y≈36.5; minimal bezel; VESA 100×100 at rear center |

---

## 6. Materials

| Material | Applies to | Base color (hex) | Texture | Roughness | Metallic / notes |
|---|---|---|---|---|---|
| `unistrut_steel` | All P1000 members (CR, SR, PR, UP, CB, CD, WS, PS-C, HL, HA, AS) | `#B8BCC0` | Pre-galvanized zinc, faint spangle; 9/16" slot pattern on open channel face, slots on ~1-7/8" centers | 0.55 | 0.9; open face toward rig centerline |
| `black_steel` | DB-L/R flat bar, AD-01 plate, P2751/P1325 fittings, WH-01 hub | `#2B2B2B` | Smooth painted steel | 0.5 | 0.6 |
| `zinc_hardware` | Spring nuts, hex bolt heads, washers, P2058 clamps | `#A8ACB0` | Bright zinc | 0.4 | 0.9 |
| `plywood` | PP-01, PC-P1, HT-PL, HT-PR | `#D9B98A` | Fine face grain, ply layers visible on edges | 0.7 | 0 |
| `matte_plastic` | TH-01, JS-01/02, MN-01 bezel & housing, MA-01/02 arm, PC-01 body | `#141414` | Fine matte grain; WINWING units dark gray `#23262B` with light-gray grips | 0.85 | 0.1 |
| `seat_fabric` | ST-01, ST-02 | `#1E1E24` | Woven fabric, red contrast stitching `#E03A3A` on bolster seams | 0.95 | 0 |
| `rubber` | FT-01…04 | `#111111` | Matte rubber | 0.9 | 0 |
| `screen_emissive` | MN-01 front face | `#9FC4FF` | Emissive; dim cockpit-HUD-style image or uniform glow across the 1800R curve | — | Emission strength ≈ 3 |
| `pc_led` | PC-01 front strip (10" × 0.4") | `#33E0FF` | Emissive strip | — | Emission strength ≈ 5; spills from under seat |
| `floor` | Ground plane 160 × 220 centered (14, 30) | `#4A4A4F` | Lightly mottled concrete | 0.9 | 0; receives shadows |

---

## 7. Lighting Rig

| Light | Type | Position (x, y, z) | Aim / target | Color | Intensity | Notes |
|---|---|---|---|---|---|---|
| Key | Directional (sun) | (90, 120, 110) | (14, 30, 20) | 4500 K warm white | 3.0 | Primary shadows, ~40° elevation from front-right |
| Fill | Point (soft, radius 20") | (−70, −20, 70) | — | 6500 K cool white | 0.8 | Lifts rear-left shadows |
| Screen glow | Area 42 × 13 | (14, 38, 48) | Facing −Y toward seat | `#9FC4FF` | 2.0 | Just in front of monitor face; lights seat, HOTAS, wheel |
| PC LED | Point (radius 8") | (14, 10, 14) | — | `#33E0FF` | 0.6 | Cyan accent spilling from under the seat |

World/ambient: dark studio background `#101014`, ambient strength 0.15.

---

## 8. Camera Angles (render all five)

| # | Name | Position (x, y, z) | Look-at target | Lens (35 mm equiv) | Notes |
|---|---|---|---|---|---|
| 1 | Front three-quarter | (75, 135, 55) | (14, 35, 28) | 35 mm | Hero shot from front-right; monitor + mast + pedal deck |
| 2 | Rear three-quarter | (72, −60, 52) | (14, 24, 26) | 35 mm | Shows PC shelf, seat back, braces, crossbar rear |
| 3 | Left profile | (−85, 28, 30) | (14, 28, 28) | 50 mm | True side elevation; verify 15° pedal angle, brace runs, table heights |
| 4 | Top-down | (14, 32, 150) | (14, 32, 0) | 35 mm | Plan view; verify 28 × 72 footprint, 12" table overhangs, 54" crossbar span |
| 5 | Cockpit POV | (14, 16, 46) | (14, 40, 48) | 24 mm | Seated eye position looking at screen; throttle lower-left, stick lower-right in frame |

Render settings: 1920 × 1080, filmic/AgX tone mapping, soft shadows on.

---

## 9. Validation Checks (run after modeling)

1. Strut members intersect only at declared joints (face-contact bolted connections expected).
2. Blueprint height callouts hold: seat cushion top **Z=16**, HOTAS table tops **Z≈22.1**,
   armrest shelf stubs **Z≈28.8** ("28" arm height"), uprights **Z=60**, pedal deck **15°**.
3. Footprint: main frame 28 × 48, pedal deck adds 24 → **72" total depth** (blueprint callout).
4. PC-01 (Y 2–14) clears seat cushion (Y 15–33) and slider travel.
5. Monitor bottom edge (Z≈41.4) clears wheel rim top (Z≈22.5) and sits below crossbar top (Z=60);
   screen center (14, 40, 48) is on the rig centerline and ~24" from the POV eye point.
6. HOTAS tables cantilever 12" outboard of the 28" frame on each side (per top plan).
7. Total bounding box ≈ X −13…41 × Y 0–72 × Z 0–62.2.

---

## 10. Bill of Materials Cross-Reference

| Item | Qty | Description | Model IDs | Tag |
|---|---|---|---|---|
| 1 | 2 | 60" Unistrut P1000 — rear uprights | UP-L, UP-R | |
| 2 | 1 | 54" Unistrut P1000 — monitor crossbar | CB-01 | |
| 3 | 2 | 48" Unistrut P1000 — base side rails | SR-L, SR-R | |
| 4 | 2 | 28" Unistrut P1000 — base cross rails | CR-R, CR-F | |
| 5 | 2 | 24" Unistrut P1000 — pedal deck rails | PR-L, PR-R | |
| 6 | 2 | 28" Unistrut P1000 — PC shelf cross supports | PS-C1, PS-C2 | NEW |
| 7 | 2 | 14" Unistrut P1000 — steering/yoke stubs | WS-L, WS-R | OPT |
| 8 | 1 | 60" Unistrut P1000 — center support drop | CD-01 | OPT |
| 9 | 2 | 14" Unistrut P1000 — armrest shelf stubs | AS-L, AS-R | NEW |
| 10 | 4 | 16" Unistrut P1000 — HOTAS table H-frames | HL-L/R, HA-L/R | NEW |
| 11 | 8 | P2751 90° fittings | joint props at upright bases | |
| 12 | 4 | P1325 flat corner brackets | joint props at base corners | |
| 13 | 6 | P2058 strut clamps | joint props on DB, CD | |
| 14–16 | — | Spring nuts + hex bolts 3/8-16 | optional bolt-head instances | |
| 17 | 2 | Universal seat slider rails | SL-L, SL-R | |
| 18 | 2 | 36" × 1/8" steel flat bar — diagonal braces | DB-L, DB-R | |
| 19 | 1 | 3/4" plywood 24 × 24 — pedal deck | PP-01 | |
| 20 | 1 | 3/4" plywood 20 × 16 — PC shelf | PC-P1 | NEW |
| 21 | 2 | 3/4" plywood 12 × 10 — HOTAS table tops | HT-PL, HT-PR | NEW |
| 22 | 1 | 6 × 6 × 1/4" steel plate — arm adapter | AD-01 | NEW |
| 23 | 1 | 4× M6 × 20 mm bolts + washers | AD-01 fasteners | NEW |
| 24 | 4 | Rubber leveling feet | FT-01…04 | |
| 25 | 1 | Zip ties + cable clips | omit from model | |
| 26 | 1 | HUANUO 49" ultrawide arm | MA-01, MA-02 + wall plate | OWNED |
| 27 | 1 | WINWING Orion 2 HOTAS | TH-01, JS-01, JS-02 | OWNED |
| 28 | 1 | Samsung 49" G93SC QD-OLED | MN-01 | MONITOR |

---

## 11. Output Files

Export the finished model as all of the following, Z-up, real-world scale (1 unit = 1 inch,
or converted to mm at ×25.4):

| File | Format | Purpose |
|---|---|---|
| `cockpit.blend` | Blender native | Editing source with materials, lights, cameras |
| `cockpit.glb` | glTF 2.0 binary | Web/AR viewing, materials embedded |
| `cockpit.stl` | STL (frame geometry only, no props/emissives) | 3D printing a scale model |
| `cockpit.obj` + `.mtl` | Wavefront | Universal interchange |

Plus the five rendered PNGs, named `render-01-front34.png` … `render-05-pov.png`.
