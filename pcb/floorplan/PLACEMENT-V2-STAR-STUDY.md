# K1-CORE-VAL-R0 — Placement Architecture Variant 2: RT-centric star / dual-spine

```text
STATUS   = STUDY_INPUT (adversarial architecture study)
BINDING  = NO — nothing here binds the authoritative PCB
CLASS    = CopperPilot-class geometry proposal
GATE     = VAL-G3 / VAL-G4 input, companion to PLACEMENT-ORIENTATION-STRATEGY.md (V1)
RATIFIED = NOTHING_IN_THIS_FILE
DATE     = 2026-08-29
```

V2 is not a rearrangement of V1. It was derived from a blank 155.0 × 38.0 board in the
mandated physical order (§2), against the V1 premortem (§9), using the same verified data
set as V1: the parsed .epro2 netlist, the project's own RT1062 ball map and ESP32-S3 module
pin geometry. Every rotation claim below was recomputed from extracted ball/pin coordinates,
not re-used from V1.

**Study constants honoured:** 155.0 × 38.0 × 1.60 mm six-layer (V1's render used the .epro2
snapshot outline of 158.0 mm — the delta is declared, not hidden). J1 for this study is
**TE 2129691-1 / C590834** (catalogue-level mechanics: SMT signal contacts + through-hole
shell posts; exact drawing dimensions to be re-verified against the TE customer drawing
before any promotion — flagged, not assumed). Ownership, interfaces, two LED channels,
continuous grounds: unchanged.

---

## 1. V2 thesis

RT1062 is the electrical connectivity centroid, so it sits near the geometric centre of the
usable board and every latency- or integrity-critical interface attaches to the package face
that natively carries it. Mechanically and RF-committed functions are pushed to the
perimeter. Long runs are permitted only for slow control and deliberately engineered power
distribution. Two spines: **north** = USB, high current, LED power, anchored connectors;
**south** = service, isolation, low-energy validation. The S3↔RT bridge gets a **sovereign
corridor** that nothing else may occupy.

The single biggest structural move: **the S3 antenna leaves the south long edge and takes
the west short edge.** That one decision de-conflicts almost everything the V1 premortem
worries about (§2.2).

## 2. Derivation in the mandated order

### 2.1 Outline, connector mechanics, mounting
- Outline: plain 155.0 × 38.0 rectangle, r2 corners, **no notches** — with the antenna on
  the short edge, no mid-edge RF cut-away is needed at all. Simplest possible profile;
  panelises trivially.
- J1 (TE 2129691-1): north edge, x≈44. Through-hole shell posts take the insertion load
  into the barrels — the reason this MPN is the study part — supplemented by a passive
  support pad under the connector edge and the H1 mounting point 8 mm west.
- Mounting (3-point kinematic + passive 4th, G3 default): H1 (36, 31.5), H2 (36, 8),
  H3 (124.5, 33) — all outside both RF fields, H3 west of the x=128 reserve, H1/H2 clear
  of the recovery header and service row; P4 passive rest under J1 at (48, 36.5).
  Hypothesis geometry; the enclosure study owns final numbers.

### 2.2 RF apertures
- **S3 antenna, west short edge.** Module rotated 90° CCW: antenna section occupies
  x 0.8–6.8 over board material with a **full six-layer copper/via/component keepout**
  x 0–8.5, y 8.5–29.5, plus a 3-D keepout volume projecting ≥15 mm beyond the west edge
  (no metal, no cables, no standoffs — enclosure end-cap territory). Verified consequence
  of the rotation (from the module's own pin map): the antenna face carries zero signals,
  the K1BR pads (IO10–14) land on the module's **east face**, USB (IO19/20, fixed) lands
  on the **south face east end**, UART0 (fixed) on the **north face west end**, EN on the
  south face west end. Espressif's three valid arrangements include antenna-at-edge with
  keepout beneath; a short edge is as valid as a long one. RF-A/RF-B on the south edge
  remain V1's position — V2 exists to test this alternative.
- **NFC reserve, east far end:** x 128–155, full height, genuinely empty — no mounting
  hardware, no cable paths, no metal in the loop airspace. ST25R3916B island sits west of
  it (§2.14-adjacent), not inside it.

### 2.3 Cable mating / bend volumes
North: J1 plug body + cable bend (≥10 mm projection), LED cables at J2/J3 (x 105–120).
South: mic flex exit at the audio enclave (x≈92) — deliberately the opposite edge from LED
cables, and **nowhere near the NFC reserve** (V1's flex exit at x≈130.5 north sat in the
reserve's corner airspace — a real finding of this study). West: nothing but antenna
clearance. East: U.FL test lead only, dressed away from the loop.

### 2.4 RT1062 electrical centroid and rotation — **θ = 90°**
Centre: **(68, 19)** — middle third, pulled slightly west of the pure centroid so the east
side holds audio + motion + NFC digital without compression.

Rotation study (package faces from the extracted ball map: top = AD banks; bottom = EMC +
SD_B0 + SD_B1 + DCDC; right = USB/XTAL/POR analogue; left = B banks):

| θ | K1BR→W possible? | USB→N possible? | Verdict |
|---|---|---|---|
| 0 | only via B-bank SPI (left face W) | no — USB lands E | reject |
| 90 | **yes — LPSPI3 on the AD face (top→W)** | **yes — OTG1 balls escape N** | **selected** |
| 180 | no (SD_B0 lands N) | no (USB lands W) | reject |
| 270 | yes (SD_B0 bottom→W) | no — USB lands S | reject; also puts AD service face E into audio |

The decisive fact: SD_B0 (native LPSPI1) and the USB balls sit on **adjacent** package
faces, but V2 wants them on W and N — which is the opposite chirality. No rotation of a
BGA can do it. Two legal Class-G moves resolve it, and this is exactly the
pinmux-after-geometry doctrine (D-031) doing real work:
- **K1BR moves to LPSPI3** with pads on the AD face (candidate sets GPIO_AD_B0_00–03 /
  GPIO_AD_B1_12–15 — both land on the west face at θ=90; final set chosen by the sweep;
  pad-set legality to be re-verified against IMXRT1060RM at capture).
- **Audio moves to SAI2 (+SAI3 for the PDM experiment) on the EMC bank** — east face.

Verified face map at θ=90 (ball (x,y) → board (−y, x)):

| Board face | Carries (recomputed from real balls) |
|---|---|
| **W** | K1BR (LPSPI3/AD), LPUART1 K14/L14 (fixed, N half), SWD E14/F12 (fixed, S half), boot straps F11/G14 (fixed), LED_THERM ADC inputs |
| **N** | USB_OTG1 L8/M8 (fixed) centre, XTAL P11/N11 (fixed) W half, POR_B M7, FlexSPI SD_B1 E end |
| **E** | SAI2/SAI3 audio (EMC, S half), DCDC island (fixed, N end), EMC spares |
| **S** | LED data (FlexIO2 on B banks), B-bank spares |

### 2.5 BGA escape faces
Approximate signal escapes: W ≈ 13 (K1BR 5 + UART 2 + SWD 2 + straps 2 + therm 2), N ≈ 9
(USB 2 + FlexSPI 6 + POR 1), E ≈ 7 (SAI/PDM 6 + spares), S ≈ 3 (LED 2 + spare). Worst face
13 vs V1's 15; no face is triple-booked with unrelated domains except W (see §11 #1), and
the NW-corner pile-up of V1 (K1BR + DN1 + FlexSPI + DCDC in one corner) is gone: FlexSPI NE,
DCDC E-N, K1BR W, USB N — four different sectors.

### 2.6 Sovereign K1BR corridor
S3 east face (x≈26.5, y 16–23.5) → RT west face (x=62, y≈15.5–22.5). **Straight, ~36 mm,
zero bends, zero vias, L1 over continuous L2.** Nothing else lives in x 26.5–62 × y 15–24:
not the hub, not power, not service. One documented exception crosses it perpendicular
(§2.7). Series-R + test points sit at the S3 end (already in the netlist: R23-family, TP1-4).

### 2.7 USB point-to-point topology
Hub island north of the corridor and NW of RT: USB2422 at (58, 29.5), TPS7A2550 (52, 31.5),
TPS2052B (62, 31.5), straps B-side (§7).
- **US:** J1 (44, 35.3) → hub: ~15 mm, L1.
- **DN1 (HS):** hub → RT OTG1 balls (north face): ~10 mm straight drop, L1.
- **DN2 (FS):** hub → S3 USB pads (module south face east end, ≈(20.5, 9.6)). The naive
  path would cross the corridor; the derived path does not: west along y≈29 on L1 (north
  of the corridor band), transition to L6 at x≈24.8 and run **south under the module
  body** (body, not antenna — under-body copper is legal where under-antenna copper is
  not), resurfacing at the pad row. ~50 mm total, 2 layer transitions, **zero corridor
  crossings** — the corridor stays fully sovereign. Deliberate allocation: the long,
  transitioned pair is the **full-speed** one, where V1 gave its long run to the HS
  upstream pair.
- No USB segment comes within 35 mm of the antenna keepout.

### 2.8 RT ↔ flash
U8 **B-side, directly under the SD_B1 corner — now the NE corner** (θ=90), ≤8 mm nets,
6 signal vias. Unlike V1, the corner above it holds only the DCDC island — the hub and
bridge no longer compete for the same corner.

### 2.9 RT ↔ audio — the quiet enclave
Enclave: **x 80–102, y 3.5–12.5**, attached to RT's east face south half (the SAI2/EMC
escape field), with one signal gate at its NE corner. U11 at (86, 8.5), θ=270 → TDM face
west toward RT (SAI ~12–16 mm, no vias), I²C face south, VREF/AVDD shelf north, PDM wraps
the east side to J9. J9 mic flex on the **south edge** (92, 2.8); J8 external-clock header
at the enclave's SE boundary (103, 3.1); 3V3_MIC point-of-load LDO+switch inside the north
edge of the enclave (95, 11.5). Enclave rules: no LED 5 V path, no switch node, no USB
through-route, no unrelated fast clock crosses it. The one boundary-adjacent aggressor is
the LED data seam (§2.10), held ≥2 mm outside with a via-stitched guard — documented, not
smuggled.

### 2.10 RT ↔ LED logic
LED data exits RT's **south** face (FlexIO2/B-bank, fixed by silicon geography — the cost
of θ=90). Study decision per the brief: shifters and connectors are decoupled.
- Connectors J2 (108, 35.2) / J3 (115, 35.2): north edge, east block — cable geometry and
  the +5 V power spine own this position.
- Shifters U14/U15 at (107, 31)/(113, 31), **at the connectors** — the 5 V post-shifter
  stub stays <3 mm, and the long segment is the 3.3 V RT→shifter run (~45–50 mm) routed on
  the guarded seam east along y≈13.5–14 then north at x≈104–106, or on L4 as the designated
  slow layer (2 transitions). Source-series R at the RT end. The alternative (shifters at
  RT, long 5 V run) is recorded as the fallback if the seam proves noisy — either way this
  is V2's worst corridor and it is priced honestly in §10/§11.

### 2.11 High-current loops and distribution
- Entry chain, north spine, left-to-right: J1 (44) → TVS/CC (38–41) → eFuse U1 (50, 34.6,
  IN facing J1) → RSH1 (55, 34.7) → INA226 (55, 31.5, Kelvin north) → 5V_SYS trunk east on
  L3 (12–15 mm wide region + top reinforcement, return directly on L2 above/below it).
- Buck TPS62913 at (76, 34.5), inductor east, hot loop closed northward, ≥20 mm from the
  enclave, ≥8 mm from any USB pair, 3V3 region on L3.
- **LED power inverted vs V1: the switch moves to the load.** TPS2561 + FBs at
  (102–105, 33.5–34.6), directly beside J2/J3. The shared, bulk-decoupled 5V_SYS trunk does
  the ~48 mm of travel; the switched, inrush-carrying +5V_LED_L/R branches are ~8 mm.
  Switched-branch resistance ≈ 0.5 mΩ vs V1's ~4–6 mΩ across 70–84 mm of switched rail.
  Fault isolation and PG sensing sit at the connector where the event happens.
- Returns: L2/L5 continuous everywhere; no functional splits; the only plane voids on the
  board are the two RF keepouts.

### 2.12 Motion — mechanical first principles
U13 at (107, 20): on the H1-H2-H3 stiffness triangle's interior, mid-height (neutral axis
of the long board's first bending mode), away from J1 insertion, LED cable tugs, tactile
switches and both RF ends. Axes aligned to board axes. Its 0R ownership matrix sits 3 mm
west. Final position re-derives when the enclosure fixes the mounts — same caveat as V1,
but V2's candidate is chosen from stiffness, not from schematic adjacency.

### 2.13 Debug / service access
South spine, west-to-east: SW3/SW2 (S3 EN/BOOT, (12–17, 3.4) — their pads face this
corner), J5 LPUART1 (33, 3.2), J11 options (46.5, 3.2), SW4 SDL (57, 3.4), SW1 reset
(61, 3.4), J4 SWD Cortex-10 (67.5, 3.4) directly under its fixed west-face balls, then the
audio enclave's J9/J8. J6 recovery header north-west (30, 35.2) where S3's fixed UART0 pads exit
the module's north face. U16/Q2 (RT_PWR_VALID / POR gate) between owners at (44, 9.5).
The corridor carries probe pads and isolation links for its own neighbours only — it is an
access lane, not a routing dump: no through-traffic is assigned to it.

### 2.14 Local support and decoupling
Crystal Y1 tight NNW at (64.5, 27.5) on its fixed balls; DCDC inductor top-side at the E-N
face (74.5, 26.5→) with its loop local; NFC island (U12 at (122.5, 19), θ=90: digital face
west into the I²C spine, RF face east into matching at (126.6, 19) then the reserve; Y2 south
of U12; rail caps ringed; NFC_5V POL filter at (119, 24)). Decoupling: top ring plus
**B-side ring under the BGA core rails** (§7). I²C spine on L4 at y≈15→ east, INA spur west.

### Zones — inferred only now, as output
W RF end (0–8.5) · S3 body (0.8–26.5) · sovereign bridge (26.5–62 × 15–24) · N spine
(USB/power/LED, y>27) · RT core (62–74) · SE audio enclave (80–102 × 3.5–12.5) · NE LED
block (102–120 × 29–38) · motion/I²C mid-east (102–118) · NFC island + reserve (119–155) ·
S service lane (y<6.5). The zones fell out of steps 1–14; they were not inputs.

## 3. Pin-face orientation register (V2)

| Part | θ | Faces (recomputed from extracted pin/ball coordinates) | Cost |
|---|---|---|---|
| U6 RT1062 | **90°** | W = K1BR(LPSPI3)+service(fixed)+straps · N = USB(fixed)+XTAL(fixed)+FlexSPI · E = SAI2/3+DCDC · S = LED | W face multiplexed; LED data exits away from connectors; therm ADC far from thermistors |
| U9 ESP32-S3 | **90° (antenna W, locked)** | antenna W = 0 signals · E = K1BR 5 · S = USB(fixed)+EN · N = UART0(fixed)+IO0+swept I²C | DN2 pays ~50 mm with an under-body B-side leg |
| USB2422 | at capture | US→W/NW to J1 · DN1→S/SE to RT · DN2→SW | orientation from the real QFN-24 map |
| U11 ADC6120 | **270°** | TDM W → RT · I²C S → spine · PDM E wrap → J9 · VREF shelf N | PDM wraps one corner (~6 mm) |
| U12 ST25R3916B | **90°** | digital W ← spine · RFO/TX E → matching → reserve · XTAL S | unchanged from V1 — V1 got this right |
| U14/U15 | at connectors, inputs S | 5 V stub <3 mm; 3.3 V run is the long segment with source-series R | V2's worst corridor |
| U8 flash | **B-side NE** | six FlexSPI nets ≤8 mm under their corner | 6 signal vias |
| J1 TE 2129691-1 | N edge x≈44 | THR shell posts anchor insertion; US pair exits east | drawing verification pending |
| U13 LIS2DH12 | 0°, (107, 20) | stiffness-triangle interior, neutral axis | pending enclosure mounts |

## 4–6. Keepouts, corridors, high-current paths
Rendered in the interactive study (V2 view): RF keepouts (west aperture all-6-layer +
3-D end volume; NFC reserve + loop airspace), mating volumes (J1/J2/J3/J9), thermal watch
zone (RT+DCDC+buck+hub cluster, north-centre), sovereign-corridor boundary, DN2 crossing
gate, LED seam guard, 5V_SYS trunk and switched-branch arrows with L2 return notes.

## 7. B-side register — every part justified, or it stays on top

| B-side item | Justification (required form) |
|---|---|
| U8 flash | B-side because six FlexSPI nets become ≤8 mm dogbones under their own corner, and because the top NE courtyard frees for the DCDC island |
| RT core-rail decoupling ring (~8–10 caps) | B-side because each cap's loop closes through the ball via field directly (lowest loop inductance available on this stack), and because the top ring alone cannot reach the inner VDD_SOC balls cleanly |
| USB2422 straps + VBUS_DET divider | B-side because the top face around the hub is reserved for three unbroken 90 Ω pairs; straps are DC and don't care |
| RT boot-strap / K1BR series resistors | B-side under the W courtyard because the top W face is the K1BR landing and service escape — removing eight passives from it removes the last V1-style face contention |
| Everything else | top — no qualifying justification exists |

Unjustified B-side parts: **0** (rule enforced by register).

## 8. Approximate critical-net lengths / transitions
Manhattan estimates on hypothesis coordinates — see the matrix (§12); method: centre-to-pad
straight-line + 15 %, transitions counted per net class.

## 9. Premortem mapping (V1 failure modes → V2 mechanism)
Hub obstructing bridge → hub and bridge on different RT faces; corridor sovereign.
BGA face congestion → four-sector spread, worst face 13 vs 15.
LED-power distribution noise → switch-at-load; switched branch 8 mm.
LED connectors in audio territory → connectors NE, enclave SE, different edges.
USB near switching loops → buck ≥8 mm from any pair, loop faces north.
S3 antenna/harness interaction → short-edge aperture; no cable family crosses the west end.
NFC detuning → reserve empty; mic flex moved off its corner (V1 defect found).
Service dumping ground → access lane rule, no through-traffic.
Excess layer transitions → total HS transitions: 2 (DN2 only) + flash vias; K1BR/US/DN1 at 0.
Zoning overriding affinity → zones were derived last, from steps 1–14.

## 10. What V2 proves V1 got wrong
1. **The NW gateway was real, not hypothetical.** In V1, DN1 runs parallel to the K1BR
   arc's descent within ~3–4 mm at the RT NW corner, while FlexSPI's B-side vias and the
   DCDC island occupy the same corner. V2 demonstrates the four functions can occupy four
   sectors — so V1's pile-up is a choice, not a necessity.
2. **V1's mic flex violates its own NFC doctrine.** J9 at x≈130.5 on the north edge puts
   the flex and its bend volume inside the NFC reserve's corner airspace (reserve
   x≥128). V2's south-edge exit shows the conflict was avoidable. This must be fixed in
   any V1-derived layout regardless of the verdict.
3. **The long switched LED rail was inherited, not derived.** Switch-at-load is available,
   shortens the inrush/fault branch from ~75 mm to ~8 mm, and puts PG sensing where the
   event is. V1 never priced this alternative.
4. **South-face overload.** V1 stacks 15 escapes (all service + all audio) on one face
   because 180° was chosen to serve the hub. V2 shows a rotation exists that caps the
   worst face at ~13 while separating USB from the bridge — V1's face budget was skewed
   by one neighbour.
5. **The aperture does not have to cost outline complexity.** V1 carries a notched south
   edge and a service row within ~12 mm of the aperture band. The short-edge aperture
   yields a rectangle and a signal-free west end.

## 11. What V1 proves V2 got wrong
1. **The sovereign corridor just moves the multiplexing.** V2's west face carries K1BR +
   fixed SWD + fixed UART + fixed straps + therm ADC — the same "one face does too much"
   disease V2 accuses V1 of, one face over. V1's split of service (S) from bridge (N) is
   cleaner on this specific axis.
2. **LED logic pays for everything.** V1: ~15–25 mm same-face LED data. V2: ~45–50 mm
   guarded seam or L4 with 2 transitions, skirting the audio enclave it swore to protect.
   V1's E-face-to-LED adjacency was genuinely good engineering, not habit.
3. **K1BR leaves its native pads.** LPSPI1/SD_B0 (proven, boot-time-simple) is traded for
   LPSPI3 on AD pads that still need RM-level verification. If that verification fails,
   V2's centrepiece degrades into GPIO-matrix territory it cannot justify.
4. **DN2 pays heavily.** ~50 mm against V1's ~6 mm, two layer transitions, and a ~19 mm
   B-side leg under the module body that needs an explicit under-module copper sign-off.
   FS tolerance makes it workable; V1 makes it trivial.
5. **Thermal stacking.** V2 gathers RT, its DCDC, the buck and the hub into the
   north-centre; V1 spreads conversion west of the radio. V2 needs a thermal check V1
   arguably doesn't.
6. **Two cable edges.** V1 keeps every cable family on the north edge; V2 sends the mic
   flex south, which the enclosure must now accommodate on a second face.
7. **LED_THERM analogue return.** Fixed to AD-bank ADC inputs → V2's west face, ~50 mm
   from the NE thermistors; V1's south face was no better in principle but ~15 mm shorter.

## 12. Comparison matrix
(also rendered in the study page; estimates, Manhattan + 15 %)

| Metric | V1 | V2 |
| --- | --: | --: |
| RT↔S3 bridge length / transitions | ~32 mm, 0 via, shares NW gateway with DN1 (3–4 mm) | ~36 mm, 0 via, straight, fully sovereign |
| J1↔USB hub route | ~45 mm (HS US pair pays) | ~15 mm |
| hub↔RT USB route | ~8 mm | ~10 mm |
| hub↔S3 USB route | ~6 mm | ~50 mm FS + 2 transitions, under-body B-side leg, 0 corridor crossings |
| RT↔flash length/vias | ≤8 mm / 6 vias, contested NW corner | ≤8 mm / 6 vias, quiet NE corner |
| RT↔audio route | ~20 mm, 0T, SAI1/AD south face | ~12–16 mm, 0T, SAI2/EMC east face |
| RT↔LED logic route | ~15–25 mm direct | ~45–50 mm guarded / L4 +2T |
| LED 5 V switched-path R (est.) | ~4–6 mΩ over 70–84 mm switched rail | ~0.5 mΩ over ~8 mm (trunk shared, ~3 mΩ) |
| aggressor crossings through audio | 1–2 near-crossings (LED data NW corner; C4 adjacency) | 1 gated seam, ≥2 mm + guard |
| RT BGA escape congestion (worst face) | 15 (S), NW corner triple-booked | ~13 (W), corners spread |
| high-speed layer transitions | 0 USB + 6 flash vias | 2 (DN2) + 6 flash vias |
| RF keepout violations / near | 0 / service row ~12 mm from aperture band | 0 / nothing within 25 mm |
| NFC 3-D obstruction risk | **mic flex in reserve corner airspace** | none identified |
| service accessibility | S row + W bay, consolidated | S row + NW recovery, equal |
| cable/harness conflicts | 3 families on N edge; flex over NFC corner | families split N/S; RF ends clean |
| bottom-side part count | 1 group (flash) | 5 groups (~20 parts) |
| unjustified B-side parts | 0 | 0 |
| thermal concentration | spread (entry W, RT centre) | clustered N-centre — needs a check |
| unallocated VAL experiment area | ~14 %, peripheral pockets | ~19 %, central pockets |

## 13. Recommendation — synthesis, explicitly identified
Neither variant survives contact with the other intact.

**S1 (recommended): V1 longitudinal topology + five V2-derived amendments**
1. Fix the mic flex immediately: off the NFC reserve corner (south-edge or x≤122 exit) —
   mandatory whatever else happens.
2. Adopt switch-at-load LED power (TPS2561 + FBs beside J2/J3; trunk travels, switched
   branch does not).
3. De-conflict the NW gateway inside V1: hub drops to ~(72, 24) so DN1 enters the RT west
   face centre ≥6 mm below the K1BR descent; FlexSPI stays B-side; DCDC loop pulled 2 mm
   further north-west. If the G4 escape study still congests, that is the trigger to
   escalate to V2 proper.
4. Import V2's enclave rule-set verbatim (named boundary, gated crossings, aggressor list)
   onto V1's audio zone.
5. Record the west short-edge antenna as the qualified fallback RF arrangement if RF-B
   fails the enclosure study — it is no longer an unknown.

**V2 stands as the escalation architecture**, pre-derived and priced, if V1+S1 fails at
G4 (escape congestion) or G3 (enclosure kills the south aperture). What V2 must first
retire before any promotion: LPSPI3 pad-set verification against IMXRT1060RM, the LED seam
noise question, and the thermal cluster check.

This file and the V1 strategy are peer study inputs. Promotion of either — or of S1 —
requires the normal evidence path and a Captain ruling.
