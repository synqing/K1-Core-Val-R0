# K1-CORE-VAL-R0 — Placement & Orientation Strategy

```text
STATUS   = STUDY_INPUT
BINDING  = NO
CLASS    = CopperPilot-class geometry proposal (AGENTS.md: proposals until independently reproduced)
GATE     = VAL-G3 / VAL-G4 input
RATIFIED = NOTHING_IN_THIS_FILE
DATE     = 2026-08-28
```

Every coordinate below is a **hypothesis with a stated test**, not a placement. Nothing here
mutates EasyEDA. Promotion requires the normal evidence path and a Captain ruling.

---

## 0. Evidence basis — what is verified, what is not

**Verified (parsed from the project's own data, not recalled from memory):**

- Netlist, per-pad: `ProPrj_K1CoreValR0_20260829.epro2` → PCB document `PAD_NET` records
  (225 components, 146 named nets), cross-checked against
  `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/connectivity-489736-fullpins.json`.
- RT1062 ball geography: all 196 ball names and X/Y positions extracted from the project's own
  `MIMXRT1062DVJ6B` symbol + LFBGA-196 footprint (not from a datasheet from memory).
- ESP32-S3-WROOM-1 pin-side geometry: from the project's own module footprint (left column
  pins 1–14, bottom row 15–26, right column 27–40, antenna beyond the pin-1 end).
- Current board outline ≈ **158.0 × 38.0 mm**; current placeholder positions/rotations
  (U6 at 45°, S3 at 180° antenna-south, J1 north-west, switch row south) read from the PCB doc.
- Authority: AGENTS.md, STATUS.md, D-001…D-050, G3-FLOORPLAN-DOCTRINE, FLOORPLAN-STUDY,
  LAYER-USE-POLICY, STACKUP-STATUS, all interface contracts.

**Known deltas between the uploaded snapshot and living authority (map ≠ territory):**

| # | Snapshot state | Living authority |
|---|---|---|
| Δ1 | `J7-ESP` USB-C + its CC/ESD circuitry present; `USB_DP/DM` terminate at J7/USBLC6 | D-049: J7 **deleted**; one Type-C; USB2422 hub; nets `USB_DP_UP/USB_DM_UP`, `USB_*_DN1/DN2` do not exist yet |
| Δ2 | No USB2422, TPS7A2550 (`5V0_USB_VALID`), TPS2052B anywhere in the archive | D-049 requires all three; hub capture is Phase K, ERC pending |
| Δ3 | J1 symbol is USB4105-GF-A | D-050 binds **GT-USB-7005A / C5250872** |
| Δ4 | `5V_LED_L_SW` / `5V_LED_R_SW` are one-pin islands (FB1/FB2 only); no TPS2561 part wired; `TPS2561_ILIM` only on RILIM-LED | LED eFuse capture incomplete — must close before G4 |
| Δ5 | `OPT_USB_AUD_RT` lands on ball M8 (USB_OTG1_DN) only; L8 (DP) unconnected | Option pair incomplete; D-049 re-plumbs OTG1 to hub DN1 anyway |
| Δ6 | Stray component `USB2` (HYCW78 Type-C footprint, **zero nets**) at (8, 6.4) mm | Orphan — delete at next authorised PCB write |
| Δ7 | `PWR_ENTRY_PG_RT_IOMUX_TBD` net name | Correctly deferred pin — resolved by the §4 sweep, not before |

This strategy is written against **D-049/D-050 living truth**, with the snapshot netlist as the
signal inventory. GPT's brief assumed J1 USB terminates on RT1062 — that is D-044, amended: the
real topology is J1 → ESD → USB2422 US; DN1 → RT OTG1; DN2 → S3 GPIO19/20. The hub island is a
first-class placement object even though it is not in the netlist yet.

---

## 1. What "electrically optimum" means for THIS board

Job to be done (MISSION.md): prove the production architecture — observability, isolation,
reversible configuration, measurement access. Not compactness, not BOM. So the objective
function, in order:

1. Legal RF apertures (2.4 GHz zone D-008; NFC island) with zero signal traffic through them.
2. Short, reference-continuous fast nets: three USB 90 Ω pairs, K1BR, FlexSPI, SAI/PDM, LED data.
3. Compact converter current loops (buck, RT internal DCDC, LED switch) far from audio/NFC.
4. Every option matrix (0R / DNP / iso-R) sitting **at the boundary it arbitrates**, probeable.
5. Human access: probe pads, headers, buttons on reachable edges without crossing prime routing.
6. Whitespace preserved. Board may grow east-west (AGENTS.md) — never compress to look finished.

Orientation is a first-class citizen: each major part's rotation is chosen from its **measured
pin-face → neighbour vector**, with the 0/90/180/270 study shown, before any passive is placed.

---

## 2. Macro floorplan (hypothesis coordinates, board frame: X=0 west … 158 east, Y=0 south … 38 north)

```text
      N edge   J1(x≈20)  [inlet/CC/ESD]   [+5V_LED region →→→]   J2 J3 (x≈105–118)   mic flex J9 (x≈122–130)
    ┌────┬──────────────┬───────────┬──────────────┬──────────────────┬──────────────┬───────────────┐
    │ W  │ POWER ENTRY  │  S3 RADIO │ HUB ISLAND   │   RT1062 CORE    │ AUDIO+MOTION │  NFC ISLAND   │
    │ bay│ + CONVERSION │  (U9@180) │ USB2422+F6   │   (U6 @ 180°)    │ U11 U13 +POL │ U12@90°+match │
    │J6  │ U1 RSH1 U2   │ body 6–31 │ TPS7A2550    │  flash B-side NW │ 3V3_MIC LDO  │ Y2, J10       │
    │SW2 │ U3 buck      │           │ TPS2052B     │  DCDC isl. NNW   │              │ ANTENNA       │
    │SW3 │ TPS2561+FBs  │           │ x≈66–80      │  x≈84–100        │ x≈104–126    │ RESERVE       │
    ├────┴──────────────┼───────────┼──────────────┴──────────────────┴──────────────┤ x≈128–158    │
    │                   │ ANTENNA   │   SOUTH SERVICE CORRIDOR  x≈78–110             │ keep empty,   │
    │                   │ ZONE      │   SW1 U7 | J5 J11 SW4 straps | J4 SWD          │ no mounting   │
    └───────────────────┴───(RF-B)──┴────────────────────────────────────────────────┴───────────────┘
      S edge              x≈47–65: 2.4GHz aperture — ZERO signal escapes (verified §3.2)
```

| Zone | X band (mm) | Contents | Character |
|---|---|---|---|
| Z0 West bay | 0–6 (short edge) | J6-ESP recovery, SW2/SW3 (EN, BOOT) | recessed side service bay (G3 §4 direction) |
| Z1 Power entry + conversion | 4–44, N-biased | J1 (N edge, x≈20), D1, U1 eFuse, RSH1, U2 INA226, U3 TPS62913 + L, TPS2561 + FB1/FB2 | noisy, high-current, mechanical |
| Z2 S3 radio | 47–65 | U9 @ 180°, antenna aperture south | RF; antenna face has **0** signals |
| Z3 Hub island (D-049, to be captured) | 66–80, y≈22–33 | USB2422, TPS7A2550, TPS2052B, straps, VBUS_DET divider | 3× 90 Ω pair star |
| Z4 RT core | 84–100 | U6 @ **180°**, U8 flash **B-side** under NW corner, DCDC inductor NNW, U7+SW1 W/SW | dense digital hub |
| Z5 Audio + motion | 104–126 | U11 @ 180°, iso-R/0R matrices, U5+Q1 (3V3_MIC POL), U13 motion, J8, J9 (N edge) | quiet |
| Z6 NFC island | 128–158 | U12 @ 90°, Y2, matching, J10; **antenna reserve 140–158, all layers, no hardware** | 13.56 MHz RF |
| Z7 South service corridor | 78–110, y 0–6 | J5, J4, J11, SW4, SW1, boot-strap resistors, test pads | humans & instruments |

Differences from GPT's brief, with reasons: RT moves left to x≈92 (it said 10–20 mm left —
agreed, but now **derived**: S3 body ends ≈65, hub needs 66–80, RT west courtyard at ≈84).
LED **data** stays east-short / LED **power** travels (its item 9/10, sharpened by the verified
B0-ball position). Audio sits south-east of RT, not due east at mid-height, because the SAI/PDM
balls verifiably exit the **south** face at 180° (§3.1). J1 is on the **north long edge**
(G3 §1 hypothesis), not the west short edge. NFC east reserve: already repo doctrine; the
external-antenna escape hatch it wanted **already exists** (J10 U.FL, verified on `NFC_ANT`).

---

## 3. Orientation — the first-class citizen

### 3.1 U6-RTC (MIMXRT1062DVJ6B, 196-ball) — **180°**, not 45°

Verified ball-field geography (package frame, from the project library):

| Field | Package region | Carries today (netlist) |
|---|---|---|
| GPIO_AD_B0/B1 (32) | **top edge**, X −2.0…+3.6 | SWD, LPUART1, BOOT_MODE0/1, SAI1 audio, PDM, therm ADC, MIC_PWR_EN |
| GPIO_B0/B1 (32) | **left edge**, X −5.2…−2.0 | LED_D0/D1 (B0_00/01, FlexIO2-capable) |
| GPIO_EMC (42) | bottom-left | unassigned reserve (SAI2/3, FlexPWM, SEMC) |
| GPIO_SD_B0 (6) | bottom centre-right | K1BR SPI (LPSPI1 native) |
| GPIO_SD_B1 (12) | bottom-right | FlexSPI boot flash (fixed group) |
| Fixed analogue | right edge | USB_OTG1 DP/DN (L8/M8), XTAL (P11/N11), RTC_XTAL, POR_B (M7), ONOFF, DCDC (K3/L1/L2/M1/M2, SE corner) |

Rotation study (package top/right/bottom/left → board):

| θ | AD (service+audio) | SD_B0 (K1BR) | USB/XTAL/POR | B (LED) | Verdict |
|---|---|---|---|---|---|
| 0° | N | S | E | W | K1BR faces away from S3's bridge face; hub forced east of RT, ~80 mm from J1 |
| 90° | W | E | N | S | K1BR faces east — S3 is west. Reject |
| **180°** | **S → service corridor** | **N → K1BR corridor** | **W → hub** | **E → LED** | **Selected** |
| 270° | E | W | S | N | K1BR west ✓ but USB pair faces **south**, pulling the hub toward the antenna band; service face buried against audio |

Measured signal escapes for U6 @ 180° (power/GND excluded, from the netlist):
**N = 5** (all K1BR — meets S3's K1BR face in a straight corridor), **W = 9** (FlexSPI local,
POR_B, XTAL local, options; DN1 pair will be added here by D-049), **S = 15** (SWD, LPUART1,
boot straps, SAI, PDM, therm — the entire service/audio face; note the *fixed-silicon* service
pads AD_B0_04/05/12/13, E14/F12 all land on this face), **E = 2** (LED data).

45° is rejected: 0.8 mm BGA escape is a rectilinear dogbone pattern; a diagonal package breaks
the fanout grid, inflates the courtyard, misaligns every corridor above, and D-031 already says
orientation is co-optimised with pinmux — there is no pin-affinity case for 45° here.

Cost of 180° (stated per FLOORPLAN-STUDY): the package's busy SE corner (DCDC + FlexSPI +
SD_B0) maps to the board **NW corner** of the RT zone — the same neighbourhood the hub and K1BR
arrivals want. Mitigation: U8 flash goes **bottom-side directly under the SD_B1 corner**
(double-sided placement is already authorised; cost = ~6 vias in the FlexSPI group), and the RT
DCDC inductor loop is inherently local (K3/L1/L2/M1/M2 cluster + L4-RTC), placed tight NNW.
Audio SAI exits south then turns east into Z5 — one 90° turn, ~10–18 mm, over continuous L2.

### 3.2 U9-ESP (ESP32-S3-WROOM-1) — **180° locked by the antenna**

With the antenna aperture on the south edge (D-008; RF-B notch is the G3 candidate), the module
rotation has **zero freedom** — 180° exactly. The good news, measured: at 180° the faces come
out right without a fight:

| Face | Signals (verified) | Neighbour |
|---|---|---|
| **S (antenna)** | **0** | aperture — keep zero forever |
| N | 5 — K1BR (IO10–14, native FSPI timing) | RT's K1BR face, same latitude ✓ |
| E | 8 — USB_DP/DM_S3 (IO19/20 **fixed**, north end of face), EN, VBUS sense, NFC_IRQ, MOTION_INT_S3, RT_PWR_VALID, S3_POR_REQ | hub (USB), east spine (the rest) |
| W | 5 — UART0 TX/RX (fixed), IO0, I2C_SDA/SCL | J6/SW west bay ✓ — but I2C belongs east: **re-sweep** (§4) |

### 3.3 Orientation table — remaining majors (angle in board frame; every entry pin-derived)

| Part | θ | Pin-facing reason (verified faces) | Cost |
|---|---|---|---|
| J1-PWR1 (GT-USB-7005A) | 180° (mate north) | Receptacle mates off the N edge; A/B rows symmetric; shell tabs into GND per D-050 | inlet current + US pair share one part — corridor discipline (§5) |
| U1 eFuse TPS259474 | 0° | IN (p5) on W face ← J1 filter; OUT (p6) E → RSH1; power flows W→E in one line | PG pin faces W — PG_RT route crosses back east (slow net, L4) |
| RSH1 → U2 INA226 | 0° | RSH1 axial W→E inline; U2 directly S of shunt, VIN+/VIN− Kelvin stubs symmetric, north face | I2C exits S/E face into the L4 spine going east — long but slow |
| U3 TPS62913 + L | 0°, loop closed N | VIN (p6, E face) taps 5V_SYS trunk; SW (p2, W) → inductor immediately W; FB/SS/PG on N away from SW node | keep ≥15 mm from U11/mic anything; buck sits x≈32–40 |
| TPS2561 + FB1/FB2 (Δ4) | capture first | IN near 5V_SYS trunk; OUT→FB→`+5V_LED_x` **region** on L3 heading east | ~70 mm power run to J2/J3 — paid in copper area, not in data-edge quality |
| USB2422 (Δ2) | US pins → NW, DN1 → E, DN2 → W | orient from the real QFN-24 pin map at capture — the island position is fixed here, the rotation is decided the day the footprint exists | if the pinout fights (US and DN adjacent), bias for DN1/DN2 shortness; US pair tolerates the longer run |
| U8 IS25LP064A | B-side, under RT SD_B1 corner | six FlexSPI nets ≤8 mm, via-in-group | bottom-side assembly (already Standard PCBA); 6 via pairs |
| U7 TPS3808 + SW1 | 0°, W of RT (x≈81) | RESET#/MR# on E face → POR_B ball M7 (RT W face at 180°); SW1 pushes S into service corridor reach | none material |
| U11 ADC6120 | **180°** | TDM face (SDOUT/BCLK/FSYNC, pkg S) → **N** toward RT's audio exit; I2C/PDM-CLK face (pkg E) → **W** into the spine; PDM-DATA/IN face (pkg W) → **E** toward J9 flex arrival; AVDD/VREF/MICBIAS-MCLK (pkg N) → **S** quiet cap shelf + J8 | ext-clock header J8 sits S of U11 in the corridor — acceptable, it is test gear access |
| U5 TLV75533 + Q1 (3V3_MIC) | 0°, at Z5 edge x≈118 | point-of-load: OUT (W face) → FB5 → J9 pin 1; IN taps 5V_SYS spine | GPT item 8 confirmed by netlist: mic rail is POL, not a Z1 resident |
| U13 LIS2DH12 | 0°, x≈122 y≈18 | SDA/SCL (S face) drop into the L4 spine; INT1 (W face) → 0R XOR matrix placed W of it | final position is **mechanical** (contract: rigid, near structural centre) — re-site when mounting triangle lands |
| U12 ST25R3916B | **90°** | digital face (I2C, IRQ; pkg N) → **W** toward incoming spine; RF face (RFO1/VDD_TX/DR; pkg S) → **E** into matching → antenna; RFI (pkg E) → N short; XTAL face (pkg W) → **S**, Y2 tucked local | matching stays over solid L2, no vias in match path (contract); antenna reserve stays empty of mounting hardware |
| U14/U15 74AHCT | at J2/J3, Y-face → connector | A/OE (E face) receive 3.3 V data from RT's E face; Y (W face) exits ≤3 mm into J2/J3 pin 2 | 3.3 V data crosses ~12–18 mm from RT — fine; **5 V post-shifter stubs stay <3 mm** |
| J2/J3 XH | 90°, wires exit N | N-edge exit x≈105–118; +5V_LED region arrives on L3 | harness study may move both to one end — decide at G3 mechanics, cheap to slide along N edge |
| J9 FFC-10 | contacts S, flex exits N | PDM_CLK/DAT + 3V3_MIC_FLEX + grounds; interleaved GND already in connector pinout (verified 2/4/6 = GND) | exit position is enclosure-owned — G3 mechanical input, flagged open |
| J4 Cortex-10 | keyed S, x≈100–108 | SWD balls land RT S face E half at 180°; POR_B on p10 already | none |
| J5 UART 1×4 | S edge x≈88–96 | LPUART1 fixed balls land S face W half | none |
| J11 + SW4 | S edge x≈93–99 | OPT_* nets terminate beside the straps they arbitrate; SDL_SW → R61 → BOOT_MODE0 adjacent | none |
| J6 + SW2/SW3 | W short edge bay | UART0 fixed pins exit S3's W face; EN/BOOT buttons are slow nets | EN pin is on S3's E face — ~20 mm walk for one slow net; accepted |
| J10 U.FL | as antenna study dictates | already on `NFC_ANT` — this IS the external-antenna escape hatch | none; keep clear of the loop field |
| Y1 24 MHz | tight to RT XTALI/XTALO (W face at 180°) | XTALI P11 / XTALO N11 + R13 series — crystal universe ≤3 mm | none |
| Y2 27.12 MHz | tight to U12 S face | XTI/XTO local | none |

---

## 4. Pin/GPIO assignment doctrine — placement first, IOMUX second (D-031, enforced)

**The failure this kills:** pre-selecting MCU pins at schematic time, then discovering at layout
that every corridor crosses every other. The register already forbids it in spirit
(AGENTS.md "Do not assign GPIO before ownership and physical requirements are understood";
D-031 "flexible pinmux, package orientation and BGA escape are co-optimised at VAL-G3";
JLC-LAYOUT-READY requires "final layout-relevant IOMUX" **after** JLC-SCH-READY). This section
makes it mechanical.

### 4.1 Pin classes (verified against the project symbol + D-020)

**Class F — fixed silicon. Never sweepable:**

- RT: USB_OTG1_DP/DN (L8/M8), USB_OTG1_VBUS (N6), XTALI/XTALO (P11/N11), RTC_XTAL (N9/P9),
  DCDC group (K3/L1/L2/M1/M2/N1/N2/J5/K4), POR_B (M7), ONOFF (M6), TEST_MODE (K6), WAKEUP (L6),
  PMIC_* (K7/L7), BOOT_MODE0/1 (F11/G14 = AD_B0_04/05), LPUART1 boot console
  (K14/L14 = AD_B0_12/13), FlexSPI-A boot group (SD_B1), all supplies/caps.
- S3: USB (IO19/20 = module pins 13/14), strapping IO0/IO3/IO45/IO46, UART0 console
  (TXD0/RXD0 pins 37/36), EN; IO35–37 unavailable on N16R8 (octal PSRAM).

**Class G — group-constrained. The *group* is chosen by geometry; members move together:**
SAI1/2/3 pad sets; LPSPI1/3/4 sets (K1BR); LPI2C1–4 sets; FlexIO2 (LED — B0/B1 bank only, which
is why LED data faces east at 180° and must stay in that bank); ADC-capable pads only for
LED_THERM_L/R; FlexPWM sets. On S3 the GPIO matrix makes nearly everything Class M, with the
caveat that K1BR stays on IO10–13 (native FSPI timing) unless the corridor proves otherwise.

**Class M — matrix/mux free. Assigned ONLY by the §4.2 sweep:** every remaining GPIO on both
parts — IRQs, enables, straps' companions, option lines, `PWR_ENTRY_PG_RT_IOMUX_TBD` (the
netlist already names the deferral — keep that discipline).

**Standing rule:** every Class-G/M assignment now present in the schematic is *provisional
wiring for ERC completeness*, not authority. The sweep may rewrite any of them; the sheet is
updated in one closed transaction before JLC-LAYOUT-READY. No agent "optimises" a GPIO choice
during capture, ever.

### 4.2 The geometric sweep (runs once, after G4 placement freeze)

1. Freeze zones, orientations, corridor definitions (§2, §3, §5) and the outline.
2. For each Class-G peripheral, compute the centroid of each *legal* pad-set; pick the set whose
   centroid faces the target corridor (e.g. SAI1-on-AD_B1 east-half beats SAI2-on-EMC for a
   south-east audio zone; LPSPI1-on-SD_B0 keeps K1BR on the north face).
3. Within each face, order individual Class-M signals to match the left-to-right order of their
   destinations — an uncrossing pass; crossings that remain are counted, not shrugged at.
4. Re-run the escape-pressure table (§5) with the real assignment. One iteration back to step 2
   is allowed; more than one means the placement, not the pinmux, is wrong.
5. Update the canonical sheet in closed transactions (mutation gate, screenshots, read-back),
   then and only then run the BGA escape study D-026/D-031 demands.

### 4.3 Sweep targets already visible in the verified netlist

- S3 `I2C_SDA/SCL` currently exit the **west** face (IO1/IO2) while every load except INA226
  sits east → re-sweep to east-face pins (IO4–IO8 field).
- S3 slow easts (NFC_IRQ, MOTION_INT_S3, RT_PWR_VALID, S3_POR_REQ) already sit on the east
  face — keep; VBUS sense stays adjacent to the USB pins.
- RT `LED_THERM_L/R` must stay on ADC-capable AD pads (Class G), so they land on the south
  face; route on L4. Do not "tidy" them onto non-ADC balls.
- RT K1BR stays SD_B0 (north face at 180°); RT audio sweeps within AD_B1 to the east half of
  the south face; SWD/UART/straps are Class F and conveniently already on that face.

---

## 5. Corridors and escape pressure (weights per FLOORPLAN-STUDY)

| Corridor | Contents | Pressure | Layer / reference |
|---|---|---|---|
| C1 North power | J1 inlet → Z1; `+5V_LED` region east; 5V_SYS trunk | power-corridor calc, not an escape | L3 regions + top reinforcement, via arrays |
| C2 K1BR bridge | 5 signals + grounds, S3-N ↔ RT-N, straight, series-R at source (R23-family already in netlist ✓), TP1-family probes in-corridor | 5 × w2 = 10 | L1 over L2, ≥4 mm width reserved |
| C3 USB star | US pair hub→J1 (~45 mm, N corridor); DN1 hub→RT-W (~8 mm); DN2 hub→S3-E (~6 mm); all 90 Ω | 3 coupled routes, high constraint | L1 over continuous L2 only; ESD upstream only (contract) |
| C4 South service | SWD ×2, UART ×2, straps ×2, options ×4, buttons | ~10 × w1 | L1/L4; keeps humans off prime routing |
| C5 I2C spine | SDA/SCL east from S3 (+ west spur to INA226) + IRQ returns | ~5 × w1 | **L4** (the layer policy's designated slow layer) |
| C6 Audio | MCLK/BCLK/FSYNC/DOUT RT-S → U11-N (~12 mm incl. iso-R row); PDM J9 → U11/RT | 4 × w2.5 + 2 × w2 | L1 over L2; iso/0R matrices mid-corridor, probeable |
| C7 LED data | 2 × 3.3 V fast-edge RT-E → shifters at J2/J3 | 2 × w2 | L1; 5 V side <3 mm |
| C8 NFC digital | SDA/SCL/IRQ/EN into U12-W | 4 × w1 | L4 → L1 at island edge |
| RF apertures | S3 south aperture; NFC east reserve | not escapes | all-layer keepouts, zero traffic |

Hot spot by inspection: the **RT NW corner** (C2 arrival + C3 DN1 + FlexSPI-under + DCDC
island). This is the corridor the G4 escape study must clear **first**; if it fails, the
relief valve is stretching Z3–Z4 east (board may grow), not squeezing the antenna gap.

Ground: L2/L5 stay unbroken (LAYER-USE-POLICY; GPT item 23 agrees with standing doctrine).
No AGND/DGND moats. Quiet is achieved by the zone gradient + POL filtering above.

---

## 6. Red team — what breaks this plan, and the test that catches it

1. **USB2422 pinout defeats the Z3 star** (US/DN faces wrong way round). Test: the day the
   footprint is real, run the same face study as §3; if US and DN1 end up adjacent, slide the
   island north and let the US pair take the detour, never DN1/DN2.
2. **BGA escape at RT NW fails on six layers** (D-026 OPEN). Test: fanout study on the frozen
   placement before any routing; escalation path is D-022's evidence-triggered 8-layer, with
   "area before layers" tried first.
3. **RF-B notch fails detuning/clearance** against the real enclosure. Fall-back is RF-A
   overhang (G3 §3) — Z2's x-band is unchanged either way, which is why nothing else here
   depends on the notch choice.
4. **Mic flex exit lands elsewhere** (enclosure-owned). J9 slides along the north edge without
   disturbing C6's order; if it must exit south, U11 flips 0° and the audio shelf mirrors —
   cost: PDM crosses C4. Flag to G3 mechanics now.
5. **Hub ERC (Phase K) changes VBUS plumbing** — F6-B wiring touches Z1/Z3 only; contained.
6. **Anomaly 3 hold** (Single-TT) — no placement consequence; do not let anyone argue USB audio
   proximity "optimisations" into Z4 on its back.
7. **Motion mounting triangle** (G3 §5) may relocate U13 — its buses are slow; re-site freely,
   but never onto the NFC reserve or a cantilever.
8. **The 15-signal south face congests** where C4 and C6 share x≈88–110. Test in the sweep's
   crossing count; relief: move J5/J11 west along the edge (slow nets stretch cheaply).

## 7. Cost ledger (no proposal without its price)

| Proposal | Benefit | Cost |
|---|---|---|
| RT @ 180° | hub W, K1BR N, service S, LED E — all verified faces | DCDC+FlexSPI+bridge share NW corner; flash goes B-side (+6 via pairs) |
| Hub island Z3 centre-north | DN1 8 mm, DN2 6 mm, antenna kept ≥25 mm from all USB | US pair pays ~45 mm (the pair that best tolerates it) |
| LED power travels / data short | edge-rate integrity at the shifters; loops local | ~70 mm of L3 region copper + stitching |
| Audio SE shelf | SAI drop is one turn; PDM meets flex arrival; POL mic rail | J8/ext-clock access sits inside C4's east end |
| J1 north-edge x≈20 | inlet + US on one edge; far from aperture; W mounting pair takes insertion load | N edge x<44 becomes the board's densest seam (C1+C3) |
| South service corridor x≈78–110 | every human touchpoint on one reachable edge, buffer between RF and audio | 15-signal south face must be sequenced by the sweep |

## 8. Handoff

- VAL-G3 owes this file the same verdict it owes G3-FLOORPLAN-DOCTRINE: promote each hypothesis
  with evidence or record why it dropped (G3 §7 discipline).
- Before G4: close Δ1–Δ6 (hub capture, J7 deletion, TPS2561, J1 MPN swap, orphan `USB2`).
- G4 order: outline + mounting → Z-anchors (J1, U9, U6, U12) at the §3 orientations → Z3 island
  → corridors reserved → §4.2 sweep → escape study → passives collapse onto owners → freeze.
- DeepPCB remains routing-only (AGENTS.md; F79). This document is placement engineering input,
  never a router constraint file.
