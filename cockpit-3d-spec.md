# Sim Cockpit Frame — 3D Model Specification

> **Purpose:** This file is a machine-parseable build specification for generating a 3D model
> of a DIY sim-racing / flight-sim hybrid cockpit. Every structural member, prop, material,
> light, and camera is defined numerically. Generate the model directly from the tables below —
> no dimension should need to be guessed.

---

## 1. Global Conventions

| Property | Value |
|---|---|
| Units | millimeters (mm) |
| Coordinate origin | Rear-left corner of the base frame, at floor level |
| +X axis | Left → Right (width) |
| +Y axis | Rear → Front (toward pedals) |
| +Z axis | Floor → Up (height) |
| Member coordinates | Centerline start → end points unless noted as a plate/prop |
| Plates & props | Defined by center point + W×D×H extents + rotation |
| Rotation convention | Degrees, right-hand rule about the named axis |
| Overall envelope | 560 W × 1600 D × ~1005 H |

**Lumber stock:** all framing members are dimensional 2×4 lumber, actual cross-section
**38 × 89 mm**. Each member row states its cross-section orientation as `thickness-axis × height-axis`
(e.g. `38(X) × 89(Z)` = 38 mm along X, 89 mm along Z).
**Sheet stock:** all plates are 18 mm plywood unless noted.

---

## 2. Assembly Hierarchy

```
CockpitRig (root)
├── BaseFrame            BF-01 … BF-05
├── PedalExtension       PE-01 … PE-04
├── FrontTower
│   ├── Uprights         UP-01, UP-02
│   ├── Crossbar         CB-01
│   ├── Braces           BR-01, BR-02
│   ├── CenterDrop       CD-01
│   ├── SteeringColumn   SC-01
│   └── WheelDeck        WD-01, WD-02, WD-03
├── PCShelf              PS-01, PS-02, PC-01
├── SeatAssembly         SR-01, SR-02, ST-01, ST-02
├── ArmrestShelves
│   ├── Left (throttle)  AR-01, AR-02, AT-01, HT-01
│   └── Right (stick)    AR-03, AR-04, AT-02, HS-01, HS-02
└── MonitorAssembly      MA-01, MA-02, MN-01
```

---

## 3. Structural Members (framing, 2×4 lumber)

| ID | Component | Start (x, y, z) | End (x, y, z) | Cross-section | Length | Notes |
|---|---|---|---|---|---|---|
| BF-01 | Left base rail | (19, 0, 44.5) | (19, 1200, 44.5) | 38(X) × 89(Z) | 1200 | On edge, runs full main-frame depth |
| BF-02 | Right base rail | (541, 0, 44.5) | (541, 1200, 44.5) | 38(X) × 89(Z) | 1200 | Mirror of BF-01 |
| BF-03 | Rear cross member | (38, 19, 44.5) | (522, 19, 44.5) | 38(Y) × 89(Z) | 484 | Butts between rails |
| BF-04 | Mid cross member | (38, 600, 44.5) | (522, 600, 44.5) | 38(Y) × 89(Z) | 484 | Anchors center drop CD-01 |
| BF-05 | Front cross member | (38, 1181, 44.5) | (522, 1181, 44.5) | 38(Y) × 89(Z) | 484 | End of main frame |
| PE-01 | Left extension rail | (19, 1200, 44.5) | (19, 1600, 44.5) | 38(X) × 89(Z) | 400 | Continues BF-01 forward |
| PE-02 | Right extension rail | (541, 1200, 44.5) | (541, 1600, 44.5) | 38(X) × 89(Z) | 400 | Continues BF-02 forward |
| PE-03 | Pedal cross member | (38, 1581, 44.5) | (522, 1581, 44.5) | 38(Y) × 89(Z) | 484 | Front-most member |
| UP-01 | Left upright | (19, 950, 89) | (19, 950, 650) | 38(X) × 89(Y) | 561 | Sits on top of BF-01 |
| UP-02 | Right upright | (541, 950, 89) | (541, 950, 650) | 38(X) × 89(Y) | 561 | Mirror of UP-01 |
| CB-01 | Crossbar | (0, 950, 605.5) | (560, 950, 605.5) | 38(Y) × 89(Z) | 560 | Face-screwed across both uprights; top flush at Z=650 |
| BR-01 | Left diagonal brace | (19, 760, 89) | (19, 950, 400) | 38(X) × 89 | ~364 | Rail → upright, resists wheel torque |
| BR-02 | Right diagonal brace | (541, 760, 89) | (541, 950, 400) | 38(X) × 89 | ~364 | Mirror of BR-01 |
| CD-01 | Center drop | (280, 620, 89) | (280, 620, 300) | 38(X) × 89(Y) | 211 | Vertical, on top of BF-04; foot of steering column |
| SC-01 | Steering column support | (280, 620, 300) | (280, 930, 605) | 38(X) × 89 | ~435 | Angled ~44.5° from horizontal, meets CB-01 underside |
| SR-01 | Front seat riser | (38, 420, 133.5) | (522, 420, 133.5) | 38(Y) × 89(Z) | 484 | On top of rails, Z 89–178 |
| SR-02 | Rear seat riser | (38, 780, 133.5) | (522, 780, 133.5) | 38(Y) × 89(Z) | 484 | On top of rails, Z 89–178 |
| AR-01 | Left armrest post (front) | (19, 700, 89) | (19, 700, 620) | 38(X) × 89(Y) | 531 | Bolted to outside face of BF-01 |
| AR-02 | Left armrest post (rear) | (19, 480, 89) | (19, 480, 620) | 38(X) × 89(Y) | 531 | Bolted to outside face of BF-01 |
| AR-03 | Right armrest post (front) | (541, 700, 89) | (541, 700, 620) | 38(X) × 89(Y) | 531 | Mirror of AR-01 |
| AR-04 | Right armrest post (rear) | (541, 480, 89) | (541, 480, 620) | 38(X) × 89(Y) | 531 | Mirror of AR-02 |

---

## 4. Plates & Shelves (18 mm plywood)

| ID | Component | Center (x, y, z) | Extents W(X) × D(Y) × T | Rotation | Notes |
|---|---|---|---|---|---|
| PE-04 | Pedal plate | (280, 1412, 220) | 480 × 420 × 18 | −35° about X | Inclined; bottom edge center ≈ (280, 1240, 100), top edge center ≈ (280, 1584, 341) |
| WD-01 | Wheel deck | (280, 1000, 659) | 350 × 300 × 18 | −12° about X | Rests on CB-01 + SC-01; tilted toward driver |
| WD-02 | Left deck gusset | (200, 990, 620) | 18 × 200 × 80 | 0 | Triangular gusset, vertical, under WD-01 |
| WD-03 | Right deck gusset | (360, 990, 620) | 18 × 200 × 80 | 0 | Mirror of WD-02 |
| PS-01 | PC shelf plate | (280, 130, 98) | 560 × 260 × 18 | 0 | Spans rail tops at rear, Z 89–107 |
| PS-02 | PC shelf support | (38, 240, 44.5)→(522, 240, 44.5) | 38(Y) × 89(Z) 2×4 | — | Extra cross member under front edge of PS-01 |
| AT-01 | Left HOTAS table (throttle) | (100, 590, 629) | 250 × 300 × 18 | 0 | On AR-01/AR-02, top at Z=638; overhangs inboard to X=225 |
| AT-02 | Right HOTAS table (stick) | (460, 590, 629) | 250 × 300 × 18 | 0 | On AR-03/AR-04, top at Z=638; overhangs inboard to X=335 |

---

## 5. Props (non-structural, modeled as simplified shapes)

| ID | Component | Center (x, y, z) | Extents W(X) × D(Y) × H(Z) | Rotation | Shape / notes |
|---|---|---|---|---|---|
| PC-01 | PC tower | (280, 125, 332) | 450 × 210 × 450 | 0 | Box on PS-01; front (+Y) face has LED strip and mesh texture; clears reclined seat back by ≥75 mm |
| ST-01 | Seat cushion | (280, 630, 330) | 460 × 500 × 140 | −4° about X | Bucket seat base on SR-01/SR-02; top ≈ Z=400, side bolsters raised +60 |
| ST-02 | Seat backrest | (280, 350, 680) | 460 × 120 × 620 | −12° about X | Reclined; bottom hinge at (280, 400, 360), top ≈ (280, 273, 1000); integrated headrest |
| HT-01 | Throttle unit | (100, 590, 698) | 150 × 200 × 120 | 0 | Box on AT-01 with lever angled −20° about X |
| HS-01 | Stick base | (460, 590, 668) | 180 × 180 × 60 | 0 | Box on AT-02 |
| HS-02 | Flight stick | (460, 590, 788) | Ø45 × 180 tall | +8° about Y | Cylinder + grip on HS-01, top ≈ Z=878 |
| MA-01 | Monitor arm pole | (280, 960, 792) | Ø35 × 375 tall | 0 | Steel pole clamped to CB-01, Z 605–980 |
| MA-02 | Monitor arm | (280, 1010, 940) | Ø30 × 100 long | 90° about X | Horizontal reach from pole to monitor VESA mount |
| MN-01 | Monitor 32″ 16:9 | (280, 1080, 790) | 715 × 25 × 425 | −5° about X | Screen faces −Y (toward seat); panel top ≈ Z=1005; 12 mm black bezel |

---

## 6. Materials

| Material | Applies to | Base color (hex) | Texture | Roughness | Specular / notes |
|---|---|---|---|---|---|
| `pine_lumber` | All 2×4 members (BF, PE-01…03, UP, CB, BR, CD, SC, SR, AR) | `#C8A165` | Subtle longitudinal wood grain, occasional knots | 0.75 | Low specular; grain runs along member length |
| `plywood` | PE-04, WD-01…03, PS-01, AT-01, AT-02 | `#D9B98A` | Fine face grain + visible ply layers on edges | 0.7 | Low specular |
| `black_steel` | MA-01, MA-02, bolt heads/washers at joints | `#2B2B2B` | Smooth powder-coat | 0.4 | Medium specular |
| `matte_plastic` | HT-01, HS-01, HS-02, MN-01 bezel, PC-01 body | `#141414` | Fine matte texture | 0.85 | Very low specular |
| `seat_fabric` | ST-01, ST-02 | `#1E1E24` | Woven fabric with red contrast stitching `#E03A3A` on bolster seams | 0.95 | No specular |
| `screen_emissive` | MN-01 front face (inside bezel) | `#9FC4FF` | Emissive; render a dim cockpit-HUD-style image or uniform glow | — | Emission strength ≈ 3; also lights the scene |
| `pc_led` | PC-01 front strip | `#33E0FF` | Emissive strip, 10 mm tall, full width | — | Emission strength ≈ 5 |
| `floor` | Ground plane 3000 × 3500 centered under rig | `#4A4A4F` | Lightly mottled concrete | 0.9 | Receives shadows |

Optional detail: 8 mm hex-head bolt + washer instances at every member-to-member joint
(2 per butt joint, 4 per upright/brace face joint), material `black_steel`.

---

## 7. Lighting Rig

| Light | Type | Position (x, y, z) | Aim / target | Color temp / hex | Intensity | Notes |
|---|---|---|---|---|---|---|
| Key | Directional (sun) | (2000, 1500, 2500) | (280, 700, 400) | 4500 K warm white | 3.0 | Primary shadows, ~40° elevation |
| Fill | Point (soft, radius 500) | (−1500, 300, 1500) | — | 6500 K cool white | 0.8 | Lifts left-side shadows |
| Screen glow | Area 600 × 350 | (280, 1065, 790) | Facing −Y toward seat | `#9FC4FF` | 2.0 | Coplanar with monitor face; simulates screen light on seat/wheel |
| PC LED | Point (radius 200) | (280, 240, 340) | — | `#33E0FF` | 0.6 | Cyan accent spill at rear of rig |

World/ambient: dark studio background `#101014`, ambient strength 0.15.

---

## 8. Camera Angles (render all five)

| # | Name | Position (x, y, z) | Look-at target | Lens (35 mm equiv) | Notes |
|---|---|---|---|---|---|
| 1 | Front three-quarter | (1600, 2400, 1300) | (280, 700, 500) | 35 mm | Hero shot from front-right |
| 2 | Rear three-quarter | (1500, −900, 1300) | (280, 600, 500) | 35 mm | Shows PC shelf, seat back, braces |
| 3 | Left profile | (−1800, 700, 600) | (280, 700, 550) | 50 mm | True side elevation; verify column & brace angles |
| 4 | Top-down | (280, 700, 3000) | (280, 700, 0) | 35 mm | Plan view; verify footprint & shelf overhangs |
| 5 | Cockpit POV | (280, 480, 1050) | (280, 1080, 790) | 24 mm | Eye position of seated driver, looking at screen over the wheel deck |

Render settings: 1920 × 1080, filmic/AgX tone mapping, soft shadows on.

---

## 9. Validation Checks (run after modeling)

1. No framing member intersects another except at declared joints (butt/face contact is expected).
2. PC-01 top (Z=557) clears the reclined seat back plane — minimum 75 mm gap at that height.
3. ST-01 cushion (X 50–510) clears armrest posts AR-01…04 (posts occupy X 0–38 and X 522–560).
4. WD-01 wheel deck top sits at Z≈650–660 and PE-04 pedal plate heel point at Z≈100 — consistent with a seated driver at cushion height Z=400.
5. MN-01 screen center is on the rig centerline X=280 and inside camera 5's frustum.
6. Total bounding box ≈ 560 (X, framing) / 715 (X, monitor overhang) × 1600 (Y) × 1005 (Z).

---

## 10. Output Files

Export the finished model as all of the following, Z-up, millimeter scale:

| File | Format | Purpose |
|---|---|---|
| `cockpit.blend` | Blender native | Editing source with materials, lights, cameras |
| `cockpit.glb` | glTF 2.0 binary | Web/AR viewing, materials embedded |
| `cockpit.stl` | STL (frame geometry only, no props/emissives) | 3D printing a scale model |
| `cockpit.obj` + `.mtl` | Wavefront | Universal interchange |

Plus the five rendered PNGs, named `render-01-front34.png` … `render-05-pov.png`.
