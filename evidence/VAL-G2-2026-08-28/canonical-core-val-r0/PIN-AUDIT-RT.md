---
abstract: "REVISION 2. Pin-level audit of the RT1062 core/boot/clock/debug/recovery block on K1-CORE-VAL-R0. 342 pins, 196/196 U6-RTC balls, 100% pin-level coverage. Revision 1 was materially wrong - a stale read-back had moved one of the two U6 symbol parts by (+210,-170), manufacturing 22 false floating-ball claims including all the core-power, ground, boot-strap and SWD findings; those are retracted here in full. What survives: SW1-RTC is wired across the tact switch's permanently-closed terminal pair, hard-shorting the supervisor's MR# to ground so the RT1062 never leaves reset. Plus the USB OTG1 gap (D-044), JTAG_MOD floating, and two missing grounds on the Cortex header hidden behind NO_CONNECT flags. Carries the RT1062 ball-map verification (PASS), the USB_OTG1 ball ruling for A1-USB-POWER, and a geometry-vs-DRC reconciliation. PROPOSALS ONLY."
---

# PIN-AUDIT-RT — RT1062 core, boot, clock, debug and recovery

**Revision 2. Status: PROPOSAL. Nothing here has been applied to the schematic.**

## Revision 1 was wrong, and here is why

Revision 1 of this document reported that the RT1062 block could not boot for three
independent reasons. **Two of those three were my error.** They are retracted below in full.

The cause was a single bad input. I built pin geometry from
`jobs/all-pins-nc-audit.results.json` and `jobs/read-rt1062-all-pins.results.json`. Diffing
those against `jobs/full-pin-harvest.results.json` pin by pin: **exactly one of 229 component
parts differs — `U6-RTC` part `e3295`, by a uniform `(+210, −170)` across all 98 of its pins.**
Every other part is identical. So I measured the schematic's current wires against stale
coordinates, for schematic rows A–G only, and manufactured 22 false floating-ball claims.

I had checked the coordinate transform *globally* — 629 of 880 pins landing exactly on a wire
endpoint under `(x, −y)` versus 13 under the alternative — and treated 71 % as good enough. It
was not. A whole component part can be displaced inside a 71 % global rate without moving it
much. The tell was in my own Revision 1 text: I wrote that the boot-strap and SWD stubs sat
"roughly 210 units distant" from their balls, and read that as a drawing defect. **A uniform
rigid translation across all 98 pins of one part is the signature of a registration error, not a
drawing error.** I had the number and drew the wrong conclusion from it.

My fault battery proved the oracle could go red and green on demand. It never proved the *input*
was current. That is the gap: a working instrument pointed at stale data.

## What actually stands

The block still cannot boot as drawn, but for **one** reason, not three:

**`SW1-RTC` is wired across the reset switch's permanently-closed terminal pair.** The C&K
PTS645's terminals 1 and 2 are permanently common to each other. The board wires pin 1 → `GND`
and pin 2 → `RT_RESET_REQ_N`, so `RT_RESET_REQ_N` is hard-shorted to ground. It drives
`U7-RTC.3` = `MR#`, the TPS3808's active-low manual-reset input, which is therefore held
asserted forever, so `RESET#` is asserted forever, so `POR_B` never releases. This is a
component-datasheet fact and is independent of geometry, registration, or which snapshot you
read. Repair is free: move the net to terminal 3.

Everything else that survives is smaller: the USB OTG1 gap under D-044, `JTAG_MOD` floating, two
missing grounds on the Cortex header, and a set of component-value risks on the crystal.

## Two claims, kept apart

`harness/check_schematic_connectivity.py` is explicit that it is a **drawing** oracle, not a
netlist oracle, and it carries its own disproof on the record. So this document never merges:

- **"the wire does not meet the pin in the drawing"** — a real finding, and a
  `SINGLE-SHEET-CONTRACT.md` violation, measured on the frozen snapshot;
- **"the pin is electrically unconnected"** — a netlist claim, which geometry alone cannot make
  on this host, and for which EasyEDA's own DRC is the witness.

## Instruments

| | Drawing oracle | Netlist witness |
| --- | --- | --- |
| Tool | `harness/check_schematic_connectivity.py` | EasyEDA GUI DRC |
| Ran against | frozen source `489736:464c27d4`, captured ~13:57 | the **live** document, 14:58:52 |
| Result | `CONNECTIVITY=RED` | Fatal 0 / Error 0 / Warn 15 / Info 414 |
| Self-proof | `SELF_TEST=OK` — 13 battery cases, 4 RED, 3 FAIL-CLOSED, plus abstention and tolerance-guard controls | — |
| Key settings | snap tolerance **0** applied; `wrong_pin_bindings = 0` | — |

I ran the harness rather than hand-rolling geometry, and I quote its numbers. Per the retraction
of the DRC-fit method, **no per-component translation was fitted to anything.** Components are
measured against their own source anchors, and the DRC is used only to *disagree* with geometry,
never to calibrate it.

## Coverage

| Quantity | Value |
| --- | --- |
| Source records parsed | 6 631 |
| Wires / named nets | 675 / 143 |
| Component parts with pin geometry | 231 |
| **Pins loaded** | **881, 0 failures** |
| Pins landing on wire geometry | 654 (**74.2 %**) |
| Scope component primitives / designators / pins | 63 / 62 / **342** |
| **U6-RTC balls audited** | **196 / 196 = 100 %** |

`U6-RTC` is **one** multi-part component, not a duplicate MCU: parts `e3295` (rows A–G) and
`e3673` (rows H–P), 98 balls each, disjoint, union exactly 196 — the DVJ6B ball count. EasyEDA's
own DRC independently confirms it as multi-part.

**Registration, reported not cancelled.** Of the 63 scope parts, exactly one has a pin cloud more
than 10 units from its own anchor: `J5-RTDBG` at `(−20, 0)`, which is symbol asymmetry on a
single-row 1×4 header, not displacement. **Both `U6-RTC` parts are well registered.** The one
genuinely displaced component on the sheet, `U9-ESP` at `(5, −20)`, is outside this scope.

## Ball map verification — PASS

Every ball designation and signal name in the `U6-RTC` symbol matches **NXP IMXRT1060CEC Rev. 4
(04/2024) §6.2.2 Tables 85 and 86**: 19 `VSS`, 9 `VDD_SOC_IN`, and every functional ball checked
individually (F11, G14, E14, F12, F13, F14, G13, G10, K14, L14, L8, M8, N6, N12, M7, M6, L6, P11,
N11, N9, P9, P10, P8, M10, K8, N14, K3, K4, J5, L1, L2, M1, M2, N1, N2, K6, K7, L7, K9, N10, N13,
P13). The symbol is trustworthy. One cosmetic wart: `K4` is named `DCDC__IN_Q` (double
underscore) where NXP writes `DCDC_IN_Q`.

## The floating-ball reconciliation

| Measurement | U6-RTC balls |
| --- | ---: |
| Drawing oracle: no wire endpoint meets the ball (frozen, 13:57) | **111** |
| GUI DRC: reported floating (live, 14:58) | **80** |
| Both agree floating | **80** |
| **DRC-only** (DRC says floating, drawing says wired) | **0** |
| Drawing-only (drawing says no wire, DRC does not flag it) | **31** |

**The DRC's 80 is a strict subset of the drawing oracle's 111, with zero DRC-only balls.** That
nesting is the meaningful agreement: nothing the live netlister calls floating is drawn as
connected in the frozen snapshot.

The 31 drawing-only balls are all in part `e3673`, sitting 10–50 units from the nearest wire
endpoint — and **that endpoint always belongs to a neighbouring ball's stub**, at a pin pitch of
10. They are not near-miss bindings. The leading explanation is simply the ~1 hour between the
13:57 freeze and the 14:58 DRC. They are marked `DRAWING_GAP_NETLIST_OK` and are **UNRESOLVED**
until the source is re-frozen; that is an explicit marker, not a pass.

**Correcting the number I was given:** the earlier "111 unconnected, and the DRC agrees to the
ball" was coincidental — my geometry at that point said 133, not 111. The 111 is reproducible,
but it is the *drawing* number. **80 is the netlist number, and dispositions are assigned against
the 80.**

## Disposition census

Every one of the 342 audited pins carries exactly one disposition. No silent unknowns.

| Disposition | Scope (342) | U6-RTC (196) |
| --- | ---: | ---: |
| `POWER` | 82 | 30 |
| `GND` | 73 | 23 |
| `RESERVED_WITH_DOCUMENTED_REASON` | 72 | 71 |
| `CONNECTED` | 65 | 32 |
| `DRAWING_GAP_NETLIST_OK` *(unresolved)* | 31 | 31 |
| `INTENTIONAL_NC` | 9 | 5 |
| **`DEFECT_MISWIRED`** | **6** | **0** |
| **`DEFECT_FLOATING`** | **4** | **4** |

**All 80 DRC-floating U6 balls have a disposition:** 71 `RESERVED_WITH_DOCUMENTED_REASON`
(70 spare IOMUX-flexible GPIO deferred to VAL-G3 per **D-031**/**D-030**, plus `G10 JTAG_TRSTB`),
5 `INTENTIONAL_NC` (`G13`, `K6`, `N7`, `P6`, `P7`), and 4 `DEFECT_FLOATING`
(`L8`, `N6`, `N12`, `F13`).

Every one of those 80 should also receive a **NO_CONNECT mark**, so that the DRC's floating-pin
census stays a meaningful signal instead of a wall of expected noise.

Three dispositions go beyond the brief's seven. The brief has no bucket for "ought to be
connected and is not", nor for "the two instruments disagree". Forcing those into `RESERVED` or
`INTENTIONAL_NC` would be the annotation-over-property failure this repository has already been
burned by.

---

# Findings

**S1** blocks bring-up · **S2** breaks a D13.1 or D-0xx requirement · **S3** deviates from vendor
guidance · **S4** advisory.

## RT-D01 — S1 — `SW1-RTC` hard-shorts `RT_RESET_REQ_N` to GND. The RT1062 never leaves reset.

The only S1 in this block, and the only finding here that does not depend on any snapshot.

`SW1-RTC` is a **C&K PTS645SM43SMTR92LFS**. On the PTS645, **terminals 1 and 2 are permanently
common to each other, and terminals 3 and 4 are permanently common to each other**; the momentary
normally-open contact bridges the {1,2} rail to the {3,4} rail when pressed.

The schematic wires **pin 1 → `GND`** and **pin 2 → `RT_RESET_REQ_N`** — across the always-closed
pair — and leaves pins 3 and 4 unwired. Confirmed against the corrected harvest.

- `RT_RESET_REQ_N` is permanently tied to `GND`.
- It drives `U7-RTC.3` = `MR#`, the TPS3808's active-low manual-reset input (90 kΩ internal
  pull-up to VDD).
- `MR#` held low ⇒ the supervisor asserts `RESET#` continuously.
- `U7-RTC.1` (`RESET#`) is on net `POR_B`, which reaches `U6-RTC.M7`.
- **`POR_B` is held asserted permanently and the processor never starts.**

**Repair:** move `RT_RESET_REQ_N` from `SW1-RTC.2` to `SW1-RTC.3`. Recommended additionally, for
contact redundancy: `SW1-RTC.4` → `RT_RESET_REQ_N`, `SW1-RTC.2` → `GND`. No component change.

*Sources: C&K/Littelfuse PTS645 datasheet, Revised CM.10/23/24, contact schematic (same schematic
in the 09 sept 14 C&K revision, pp. B-84/B-85); TI TPS3808 SBVS050M (Rev. Mar 2023) Table 6-1.*

## RT-D02 — S2 — USB OTG1 is a half-connected pair. Ruling for A1-USB-POWER.

**Ball designations (IMXRT1060CEC Rev. 4 Table 86, p. 110):**

| Signal | Ball | State |
| --- | --- | --- |
| `USB_OTG1_DP` | **L8** | **floating** (both instruments) |
| `USB_OTG1_DN` | **M8** | wired, on `OPT_USB_AUD_RT` |
| `USB_OTG1_VBUS` | **N6** | **floating** (both instruments) |
| `USB_OTG1_CHD_B` | **N12** | **floating** (both instruments) |

**Required VBUS arrangement — the part most likely to be got wrong.** `USB_OTG1_VBUS` connects
**DIRECTLY to the 5 V VBUS node. No resistor divider.** It is the supply input to the on-chip
`LDO_USB` (regulating VBUS to 3.0 V on `VDD_USB_CAP`) *and* the VBUS-valid detector. Operating
range 4.4 / 5.0 / 5.5 V; **absolute maximum 5.5 V**; 5 V tolerant by design, not a 3.3 V I/O.
Decoupling **1 × 1 µF, 10 V**. A divider breaks both the LDO and VBUS-valid detection.
`USB_OTG1_CHD_B` needs no external component; NXP specifies a treatment only for the unused case.
D+/D− route as **90 Ω differential**, length-matched < 5 mil, no vias or stubs, continuous
reference plane.
*Sources: IMXRT1060CEC Rev. 4 §4.1.1 Table 7, Table 10, §3.2 Table 5; IMXRT1060RM Rev. 3
§13.4.1.1.3; MIMXRT105060HDUG Rev. 4 §3 Table 2, §7.5.*

**The repair is smaller than Revision 1 implied**, and the team lead is right about that: `M8`
already carries a net, so **one data line plus VBUS sense and conditioning** is what is missing,
not the whole path. But two caveats:

1. `M8`'s net is `OPT_USB_AUD_RT`, which runs to `R56-VAL.2` — and **`R56-VAL` is marked DNP** —
   then to `OPT_USB_AUD` on option header `J11-VAL.2`. So `M8` is currently wired *as an option
   stub*, not as half of a USB pair. Whoever closes D-044 has to re-purpose that net, not just
   add `DP` beside it.
2. **`J1-PWR1` has `A6`/`B6` (DP1/DP2), `A7`/`B7` (DN1/DN2) and `A5`/`B5` (CC1/CC2) all unwired**,
   with only one of its four `VBUS` pins and one of its four `GND` pins connected. The DRC
   reports 9 floating pins on `J1-PWR1`. **D-044 is unimplemented at both ends.** Co-own with
   A1-USB-POWER, who owns the J1 side.

## RT-D03 — S3 — `JTAG_MOD` (ball F13) is floating.

Confirmed floating by both instruments. NXP requires an external **4.7 kΩ pull-down or a direct
tie to GND** for SWD / software-debug mode; `MOD` high selects IEEE 1149.1 JTAG. The internal
100 kΩ pull-down makes it survivable, but it is not the documented treatment and it is the kind
of thing that fails intermittently under noise on a validation board.

**Repair:** tie F13 to `GND`, or fit a 4.7 kΩ pull-down.
*Sources: MIMXRT105060HDUG Rev. 4 §5 Table 6 item 3; IMXRT1060CEC Rev. 4 §3.1 Table 3.*

## RT-D04 — S2 — `J4-RTDBG` is missing two of three ground returns, and NO_CONNECT flags are hiding it.

The Arm Cortex Debug 10-pin 1.27 mm connector places **GND on pins 3, 5 and 9**, where pin 9 is
`GNDDetect` — the pin a probe uses to sense that a target is present.

| Pin | Arm spec | As drawn | Verdict |
| --- | --- | --- | --- |
| 1 | VTref | `3V3` | correct |
| 2 | SWDIO / TMS | `SWD_SWDIO_H` | correct |
| 3 | GND | `GND` | correct |
| 4 | SWCLK / TCK | `SWD_SWCLK_H` | correct |
| **5** | **GND** | **`NO_CONNECT`** | **DEFECT** |
| 6 | SWO / TDO | `NO_CONNECT` | acceptable — D13.1 permits SWO to be reserved |
| 7 | KEY | `NO_CONNECT` | correct |
| 8 | NC / TDI | `NO_CONNECT` | correct for SWD-only |
| **9** | **GNDDetect (GND)** | **`NO_CONNECT`** | **DEFECT** |
| 10 | nRESET | `POR_B` | correct |

**The grounds are not correct** — only one of three is wired. And the `NO_CONNECT` flags on pins
5 and 9 **suppress the DRC's floating-pin warning**, so this defect is invisible to the netlist
check. It is exactly the class of thing that only a design-intent audit catches.

Missing `GNDDetect` can prevent some probes from enabling at all; missing the pin-5 return
degrades SWD signal integrity as clock rates rise.

**Repair:** pins 5 and 9 → `GND`; remove their `NO_CONNECT` marks.
*Source: Arm, "Cortex-M Debug Connectors", Cortex Debug Connector section; Arm KA003182.*

## RT-D05 — S2 — `Q2-VAL`'s gate has no pull-down, so the S3 cannot be safely dead.

The `POR_B` wired-OR **topology is correct** and satisfies the hardest requirement in D13.1.
Contributors on net `POR_B` (5 pin endpoints, measured):

| Contributor | Path | Can it drive `POR_B` high? |
| --- | --- | --- |
| Supervisor | `U7-RTC.1` `RESET#` — **open-drain**, external pull-up required and present (`R12-RTC` 10 kΩ → `3V3`) | No |
| Manual reset | `SW1-RTC` → `RT_RESET_REQ_N` → `U7-RTC.3` `MR#` → supervisor re-times it | No |
| ESP32_S3 request | `S3_POR_REQ` → `R60-VAL` 100 Ω → `S3_POR_GATE` → `Q2-VAL` 2N7002 **gate**; source → `GND`; drain → `S3_POR_OD` → `R59-VAL` 100 Ω → `POR_B` | **No — physically cannot** |
| Debug probe | `J4-RTDBG.10` nRESET | open-drain by probe convention |

`Q2-VAL` is an N-channel FET, source grounded, drain feeding `POR_B` through 100 Ω. It can only
pull down or release to high-Z. **D13.1's "may assert `POR_B` low or release it to high
impedance, must never actively drive `POR_B` high" is enforced by the topology, not by
convention.** That is the right way to build it.

**The defect:** `S3_POR_GATE` has no pull-down to `GND`. With the ESP32_S3 unpowered or absent the
gate floats, and leakage or capacitive coupling can turn the FET on and hold the RT1062 in reset
— contradicting D13.1's "RT1062 boot and recovery must remain fully functional with ESP32_S3 dead
or absent".

**Repair:** add a 100 kΩ resistor from `S3_POR_GATE` to `GND`. One new component.

**Separately, `U16-VAL.5` (`SENSE`) is floating**, along with its `MR#` and `CT` — DRC-confirmed.
So the RT power-valid supervisor is **not monitoring any rail**, and D13.1's "an RT power-valid
indication is available to ESP32_S3" is unmet at the source, regardless of the wiring downstream.
`RT_PWR_VALID` binds only `R62-VAL.2` and `U16-VAL.1`.

## RT-D06 — S2 — LPUART1: neither an active mux nor a passive selector. The S3 leg does not exist.

**The brief asks which it is. It is neither.** The measured topology is a bare series-resistor
fan-out to a single 4-pin header:

```
U6-RTC.K14 (GPIO_AD_B0_12) ──[LPUART1_TX]──> R17-RTDBG 22R ──[LPUART1_TX_H]──> J5-RTDBG.1
U6-RTC.L14 (GPIO_AD_B0_13) <─[LPUART1_RX]─── R18-RTDBG 22R <─[LPUART1_RX_H]─── J5-RTDBG.2
                                                                                J5-RTDBG.4 → GND
```

Pads are correct: `LPUART1_TX` = `GPIO_AD_B0_12` = ball **K14**, `LPUART1_RX` = `GPIO_AD_B0_13` =
ball **L14**, matching D-020.

| D13.1 requirement | Verdict |
| --- | --- |
| Exactly one active writer to RT RX | **Satisfied — but vacuously.** Only `J5.2` can write, because the ESP32_S3 leg the contract requires does not exist. |
| ESP32_S3-independent physical takeover overriding software selection | **Satisfied vacuously.** No software selection, no ESP32 in the path. |
| Safe behaviour when either domain is unpowered | **Not applicable** — no second driver to protect against. |
| Hardware-defined default before firmware runs | **Satisfied** — the header is always the writer. |

The requirement actually broken is the one above them all: **the ESP32_S3 cannot reach the
RT1062's LPUART1 at all**, so the Debug Fabric's central deliverable — a transparent binary RT
BootROM UART tunnel through the S3 service endpoint — is not implementable on this schematic.
`contracts/debug-fabric.md` is `status: REQUIREMENTS_ONLY`, so this is a scope gap, not an
unambiguous defect. **It needs a Captain-level ruling: does VAL-G2 capture the S3 UART leg, or is
it deferred?** Single-writer must be re-derived once it lands.

**Also missing (S3):** NXP requires **10 kΩ pull-ups on `TXD1`/`RXD1`** to prevent a false UART
trigger in serial-downloader mode. Neither is present.
*Source: MIMXRT105060HDUG Rev. 4 §5 Table 8 item 1.*

Worth recording for that ruling: in Serial Downloader mode the BootROM polls **USB OTG1 and
LPUART1 concurrently**, falling back to USB HID if no UART host is polling. With RT-D02 open,
*both* serial-downloader doors are currently compromised.
*Source: IMXRT1060RM Rev. 3 §9.3.2 Figure 9-1; MIMXRT105060HDUG Rev. 4 §5 p. 10.*

## RT-D07 — S3 — Multi-part metadata is inconsistent across the two `U6-RTC` parts.

EasyEDA's own DRC raises this, and it doubles as the answer to why two `U6-RTC` entries exist:

> *Component MIMXRT1062DVJ6B is a multi-part component, the properties of each part should be the
> same. `$1I3295`、`$1I3673` have different property **Supplier Part, Add into BOM, supplierId**.*

The DRC confirms it is **one** multi-part component — so the two entries are not a duplicate MCU
— while flagging inconsistent metadata: `MIMXRT1062DVJ6B.1` vs `.2`, and `Add into BOM` present
on only one part.

**Repair:** make the shared properties identical across both parts — same `Supplier Part`, same
`supplierId` — while keeping `Add into BOM` set so the BOM counts the device exactly once.
Coordinate the BOM half with B-BOM before changing `Add into BOM` on either part.
*Source: EasyEDA GUI DRC 2026-08-28T14:58:52, warning 3.*

## RT-D08 — S4 — Clock: correct topology, two component-value risks.

**Correct as drawn, and worth saying so:**

| Item | As drawn | Verdict |
| --- | --- | --- |
| `XTALI` P11 | `Y1-RTDBG.1`, `C35` 8.2 pF, `R68-RTDBG` **2.2 MΩ to GND** | The 2.2 MΩ bias is exactly what NXP asks for, on the right ball |
| `XTALO` N11 | → `R13-RTDBG` 0 Ω → `XTALO_Y` → `Y1-RTDBG.3`, `C36` 8.2 pF | Correct; the 0 Ω is a sensible drive-trim provision |
| `Y1-RTDBG` pins 2, 4 | `GND` | Case ground correct |
| `RTC_XTALI` N9 | **`GND`** | **CORRECT.** NXP's *required* treatment when no 32.768 kHz crystal is fitted; auto-engages the on-chip ~40 kHz ring oscillator |
| `RTC_XTALO` P9 | no stub in the frozen snapshot; DRC does not flag it | Intent is correct (must be unconnected). Marked `DRAWING_GAP_NETLIST_OK` |
| `CCM_CLK1_P/N` N13/P13 | same | External-clock input correctly unused |

**Risk 1 — `TUNE_TBD`, load capacitance.** `Y1-RTDBG` is a **Murata XRCGB24M000F3A00R0**, a
quartz crystal with **CL = 6 pF** and **no integrated load capacitors**. With 8.2 pF per leg,
C_eff = (8.2 × 8.2)/(8.2 + 8.2) + C_stray = **4.1 pF + C_stray**. Hitting 6 pF needs
C_stray ≈ 1.9 pF, optimistic for a BGA fanout; a realistic 3–5 pF lands at 7–9 pF and pulls the
oscillator slow. **Treat 8.2 pF as provisional and bench-trim it.**

**Risk 2 — S3, ESR margin.** The Murata part is specified at **ESR 120 Ω max** against NXP's
stated typical of **80 Ω** (or 50 Ω at 200 µW), with a 250 µW max drive level. Not disqualified,
but outside NXP's typical; measure start-up margin on the first article. `R13-RTDBG` 0 Ω is the
right place to add drive limiting if needed.

*Sources: MIMXRT105060HDUG Rev. 4 §4 Table 4 items 1–2; IMXRT1060CEC Rev. 4 §3.1 Table 3; Murata
XRCGB series product documentation.*

## RT-D09 — S4 — UNRESOLVED: boot-flash quad lines.

`U8-RTDBG` is an **ISSI IS25LP064A-JBLE**, 64 Mbit 3 V serial NOR in SOIC-8 208 mil; its symbol
pinout matches the datasheet exactly. `CE#`, `SCK`, `IO0` and `IO1` reach the processor at L3, L4,
P3 and N4. `IO2`/`IO3` are pulled high by `R14`/`R69` 10 kΩ — the *correct* treatment, since the
ISSI datasheet warns against tying `WP#`/`HOLD#` directly to Vcc.

**But the two instruments disagree** about whether `IO2`/`IO3` reach the MCU. In the frozen
snapshot, nets `FLEXSPI_D2` and `FLEXSPI_D3` bind only `U8-RTDBG` plus their pull-ups, and
`U6-RTC` `P4`/`P5` carry no stub. The 14:58 DRC does **not** report `P4`/`P5` floating, so the
live netlist may already bind them.

**Do not act on this until the source is re-frozen.** If it turns out they are unbound, wire
`FLEXSPI_D2` → P4 and `FLEXSPI_D3` → P5 — losing `DATA2`/`DATA3` is unrecoverable after fab.
Single-SPI boot is retained either way \[INFERENCE — the BootROM reads the FlexSPI Configuration
Block at offset 0 in 1-bit mode, so `CS`/`SCLK`/`DATA0`/`DATA1` suffice — **not** closed against a
primary NXP document; confirm against IMXRT1060RM "System Boot" and NXP AN12238\]. Note
`IS25LP064A` single-SPI `03h` Normal Read is capped at **50 MHz** versus 133 MHz for other modes.

## RT-D10 — S4 — 80 balls need NO_CONNECT marks.

All 80 DRC-floating `U6-RTC` balls are dispositioned above, and 76 of them are legitimately
unused. But none carries a `NO_CONNECT` mark, so the DRC's floating-pin census is 80 lines of
expected noise in which the four real defects are invisible. Marking the 76 turns that warning
back into a signal.

---

# Retracted findings

Recorded in full so nobody rebuilds them from Revision 1.

| ID | Revision 1 claim | Verdict |
| --- | --- | --- |
| RT-D02 (r1) | Six of nine `VDD_SOC_IN`, seven of nineteen `VSS`, two `NVCC_GPIO`, two `NVCC_EMC` unconnected | **RETRACTED IN FULL.** F6/F7/F8/F9/G6/G9 → `1V15_CORE`; A1/A14/B5/B10/E2/E13/G7 → `GND`; E9/F10 → `3V3`; E6/F5 → `3V3`. Both instruments agree. |
| RT-D03 (r1) | Boot straps and SWD terminate on orphan stubs ~210 units away; passive default is Boot-From-Fuses | **RETRACTED IN FULL.** `BOOT_MODE0` binds `R10-RTC.1`, `R61-VAL.2`, `U6-RTC.F11`. `BOOT_MODE1` binds `R11-RTC.1`, `U6-RTC.G14`. `SWD_SWDIO` binds `R16-RTDBG.1`, `U6-RTC.E14`. `SWD_SWCLK` binds `R15-RTDBG.1`, `U6-RTC.F12`. Passive default **is** `BOOT_MODE[1:0] = 10` = Internal Boot, as D13.1 requires. The "210 units" *was* the stale offset. |
| RT-D05 (r1) | `JTAG_TDO` (G13) tied hard to GND against NXP guidance | **RETRACTED.** G13 is floating in both instruments; NXP's "fit no pull-up or pull-down on TDO" is **satisfied as built**. Reclassified `INTENTIONAL_NC`. |
| RT-D08 (r1) | Four GND stubs stop 5 units short of D4, D6, D9, D11 | **RETRACTED.** With correct coordinates the nearest endpoints are 10, 10, 70 and 50 units away and belong to other pins' stubs. Four ordinary unused GPIO. |
| RT-D09b (r1) | `S3_POR_REQ` and `RT_PWR_VALID` are 5-unit near-misses at `U9-ESP` | **True of the frozen snapshot; withdrawn as a live claim.** The 14:58 DRC reports **zero** floating pins on the ESP32-S3. Attribute to the S3 side. |
| RT-D11 (r1) | `FLEXSPI_D2`/`D3` do not reach the processor | **DOWNGRADED TO UNRESOLVED** — see RT-D09 above. |

Also correcting the brief: **`RT_RESET_REQ_N` is not a K1E-016 violation.** One wire (`e66889`,
`[[3065,4300],[3130,4300]]`), two endpoints, both landing exactly on pins. The drawing oracle's
own single-pin-net list is `BUCK_PG`, `ESP_UART0_RX`, `K1BR_IRQ_S3`, `K1BR_MISO_S3`, `K1BR_MOSI`,
`MOTION_INT_S3`, `S3_POR_REQ` — `RT_RESET_REQ_N` is not among them.

---

# What is right, and must not be "fixed"

| Item | Evidence |
| --- | --- |
| `1V15_CORE` decoupling: 5 × 220 nF + 4.7 µF + 22 µF, on all nine `VDD_SOC_IN` balls | Exactly MIMXRT105060HDUG Rev. 4 §3 Table 2 |
| Boot straps: `R10` 10 kΩ ↓ + `R11` 10 kΩ ↑ ⇒ `BOOT_MODE[1:0] = 10` = Internal Boot, reaching F11/G14 | IMXRT1060RM Rev. 3 §9.3.1 Table 9-2; D13.1 passive-default requirement **met** |
| SWD reaches E14/F12 through 22 Ω series resistors, with **no ESP32 anywhere in the path** | D13.1 "SWD is never proxied through ESP32_S3" **met** |
| `VDD_HIGH_CAP` P8: 220 nF + 4.7 µF, nothing driving it | LDO_2P5 **output**; must never be driven |
| `VDD_SNVS_CAP` M10: 220 nF + 4.7 µF | LDO_SNVS output, no load permitted |
| `VDD_USB_CAP` K8: 100 nF + 10 µF | LDO_USB output; matches the MIMXRT1060-EVK |
| `NVCC_PLL` P10 on `NVCC_PLL_1V1`, 220 nF + 4.7 µF, **nothing driving it** | **Correct and easy to get wrong** — it is the 1.1 V LDO_1P1 **output**, not a rail you supply. IMXRT1060RM Rev. 3 §13.4.1.1.2; IMXRT1060CEC Rev. 4 §4.1.7.1 Table 14 |
| `DCDC_PSWITCH` K3: `R70` 100 kΩ from `3V3` + `C89` 100 nF | τ = 10 ms; time to 0.5 × DCDC_IN = 0.693 τ ≈ **6.9 ms**, inside NXP's 5–15 ms window |
| `DCDC_SENSE` J5 → `1V15_CORE` | Feedback at the load, matching the EVK and Teensy 4.1 |
| `L4-RTC` Coilcraft **XGL4030-472MEC** 4.7 µH, `DCDC_LP` → `1V15_CORE` | NXP wants 4.7–10 µH, Isat > 1 A, ESR < 0.2 Ω. Actual **Isat 3.2 A @20 % drop, Irms 4.8 A, DCR 28.5 mΩ** — comfortable pass, though ~$5.60/1 is worth a BOM look |
| `VDD_SNVS_IN` M9 → `3V3` (shorted to `VDD_HIGH_IN`) | Explicitly permitted: MIMXRT105060HDUG Rev. 4 Table 3 item 4 |
| `R12-RTC` 10 kΩ `POR_B` pull-up to `3V3` | Required — TPS3808 `RESET#` is **open-drain**. NXP wants the pull-up on `VDD_SNVS_IN`, satisfied because `VDD_SNVS_IN` *is* `3V3` |
| `U7-RTC.4` `CT` open | Permitted; fixed 12/20/28 ms reset delay. TI SBVS050M Table 6-1, §8 |
| `U7-RTC.5` `SENSE` → `3V3`, threshold 3.07 V | NXP requires threshold **> 2.6 V**; `VDD_HIGH_CAP` and `VDD_SNVS_CAP` both derive from 3V3 |
| `Q2-VAL` open-drain `POR_B` pull-down topology | Enforces D13.1's never-drive-high requirement physically |
| `JTAG_TDO` G13 left floating | NXP: fit no pull-up or pull-down on TDO. Correct as built |
| `RTC_XTALI` N9 → `GND` | NXP's required no-32-kHz-crystal configuration |

**One observation, not a defect:** `1V15_CORE` is not monitored by any supervisor. NXP's own EVK
monitors only the 3.3 V rail, so this matches the reference — but on a validation board a
core-rail power-good would be cheap and useful.

---

# Bounded repair list

Proposals against frozen hash `489736:464c27d4`. The live document has moved past it; a single
authorised writer must reconfirm each before writing.

| # | Sev | Repair | Cost |
| --- | --- | --- | --- |
| 1 | S1 | `SW1-RTC`: move `RT_RESET_REQ_N` from pin 2 to pin 3; optionally pin 4 → `RT_RESET_REQ_N`, pin 2 → `GND` | rewire only |
| 2 | S2 | USB OTG1 per D-044: `USB_OTG1_DP` → L8 and re-purpose `M8`'s `OPT_USB_AUD_RT` so DP/DN form a real pair from J1 through ESD; `USB_OTG1_VBUS` (N6) **direct to 5 V VBUS, no divider**, 1 µF/10 V; rule on `N12`; populate or remove `R56-VAL` | co-own with A1-USB-POWER |
| 3 | S2 | `J4-RTDBG` pins 5 and 9 → `GND`; remove their `NO_CONNECT` marks | 2 wires |
| 4 | S2 | Add 100 kΩ from `S3_POR_GATE` to `GND` | 1 new part |
| 5 | S2 | Connect `U16-VAL.5` `SENSE` to the rail it is meant to monitor; rule on its `MR#` and `CT` | 1–3 wires |
| 6 | S3 | Tie F13 (`JTAG_MOD`) to `GND` or fit a 4.7 kΩ pull-down; add 10 kΩ pull-ups on `LPUART1_TX` and `LPUART1_RX` | 1 wire, 3 new parts |
| 7 | S3 | Make `Supplier Part` and `supplierId` identical across `U6-RTC` parts `e3295`/`e3673`, keeping the device counted once in the BOM | metadata only — coordinate with B-BOM |
| 8 | S4 | Add `NO_CONNECT` marks to the 76 legitimately-unused `U6-RTC` balls | marks only |
| 9 | S4 | Bench-trim `C35`/`C36` against the 6 pF crystal CL; measure start-up margin against the 120 Ω max ESR | bench |

**Blocked on a re-freeze:** `FLEXSPI_D2`/`D3` → P4/P5 (RT-D09), and the 31 `DRAWING_GAP_NETLIST_OK`
balls in part `e3673`.

**Open ruling required:** does VAL-G2 capture the ESP32_S3 leg of LPUART1 that D13.1 requires, or
is it deferred? (RT-D06.)

---

**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:RT-boot-clock-debug-audit | Created. 342 pins across 62 designators, 196/196 U6-RTC balls, geometric connectivity oracle, NXP primary-source ball-map verification, 12 bounded repairs. |
| 2026-08-28 | agent:RT-boot-clock-debug-audit | **Revision 2.** Re-derived from `jobs/full-pin-harvest.results.json` after finding that `U6-RTC` part `e3295` was displaced by `(+210,−170)` in the read-back used for Revision 1. Retracted RT-D02, RT-D03, RT-D05, RT-D08 in full and downgraded RT-D09b and RT-D11. Replaced hand-rolled geometry with `harness/check_schematic_connectivity.py`; added the 14:58 GUI DRC as an independent netlist witness with drawing/netlist claims kept separate; dispositioned all 80 DRC-floating balls; added the multi-part metadata defect. |
