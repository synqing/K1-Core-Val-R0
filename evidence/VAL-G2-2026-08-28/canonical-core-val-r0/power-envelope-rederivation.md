---
abstract: "Re-derivation of the K1-CORE-VAL-R0 5 V current envelope from the actually-selected parts, replacing the inherited 2.35 A / 0.95 A / 0.60 A design inputs. Result: 3V3 rail 0.18 A sustained and 0.65 A peak; 5 V trunk 1.15 A sustained, 2.08 A coincident peak, 2.40 A with 15 % validation margin. The inherited 2.35 A trunk is confirmed, the 0.60 A 3V3 figure is slightly low, and the 0.95 A LED figure turns out to be the U4-PWR2 eFuse ILIM setting read back rather than a load derivation. Answers plainly whether an arbitrary Type-C source can supply the board: no — 2.40 A at 5 V needs a source advertising 3.0 A, nothing on the board measures CC, and the largest load cannot be shed. Section 6 derives the two eFuse ILIM resistor values as an explicit output (R1-PWR1 = 1.24 kohm, R8-PWR2 = 3.48 kohm unchanged) and shows the trunk window has only 2.4 % of total slack."
---

# Power envelope re-derivation

**Status: PROPOSAL, not an instruction.** Derived from the frozen snapshot
`489736:464c27d4` and from primary vendor datasheets. The single writer owns the live canvas.

`architecture/POWER-ARCHITECTURE.md` carries 2.35 A trunk / 0.95 A LED branch / 0.60 A 3V3 as
*"carried forward from prior K1 power-class work as design input, to be re-derived for this
board."* This document is that re-derivation.

## How each number is labelled

| Tag | Meaning |
| --- | --- |
| **[DS]** | Taken from a primary vendor datasheet, cited inline |
| **[MEAS]** | Vendor's own measured application note, not a worst-case limit |
| **[SET]** | Fixed by a component value on this sheet — re-derived from the vendor equation |
| **[BUDGET]** | My engineering allocation where the vendor publishes no figure. Stated so it can be challenged |

Sustained and peak are kept in separate columns throughout. Collapsing them is how a supply gets
specified to a number nobody can defend.

---

## 1. The 3V3 rail — U3-PWR2 TPS62913

| Load | Sustained mA | Peak mA | Basis |
| --- | --- | --- | --- |
| RT1062 DCDC_IN @ 600 MHz | 53.1 | 110 | **[MEAS]** NXP AN12245 Rev 1 Table 7, 600 MHz overdrive, code in RAM · **[DS]** IMXRT1060CEC Rev 4 Table 12 worst case @ 95 °C |
| RT1062 VDD_HIGH_IN | 25 | 50 | **[DS]** IMXRT1060CEC Rev 4 Table 12 (peak) · **[BUDGET]** sustained |
| RT1062 VDDA_ADC_3P3 | 0.75 | 40 | **[DS]** IMXRT1060CEC Rev 4 Table 12 |
| RT1062 VDD_SNVS_IN | 0.25 | 0.25 | **[DS]** IMXRT1060CEC Rev 4 Table 12 |
| RT1062 NVCC_GPIO / SD0 / SD1 | 20 | 30 | **[BUDGET]** — NXP gives only the formula N·C·V·0.5F; no fixed figure exists |
| ESP32-S3-WROOM-1-N16R8 | 47.6 | **355** | **[DS]** Espressif v1.8 Table 6-6 modem-sleep 240 MHz peripherals on · Table 6-4 802.11b 1 Mbps @ 20.5 dBm |
| TLV320ADC6120 (AVDD + IOVDD) | 13.9 | 13.9 | **[DS]** TI SBASA92A, 2 ch @ 48 kHz, DRE enabled |
| ST25R3916B VDD | 4.5 | 23 | **[DS]** ST DS13541 Rev 5 Table 125, ready / all-active |
| ST25R3916B VDD_IO | 1 | 1 | **[BUDGET]** — DS13541 specifies no separate VDD_IO current |
| LIS2DH12 | 0.011 | 0.011 | **[DS]** ST DocID025056 Rev 6, 50 Hz ODR |
| U7-RTC, U8-RTDBG, U16-VAL, pull-ups, test points | 15 | 25 | **[BUDGET]** |
| **3V3 total** | **0.181 A** | **0.648 A** | |

**Re-derived 3V3 envelope: 0.18 A sustained, 0.65 A peak.**

The inherited **0.60 A** figure is therefore slightly **low** — by 8 % against the coincident
worst case. Recommend a 0.75 A design point (0.65 A + 15 %). The TPS62913 is a 3 A device
**[DS]** TI SLVSFP4B, so the regulator itself has enormous headroom; the number matters for the
5 V trunk it reflects upstream, not for the buck.

The single dominant term is the ESP32-S3 Wi-Fi transmit burst at 355 mA — 55 % of the peak. Under
D-007 the sole wireless control plane is BLE-MIDI, whose TX peak is 344 mA **[DS]** Espressif v1.8
Table 6-5, so parking Wi-Fi does **not** materially reduce this. The radio burst is irreducible.

### Reflected 5 V input to the buck

TPS62913 efficiency at 5 V → 3.3 V is published only as a graph; TI gives **no extractable
numeric efficiency point** at 0.3 A or 0.6 A. Using a deliberately conservative **90 %** **[BUDGET]**:

| | 3V3 out | Power out | Power in @ 90 % | 5 V input current |
| --- | --- | --- | --- | --- |
| Sustained | 0.181 A | 0.597 W | 0.664 W | **0.138 A** (incl. 5 mA I_Q) |
| Peak | 0.648 A | 2.139 W | 2.377 W | **0.480 A** |

---

## 2. The LED branches — and where the inherited 0.95 A actually came from

`J2-LED` and `J3-LED` are 3-pin JST XH headers to off-board strips. **Nothing on this board
determines the LED load.** What the board determines is the ceiling it permits, and that ceiling is
one component value:

    U4-PWR2 (TPS259474L), R8-PWR2 = 3.48 kohm
    R_ILM = 3334 / I_LIM   [DS] TI SLVSFC9C Eq. 5
    I_LIM = 3334 / 3480 = 0.958 A typ,  0.862 - 1.054 A over the +/-10 % band

**The inherited "0.95 A LED branch" is this eFuse setting read back, not a load derivation.** It is
self-referential — the design input and the thing it was supposed to constrain are the same number.
That does not make it wrong, but it means the figure has never been checked against a real strip,
and it should stop being described as a derived budget.

Both branches share `5V_LED_COMMON` downstream of one eFuse, so:

| | Value | Basis |
| --- | --- | --- |
| Combined L + R ceiling, guaranteed | **0.862 A** | **[SET]** worst-case low end of the ±10 % band |
| Combined L + R ceiling, nominal | **0.958 A** | **[SET]** |
| Combined L + R, worst-case high | 1.054 A | **[SET]** — the value the trunk must survive |
| Per-branch limit, FB1 / FB2 | 2000 mA @ 85 °C | **[DS]** Murata JENF243A_0005AE-01 — not binding |
| Per-branch limit, J2 / J3 contacts | 3 A | JST B3B-XH-A — not binding |

So a single side can draw the entire eFuse budget; the beads and connectors are not the constraint.
**The eFuse is the LED-branch specification**, and it should be stated that way in
`POWER-ARCHITECTURE.md` rather than as an independent 0.95 A load figure.

U14-LED / U15-LED (SN74AHCT1G125 level shifters) sit on the LED rails and are negligible: I_CC
10 µA max, C_pd 14 pF **[DS]** TI SCLS378P, giving ~56 µA dynamic at 800 kHz.

---

## 3. Remaining 5V_SYS branches

| Branch | Sustained | Peak | Basis |
| --- | --- | --- | --- |
| NFC — FB3 -> `NFC_5V` -> U12-NFC.10 VDD_TX | 0.005 A | **0.500 A** | **[DS]** ST DS13541 Rev 5 Table 122: I_VDD_EXT peak 500 mA. ST publishes **no** tabulated TX supply current — it is antenna-load dependent — so the absolute-maximum external-supply figure is used as the bound |
| Mic — U5-PWR2 TLV75533 -> Q1 -> `3V3_MIC` | 0.050 A | 0.050 A | **[BUDGET]**. LDO input ≈ output current; device max 500 mA **[DS]** TI SBVS320D |
| INA226 VS+ | — | — | On 3V3, already counted |

**NFC caveat that changes this line.** `U12-NFC.8 (VDD)` is on **3V3** while `U12-NFC.10 (VDD_TX)`
is on **NFC_5V**. ST DS13541 Rev 5 requires **VDD and VDD_TX to track within ±0.2 V**. The captured
split of 1.7 V violates that, so the NFC block cannot operate as drawn and its 5 V current is not
yet a settled number. Handed to the NFC owner; recorded here because it is the second-largest peak
term in the trunk.

---

## 4. The 5 V trunk

Through `J1.B4` -> F1-PWR1 -> U1-PWR1 -> RSH1-PWR1 -> `5V_SYS`.

| Branch | Sustained A | Coincident peak A |
| --- | --- | --- |
| 3V3 buck input | 0.138 | 0.480 |
| LED eFuse ceiling | 0.958 | 1.054 |
| NFC transmit | 0.005 | 0.500 |
| Mic LDO | 0.050 | 0.050 |
| **Trunk total** | **1.151 A** | **2.084 A** |
| **+ 15 % validation and accessory margin [BUDGET]** | 1.32 A | **2.397 A** |

**Re-derived trunk: 1.15 A sustained, 2.08 A coincident peak, 2.40 A design point.**

The inherited **2.35 A** is confirmed — within 2 % of the re-derived design point. It arrives there
by a different route than it was originally set, but it stands.

The 15 % margin is an engineering choice, not a datasheet figure. It covers `J11-VAL`, `J4/J5-RTDBG`,
`J6-ESP`, six test points, four switches and `U16-VAL`, all of which are low-current, plus the
board's stated mission of maximising bring-up and measurement capability. If the writer prefers a
different margin, the un-margined 2.08 A is the number to apply it to.

### What this does to the parts already selected

| Part | Rating | Against 2.08 A peak | Against 2.40 A design point |
| --- | --- | --- | --- |
| J1 VBUS contacts, all four bonded | 5.00 A collectively **[DS]** GCT USB4105 Rev A3 | pass | pass |
| J1 VBUS, **as captured (one contact)** | 1.25 A | **FAIL, 1.7x over** | **FAIL, 1.9x over** |
| F1-PWR1 BLM21PG221SN1D | 2000 mA @ 85 °C **[DS]** Murata | **FAIL, 4 % over** | **FAIL, 20 % over** |
| U1-PWR1 ILIM, R1 = 1.33 kΩ | 2.26 A guaranteed minimum **[SET]** | 8.6 % separation — inside the part's own tolerance | **FAIL, trips below load** |
| RSH1-PWR1 10 mΩ | 20.8 mV, 43 mW at peak | pass | pass |
| U1-PWR1 R_ON 45 mΩ max **[DS]** TI SLVSFC9C | 94 mV, 195 mW | 108 mV, 259 mW | pass, but note the drop |

Total series drop from connector to `5V_SYS` at the design point: F1 108 mV + eFuse 108 mV +
shunt 24 mV = **240 mV**. From a source at the low end of tolerance (4.75 V) that puts `5V_SYS` at
**4.51 V** — still above the buck's needs, but it is the number that should set the eFuse UVLO,
which is currently 4.17 V and therefore does not protect against a sagging source.

---

## 5. Can an arbitrary Type-C source supply this board?

**No.** Stated plainly, because this is the decision the numbers exist to support.

The board needs **2.40 A at 5 V = 12.0 W**. USB Type-C Spec R2.0 Table 4-18 gives exactly three
source advertisements at 5 V:

| Source advertisement | Rp | Available | Covers 12.0 W? |
| --- | --- | --- | --- |
| Default USB | 56 kΩ ±20 % / 80 µA | 500 mA (USB 2.0), 2.5 W | **No — 20 % of requirement** |
| 1.5 A @ 5 V | 22 kΩ ±5 % / 180 µA | 1.5 A, 7.5 W | **No — 62 % of requirement** |
| 3.0 A @ 5 V | 10 kΩ ±5 % / 330 µA | 3.0 A, 15 W | Yes, 80 % utilised |

Only a source advertising **3.0 A** can supply this board at its design point. That has three
consequences, and none of them is currently addressed on the sheet.

**1. The board cannot read the advertisement.** A sink learns what the source offers by measuring
the voltage its own Rd develops against the source's Rp current. J1 has **no Rd at all**, so it
never attaches. J7 has correct 5.1 kΩ Rd resistors but **no tap to any ADC** — R21-ESP and R22-ESP
go straight to GND. Nothing on this board can distinguish a 15 W charger from a 2.5 W laptop port.

**2. The board cannot shed its largest load.** `U4-PWR2.1 (EN/UVLO)` is tied hard to `5V_SYS`. The
LED branch — 46 % of the sustained trunk and 51 % of the peak — is unconditionally enabled at power
on, before any firmware runs. On a Default-USB source the board will attempt roughly 4x the
permitted current and the source will fold back or shut down.

**3. Advertisement detection wants to live on J1, and J1 is the connector with no CC circuit at
all.** J1 is the power inlet; J7 is sense-only by D-044 and correctly cannot power the board.

### Three defensible answers — the writer chooses, this document does not

- **(a) Sense and throttle.** Bring J1 CC1/CC2 to 5.1 kΩ Rd *and* tap both to RT1062 ADC inputs
  through protection dividers, and put `U4-PWR2.1` on an RT1062 GPIO. Firmware reads the
  advertisement and enables the LED branch only above 1.5 A. Highest capability, costs two ADC
  channels, one GPIO and four passives. Fits the board's stated validation mission.
- **(b) Design to 1.5 A.** Reprogram R8 so the LED ceiling plus everything else lands under 1.5 A,
  and accept a 7.5 W board that works on almost any Type-C source. Cheapest, and caps the LED
  branch at roughly 0.4 A combined.
- **(c) Specify the supply.** Declare a 3 A @ 5 V source a product requirement, keep the fixed Rd,
  and record that a Default-USB source is out of specification. Zero added circuitry, and the
  weakest position for a validation board that will be plugged into whatever is on the bench.

**Recommendation: (a).** This is the board whose mission document says it exists to maximise
bring-up capability, component evaluation and observability. Source-advertisement sensing and a
switchable LED branch are exactly the kind of measurement capability it should carry, and (b) or
(c) can still be adopted later in firmware by simply never enabling the branch. (a) is also the
only option that keeps the 2.40 A design point honest rather than aspirational.

Whichever is chosen, the CC/Rd question and the `U1-PWR1` ILIM question (`PIN-AUDIT-PWR1.md` §U1)
are the same decision seen from two ends and should be settled together.

---

## 6. Output: the required eFuse current limits

The BOM audit found both eFuse ILIM resistors bound to a shared 10 kΩ device
(`PIN-AUDIT-PWR1.md` § device-binding defect). The repair is not to restore what is drawn — those
values were chosen against the inherited figures this document replaces. **The ILIM values are an
output of this envelope, derived here.**

Governing equation, TI SLVSFC9C Eq. 5, for both TPS259474L instances:

    R_ILM(ohm) = 3334 / I_LIM(A),   accuracy +/-10 % for I_LIM > 1 A

### Trunk eFuse U1-PWR1 — two-sided constraint

| Bound | Value | Why |
| --- | --- | --- |
| **Lower** — `I_LIM(min)` must exceed the load | ≥ **2.397 A** | The design point from §4. Below this the eFuse nuisance-trips on a worst-case part |
| **Upper** — `I_LIM(max)` must stay under the source | ≤ **3.000 A** | A 3.0 A Type-C source (§5). The board should give way before the supply does |

Converting through the ±10 % band:

    typ >= 2.397 / 0.9 = 2.663 A      ->  R_ILM <= 3334 / 2.663 = 1252 ohm
    typ <= 3.000 / 1.1 = 2.727 A      ->  R_ILM >= 3334 / 2.727 = 1223 ohm

**Permitted window: 1223 Ω to 1252 Ω.** Standard values inside it:

| Value | I_LIM typ | min | max | Verdict |
| --- | --- | --- | --- | --- |
| 1.20 kΩ (E24) | 2.778 A | 2.500 A | 3.056 A | max exceeds 3.0 A |
| **1.24 kΩ (E96)** | **2.689 A** | **2.420 A** | **2.958 A** | **the only standard value that fits** |
| 1.30 kΩ (E24) | 2.565 A | 2.309 A | 3.026 A | min below the design point |
| 1.33 kΩ — *as drawn* | 2.507 A | **2.256 A** | 2.757 A | min below the design point — nuisance trip |

**Specification: R1-PWR1 = 1.24 kΩ, ±1 %, 0402.**

**This window is uncomfortably tight, and that is itself a finding.** The permitted ratio is
3.000 / 2.397 = **1.252**, and the part's own tolerance band spans 1.1 / 0.9 = **1.222**. There is
**2.4 % of total slack** in the entire design. Exactly one standard value fits, and any increase
in the validation margin — or any growth in the LED ceiling — leaves **no solution at all** from a
3 A source. That is a structural argument for capping the LED branch (§5 option b), not just a
component-selection note.

### LED eFuse U4-PWR2 — the ILIM *is* the specification

There is no independent LED load to derive from: the strips are off-board (§2). So the limit is
set by what the rest of the tree leaves available.

    non-LED coincident peak = 0.480 (buck) + 0.500 (NFC) + 0.050 (mic) = 1.030 A
    headroom under the repaired trunk's guaranteed trip = 2.420 - 1.030 = 1.390 A
    -> I_LIM(max) <= 1.390 A  ->  typ <= 1.264 A  ->  R_ILM >= 2638 ohm

| Value | I_LIM typ | max | Under the 1.390 A ceiling? |
| --- | --- | --- | --- |
| **3.48 kΩ — as drawn** | **0.958 A** | **1.054 A** | **yes, with 0.34 A to spare** |
| 2.67 kΩ | 1.249 A | 1.374 A | yes, but with no headroom |

**Specification: R8-PWR2 = 3.48 kΩ — keep the drawn value.** It is correct. Only its device
binding is wrong. Changing a value that verifies correct would be churn.

### If the board is redesigned for a 1.5 A source

§5 option (b) does not survive contact with these numbers, and it is worth recording why:

    available 1.5 A - non-LED coincident peak 1.030 A = 0.470 A for trunk headroom AND the LED branch
    after leaving any trunk-eFuse margin, the LED ceiling falls to roughly 0.15 A

A ~0.15 A LED ceiling is not a lighting product. **The LED branch forces a 3.0 A source.** Option
(b) is only viable if the non-LED peak is re-derived on a non-coincident basis — which would mean
proving that the Wi-Fi/BLE transmit burst and the NFC transmit burst cannot overlap, and that is a
firmware-scheduling claim, not a hardware one. Recorded as the lever someone will reach for; it
needs evidence before it can be used.

### Summary of BOM-affecting outputs

| Part | Function | Present | Specified | Action |
| --- | --- | --- | --- | --- |
| R1-PWR1 | Trunk eFuse ILIM | 1.33 kΩ, misbound to a 10 kΩ device | **1.24 kΩ ±1 % 0402** | New value **and** new binding |
| R8-PWR2 | LED eFuse ILIM | 3.48 kΩ, misbound to a 10 kΩ device | **3.48 kΩ ±1 % 0402** (LCSC C185418) | Binding only — value is correct |

---

## 7. Revised design inputs, for `POWER-ARCHITECTURE.md`

| Quantity | Inherited | Re-derived | Verdict |
| --- | --- | --- | --- |
| 5 V trunk | 2.35 A | 1.15 A sustained, **2.08 A peak, 2.40 A design point** | Confirmed |
| LED branch | 0.95 A | **0.958 A typ / 0.862 A guaranteed**, set by R8 = 3.48 kΩ | Confirmed, but it is an eFuse setting, not a load figure |
| 3V3 | 0.60 A | 0.181 A sustained, **0.648 A peak**; recommend 0.75 A | Slightly low |
| 5 V source requirement | *not stated* | **12.0 W; requires a 3.0 A Type-C advertisement** | New |
| NFC 5 V peak | *not stated* | 0.500 A, bounded by ST's absolute maximum | New, and blocked by the VDD/VDD_TX tracking defect |
| **R1-PWR1** trunk ILIM | 1.33 kΩ (min trip 2.26 A) | **1.24 kΩ ±1 % 0402** — 2.689 A typ, 2.42 A min, 2.96 A max | **Change.** Only standard value that fits |
| **R8-PWR2** LED ILIM | 3.48 kΩ | **3.48 kΩ — unchanged** (LCSC C185418) | Correct; binding repair only |
| Trunk ILIM design slack | *not stated* | **2.4 %** between the 2.40 A design point and a 3.0 A source | New — structural constraint on the LED ceiling |

---

**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:usb-power-audit | Created. Re-derived the 5 V and 3V3 envelopes from the selected parts against frozen hash 489736:464c27d4; confirmed the inherited 2.35 A trunk, identified the 0.95 A LED figure as an eFuse-setting readback, and answered the arbitrary-Type-C-source question. |
| 2026-08-28 | agent:usb-power-audit | Added section 6: both eFuse ILIM resistor values derived as an explicit output of the envelope in response to the BOM-audit device-binding BLOCKER. R1-PWR1 specified at 1.24 kohm; R8-PWR2 verified correct at 3.48 kohm; trunk window shown to carry only 2.4 % slack, which rules out the 1.5 A-source option. |
