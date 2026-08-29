# J1 — G-Switch `GT-USB-7005A` (LCSC `C5250872`) — 3D model

USB Type-C 24P receptacle, horizontal, board-sink, `L = 10.30 mm`.
Built for **D-050** (ADR-050, `OPEN / CONNECTOR-PHYSICS BLOCK`).
Nothing here binds anything.

---

## 1. Provenance

Both source files were captured in the Phase-D evidence sweep from the
**manufacturer's own domain**, not from an LCSC/EasyEDA cache. Receipts:
`../datasheets/_download_retry_receipt.json`.

| File | URL | SHA-256 |
| --- | --- | --- |
| `GT-USB-7005A.pdf` (2-D drawing) | `dg-switch.com/uploads/soft/230408/GT-USB-7005A.pdf` | `abe0fb3e…9223a0` |
| `GT-USB-7005A-3D.zip` (STEP) | `dg-switch.com/uploads/soft/230408/GT-USB-7005A-3D.zip` | `bac2724e…c0c88fa` |
| `GT-USB-7005A.stp` (inside the zip) | — | `3e8f2300…3ea3b8d5` |

**The drawing PDF has no text layer** — it is a raster scan, so no dimension
string can be extracted from it programmatically. Every number in this
document is therefore measured from the **STEP solid**, not read off the
drawing and not taken from catalogue prose.

The STEP is AP203 from Creo, exported 2022-05-11, as a **single fused solid**
(1 solid, 54 shells, 1 689 faces) with no part names and no usable per-part
colour. It cannot be separated into components, which is why this model was
rebuilt rather than re-skinned.

---

## 2. Datum and axes

| | |
| --- | --- |
| `Z = 0` | **PCB top surface** (the plane the 12 SMT tail solder faces lie on) |
| `-Y` | mating direction — the mouth faces `-Y`; rear at `+Y` |
| `X = 0` | connector centre line |
| units | 1 Blender unit = 1 mm (`scale_length = 0.001`) |

Transform applied to the STEP frame: `Bx = Sx`, `By = -Sz`, `Bz = Sy - 0.400`.

---

## 3. What "Board Sink 1.9" and "CH 0.4" actually mean

ADR-050 lists *"Meaning of 'Board Sink 1.9' / CH 0.4 mm / 'laminated board'"*
as a named hold. The STEP resolves the first two exactly.

The 12 SMT tails have their solder faces on one plane at STEP `Y = +0.400`.
Taking that plane as the PCB top surface:

| Quantity | Value | Matches |
| --- | --- | --- |
| shell bottom below PCB top | **1.880 mm** | "Board Sink 1.9" |
| connector axis below PCB top | **0.400 mm** | "CH = 0.4" |
| shell top above PCB top | 1.080 mm | drawing `1.08` |
| overall height above PCB top | 1.760 mm | |
| overall part height | 3.6415 mm | drawing `3.64` |

Both marketing numbers fall out of one datum choice, so the datum is very
likely correct. This is a **geometric reading of the manufacturer's own STEP.
It is not a bind, and it says nothing about recommended PCB thickness** —
the drawing carries no extractable thickness callout.

### Observation against D-012 (1.60 mm), not a decision

- Sink 1.880 > board 1.600 ⇒ on a 1.60 mm board the shell bottom sits
  **0.280 mm below the board's bottom face**. The part needs a full edge
  cut-out, not a milled pocket, and stands 0.280 mm proud underneath.
- The 12 through-hole pins reach 1.100 mm below the PCB top surface — they
  stop **0.500 mm short** of the bottom of a 1.60 mm board.

Recorded as geometry. D-012 is untouched; D-050 bind gates are unchanged.

---

## 4. Measured dimensions

| Feature | Measured | Drawing callout |
| --- | --- | --- |
| overall (X × Y × Z) | 12.3515 × 10.3015 × 3.6415 | `12.15` footprint / `10.30` L / `3.64` |
| shell outer section | 8.750 × 2.960, corner R 1.150 | `8.75`, `2.96` |
| shell cavity (plug envelope) | 8.350 × 2.560, corner R 0.950 | `8.35 +0.05/-0.03`, `2.56 ±0.04` |
| shell wall | 0.200 | `0.20` |
| corner arc centres | (±3.225, ±0.330) | — |
| tongue | 6.730 wide × 0.700 thick | `6.69 +0.045/-0.055`, `0.70 ±0.05` |
| contacts | 24 × 0.250 wide, 0.500 pitch, 5.500 span | `24-0.25 ±0.04`, `0.50`, `2.75`, `5.50` |
| exposed contact band | 0.931 long | — |
| SMT tails | 12 × 0.200 wide, 0.500 pitch, 0.100 thick | `0.20(12x)` |
| through-hole pins | 12, two rows of 6 | `⌀0.40` holes |
| mounting legs | 4, sheet 0.200, span to ±6.175 | `4-1.50` slots |

### Terminal breakdown — 24 total, **hybrid** SMT + through-hole

| Group | Count | X centres (mm) | Y band (mm) |
| --- | --- | --- | --- |
| SMT tails | 12 | ±0.25, ±0.75, ±1.25, ±1.75, ±2.25, ±2.75 | +4.11 … +4.81 |
| TH pins, front row | 6 | ±0.850, ±1.700, ±2.500 | +2.30 … +2.70 |
| TH pins, rear row | 6 | ±0.400, ±1.300, ±2.875 | +3.18 … +3.50 |

This is a **hybrid part**: it is not a pure SMT footprint. Any footprint work
must carry 12 SMD lands, 12 plated holes and 4 slots.

### Shell stamped features (scanned, not assumed)

Every face of the vendor solid was scanned with an extreme-surface height map
at 0.02 mm resolution. The shell carries exactly two kinds of opening:

| Feature | Extent |
| --- | --- |
| 2 × L-shaped **corner window** — each front leg is lanced out of the shell | `|X| ≥ 2.020` round the corner, `Y −1.680 … −0.700`, everything above `Z = −0.100` |
| 2 × **rear top notch**, open to the shell's rear edge | `|X| 2.838 … 3.213`, `Y +0.112 …` rear edge |

**There are no latch dimples on this part.** An earlier revision of this model
had four; the scan found no deviation from the nominal 1.480 / −1.480 planes
anywhere else on the top or bottom walls, so they were fabricated and have
been deleted. The corner windows are the two gaps visible on the top face in
the LCSC product photographs.

---

## 5. Parts and materials

Object names map to the drawing's materials table.

| Object | Drawing part | Material |
| --- | --- | --- |
| `J1_SHELL_stainless_Ni` | 1 SHELL | stainless steel, Ni plated |
| `J1_GROUNDPLATE_stainless_Ni` | 6 GROUND PLATE | stainless steel, Ni plated |
| `J1_LEGS_stainless_Ni_x4` | 5 LATCH | stainless steel |
| `J1_MIDPLATE_stainless` | 3 MID PLATE | stainless steel |
| `J1_HOUSING_LCP_black`, `J1_TONGUE_LCP`, `J1_TERMINALBLOCK_LCP` | 2 HOUSING | high-temperature plastic, black, UL94 V-0 |
| `J1_CONTACTS_rowA_Au`, `J1_CONTACTS_rowB_Au` | 4 TERMINALS | copper alloy, **Au plating on contact area** |
| `J1_TAILS_SMT_x12`, `J1_PINS_throughhole_x12` | 4 TERMINALS | copper alloy, solder plating |

`REF_vendor_STEP_GT-USB-7005A` (collection `09_reference`, hidden) is the
manufacturer solid itself, tessellated at 0.0035 mm linear deflection and
re-datumed. Use it to measure against; do not ship it as the model.

---

## 6. Files

| File | What it is |
| --- | --- |
| `J1_GT-USB-7005A.blend` | the model, studio, cameras, vendor reference |
| `j1_build.py` | the parametric build — every dimension is a named constant |
| `GT-USB-7005A_vendor_ref.ply` | vendor STEP tessellated + re-datumed |
| `VERIFICATION.json` | assertions + per-part deviation vs the vendor solid |
| `J1_GT-USB-7005A.{obj,stl,glb}` | exports, **millimetres** (glTF viewers assume metres) |
| `render_0*.png` | studio renders |
| `verify_top_{mine,ref}.png`, `verify_front_{mine,ref}.png` | identical orthographic A/B against the vendor solid |

Rebuild:

```sh
/Applications/Blender-4.5.9.app/Contents/MacOS/Blender \
    --background --factory-startup --python j1_build.py
```

---

## 7. Measured vs approximated — read this before trusting a number

**Measured from the vendor solid** (treat as reliable to ~0.01 mm): shell
outer and cavity sections and corner radii, wall thickness, overall envelope,
tongue width/thickness/length, all 24 contact positions and widths, the
exposed contact band, SMT tail and TH pin positions, leg positions and
extents, both shell openings, and the PCB datum.

**Approximated** (silhouette-correct, internal detail simplified):

- the rear housing moulding — modelled as a block, two ribs per side and the
  measured 11-rib castellated comb (0.120 wide on 0.500 pitch) that separates
  the SMT tails at the rear edge; the real moulding has internal cavities the
  fused solid does not expose separately, so the interior is simplified;
- the terminal block that closes the cavity behind the tongue — a plain prism;
- the internal routing of the terminals between contact and tail/pin — the
  fused solid hides it, so the visible ends are correct and the buried runs
  are plausible rather than measured;
- the mid-plate — modelled as a 0.200 steel core showing at the tongue edge;
  its true internal shape is not separable from the fused solid;
- edge breaks/bevels are cosmetic (0.02–0.05 mm) and are not chamfer callouts.

`verify_top_mine.png` / `verify_top_ref.png` are the same orthographic camera
over the rebuild and over the vendor solid — the honest way to see what still
differs. As of this revision the openings, legs, tails, comb and envelope
line up; the residual differences are in the rear moulding's outline detail
and the leg profiles.

Per-part deviation against the vendor solid is in `VERIFICATION.json`.
Interior faces necessarily report a large "deviation" because the vendor
solid has no interior surface to measure against — judge exterior parts only.

---

## 8. This is not a footprint

`PCB_REF_land_pattern_DERIVED_not_a_footprint` is derived from the terminal
geometry for visualisation. It is **not** the manufacturer's recommended land
pattern and must not be used to satisfy the D-050 *"independently rebuilt
symbol and footprint"* gate. `PCB_REF_1p60mm_D012` is a geometry study slab,
not a stackup statement.
