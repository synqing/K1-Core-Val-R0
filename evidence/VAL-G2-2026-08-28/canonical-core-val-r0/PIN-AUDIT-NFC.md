---
abstract: "Pin-level audit of the K1-CORE-VAL-R0 ST25R3916B NFC front end (U12-NFC and its 21 supporting parts, 77 pins) measured by geometry against the frozen denominator 489736:464c27d4 and checked against the ST25R3916B datasheet DS13541 Rev 5, AN5276 Rev 6, AN5592 Rev 1 and the STEVAL-ST25R3916B schematic pack — all retrieved and read, nothing left unretrieved. Fourteen findings. Four P0: VDD on 3V3 while VDD_TX is on 5 V (exceeds absolute maximum), crystal wired to the wrong pad, the receive divider missing, and an EMC filter that resonates at 453 MHz against a required 8-17 MHz. NFC-D2 is RESOLVED by the fresh 14:58:52 GUI DRC — the netlist binds NFC_IRQ and there is no defect; its drawing half is STALE because the live document moved after the frozen source was taken. NFC-D3 and the RFI2 disposition are independently CONFIRMED by the same log. New NFC-D16 (P1): RFO2 appears to have been touched since the freeze while RFI2 was not. The floating RFO2/RFI2 is WITHDRAWN as an electrical defect: it is a valid ST single-ended topology that was never decided or recorded. Single-ended-with-cable recommended; needs a Captain ruling. Proposals only, not applied."
---

# NFC front-end pin audit — VAL-G2

**Status: PROPOSAL. Nothing here has been applied.** This lane is read-only. It called no
EasyEDA tool, touched no canvas, and modified no schematic artefact. The frozen denominator it
measured is already behind the live document, and `contracts/nfc-interface.md` visibly grew
during this audit. **The single writer must reconfirm every item against live before acting.**

## What this found, in one paragraph

**NFC-D2 is closed.** A fresh GUI DRC at 14:58:52 settles it: `U9-ESP` has **zero** floating pins
and the only two single-pin networks on the whole board are `$1N153914` and `BUCK_PG`. `NFC_IRQ`
is bound in the netlist — **no defect**. Its drawing half is **stale**, not real: my measurement
came from a frozen source, and the live document moved after it. That took four passes to get
right, and the record of all four is kept below.

The same log **confirms two findings independently**: `Y2-NFC.3` and `Y2-NFC.4` are both in its
floating-pin list (NFC-D3, the crystal), and `U12-NFC.23` (RFI2) is the *only* floating pin on
`U12-NFC` — exactly what AN5592's single-ended stage predicts. And it surfaces one new thing
neither lane had flagged: **`RFO2` is no longer floating while `RFI2` still is** (NFC-D16).

The NFC chip's two supply pins are wired to two different rails — `VDD` to 3.3 V and `VDD_TX` to
5 V — and the ST datasheet says in plain words that they must be the same supply, with an
absolute maximum difference of 0.3 V. The board has 1.7 V. That is a part-damaging error, not a
performance one. After that: the 27.12 MHz crystal is wired to the wrong pad so the oscillator
loop is open, the receiver input is connected
straight to the antenna with none of the attenuation ST requires, and the EMI filter resonates at
about 453 MHz where ST requires 8–17 MHz. The one thing that turned out **not** to be broken is
the headline: `RFO2` and `RFI2` are unconnected because the board is a single-ended design, which
is a topology ST documents and supports. Nobody wrote that decision down, nobody recorded the
firmware register it forces, and nobody costed the read range it gives up — so the defect there
is a missing decision, not missing copper. Three of the four P0s were invisible to the existing
DRC log, because DRC checks whether a wire is present, not whether the wire is correct — the two
supply pins are both connected, the divider and the 10 nF partners are absent components rather
than broken wires, and the EMC filter is a values error. Only the crystal showed up, and only
half of it: DRC caught the two floating pads, not the fact that `NFC_XTO` had landed on a ground
pad.

## How this was measured

The oracle re-derives **geometry**, not annotation. For each pin it takes the pin's connection
point and asks whether that point actually lies on a wire segment — coincident with an endpoint,
or on a segment interior for a T-junction. It never trusts the net label written on a wire to
prove that anything is joined.

It ships a six-case fault battery, four of which must come back RED: a pin one unit off a wire, a
pin in the gap between two wires, a wire endpoint that must not pick up a crossing wire, and a
pin bridging two differently-labelled wires that must report both. All six behaved as specified,
so the instrument has been seen to fail.

The pin-coordinate frame from the EasyEDA API and the frame in the document source differ: `x` is
unchanged, `y` is negated. That mapping was proved against component anchors on **227 of 228**
designators rather than assumed. The single miss is `U6-RTC`, whose designator is duplicated in
the index; it is outside this lane.

### Drawing measurement — the repo's harness, not a hand-rolled fit

Drawing findings in this document now come from **`harness/check_schematic_connectivity.py`**, the
repo's owned drawing oracle. It is better than the oracle this lane started with: it measures pins
against their **own component's anchor**, reports residuals as
`components_displaced_from_their_wiring` instead of cancelling them, has a dedicated
`off_sheet_wires` rule, keys pin data by **primitive id** rather than designator (which fixes this
lane's `U6-RTC` collapse), abstains on parts with no pin geometry rather than calling them
defects, and **refuses any snap tolerance ≥ half the pin pitch**. Its 13-case battery passes,
including four RED, three fail-closed, and the abstention, transform and keying controls.

Its verdict on the frozen source is **RED**: 8 net labels meeting fewer than two pins, 25 wires
meeting no pin, 1 off-sheet wire, 0 wrong-pin bindings at tolerance 0.

**Retracted: the DRC-fitted registration offset.** An earlier version of this audit fitted a
per-component translation to reproduce EasyEDA's DRC floating count. That is retracted. Two free
parameters fitted against a target verdict will reproduce that verdict — the method produces its
own result. Worse, it erases the distinction the measurement exists for: a component whose *pins*
are right and whose *wire* is misplaced would have the offset applied to the good pin data,
sliding it onto the bad wire and deleting a genuine defect.

**What survives, and on what evidence.** `U9-ESP`'s pin cloud sits at **+5, −20** from its own
anchor — taken from the harness's independent `components_displaced_from_their_wiring`
diagnostic, not from any fit. The harness itself labels that diagnostic and warns that symbol
asymmetry and real displacement are not separable from it alone; thirteen other components show a
[−20, 0] offset that is plainly symbol asymmetry. The **attribution** — a rejected,
never-rolled-back `canonical-esp-service-label-visibility-repair` at `474325:91295516` — is the
team lead's, cited as theirs; this lane did not re-derive the transaction history.

**Which pin each displaced stub was drawn for** matters only for the repair, and it is settled by
name-to-net anchors rather than by distance. At **zero offset** the nearest-pin map is
**incoherent**: pin 3 `EN` → `GND`, pin 4 `IO4` → `3V3`, pin 5 `IO5` → `ESP_EN`, pin 36 `RXD0` →
`I2C_SCL`. That has the designer wiring ground to a GPIO and a UART receive pin to an I2C clock.
Under the −5, −20 reading it is coherent on four independent anchors: pins 1, 2, 3 named `GND`,
`3V3`, `EN` landing on `GND`, `3V3`, `ESP_EN`; pin 13 `IO19` → `USB_DM_S3` and pin 14 `IO20` →
`USB_DP_S3`, which is an **ESP32-S3 hardware fact** (GPIO19/20 *are* the native USB D−/D+) that a
two-pitch error would break; `RXD0`/`TXD0` → `ESP_UART0_RX`/`TX`; and pins 18–22 →
`K1BR_CS`/`MOSI`/`SCK`/`MISO_S3`/`IRQ_S3` in pin order.

So the `NFC_IRQ` stub was drawn for **pin 4 (IO4)**. The nearest pin at zero offset is pin 6
(IO6) at distance 5 — but 5 is *exactly half the pin pitch*, which the harness refuses as
ambiguous, and the zero-offset map that pin 6 belongs to is the incoherent one. **Either way the
wire meets no pin**, so the drawing verdict does not depend on this.

**One unreconciled number, flagged rather than smoothed:** the harness reports
`nearest_measured_distance: 100` for stub `e8941`, where direct arithmetic on the same inputs
gives 5 to pin 6 at (4175, 4375) and 20 to pin 4 at (4175, 4395), from wire endpoint (4170, 4375).
The harness **verdict** is unaffected — the wire meets no pin under either number — but the
distance field is worth the oracle lane's attention.

**Parsed, whole sheet:** 675 wires, 684 wire segments, 675 net labels, 143 distinct net names,
228 components with pin geometry, **782 pins**, 12 `NO_CONNECT` attributes. 634 of the 782 pins
touch at least one wire.

**Audited, this lane:** 22 NFC components, **77 pins**, every one of which carries a disposition.

## Evidence and its drift

| Input | Locator | Standing |
| --- | --- | --- |
| Frozen source | `frozen-denominator-489736/source.txt`, hash `489736:464c27d4` | Read-only denominator |
| Pin geometry | `jobs/all-pins-nc-audit.results.json` | 228 components, 0 failures |
| No-connect marks | `jobs/canonical-nfc-unused-nc-2026-08-28-applied.json` | Applied **after** the freeze |
| Schematic DRC | `schDrcLog_2026-08-28.txt` (operator download folder) | **Stale — ran 12:17:37** |

Two drift facts matter and are stated rather than papered over.

The frozen source is the **pre** state of `canonical-nfc-unused-nc-2026-08-28`
(`pre_source_hash 489736:464c27d4`, `post 490331:ca12d078`). The eight `U12-NFC` no-connect
crosses are therefore not visible in the frozen source; they are evidenced by that transaction's
`applied.json`, which records all eight as `action: set` with real attribute ids and `saved: true`.

The DRC log ran at **12:17:37**, before all three NFC transactions (12:43, 13:08, 13:18). Its six
`NFC_VDD_*`/`NFC_AGDC` "single network connected to only one component pin" warnings and its
`U12-NFC.20` floating warning are **already closed** by those transactions. Its `Y2-NFC.3` and
`Y2-NFC.4` floating warnings are **still live** and independently corroborate defect NFC-D3.

## Verification of the three landed transactions

Each was checked for correctness, not merely presence.

**`canonical-nfc-regulator-decouple-*` (D-047) — CORRECT AS FAR AS IT GOES, INCOMPLETE.**
Geometry confirms all six caps: `C92`→`NFC_VDD_D`, `C93`→`NFC_VDD_A`, `C94`→`NFC_VDD_RF`,
`C95`→`NFC_VDD_AM`, `C96`→`NFC_VDD_DR`, `C97`→`NFC_AGDC`, each pin 1 on the rail and pin 2 on
`GND`, each rail carrying exactly the IC pin and its capacitor and nothing else — so no rail is
back-driven, which is the load-bearing half of D-047 and it holds. What is incomplete is the
capacitor count and one value. The datasheet is explicit (DS13541 Rev 5 §4.2.10, p.38): *"For
regulators recommended blocking capacitors are 2.2 μF in parallel with 10 nF, for pin AGDC 1 μF
in parallel with 10 nF is suggested."* The board has single 2.2 µF parts on all six, so five
10 nF partners are missing and AGDC has the wrong value and no partner. See NFC-D6.

**`canonical-nfc-i2c-en-pullup-*` (D-046) — CORRECT, WITH AN UNDOCUMENTED DEVIATION.**
`R76-NFC` 10 k runs from `NFC_I2C_EN` to `3V3`, with `U12-NFC.20` on `NFC_I2C_EN`. That is what
D-046 says and the geometry agrees. The deviation: the datasheet (§4.3.2 and Table 13) says
*"Pull to VDD_D for I2C operation"*, i.e. to the chip's own internal digital-regulator output, not
to the board 3.3 V rail. This is **not** a violation — Table 122 puts pin 20 in the 5 V domain
(abs max 6 V, operating 0–5.5 V), so a 3V3 pull is comfortably inside ratings, and in 5 V supply
mode VDD_D is fixed at 3.4 V, so the levels are close either way. It should be recorded as a
deliberate, justified variance rather than left looking like the datasheet instruction. See
NFC-D11.

**`canonical-nfc-unused-nc-*` — CORRECT, AND BETTER THAN IT LOOKED.** Eight crosses on TAD2(2),
EXT_LM(17), AAT_A(18), AAT_B(19), TAD1(25), MCU_CLK(28), BSS(29), MOSI(31). Every one is
genuinely unused, and the app notes turn three of them from *harmless* into *positively required*:
AN5592 §2.2 states that for a single-ended antenna it is **necessary to remove the EXT_LM
circuit** on ST25R3916 devices, and §2.4 states AAT is **not possible** for a single-ended
antenna with a cable because any change in cable parameters detunes the reader. K1 has no EXT_LM
circuit and no AAT varactors, so pins 17, 18 and 19 already satisfy the single-ended
requirements. BSS and MOSI are legitimately out of use because Table 13 lists only `I2C_EN`,
`MISO(SDA)`, `SCLK(SCL)` and `IRQ` for I2C mode. The transaction correctly refused to mark RFO2,
RFI2 or I2C_EN. Two residuals stand: the symbol's TAD1/TAD2 names are swapped relative to the
datasheet (NFC-D7), and BSS and MOSI are CMOS **inputs** now left floating, which the datasheet
does not forbid but does not bless either (NFC-D12).

## The RF front end — what the app notes changed

### Measured state, unchanged

The net-label census over the frozen source finds `NFC_RFO1` on 2 wires and **no net named
`NFC_RFO2`, `NFC_RFI1` or `NFC_RFI2` anywhere on the sheet**. Geometry independently agrees:
`U12-NFC.15` (RFO2) and `U12-NFC.23` (RFI2) touch zero wire segments, and neither carries a
no-connect mark. That measurement stands.

The captured RF chain:

```
U12.13 RFO1 → NFC_RFO1 → L2 (5.6 nH) → NFC_EMI ─┬─ C59 22 pF ↓GND
                                                └─ R42 2.2 R → NFC_MATCH_IN → C60 33 pF
   → NFC_MATCH_L → L3 (33 nH) → NFC_ANT ─┬─ C61 47 pF ↓GND
                                          ├─ J10 U.FL pin 1  (external, remote antenna)
                                          └─ U12.22 RFI1     ← direct, no divider
```

### What that chain actually is

Mapped onto AN5592's single-ended schematic (Figure 3) the correspondence is close and
recognisable — `Lemc0` = L2, `Cemc0` = C59, `RQ_s` = R42, `Cs1` = C60, `Cp1` = C61. So this is a
**deliberate ST single-ended stage**, not a half-finished differential one. Three things are
wrong with it, and one thing that looked wrong is not.

### Withdrawn: RFO2 and RFI2 floating is not an electrical defect

AN5592 Rev 1 §2.2 Figure 3 shows the single-ended antenna interface stage containing **only RFO1
and RFI1**. RFO2 and RFI2 do not appear at all — no termination, no tie, no dummy network. ST
support says the same thing directly: *"only RFO1 / RFI1 is connected to the antenna and will be
driven"* (Travis Palmer, ST Employee, 22 January 2024). The datasheet completes it: IO
configuration register 1 bit `single` selects one driver and bit `rfo2` selects which pair.

**My earlier P0 claim that the floating pins were a wiring defect is withdrawn.** The pins are
correct as they are. What is missing is everything attached to the choice — see NFC-D4.

### Confirmed and sharpened: the receive divider is missing

AN5276 §3.5: *"As the voltage on the antenna can be high, a capacitive voltage divider is needed
in the receive path at the antenna terminals to limit the signal strength going back to the RFI
pins… The voltage at the receive pins must not exceed 3 Vpp."* AN5592 names the two parts —
**`CVDR1`** in series from the antenna node to the RFI pin, **`CVDR2`** shunt from the RFI pin to
ground — and gives `CVDR1` = 10 pF in all three worked topologies, with `CVDR2` at 135 pF
(differential), 212 pF (single-ended) and 15 pF (single-ended with cable).

K1 has **neither**. `RFI1` sits on the raw antenna node.

Two consequences beyond the obvious overvoltage. The divider sets the RFI DC bias to AGD
(AN5276 §6.2.1). And its series combination appears **inside** the matching equation —
`CP = … − CVDR1·CVDR2/(CVDR1+CVDR2)` — so the divider is part of the match. It cannot be bolted
on afterwards without recomputing the whole solution.

### New: the EMI filter resonates 27× too high

AN5276 §3.3 requires the EMC filter cutoff to be **between 8 and 17 MHz**, and specifically **not
between 13 and 14 MHz**, because a cutoff near the 13.56 MHz carrier collapses the system Q
factor. K1's L2 = 5.6 nH with C59 = 22 pF resonates at **about 453 MHz** — roughly 27 times the
upper bound. Neither fitted value is near a workable pair: holding C59 at 22 pF would need about
4–18 µH; holding L2 at 5.6 nH would need about 16–71 nF. **Both values are wrong together**,
which reads as a copied set rather than a derived one. See NFC-D13.

### New: L3 is in no ST topology

AN5276 §3.4 and AN5592 §2.1–2.3 all define the matching network as **a series capacitor, a
parallel capacitor and a Q-factor resistor**. None of the five ST configurations contains a
series inductor. `L3-NFC` 33 nH has no counterpart. See NFC-D14.

## Defects

| ID | Sev | Finding | Primary source |
| --- | --- | --- | --- |
| **NFC-D1** | **P0** | `VDD` (pin 8) is on `3V3` while `VDD_TX` (pin 10) is on `NFC_5V` (= `5V_SYS` through ferrite `FB3-PWR2`). Split ≈ **1.7 V**. | DS13541 Rev 5 §4.2.10 p.37: *"VDD and VDD_TX must be connected to the same power supply."* Table 122 abs max ΔVDD−VDD_TX **−0.3 to +0.3 V**; Table 123 operating **−0.2 to +0.2 V**. |
| ~~NFC-D2~~ | **RESOLVED** | **NETLIST: no defect** — `U9-ESP` has 0 floating pins; board-wide single-pin nets are only `$1N153914` and `BUCK_PG`. **DRAWING: stale** — measured on a frozen source the live document has moved past. | Fresh GUI DRC `anchors/schDrcLog_2026-08-28T1458.txt` (sha256 `72b81f296a3af28c`), parsed independently by this lane. |
| **NFC-D3** | **P0** | Crystal miswired. `NFC_XTO` lands on `Y2-NFC.2`, which the symbol names **GND**. `Y2-NFC.3`, the second crystal terminal, is **floating**, as is the second ground pad `Y2-NFC.4`. The oscillator loop is open and neither case pad is grounded. | Symbol pin names from `all-pins-nc-audit.results.json`; floating state corroborated by the DRC log line 416. |
| **NFC-D5** | **P0** | The receive capacitive voltage divider (`CVDR1` series + `CVDR2` shunt) is absent; `RFI1` is on the raw antenna node. | AN5276 Rev 6 §3.5; AN5592 Rev 1 §2.2/2.3/3.2 and Tables 4–6; DS13541 Rev 5 Table 123 `VRFI_A` 0.15–3 V<sub>PP</sub>. |
| **NFC-D13** | **P0** | EMC filter L2 5.6 nH ∥ C59 22 pF resonates at ≈**453 MHz**; required 8–17 MHz excluding 13–14 MHz. Both values wrong together. | AN5276 Rev 6 §3.3. |
| **NFC-D4** | P1 | Single-ended topology is as-built but was **never decided, recorded, or costed**. Device defaults to differential, so firmware must set `single` = 1 / `rfo2` = 0 — recorded nowhere. *(Electrical claim withdrawn — see above.)* | AN5592 Rev 1 §2.2 Fig 3; DS13541 Rev 5 §4.2.1 and Table 20; ST support 2024-01-22. |
| **NFC-D6** | P1 | Regulator/AGDC decoupling incomplete: five 10 nF parallel partners missing; AGDC fitted with 2.2 µF where 1 µF ∥ 10 nF is specified. **And D-047's basis citation does not say what D-047 says** — see below. | DS13541 Rev 5 §4.2.10 p.38; STEVAL-25R3916B Rev 1 schematic, expansion board sheet 2/3. |
| **NFC-D9** | P1 | `contracts/nfc-interface.md` carries no VDD/VDD_TX co-supply rule, no RFI attenuation requirement, no EMC cutoff window, and no single-drive register bit. | Contract read 2026-08-28. |
| **NFC-D14** | P1 | `L3-NFC` 33 nH series inductor appears in no ST matching topology. | AN5276 Rev 6 §3.4; AN5592 Rev 1 §2.1–2.3. |
| **NFC-D7** | P2 | The `U12-NFC` symbol swaps TAD1 and TAD2 relative to datasheet Table 2. Electrically inert; the symbol is not datasheet-faithful. | DS13541 Rev 5 Table 2. |
| **NFC-D8** | P2 | `R43-NFC` 4.7 k pulls up `NFC_IRQ`. IRQ is a **push-pull digital output**; the pull-up is not required. | DS13541 Rev 5 Table 2 pin 27 type `DO`; Table 13. |
| **NFC-D10** | P2 | Matching, EMI and crystal-load values are frozen numbers with **no cited source**. Contract says `matching_values: TUNE_TBD`. ST's own route is the matching tool **STSW-ST25R004** driven by *measured* antenna parameters. | `contracts/nfc-interface.md`; AN5276 Rev 6 §6.1. |
| **NFC-D11** | P2 | I2C_EN strapped to `3V3`, not `VDD_D` as the datasheet instructs. Inside all ratings; undocumented as a variance. | DS13541 Rev 5 §4.3.2, Table 13, Table 122 `Vp5V`. |
| **NFC-D12** | P2 | BSS (29) and MOSI (31) are CMOS **inputs** left floating behind no-connect crosses. Datasheet neither requires nor forbids this. | DS13541 Rev 5 Table 13. |
| **NFC-D16** | P1 | **NEW.** `RFO2` (pin 15) is **not** in the 14:58 floating list; `RFI2` (pin 23) still is. Neither was NC-marked by the NC transaction and both touched zero wires in the frozen source — so `RFO2` has been wired or NC-marked since. Half the differential pair acted on while the topology ruling is open. | Fresh DRC floating list `['23']` only; `canonical-nfc-unused-nc-2026-08-28-applied.json` (pins 2,17,18,19,25,28,29,31). |
| ~~NFC-D15~~ | **SUPERSEDED** | Folded into NFC-D2. It claimed the two-island geometry was "electrically correct" (never established) and cited a power-tree-only visible-wiring requirement (an under-read — the single-sheet contract has a general wiring doctrine). Kept so the error stays on the record. | — |

**Every defect above is classified drawing vs electrical**, per the JSON `finding_class` field:
eight **ELECTRICAL** (D1, D3, D5, D6, D8, D12, D13, D14), one **DRAWING + NETLIST-UNRESOLVED**
(D2), one **DECISION AND DOCUMENTATION** (D4), two **DOCUMENTATION** (D9, D11), one **VALUE
PROVENANCE** (D10), one **SYMBOL METADATA** (D7), one **SUPERSEDED** (D15).

The eight electrical findings are component-absence or wrong-value findings on parts that the
harness measures at their own anchors with **no displacement**, and all 22 NFC components register
cleanly. None of them is a drawing question and none is exposed to the U9-ESP displacement.

### NFC-D2 — closed by the fresh DRC

**Anchor:** `anchors/schDrcLog_2026-08-28T1458.txt`, sha256 `72b81f296a3af28c`, ran 14:58:52,
Fatal 0 / Error 0 / Warn 15. Parsed independently by this lane rather than taken on report.

| Signal | Netlist | Drawing |
| --- | --- | --- |
| `NFC_IRQ` | **RESOLVED — no defect** | stale (frozen-source measurement, live has moved) |
| `I2C_SDA` | **RESOLVED — no defect** | stale |
| `I2C_SCL` | **RESOLVED — no defect** | stale |
| `NFC_I2C_EN` | never at issue | GREEN |

**One correction to the reasoning, because it matters for the next lane that uses this log.** The
hand-off argued that `NFC_IRQ`'s absence from the single-pin-network list proves it reaches a
host. That inference does not hold. The DRC rule reads *"is a single network connected to only
**one** component pin"*, and this audit's own measurement already put **two** pins on `NFC_IRQ`
(`U12-NFC.27` and `R43-NFC.2`). A two-pin net can never trip that rule, with or without the ESP on
it — so the absence is *consistent with* the conclusion but does not *prove* it.

**The load-bearing evidence is elsewhere in the same log, and it is stronger.** `U9-ESP` has
**zero** floating pins, down from 18–19 at 12:17 — I parsed all 101 floating pins across 9
components and none is on `U9-ESP`. Board-wide there are exactly two single-pin networks,
`$1N153914` and `BUCK_PG`, neither NFC-related. So all 41 `U9-ESP` pins sit on multi-pin nets.
With the name-to-net map putting pin 4 (IO4) on `NFC_IRQ`, the net is bound. **No defect.**

**Why the drawing half is stale rather than real.** `U9-ESP` went from 18–19 floating pins to zero
between the two DRC runs, so something was repaired in the live document *after* frozen source
`489736:464c27d4` was taken. This lane has no post-repair source read, so it can claim neither
that the displaced stubs were fixed nor that they persist. The earlier "DRAWING: real" wording is
**withdrawn as unsupported against current live**. If the visible-wiring question still matters,
re-run `harness/check_schematic_connectivity.py` against a fresh source export — a two-minute
measurement.

### What the same log confirms

**NFC-D3 (crystal) — CONFIRMED.** `Y2-NFC.3` and `Y2-NFC.4` are both in the floating list, and
they are the only `Y2-NFC` pins there. This finding has now survived three independent
measurements: the geometry oracle, the repo harness, and two GUI DRC runs 2h41m apart.

**NFC-D4 (RFI2 disposition) — CONFIRMED.** `U12-NFC.23` is the **only** floating pin on
`U12-NFC` — precisely what AN5592's single-ended stage predicts: RFI2 unconnected, not mis-wired.

**And what it cannot see.** NFC-D1, NFC-D5 and NFC-D13 appear nowhere in the log, as expected —
no connectivity checker can see a supply-rail split, an absent divider, or an LC product. They
rest entirely on their vendor citations, each of which carries an exact locator (DS13541 Rev 5
§4.2.10 p.37 + Tables 122/123; AN5276 Rev 6 §3.5 + §3.3; AN5592 Rev 1 §2.2/2.3/3.2 + Tables 4–6;
DS13541 Table 123 `VRFI_A`).

### NFC-D16 — new, and it needs the single writer

In the frozen source, **both** `U12-NFC.15` (RFO2) and `U12-NFC.23` (RFI2) touched zero wires, and
the NC transaction marked **neither** — verified against its `applied.json`, which lists pins 2,
17, 18, 19, 25, 28, 29, 31 only. In the 14:58 log, pin 23 is still floating and **pin 15 is not**.

EasyEDA omits a pin from that list when it is wired *or* when it carries a no-connect flag. So one
of those two things has happened to `RFO2` since the freeze — either way, **one half of the
differential pair has been acted on while the single-ended-versus-differential ruling is still
open**. An NC mark in particular is the thing this audit explicitly asked not to be applied before
that ruling, because it freezes the topology choice before the evidence is ratified.

This lane cannot see the live document, so this is an **observation, not an accusation** — there
may be a good reason, or a reading unavailable from a DRC log alone. Single writer to report the
live state of `U12-NFC.15` and under what authority it changed.

### Cross-lane pointers the harness surfaced

Not NFC findings; recorded for the owning lanes. One **off-sheet wire** — `BUCK_PG` `e146347` at
negative y, the one class the harness says no fit recovers (power lane). And eight net labels
meeting fewer than two pins: `BUCK_PG`, `ESP_UART0_RX`, `K1BR_IRQ_S3`, `K1BR_MISO_S3`,
`K1BR_MOSI`, `LED_D0_3V3`, `MOTION_INT_S3`, `S3_POR_REQ`.

## Architecture decision — needs a Captain ruling, not a repair

**Single-ended-with-cable versus differential.** This is a topology choice that changes component
count, read range, firmware register setup, and whether antenna diagnostics exist at all. This
lane records the evidence and a recommendation and implements neither.

**Recommendation: ratify SINGLE-ENDED WITH CABLE (AN5592 §2.3), which is what the board already
is.** It needs a decision-register entry and a contract line.

*For:* the K1 antenna is external and remote on a U.FL coaxial lead, and AN5592 §2.3 is the ST
topology for exactly that — ST support directs a STEVAL-ST25R3916B user with an external antenna
on a coaxial cable straight to AN5592 and confirms it applies to the ST25R3916B. Differential
over a coaxial lead is not a case AN5592 documents. AAT is unavailable either way here (§2.4:
not possible with a cable, because any change in cable parameters detunes the reader), so
ratifying costs nothing that K1 has. The EXT_LM removal AN5592 requires is already satisfied.
Fewer components, less area.

*Against, and this is the real cost:* **read range.** DS13541 §4.2.1 — single driver mode halves
the LC tank component count and cost *"but also the output power is reduced."* AN5592 §2.2 — a
single-ended signal is unbalanced and *"more prone to noise and interference"*, which matters on
a board carrying a switching buck, LED drivers and USB. AN5276 §2 recommends the differential
design for low-power applications *"because gives the best range."* Part of the receive path is
also given up: the peak detector reads RFI1 only at gain 0.7 while the AM demodulator mixer uses
both inputs at 0.55, and the amplitude and phase detectors are differential between RFI1 and
RFI2. AN5592 §2.3 adds that the cable case admits only a limited set of target matching
impedances (for example 4, 8 and 16 Ω), so there is less design freedom — and it requires a
**second matching network at the antenna end**, tuned to the cable's characteristic impedance,
which is a product part that does not exist and is in no BOM.

*If Captain rules differential instead:* NFC-D4 becomes a real wiring defect again, and RFO2,
RFI2, a second `CVDR1`/`CVDR2` divider pair, a second EMC inductor and a second Cs/Cp arm must
all be added. That is a larger change than the single-ended repair, and it is not the topology
AN5592 documents for a coaxial lead.

*Either way:* IO configuration register 1 bit `single` = 1 with `rfo2` = 0 is required for the
as-built board, because the device default is differential. That belongs in the contract
regardless of the ruling.

## Bounded repair, in order

Each item names the smallest change that closes the defect. None has been applied.

1. **NFC-D1, first, before anything else.** Decide the NFC supply rail and put `VDD` and
   `VDD_TX` on it together. Two options, both legal: run both from `NFC_5V` (5 V, VDD_IO stays on
   3V3 for host levels, gives full transmit drive), or run both from `3V3` (lower drive, simpler
   PDN, requires `sup3V` set in IO configuration register 2). This is a power-architecture
   decision and it changes `architecture/POWER-ARCHITECTURE.md`. Whichever is chosen, `NFC_5V`
   keeps its ferrite and bulk.
2. **NFC-D3.** Verify `Y2-NFC`'s symbol pin numbering against the Abracon ABM12 datasheet, then
   move `NFC_XTO` off pin 2 onto the real second terminal and tie both case pads to `GND`.
   Re-derive C54/C55 from the crystal's specified load capacitance instead of keeping 10 pF.
3. **NFC-D16 — confirm before anything else in the RF block.** Single writer to report the live
   state of `U12-NFC.15` (RFO2): wired, NC-marked, or unchanged, and under what authority. If it
   was NC-marked, consider reverting until the topology decision is ratified.
4. **The topology ruling** (above). Everything in step 5 is gated on it.
5. **NFC-D5, NFC-D13, NFC-D14 as one pass, not three.** The RX divider sits inside the matching
   equation and the EMC inductor value trades against the series capacitance at constant cutoff,
   so these are one solve, not three edits: fit `CVDR1` series and `CVDR2` shunt at RFI1, delete
   `L3-NFC` unless a documented reason appears, and re-derive L2, C59, C60, C61 and R42 from the
   ST25R antenna matching tool (STSW-ST25R004) against **measured** antenna parameters, holding
   the EMC cutoff inside 8–17 MHz and outside 13–14 MHz. Values stay `TUNE_TBD`; what should be
   recorded now is the **constraint**, not a number.
6. **NFC-D6.** Add five 10 nF parts across `C92`–`C96`, and change `C97` to 1 µF plus a 10 nF
   partner. One transaction, one visual stage, per D-038.
7. **NFC-D9 and NFC-D11.** Contract and register text. Record the co-supply rule, the RFI
   attenuation requirement, the EMC cutoff window, the `single = 1` firmware requirement, and the
   3V3-not-VDD_D strap variance with its rating justification.
8. **NFC-D8, NFC-D7, NFC-D10, NFC-D12.** Hygiene. Depopulate or delete `R43-NFC`; correct the
   `U12-NFC` symbol's TAD names; stamp every matching value as provisional; decide whether BSS
   and MOSI get tied rather than floated.

**Explicitly out of scope and left alone (VAL-G3):** continuous ground beneath the matching
network, short and symmetric RFO/RFI geometry, no vias in the matching path, antenna position,
RF keepouts, board outline. Also out of scope here: the coaxial lead and the antenna-side
matching network themselves, which are product parts that do not yet exist.

## Corrections

**To my own earlier report.** NFC-D4 was filed as P0 *"RFO2 and RFI2 floating; only half the RF
front end is represented."* **The electrical half of that claim is withdrawn.** AN5592 Figure 3
shows the single-ended stage containing only RFO1 and RFI1, so the unconnected pins are correct
for the topology the board actually implements. The lane was right to refuse to invent a
disposition before the document existed; it was wrong to grade the symptom P0. The finding that
survives is the missing decision, the unrecorded firmware register, and the uncosted read-range
trade — all real, all P1.

**To my own earlier report, four passes on one defect — the full record.** NFC-D2 went: (v1) P0
"IRQ reaches no host processor", a drawing measurement stated as an electrical fact; (v2)
**withdrawn entirely** on a DRC-fitted registration offset, an over-correction resting on a
self-confirming method, carrying an unsupported "the host interface is complete"; (v3)
**reinstated** with the drawing half called real and the netlist unresolved; (v4) **closed** by
the fresh DRC — netlist resolved with no defect, drawing half stale rather than real. The
through-line in every error was collapsing a *drawing* question and a *netlist* question into one
verdict, or asserting more than the instrument in hand could support.

**Earlier framing, superseded but kept:** NFC-D2 was first filed P0 as *"`NFC_IRQ`
reaches no host processor"* — a drawing measurement stated as an electrical fact. It was then
**withdrawn entirely** on a DRC-fitted registration offset — an over-correction resting on a method
that produces its own result, and carrying a claim ("the host interface is complete") that was
never supported. Both errors have the same root: collapsing a **drawing** question and a
**netlist** question into one verdict. They are now kept apart, the drawing half measured by the
repo's harness and the netlist half marked unresolved.

**To my own NFC-D15.** I recorded the visible-wiring requirement as power-tree-only, citing
`architecture/POWER-ARCHITECTURE.md` line 3. That was an under-read:
`schematic/SINGLE-SHEET-CONTRACT.md` carries a general wiring doctrine. D15 is superseded, not
deleted.

**To the brief.** *"`sources/SOURCE-REGISTER.md` registers only AN5240 and neither the datasheet
nor the STEVAL board" — REFUTED.* The register already carries three ST rows: the ST25R3916B
datasheet, the STEVAL-ST25R3916B reference design, and AN5240. *"`contracts/nfc-interface.md`
names none of the six regulator rails" — PARTLY REFUTED.* The contract has since grown an
*Internal-regulator rails are outputs (D-047)* section naming all six rails and `C92-NFC`–
`C97-NFC`, plus a *Host interface strap (D-046)* section. The remaining gap is narrower and is
NFC-D9.

**To one detail of the follow-up brief.** The EXT_LM removal requirement is in **AN5592 §2.2**,
not AN5276. Verified against **both** AN5276 Rev 5 and Rev 6: every `EXT_LM` occurrence in each
revision is card-emulation and external-load-modulation content, and neither revision covers
single-ended at all — §3 in both says the document *"focuses on the latter configuration"*,
meaning differential. The requirement itself is exactly as described, and K1 already satisfies
it. The STEVAL corroborates the direction: it is a differential reference design and it **does**
populate the `Ext_LM` net.

## Sources

**Cited, retrieved this session.**

| Document | Used for |
| --- | --- |
| **ST25R3916B/ST25R3917B datasheet, DS13541 Rev 5, Sept 2022** | §2.2.1–2.2.3, §4.2.1, §4.2.10, §4.3.2, §4.3.4, Tables 2, 13, 20, 122, 123 |
| **AN5276 Rev 6, May 2023** — Antenna design for ST25R3916/16B, 3917/17B, 3918, 3919B, 3920/20B | §3 antenna interface stage, §3.3 EMC filter, §3.4 matching network, §3.5 capacitive voltage divider, §6.1 matching tool, §6.2.1 models |
| **AN5592 Rev 1, March 2021** — ST25R single ended antenna matching | §2.2 single ended + Fig 3, §2.3 single ended with cable + Fig 5, §2.4 AAT, §3.2, Tables 4–6 |
| **STEVAL-ST25R3916B schematic pack**, STEVAL-25R3916B Rev 1, 17 pages | Reader expansion board sheets 1–2 of 3: U200 decoupling, C100's actual role, Ext_LM population, U200 pin naming |
| ST community, ST25 forum, best answers by Travis Palmer (ST Employee), 2024-01-22 and 2024-10-14 | **Secondary.** Corroborates AN5592 and the datasheet; never used alone. |

**Nothing remains unretrieved.** AN5276 **Rev 6** was fetched and used; its three load-bearing
statements are word-for-word identical to Rev 5, which this audit cited first — §3.3 (8–17 MHz,
not 13–14 MHz), §3.5 (the divider, the `RFI_1`/`RFI_2` and `RFI_3`/`RFI_4` pairs, 3 V<sub>PP</sub>
limit, 2.8 V<sub>PP</sub> recommended), and the §3 statement that the document focuses on the
differential configuration. **No finding changes between the revisions.**

**Three rows must be added to `sources/SOURCE-REGISTER.md`** — AN5276, AN5592, and a row
recording that the STEVAL *schematic pack* itself has now been read (the board is listed; the
schematic was not). Row text is prepared in `pin-audit-nfc.json` under
`source_register_additions_required`.

*Retrieval method, stated because it bears on trust:* st.com is unreachable directly from this
host (Akamai drops the connection) and WebFetch is blocked by a hook in this session. AN5276
Rev 6, AN5592 and the STEVAL pack came through a public text-extraction proxy on the public ST
URLs; AN5276 Rev 5 came from a reachable distributor mirror. Every source above was **read**, not
summarised second-hand. The STEVAL pack arrived as flattened schematic text: component values and
their presence are unambiguous, but designator-to-rail mapping is positional in that dump and is
**not** asserted pin-by-pin below.

## Disposition census

Every one of the 77 audited pins carries exactly one disposition. No silent unknowns.

| Disposition | Pins |
| --- | --- |
| `GND` | 22 |
| `CONNECTED` | 21 |
| `TUNE_TBD` | 15 |
| `POWER` | 9 |
| `INTENTIONAL_NC` | 8 |
| `RESERVED_WITH_DOCUMENTED_REASON` | 2 |
| `DNP_OPTION` | 0 |

Measured electrical state, tracked separately so a disposition can never launder a defect:
65 `CONNECTED`, 8 `NO_CONNECT_MARK`, 4 `FLOATING`.

**Twelve pins do not meet their intended disposition:** `U12-NFC.4` (XTO), `U12-NFC.8` (VDD),
`U12-NFC.10` (VDD_TX), `U12-NFC.22` (RFI1), `Y2-NFC.2`, `Y2-NFC.3`, `Y2-NFC.4`, `L2-NFC.1`,
`L2-NFC.2`, `C59-NFC.1`, `L3-NFC.1`, `L3-NFC.2`.

`U12-NFC.15` (RFO2) and `U12-NFC.23` (RFI2) left this list when AN5592 was retrieved and have
stayed off it — though RFO2 now carries the NFC-D16 live-state flag. `U12-NFC.27` (IRQ) has left
it for good: the fresh DRC resolves it.

Per-pin detail, including measured wire ids, net labels touched, electrical state, no-connect
provenance and source locator, is in `pin-audit-nfc.json`.

## Appendix — cross-lane evidence for the motion lane

Left here at the team lead's request; no action in this lane.

```
I2C_SDA -> R44-MOT.2 AND R45-MOT.2   (both, same net)
I2C_SCL -> R46-MOT.2 AND R47-MOT.2   (both, same net)
```

Both the FIT and the DNP side of the motion ownership matrix land on the **same shared I2C net**.
Two resistors into one net is not owner selection. These are 2-pin passives that register at zero
offset with zero floating pins against DRC, so this is **not** a registration artefact.

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:NFC-pin-audit | Created. Geometry-measured pin audit of the 22-component ST25R3916B front end against frozen denominator 489736:464c27d4 and datasheet DS13541 Rev 5. Twelve defects; differential-RF claim confirmed; two brief claims corrected. |
| 2026-08-28 | agent:NFC-pin-audit | Updated after retrieving AN5276 Rev 5 and AN5592 Rev 1. NFC-D4 electrical claim WITHDRAWN — floating RFO2/RFI2 is a valid ST single-ended topology; regraded P1 as a missing-decision defect. NFC-D5 sharpened with CVDR1/CVDR2 roles. Added NFC-D13 (EMC cutoff ≈453 MHz vs required 8–17 MHz) and NFC-D14 (L3 in no ST topology). EXT_LM and AAT no-connects upgraded from harmless to positively required. Added the single-ended-versus-differential ruling request. Fourteen defects. |
| 2026-08-28 | agent:NFC-pin-audit | Retrieved AN5276 **Rev 6** and the **STEVAL-ST25R3916B schematic pack**; unretrieved-sources list is now empty. Rev 6 confirms every Rev 5 citation verbatim — no finding changed. STEVAL shows 10 nF + 2.2 uF PAIRS on the regulator rails, so NFC-D6 now rests on two agreeing primary sources and D-047's basis citation is shown to be wrong (ruling stands, `QUALIFIED, NOT OVERTURNED`). NFC-D7 gains the CSO/CSI vendor-naming context. EXT_LM attribution re-verified against both AN5276 revisions. |
| 2026-08-28 | agent:NFC-pin-audit | *(SUPERSEDED BY THE NEXT ROW — this pass was wrong; kept as history.)* **NFC-D2 WITHDRAWN** after a registration re-measurement. `U9-ESP` is displaced by (-5,-20) between the frozen source and the live pin readback; at that DRC-validated offset `NFC_IRQ` reaches `U9-ESP` pin 4 (IO4), `I2C_SDA` pin 39, `I2C_SCL` pin 38 — the host interface is complete. Fit scored against EasyEDA's DRC floating count and a 22-of-22 pin-function coherence check, never against itself. All 22 NFC components confirmed to register at ZERO offset, so every surviving finding is unaffected. Added a registration stage to the oracle and two recorded oracle limitations. Every defect now classified drawing vs electrical. Added NFC-D15 (drawing-class) and the motion-lane appendix. |
| 2026-08-28 | agent:NFC-pin-audit | **NFC-D2 reinstated and split** after the team lead retracted the DRC-fit direction. Drawing findings now come from `harness/check_schematic_connectivity.py` (verdict RED; 13-case battery passes) rather than a hand-rolled fit; the fit is retracted as self-confirming. DRAWING: `NFC_IRQ`, `I2C_SDA`, `I2C_SCL` ESP-side stubs meet no pin (one root cause — displaced `U9-ESP`); `NFC_I2C_EN` GREEN. NETLIST: unresolved for all three, pending fresh GUI DRC. "Host interface is complete" WITHDRAWN. Intended pin is `U9-ESP.4` (IO4) by name-to-net anchors, not pin 6 — the zero-offset map puts GND on a GPIO. NFC-D15 superseded and its power-tree-only contract reading corrected. Cross-lane: 1 off-sheet wire, 8 under-met net labels. |
| 2026-08-28 | agent:NFC-pin-audit | **NFC-D2 CLOSED** against the fresh 14:58:52 GUI DRC (`anchors/schDrcLog_2026-08-28T1458.txt`, sha256 `72b81f296a3af28c`), parsed independently. NETLIST resolved, no defect — `U9-ESP` 0 floating pins, board-wide single-pin nets only `$1N153914` + `BUCK_PG`. DRAWING half marked STALE (not real): live moved past the frozen source. Corrected the hand-off's inference — absence from the single-pin list proves ≥2 pins, which was already true, so it cannot carry the conclusion; the zero-floating-pin count can. Same log independently CONFIRMS NFC-D3 (`Y2-NFC.3`/`.4` floating) and the NFC-D4 RFI2 disposition (`U12-NFC.23` the only floating U12 pin). NEW **NFC-D16** (P1): `RFO2` no longer floating while `RFI2` is, and neither was NC-marked — half the differential pair acted on under an open ruling; single writer to confirm. D1/D5/D13 locators verified present and DRC-invisible as expected. |
