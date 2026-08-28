---
abstract: "Pin-by-pin audit of K1-CORE-VAL-R0 power conversion, distribution and supervision (42 components, 120 pins) against the frozen denominator 489736:464c27d4. Two P0 defects: the TPS62913 PG pin is not connected because its BUCK_PG wire is mirrored to negative y off-sheet, and RT_PWR_VALID is decorative because the TPS3808 supervisor's SENSE input floats and no consumer is attached. Four P1 (LED buffer OE wired to the unsafe boot state with no controller, TLV75533 with no output capacitor, R8-PWR2 bound to the wrong library device, ESP32-S3 systematic +5-unit wiring offset). Power tree is electrically complete and passes K1E-017 but is visually a set of labels, not a tree."
---

# Pin audit — power conversion, distribution and supervision (PWR2 scope)

**Denominator:** `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/frozen-denominator-489736/` — hash `489736:464c27d4`, 228 designators, 143 nets, 675 wires.
**Machine-readable twin:** `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/pin-audit-pwr2.json`
**Status:** these are **proposals**. Live has moved past this hash; a single writer must reconfirm before mutating.

---

## 1. What was measured, and how it was proven able to fail

The sheet annotates 675 wires with net names. A checker that reads those names cannot tell a
connected pin from a stub labelled `BUCK_PG` that touches nothing — so this audit measures
**geometry**, not labels.

**Engine.** Union-find over all wire segments, merging on shared endpoints and on
endpoint-lies-on-segment T-junctions. Pin anchors from the host readback were matched into the
source frame as `(x, −y_readback)`; that frame was not assumed, it was **verified**: 629 of 782
pin anchors land exactly on a wire endpoint (80.4%), and all ten U3-PWR2 pins except the defective
one resolve cleanly.

**Fault battery.** An instrument nobody has seen go red is not an instrument.

| Case | Expected | Measured |
| --- | --- | --- |
| Control | 675 islands, 634 pins on copper, 0 multi-name bridges | as expected |
| Inject a wire bridging a `GND` stub to a `3V3` stub | RED | islands 675→674, bridges 0→**1** |
| Delete the wire feeding `C1-PWR1.1` | RED | that pin's `on_copper` True→**False** |
| Positive control: delete an unrelated wire | GREEN | victim pin still on copper |

The engine goes red for the right reasons and stays green on the control.

**Coverage.** 42 components in scope, **120 of 120 pins parsed and classified**, zero silent
unknowns. Sheet-wide: 228 of 228 designators returned a pin readback, 0 failed.

**Coverage gap, stated because it changes conclusions.** `U6-RTC` (MIMXRT1062DVJ6B) is a
**two-part symbol** — `COMPONENT` records `e3295` @ (2315,4440) and `e3673` @ (2250,3930). The
readback returned 98 pins for `e3673` **only** (bounding box y 3820–4040). Roughly twenty dangling
stubs sit at y 4200–4680, squarely in the unread `e3295` band. **Those are UNVERIFIED, not
defects** — including stubs labelled `1V15_CORE`, `3V3`, `LED_D0_3V3` and `LED_D1_3V3`. Any claim
about RT1062 rail or data completeness in that band is out of evidence and I make none. Every
finding below rests on components whose readback is complete.

**Verdict census (120 pins):** CONNECTED 37 · POWER 41 · GND 31 · INTENTIONAL_NC 9 ·
FLOATING_DEFECT 2.

The nine `INTENTIONAL_NC` calls are each backed by a vendor sentence, not by convention — the
TPS3808 `CT` and `MR` pins, the TPS25947 `PG`/`PGTH`/`ITIMER` pins, the TLV755P `NC` pin and the
tactile switch's second contact side are all explicitly permitted open by their datasheets. Two
pins resolve to none of the permitted states. `FLOATING_DEFECT` is used deliberately: the required
vocabulary has no honest slot for "this pin should be connected and is not", and forcing one of
them would hide the defect.

---

## 2. The two P0 defects

### PWR2-001 — the TPS62913 PG pin is not connected. D-045 is not satisfied.

The ledger records `R75-PWR2` as landed with `U3-PWR2` pin 5 on `BUCK_PG`. The pull-up half is
correct. **The pin half never landed.**

- `U3-PWR2` pin 5 (PG), absolute (1140, 4535), touches **zero wires**. Readback complete, 10 of 10.
- Net `BUCK_PG` has two wires. `e146317` = `[[990,4480],[1010,4480]]` lands correctly on
  `R75-PWR2` pin 1. `e146347` = `[[1000,−4535,1130,−4535],[1000,−4480,1000,−4535]]` lands on nothing.
- `e146347` is the **only wire on the entire 675-wire sheet with a negative y coordinate**. Its
  nearest pin of any kind is **6969 units** away. Every other dangling stub on the sheet is within
  452 units. It is drawn mirrored below the sheet frame.
- Two faults compound: the y sign is inverted, **and** the horizontal run stops at x=1130 where
  U3's left-column pins anchor at x=1140 (proven by pins 1, 2, 3 and 4, whose wires all terminate
  exactly at 1140).

An open-drain PG left floating reports nothing — which is precisely the sentence D-045 was written
to prevent, and this board exists to be measured.

> TI **SLVSFP4B** Table 5-1, pin 5: *"Open-drain power-good output... It requires a pullup resistor
> to output a logic high."*

**Bounded repair:** replace `e146347` with `[[1000,4535,1140,4535],[1000,4480,1000,4535]]`. One wire
edit, no component moves. Acceptance: `U3-PWR2` pin 5 reads `net=BUCK_PG` and `BUCK_PG` becomes a
two-pin net.

### PWR2-002 — RT_PWR_VALID is decorative. Both ends are broken.

This is the P0-H the brief predicted, and it is worse than predicted.

- `U16-VAL` (TPS3808G33DBVR) pin 5 **SENSE touches zero wires**. Readback complete, 6 of 6.
- Its only connected pins are `1 RESET# → RT_PWR_VALID`, `2 GND`, `6 VDD → 3V3`. **It monitors nothing.**
- Net `RT_PWR_VALID` has three wires but only two pins: `R62-VAL.2` (10 k pull-up to 3V3 — correct,
  and inside SBVS050M's 10 kΩ–1 MΩ window) and `U16-VAL.1`. The third wire `e8950` dangles **5.0
  units** from `U9-ESP` pin 9, the intended ESP32-S3 consumer. **Nothing reads the signal.**

The fixed-threshold G33 option does not excuse the floating SENSE — it moves the divider inside the
part, it does not remove the requirement to connect SENSE to the rail being watched.

> TI **SBVS050M** Table 6-1, SENSE: *"This pin is connected to the voltage to be monitored. If the
> voltage at this terminal drops below the threshold voltage V_IT, then RESET is asserted."*

There is also a **design question the repair cannot dodge**. Even wired to 3V3 (as its sibling
`U7-RTC` is), U16 would report on the shared 3V3 rail, not on anything RT-specific. The RT1062 core
rail is `1V15_CORE`, produced by the RT1062's own internal DCDC through `L4-RTC`
(`DCDC_SW → 1V15_CORE`). Monitoring 3V3 with a G33 is the defensible reading of D13.1 for a
fixed-threshold part; monitoring `1V15_CORE` needs the adjustable TPS3808G01 plus a divider, which
is a part change, not a wire edit. **That is a decision, not a chore.**

**Bounded repair:** (a) wire `U16-VAL` pin 5 to the chosen rail; (b) extend `e8950` by +5 in x onto
`U9-ESP` pin 9.

**Do not conflate the two PG signals.** The TPS62913 `BUCK_PG` of PWR2-001 and the supervisor's
`RESET#` are different signals with different meanings. Neither substitutes for the other.

---

## 3. P1 findings

### PWR2-003 — LED buffer output-enable is wired to the unsafe boot state, and nothing controls it

`R53-LED` and `R54-LED` are 10 k **pull-downs** to GND on `LED_OE_L` / `LED_OE_R`. `OE#` low means
**enabled**. TI says the opposite, explicitly:

> TI **SCLS378P** §7: *"To ensure the high-impedance state during power up or power down, OE should
> be tied to VCC through a pullup resistor."*

Worse, `LED_OE_L` has exactly two wires and two pins (`R53-LED.1`, `U14-LED.1`), with **no dangling
stub** — so there is no hidden third member and **no controller exists**. `LED_OE_R` is identical.
The buffers are permanently enabled, and their `A` inputs (`LED_D0_3V3` / `LED_D1_3V3`) are in the
unread RT1062 band, so at boot a permanently-enabled 5 V buffer may be driving the WS28xx strings
from an input of unknown state.

**Bounded repair:** move `R53`/`R54` from GND to `+5V_LED_L` / `+5V_LED_R`, and wire `LED_OE_L/R` to
RT1062 GPIOs. Until a controller exists the strings cannot be turned off.

### PWR2-004 — the mic LDO has no output capacitor; the 10 µF is on the wrong side of the switch

`3V3_MIC_REG` has exactly two wires and two pins — `U5-PWR2.5` (OUT) and `Q1-PWR2.2` (P-FET source)
— with no dangling stub, so no hidden capacitor exists. `C15-PWR2` 10 µF sits on `3V3_MIC`, which is
Q1's **drain**, downstream of the load switch; it cannot stabilise the regulator loop.

> TI **SBVS320D** Recommended Operating Conditions: C_OUT **1 µF minimum**. Features: *"Stable with
> a 1 µF ceramic output capacitor."*

Measured chain: `5V_SYS → U5 (TLV75533) → 3V3_MIC_REG → Q1 (DMG2305UX P-FET, gate MIC_PWR_EN,
R9 100 k pull-down ⇒ default ON) → 3V3_MIC → C15 → FB5-AUD → 3V3_MIC_FLEX → J9-AUD`.

**Bounded repair:** add ≥1 µF from `3V3_MIC_REG` to GND at `U5-PWR2` pin 5. One part.

### PWR2-005 — R8-PWR2 is bound to the wrong library device, and one candidate part kills the LED branch

The BOM row contradicts itself: `Name=3.48k`, `Manufacturer Part=RC0402FR-073K48L`,
`Supplier Part=C185418` — but `supplierId=RC0402FR-0710KL.1`, a **10 k** part.
LCSC **C185418 is confirmed as YAGEO RC0402FR-073K48L, 3.48 kΩ ±1%** — the correct part.

Root cause: `R8-PWR2` shares Device UUID `e1b1f220e40a4edea589adfa05a5d8c7` with `R75-PWR2`, the
10 k. R8 is bound to the 10 k library device with its value text overridden.

> TI **SLVSFC9C** Equation 5: `R_ILM(Ω) = 3334 / I_LIM(A)`. Recommended Operating Conditions:
> R_ILM **549 Ω to 6650 Ω**. Pin 9 ILM: *"Do not leave floating."*

| R8 fitted | I_LIM | Inside 549 Ω–6.65 kΩ? | Consequence |
| --- | --- | --- | --- |
| **3.48 kΩ** (intended) | **0.958 A** | yes | matches the 0.95 A LED branch figure carried forward in `POWER-ARCHITECTURE.md` |
| 10 kΩ (what `supplierId` names) | 0.333 A | **no** | below branch load *and* out of spec — the LED branch trips during inrush |

The wiring itself is correct (`R8.1 → LED_EFUSE_ILIM → U4-PWR2.9`, `R8.2 → GND`). The design intent
is right; the library binding is not. *(The 2.35 / 0.95 / 0.60 A envelope belongs to A1-USB-POWER to
re-derive — it is consumed here only as the comparator, not restated as my own result.)*

**Bounded repair:** rebind `R8-PWR2` to the C185418 device so all four BOM fields agree. No wiring change.

### PWR2-012 — ESP32-S3 is systematically unwired by a +5-unit offset (handoff)

`U9-ESP` readback is complete (41 of 41 pads) and **36 have no wire**. Seventeen dangling stubs sit
5.0–20.6 units away with a repeating delta: `(+5, 0)` down the left column
(`GND`→3, `3V3`→4, `ESP_EN`→5, `NFC_IRQ`→6, `MOTION_INT_S3`→7, `S3_POR_REQ`→8, **`RT_PWR_VALID`→9**,
`ESP_USB_VBUS_SENSE`→10) and `(−5, +20)` across the K1BR bus (pins 17–21). This is **one systematic
placement offset, not seventeen errors** — one batch stub-translation fixes it. Flagged here because
it holds the `RT_PWR_VALID` consumer and ESP 3V3/GND rail members; the repair belongs to the ESP/debug lane.

---

## 4. P2 / P3 findings

| ID | Sev | Finding | Basis |
| --- | --- | --- | --- |
| PWR2-006 | P2 | Buck FB bottom leg `R6-PWR2` = **32.4 kΩ**, 6.5× the vendor maximum. This defeats the low-noise property that is the only reason to pick a TPS62913. | SLVSFP4B §8.2.2.2.6: *"set R2 equal to or lower than 5 kΩ"* |
| PWR2-007 | P2 | `LED_THERM_L`/`_R` NTCs have **no bias resistor**. `RT1-LED` pin2→GND, pin1→`LED_THERM_L`; the net has exactly 2 wires / 2 pins and no dangling stub, so no hidden top leg exists. The node sits at 0 V regardless of temperature. | Elementary divider; NCP15XH103F03RC is passive |
| PWR2-011 | P2 | Buck C_OUT is 2 × 47 µF (10 V 0805 X5R) = 94 µF nominal, but effective capacitance after DC-bias derating at 3.3 V is likely 50–60 µF. Against a **40 µF effective minimum** this probably passes — but it is not proven, and the datasheet warns about exactly this. | SLVSFP4B ROC: effective C_OUT 40 µF min / 47 typ / 80 µF max |
| PWR2-008 | P3 | LED eFuse `PG`/`PGTH` unused. Legitimate (both are datasheet test conditions), but the same argument D-045 makes for the buck PG applies to a board built to be measured. | SLVSFC9C §6.5 |
| PWR2-009 | P3 | V_OUT = 0.8 × (1 + 100 k/32.4 k) = **3.269 V**, −0.94% from 3.3 V. Within every downstream tolerance; E96 pairs bracket 3.3 V at roughly ±1% anyway. Report, do not chase. | SLVSFP4B Eq. 8, V_FB = 0.8 V |
| PWR2-010 | P3 | `S-CONF → VIN` is **valid and correctly matched**: it selects 2.2 MHz / spread-spectrum OFF / discharge OFF, and `L1-PWR2` is 2.2 µH exactly as required. `PSNS → GND` is also correct (abs max ±0.3 V — GND is mandatory). But the sheet never says so, and fixed 2.2 MHz with no spread spectrum beside a 13.56 MHz NFC front end is a deliberate EMC choice that should be recorded, not rediscovered at test. | SLVSFP4B Table 7-1; §8.2.2.2.2 *"When using the 2.2-MHz frequency, only use a 2.2-µH inductor"* |

**Confirmed correct** (worth stating, because two of these were the landed transactions under review):
`C10-PWR2` 100 nF on `BUCK_SS`→GND with `U3-PWR2.8` attached — **correct**; `R75-PWR2` 10 k
`BUCK_PG`→`3V3` — the resistor half is **correct**, only the U3 pin is missing; `U3-PWR2` pin 7
PSNS→GND; pin 3 VO→3V3 correctly after the inductor; `U4-PWR2` `DVDT` with `C68-PWR2` 2.2 nF;
`U4-PWR2` `OVLO→GND` (SLVSFC9C's own test condition is `V_OVLO = 0 V`; OVLO trips on **rising**
voltage, so GND means enabled — this is right, not a tie-off error); `U7-RTC` fully and correctly
wired including the `RT_RESET_REQ_N` manual-reset path to `SW1-RTC`.

---

## 5. The two questions the brief asked directly

### Does `RT_PWR_VALID` actually sense something?

**No. FAIL.** The supervisor's SENSE input floats and no consumer is attached. This is a decorative
PGOOD IC, which is a defect, not a feature. D13.1 is not satisfied. See PWR2-002 — and note the
repair carries a genuine strategic fork (monitor 3V3 with the fitted G33, or monitor `1V15_CORE`
with a part change to the adjustable G01).

### Does the sheet show a power tree, or a set of labels?

**Both answers are true and both matter.**

**Electrically it is a complete, correct tree, and it passes K1E-017.** Measured end to end:

```
J1-PWR1 → U1-PWR1 (USB eFuse) → 5V_PROTECTED → RSH1-PWR1 (Kelvin shunt, U2-PWR1 INA226 on pins 8/9/10)
   → 5V_SYS ─┬→ U3-PWR2 TPS62913 ──────────────→ 3V3
             ├→ U4-PWR2 TPS259474L → 5V_LED_COMMON → FB1/FB2 → +5V_LED_L / +5V_LED_R
             ├→ U5-PWR2 TLV75533 → 3V3_MIC_REG → Q1-PWR2 → 3V3_MIC → FB5-AUD → 3V3_MIC_FLEX
             └→ FB3-PWR2 ─────────────────────→ NFC_5V
1V15_CORE ← L4-RTC ← DCDC_SW  (RT1062 internal DC-DC — real silicon, inside the MCU)
```

Every branch has a real active source. `NFC_5V` is a ferrite filter from 5 V to 5 V, which is a
legitimate use of a passive; it is not a rail conjured out of nothing. No rail in scope is a
passive-only fanout.

**Visually it is not a tree.** Zero of the 675 wires touch any other wire anywhere on the sheet —
every net is stub-and-label, `5V_SYS` as 12 disjoint wires and `3V3` as 90. The contract permits
that for global rails and major buses, so this is a readability finding, not an electrical one. But
`POWER-ARCHITECTURE.md` singles out this exact spine — *"six disconnected `5V_SYS` labels are not a
power tree"* — and asks for it as visible wiring. That specific request is unmet.

**Bounded repair, scoped to the request rather than the whole sheet:** draw the eight trunk hops
above as continuous wiring inside the PWR1/PWR2 block only — entry → eFuse → `5V_PROTECTED` → shunt
→ `5V_SYS` → the four branch heads — and leave the leaf decoupling on labels. Roughly 12–15 wire
additions in one region. Do not attempt to de-label the 90-wire `3V3` net; that is not what the
architecture document asks for and it would make the sheet worse.

---

## 6. Evidence hygiene and authority

**PWR2-013 — the DRC anchor is stale and must not be quoted as clearance.**
`anchors/schDrcLog_2026-08-28.txt` is timestamped 12:17:37–12:17:39; the frozen denominator's
title-block `@Update Time` is **13:05:07**. The log warns about `BUCK_SS` naming wire `e2873`, which
**no longer exists** — `BUCK_SS` is now carried by `e145984` and `e2945`. It contains **zero**
mentions of `BUCK_PG`, `RT_PWR_VALID`, `LED_OE` or `LED_THERM`. Its
`Fatal Error: 0, Error: 0, Warning: 22` line is **not** evidence about PWR2-001 or PWR2-002 — the log
ran before those transactions. It does independently corroborate my floating-pin calls for
`U16-VAL.3/4/5`, `U4-PWR2.3`, `U5-PWR2.4` and `SW4-VAL.3/4`. Re-run and re-anchor after repair.

**PWR2-014 — the TPS62913 register entry cites the wrong TI document.**
Correcting the brief's premise: **SLUSEA4 *is* registered** — `sources/SOURCE-REGISTER.md` line 16
reads *"Texas Instruments | TPS62913 datasheet, SLUSEA4"*. The problem is different and worse: the
document at `ti.com/lit/ds/symlink/tps62913.pdf` self-identifies as **SLVSFP4B**, and **SLUSEA4 is
the TPS62933 datasheet** — a different converter in a different package with a different pinout. The
entry's two substantive claims (PG open-drain needs a pull-up; NR/SS needs a soft-start capacitor)
are both correct and were independently re-derived here from SLVSFP4B Table 5-1, so **D-045 stands
on its merits**. Only the citation is wrong.

**Sources relied on, none currently registered under these numbers:**

| Doc | Part | Registered? |
| --- | --- | --- |
| **SLVSFP4B** | TPS62912 / TPS62913 | no — register carries `SLUSEA4` (wrong part) |
| SBVS050M | TPS3808 | no |
| SBVS320D | TLV755P / TLV75533 | no |
| SLVSFC9C | TPS25947 / TPS259474L | no |
| SCLS378P | SN74AHCT1G125 | no |
| LCSC C185418 | YAGEO RC0402FR-073K48L 3.48 k | no |

---

## 7. Repair order

| # | ID | Sev | Action | Blast radius |
| --- | --- | --- | --- | --- |
| 1 | PWR2-001 | P0 | Redraw `e146347` with corrected y sign and x=1140 | 1 wire |
| 2 | PWR2-002 | P0-H | **Decision first** (which rail), then wire `U16-VAL.5`; extend `e8950` +5 x | 1 decision, 2 wires |
| 3 | PWR2-005 | P1 | Rebind `R8-PWR2` to the C185418 device | 1 BOM row |
| 4 | PWR2-004 | P1 | Add ≥1 µF at `U5-PWR2` OUT | 1 part |
| 5 | PWR2-003 | P1 | Flip `R53`/`R54` to the LED VCC rails; wire OE to GPIOs | 2 nets + GPIO budget |
| 6 | PWR2-007 | P2 | Add NTC bias resistors | 2 parts |
| 7 | PWR2-006 | P2 | Rescale FB divider to R2 ≤ 5 kΩ | 2 values |
| 8 | PWR2-011 | P2 | Confirm effective C_OUT ≥ 40 µF from the bias curve | evidence only |
| 9 | PWR2-013/014 | — | Re-run DRC and re-anchor; correct and extend the source register | docs |

Out of scope and untouched, as instructed: PCB geometry, placement, routing, copper, layer count;
any schematic edit; the current-envelope re-derivation; Option B, the RT1062 package and the
ownership matrix. PWR2-012 is handed to the ESP/debug lane.

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:A2-PWR-SUPERVISOR | Created. Pin-by-pin audit of 42 components / 120 pins against frozen denominator 489736:464c27d4 using a fault-proven geometric connectivity engine. |
