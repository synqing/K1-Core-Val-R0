---
abstract: "VAL-G2 pin audit of the K1-CORE-VAL-R0 LED output block (U14/U15-LED SN74AHCT1G125, J2/J3-LED, C64/C65-LED, R51-R54-LED, RT1/RT2-LED) against the TI SN74AHCT1G125 and TPS2594 datasheets and contracts/led-interface.md. Verdict: all 32 in-scope pins are wired and RT1062 owns both channels as contracted; the level shifter is correctly unidirectional and deterministic; but the boot state is indeterminate (OE# hard-tied enabled, no pull-down anywhere on the data path), both NTC thermal channels have no bias resistor and cannot be read, branch separation is ferrite beads only with no per-branch protection or enable, and the series data resistors are frozen at 33R when they must be TUNE_TBD. Proposals only."
---

# PIN-AUDIT-LED — VAL-G2

**Lane:** A6-MOTION-LED · **Date:** 2026-08-28 · **Status:** PROPOSAL, not a write

Denominator: `frozen-denominator-489736`, source hash `489736:464c27d4`. Machine-readable form:
`pin-audit-motion-led.json`. Method, oracle fault battery and the incomplete-denominator
correction are documented in `PIN-AUDIT-MOTION.md` §1 and are not repeated here.

**Coverage.** 12 in-scope components, 32 in-scope pins, 32 classified, 0 unclassified,
**0 floating**. Every LED-block pin lands on wire geometry.

> **Read this before trusting any earlier LED finding.** The obvious pin-readback file,
> `jobs/all-pins-nc-audit.results.json`, silently omits RT1062 symbol part `e3295` and its
> 98 balls — which is where **both LED data pads live**. An audit run on that file concludes
> the LED data path does not exist. Use `jobs/full-pin-harvest.results.json` (230 of 230
> source parts). This audit's own self-test is what caught it.

---

## 1. Channel ownership — PASS

| Channel | Buffer | Driven by | Net | Series | Connector |
| --- | --- | --- | --- | --- | --- |
| 0 (Left) | U14-LED | **U6-RTC ball D7 (GPIO_B0_00)** | `LED_D0_3V3` | R51-LED | J2-LED.2 |
| 1 (Right) | U15-LED | **U6-RTC ball E7 (GPIO_B0_01)** | `LED_D1_3V3` | R52-LED | J3-LED.2 |

The ESP32-S3 touches **no** LED net. U9-ESP binds five nets in total across the whole board:
`GND`, `I2C_SDA`, `I2C_SCL`, `ESP_UART0_RX`, `ESP_UART0_TX`. Independently corroborated:
the connectivity harness's `net_labels_meeting_fewer_than_two_pins` list contains
`MOTION_INT_S3` but **not** `LED_D0_3V3` or `LED_D1_3V3`.

`contracts/led-interface.md` — *"J2 and J3 therefore belong electrically to RT1062, not to
ESP32_S3"* — is satisfied for both channels. **PASS.**

---

## 2. Level shifting — PASS

Fitted part: **SN74AHCT1G125DBVR**, SOT-23-5, one per channel.

| Property | Requirement | Measured |
| --- | --- | --- |
| Direction | Unidirectional 3V3 → 5V | **Unidirectional A → Y only.** TI: *"single bus buffer gate/line driver with 3-state output… when OE̅ is low, true data is passed from the A input to the Y output."* Not a bidirectional autosensing part. |
| Determinism | Deterministic | Function table: OE̅ L → Y = A; OE̅ H → Y = Hi-Z. No direction sensing, no charge-pump, no pass-FET ambiguity. |
| Threshold | 3.3 V CMOS high must read as high at 5 V VCC | V_IH = 2.0 V min across the whole 4.5–5.5 V VCC range. 3.3 V clears it. |
| Pinout | 1=OE̅, 2=A, 3=GND, 4=Y, 5=VCC | Matches the schematic symbol exactly on both parts. |
| Drive | — | I_OH / I_OL = 8 mA. |

One caveat to carry forward: **VCC recommended range is 4.5–5.5 V.** The buffers are powered
from `+5V_LED_L` / `+5V_LED_R`, which are the strip rails. Rail droop under LED load below
4.5 V puts the shifters out of spec — a placement and copper-sizing concern for VAL-G3, noted
not acted on.

---

## 3. Boot state — **FAIL**

This is the defect the brief asked for, and it is real.

**Measured.** `LED_OE_L` binds exactly two pins: `U14-LED.1 (OE̅)` and `R53-LED.1`. R53-LED is
a 10 kΩ whose other end is on `GND`. `LED_OE_R` is identical through R54-LED. **No controller
reaches either OE̅ pin.**

**Consequence.** OE̅ is hard-tied low. Per the TI function table the buffers are enabled from
the instant `+5V_LED_L/R` is valid, and Y follows A unconditionally. The A inputs come from
RT1062 pads GPIO_B0_00 and GPIO_B0_01. At cold power-on, and throughout RT1062 reset, before
firmware configures those pads, **nothing in this circuit holds the buffer inputs or the 5 V
strip data lines at a defined level.** There is no pull-down on `LED_D0_3V3` / `LED_D1_3V3`,
none on `LED_D0_J` / `LED_D1_J`, and no path for firmware to force the outputs into Hi-Z.

The strip data state between power-on and RT firmware taking control is indeterminate. On a
WS28xx-class strip that presents as random pixel garbage on every power-up at best, and as a
sustained high-current white frame at worst. TI's own recommended-operating-conditions note 3
— *"All unused inputs of the device must be held at V_CC or GND to ensure proper device
operation"* — is the same rule applied to a pad that is not yet driven.

### Bounded repair — two options, one recommendation

**Option A (recommended).** Add a 10 kΩ pull-down from `LED_D0_3V3` to `GND` and from
`LED_D1_3V3` to `GND`. Two 0402 parts. Holds each buffer input low until the RT drives it, so
both outputs sit at a defined 0 V through power-on and reset. Costs no RT1062 pads and no
firmware sequencing.

**Option B.** Flip R53-LED / R54-LED to pull OE̅ **up** to `+5V_LED_L` / `+5V_LED_R`, and route
`LED_OE_L` / `LED_OE_R` to two RT1062 pads. Outputs boot Hi-Z and firmware enables them
explicitly. Costs two RT pads, and it still needs a pull-down at J2/J3 to define the strip data
line while the buffer is in Hi-Z — so it does not remove the need for Option A's resistors, it
adds to them.

**Recommendation: A.** Add B on top only if a firmware-commanded LED blackout is wanted for
thermal or fault response — which, given §5, is a conversation worth having, but a separate one.

---

## 4. Thermal feedback — **FAIL**

**Measured.**

- `LED_THERM_L` binds exactly two pins: `RT1-LED.1` and `U6-RTC ball L12 (GPIO_AD_B1_04)`.
- `LED_THERM_R` binds exactly two pins: `RT2-LED.1` and `U6-RTC ball K12 (GPIO_AD_B1_05)`.
- RT1-LED and RT2-LED are NCP15XH103F03RC 10 kΩ NTCs. Their other terminal is on `GND`.

**Defect.** There is no bias resistor from `3V3` to either `LED_THERM` net, so **no divider
exists**. An NTC with one end on GND and the other on an ADC input has no excitation — the ADC
reads an undriven node, not a temperature. Both thermal-feedback channels are unreadable as
drawn, and the failure is silent: firmware will get a plausible-looking ADC number that means
nothing.

**Bounded repair.** Add one bias resistor per channel from `3V3` to `LED_THERM_L` and to
`LED_THERM_R`. The conventional match to a 10 kΩ-at-25 °C NTC is 10 kΩ, but the value should be
chosen so the NTC sits mid-span across the intended monitoring range — that choice belongs to
the thermal lane (D15), not to this audit. What this audit asserts is only that the resistor
must exist.

---

## 5. Branch protection and enable — **PARTIAL**

**Measured topology.**

```
5V_SYS -> U4-PWR2 (TPS259474L eFuse, ONE device)
       -> 5V_LED_COMMON (+ C11-PWR2 22uF)
          |-- FB1-PWR2 (BLM21PG221SN1D, 220R @ 100MHz) --> +5V_LED_L  (C12 22uF, C64 100nF, U14 VCC, J2.1)
          \-- FB2-PWR2 (BLM21PG221SN1D, 220R @ 100MHz) --> +5V_LED_R  (C13 22uF, C65 100nF, U15 VCC, J3.1)
```

| Requirement | Verdict |
| --- | --- |
| Branch protection | **NO per-branch protection.** The only element between the common node and each branch is a ferrite bead. A ferrite is an EMI element, not a protection device. A short on one strip pulls the shared eFuse down and takes **both** channels out. |
| Branch enable | **NO per-branch enable.** A ferrite is not a switch. Neither channel can be independently powered down for thermal response, fault isolation, or bring-up. |
| Fault visibility | **NONE.** U4-PWR2 pins 3 (PG/AUXOFF) and 4 (PGTH/FLT̅) carry No-Connect flags, and pin 10 (ITIMER) is also No-Connect. |

The three No-Connects are *legitimate* — the TI datasheet explicitly characterises the device
with `AUXOFF = Open`, `FLT = Open`, `PGTH = Open`, `PG = Open`, and an open ITIMER simply gives
minimum overcurrent blanking. So they are correctly classed `INTENTIONAL_NC`, not defects. But
the consequence is a product-level risk that should be a deliberate decision rather than a
side effect:

> **The fitted part is the `L` suffix — latched off.** EN/UVLO is hard-tied to `5V_SYS`, and
> FLT̅ is not connected. A latched LED overcurrent trip therefore cannot be cleared by firmware,
> requires a full input power cycle, and gives firmware no signal whatsoever to explain why the
> strips went dark. With ITIMER open the blanking interval is at its minimum, so an inrush
> transient from hot-plugging a strip is the most likely way to reach that state.

**Current limit: ~0.96 A, determined.** `LED_EFUSE_ILIM` binds `U4-PWR2.9 (ILM)` and
`R8-PWR2.1`. Per TI, `I_ILM = 3334 / R_ILM(Ω)`. R8-PWR2's orderable identity is
`Supplier Part = C185418`, `Manufacturer Part = RC0402FR-073K48L` — a genuine **3.48 kΩ**,
matching its drawn value and giving **0.96 A**, comfortably inside the TI recommended R_ILM
range of 549 Ω to 6.65 kΩ.

> **Correction, 2026-08-28.** An earlier revision of this document called this current limit
> UNDETERMINED, on the grounds that R8-PWR2's `supplierId` field reads `RC0402FR-0710KL.1`
> (a 10 kΩ). That was wrong. `supplierId` on this sheet is a stale library-inherited string on
> several parts; the field that carries the orderable identity is `Supplier Part`, and for
> R8-PWR2 it is a real LCSC code for the correct 3.48 kΩ. The distinguishing test for the seven
> fake-DNP resistors is precisely this: parts with a genuine value carry a real LCSC `Cxxxxxxx`
> code in `Supplier Part`, while the fake DNPs carry the inherited `RC0402FR-0710KL.1` 10 kΩ
> string in **both** fields. Verified by re-reading `bom_flat.csv` field by field.

Soft-start is fine: C68-PWR2 = 2.2 nF gives SR = 2000/2200 ≈ 0.91 V/ms, so the rail ramps in
about 5.5 ms.

**Bounded repair — stated, but this is a rails decision, not this lane's to take.** If
per-branch protection and enable are genuinely required by the contract's intent, the minimum
honest change is one protection/switch element per branch in place of (or in series with) the
ferrites, plus routing FLT̅ to an RT1062 input so firmware can see a trip. **A2-RAILS owns the
device choice.** This lane's finding is only that ferrite beads do not satisfy "branch
protection" or "branch enable".

---

## 6. Series data resistors — **TUNE_TBD**

R51-LED and R52-LED are `RC0402FR-0733RL` — 33 Ω — in series between each buffer output and its
connector data pin.

The **footprint is justified**: it damps the fast AHCT edge into an unterminated strip lead,
which is exactly what it is for. The **value is not**. Series termination is transmission-line
dependent — it is a function of the driver output impedance and the routed trace and lead
geometry, none of which exists yet. 33 Ω is a donor-circuit number.

**Action:** mark R51-LED and R52-LED `TUNE_TBD` in the BOM and in the schematic value field.
Set the value at VAL-G3 from the routed geometry. Do not freeze it at this gate. Recorded as
**VAL-G3-LED-01**.

---

## 7. The branch-bypass candidate

The Voice PE-inspired LED branch-bypass idea remains a **CANDIDATE only**. It is not fitted, it
is not a schematic requirement, and nothing in this audit adds it or assumes it.

---

## 8. Verdict

| Requirement | Verdict |
| --- | --- |
| Two channels, both owned by RT1062; S3 never owns the LED pipeline | **PASS** — D7/E7 drive both; U9-ESP touches no LED net |
| Deterministic unidirectional 3V3 → 5V level shifting | **PASS** — SN74AHCT1G125, unidirectional 3-state buffer, not autosensing |
| All in-scope pins accounted for | **PASS** — 32/32 classified, 0 floating, 0 unknowns |
| Safe boot state | **FAIL** — OE̅ hard-enabled, no pull-down anywhere on the data path, strip state indeterminate until firmware runs |
| Branch protection | **FAIL** — one shared eFuse, ferrite beads only between branches |
| Branch enable | **FAIL** — no switch on either branch |
| Thermal feedback | **FAIL** — no bias resistor on either NTC; both channels unreadable |
| Series data resistors not frozen | **FAIL as drawn** — 33 Ω frozen; must be TUNE_TBD |
| eFuse fault reporting | Legitimate INTENTIONAL_NC, but latched part + no FLT̅ + no firmware-clearable EN is a product-level risk for A2-RAILS |

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:A6-MOTION-LED | Created. VAL-G2 LED pin audit against frozen denominator 489736:464c27d4, TI SN74AHCT1G125 and TI TPS2594 datasheets. |
| 2026-08-28 | agent:A6-MOTION-LED | Section 5 corrected: LED-branch eFuse current limit is a determined 0.96 A, not UNDETERMINED. R8-PWR2 orders as a genuine 3.48k (C185418 / RC0402FR-073K48L); the earlier claim misread the stale supplierId field. R53-LED value/binding confirmed consistent. |
