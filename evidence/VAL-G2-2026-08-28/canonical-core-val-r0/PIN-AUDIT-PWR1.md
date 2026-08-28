---
abstract: "Pin-level disposition audit of the power-entry and protection chain on the frozen canonical sheet (hash 489736:464c27d4): J1-PWR1, J7-ESP, D1-PWR1, F1-PWR1, U1-PWR1 eFuse, U2-PWR1 INA226, RSH1-PWR1, U10-ESP, U4-PWR2 LED eFuse and the three BLM21PG221SN1D ferrites. 94 pins adjudicated, 31 defective. Headline defects: D1-PWR1 is a USBLC6-2SC6 data-line ESD array misapplied as a rail TVS with its VBUS clamp pin floating, so it clamps nothing; F1-PWR1 is a 2 A ferrite carrying a 2.08 A trunk; the eFuse OVLO trips at 5.46 V, inside the USB VBUS tolerance band; and the INA226 address pins carry No-Connect flags that bless a state the TI datasheet forbids. Also re-derives the BOM-audit BLOCKER independently: both eFuse ILIM resistors are bound to a shared 10 kohm device, which would limit each eFuse to 0.300 A guaranteed and leave the board unable to power up; every other programming resistor and divider in the family, including the buck feedback pair, verifies clean."
---

# Pin audit — power entry and protection

**Status: PROPOSAL, not an instruction.** Measured against a frozen snapshot. The single writer
owns the live canvas and must reconfirm every item against live before acting. Live has already
moved past this hash.

Machine-readable companion: `pin-audit-pwr1.json`.
USB topology, D-044 conformance and the J1/J7 connector verdicts: `USB-TOPOLOGY-AUDIT.md`.
Current envelope arithmetic: `power-envelope-rederivation.md`.

## What was measured, and how

| | |
| --- | --- |
| Frozen source | `frozen-denominator-489736/source.txt`, hash `489736:464c27d4` |
| Wires parsed | 675 |
| Pins parsed | **782** across 228 designated components |
| Named nets | 143 |
| Pins adjudicated in this document | **94** |
| Pins defective | **31** |

Connectivity comes from a union-find over the sheet's own wire geometry — segment vertices,
T-junctions where a vertex lands on another segment's interior, crossings deliberately excluded —
with pins unioned at their read-back coordinates, then a second pass merging clusters that share a
`NET` label. Net names were never used to decide whether a pin is attached. The oracle carries a
7-case fault battery with two cases that must go red; both do. See `USB-TOPOLOGY-AUDIT.md` for the
method note and for the reconciliation against Captain's DRC log.

**Disposition convention.** `disposition` in the JSON is the **audit verdict** — the state the pin
must end in, with a vendor citation. `as_captured` is what the frozen sheet actually shows. Where
they differ the pin is marked `defect: true`. `INTENTIONAL_NC` is satisfied only when a
No-Connect flag is actually present; a bare float is not a documented open.

| Disposition | Count |
| --- | --- |
| POWER | 29 |
| CONNECTED | 32 |
| GND | 15 |
| INTENTIONAL_NC | 12 |
| RESERVED_WITH_DOCUMENTED_REASON | 5 |
| TUNE_TBD | 1 |

| Component | Defects / pins |
| --- | --- |
| J1-PWR1 | **15 / 17** |
| U6-RTC USB balls | **7 / 8** |
| D1-PWR1 | **4 / 6** |
| U2-PWR1 | **2 / 10** |
| J7-ESP | 2 / 17 |
| U1-PWR1 | 1 / 10 |
| F1-PWR1, RSH1-PWR1, U10-ESP, U4-PWR2, FB1/2/3-PWR2 | 0 |

J1-PWR1 and the RT1062 USB balls are covered in `USB-TOPOLOGY-AUDIT.md`. This document covers the
protection chain.

---

## D1-PWR1 — a data-line ESD array wired as a rail TVS, clamping nothing

`USBLC6-2SC6` (ST Doc ID 11265 Rev 5, October 2011). Six pins; **four float**.

| Pin | ST signal | As captured |
| --- | --- | --- |
| 1 | I/O1 | `5V_PROTECTED` |
| 2 | GND | `GND` |
| 3 | I/O2 | float |
| 4 | I/O2 | float |
| 5 | **VBUS** | **float** |
| 6 | I/O1 | float |

Three separate faults, in order of severity.

**1. It clamps nothing.** Pin 5 is the VBUS clamp node — the internal zener sits between pin 5 and
GND, and each I/O line reaches it through a steering diode. With pin 5 open, the only path from
I/O1 to GND is the reverse-biased lower steering diode. **The device as wired provides no clamp at
all.** This is the failure mode where a part is present, populated, costed, and electrically inert.

**2. It is the wrong class of part for a rail.** ST's datasheet specifies pulse ratings only —
1 A peak pulse gives VCL 12 V max, 5 A gives 17 V max, both 8/20 µs — and gives **no continuous
current rating anywhere**. §2.1–2.3 treat all three terminals as short-track shunt connections for
ESD clamping. It is a 2.5 pF-typ low-capacitance array built for D+/D-, not a bulk VBUS TVS.

**3. It is on the wrong side of the eFuse.** `5V_PROTECTED` is *downstream* of U1-PWR1. The part
that needs protecting from an inlet transient is the eFuse itself — TPS259474L absolute maximum
28 V, and it is the first silicon the transient reaches. Protection placed behind it protects
nothing that was at risk.

### Correct topology

Split the two jobs that have been conflated:

- **Input transient protection** belongs on `5V_USB`, upstream of F1-PWR1 and U1-PWR1: a
  unidirectional VBUS TVS with working voltage above 5.5 V and clamping voltage comfortably below
  the eFuse's 28 V absolute maximum, sized for the inlet surge, not for ESD.
- **D+/D- ESD** is exactly what this USBLC6-2SC6 is for. Redeploy it onto J1's data pair, pins 1/6
  as the D+ pass-through, pins 3/4 as the D- pass-through, **pin 5 to the VBUS being protected**,
  pin 2 to GND — the same arrangement U10-ESP already uses correctly on J7. The JSON therefore
  records D1 pins 1/6 and 3/4 as `RESERVED_WITH_DOCUMENTED_REASON` rather than as errors: the part
  is right, the application is wrong.

---

## F1-PWR1 — undersized, and in the wrong place

`BLM21PG221SN1D` (Murata JENF243A_0005AE-01), in series between `J1.B4` and the eFuse input, so it
carries **the entire board trunk**.

| Parameter | Value | Against a 2.08 A coincident peak |
| --- | --- | --- |
| Rated current @ 85 °C | 2000 mA | **exceeded by 4 %** |
| Rated current @ 125 °C | 1250 mA | **exceeded by 66 %** |
| DC resistance, max | 0.045 Ω | 94 mV drop, 195 mW dissipated in an 0805 |
| Impedance @ 100 MHz | 220 Ω ±25 % | nominal only; collapses under DC bias at amps |

At the 2.40 A design point with validation margin the numbers become 108 mV and 259 mW, and the
bead is 20 % over its 85 °C rating. Murata publishes a derating curve rather than a table, and does
not publish a separate saturation current — but the two rated points it does publish are already
enough to fail this application.

Two independent problems, and they want different fixes:

1. **Rating.** If a series element stays in the trunk it must be rated ≥ 3 A with DCR ≤ 20 mΩ.
2. **Position.** A ferrite in series with the whole rail, upstream of the eFuse and followed by
   C1-PWR1 22 µF, forms an LC tank across the hot-plug event. The resulting overshoot lands on the
   eFuse input — whose OVLO is set to 5.46 V (below). Input EMI filtering generally does not belong
   in series with the full trunk ahead of the protection device.

The same part is used at FB1/FB2 (LED branches, ≤ 1.05 A) and FB3 (NFC 5 V, ≤ 0.5 A peak). **Those
three are correctly sized.** Only F1 is out of its envelope, because only F1 sees the whole trunk.

---

## U1-PWR1 — TPS259474L trunk eFuse

`TPS259474LRPWR`, TI SLVSFC9C (Oct 2020, rev. May 2026). All 10 pins adjudicated; the programming
is coherent, and two of the four programmed thresholds are wrong.

| Pin | Function | Set by | Re-derived value |
| --- | --- | --- | --- |
| 9 | ILM | R1 = 1.33 kΩ | `R_ILM = 3334 / I_LIM` -> **2.507 A typ**, 2.26–2.76 A over ±10 % |
| 1 | EN/UVLO | R63 1.05 M / R2 100 k / R64 324 k | V_IN(UV) = 1.20 × 1474/424 = **4.17 V** |
| 2 | OVLO | same stack | V_IN(OV) = 1.20 × 1474/324 = **5.46 V** |
| 4 | PGTH | R65 274 k / R66 100 k | V_OUT(PG) = 1.20 × 374/100 = **4.49 V** |
| 7 | DVDT | C67 = 2.2 nF | `C = 2000/SR` -> SR = **0.909 V/ms**, 0→5 V in 5.5 ms |
| 3 | PG/AUXOFF | R67 10 k to 3V3 | open-drain, correct pull-up |
| 10 | ITIMER | open | vendor-recommended, see below |

### Defect: OVLO at 5.46 V sits inside the USB VBUS tolerance band

USB VBUS is specified to **5.50 V** at the top of tolerance. The eFuse is programmed to latch off
at **5.46 V**. A compliant source at the high end of its range trips the board off before any fault
exists — and with F1's LC tank ahead of it, hot-plug ringing will reach that threshold on a source
that is nowhere near 5.5 V steady-state. Raise OVLO to a value with real headroom above 5.5 V
(6.0–6.5 V is the usual choice, still far below the 23 V operating and 28 V absolute maximum).

### Defect: ILIM minimum is below the trunk requirement

The re-derived coincident peak is 2.08 A and the design point with validation margin is 2.40 A.
The eFuse's **guaranteed minimum** trip is 2.26 A. So:

- against the un-margined peak, separation is 8.6 % — inside the part's own ±10 % band;
- against the 2.40 A design point, the minimum trip is **below the load**, i.e. guaranteed nuisance
  trip on a worst-case part.

Either the trunk is capped below ~2.0 A (which means capping the LED branch, since that is where
the current is), or R1 comes down. R1 = 1.10 kΩ gives 3.03 A typ / 2.73 A minimum, which clears
2.40 A — but then the **connector**, not the eFuse, becomes the binding limit, and J1's VBUS
contacts must all be bonded (see `USB-TOPOLOGY-AUDIT.md` §1). These two decisions are coupled and
should be taken together.

### Correct, but worth recording

- **ITIMER (pin 10) open is the vendor-recommended state**, not an omission. TI SLVSFC9C Table 5-1:
  *"Leave this pin open for fastest response to overcurrent events."* Repeated in §7.3.5.2. It is
  adjudicated `INTENTIONAL_NC` — but the sheet carries no No-Connect flag, so the intent is not
  recorded. Add the flag. Contrast U4-PWR2, where the equivalent pin *does* carry one.
- **PG is unmonitored.** `USB_EFUSE_PG` reaches R67 and nothing else. Nothing on the board can tell
  whether the trunk eFuse has faulted. The same is true of the LED eFuse, whose PG is NC-flagged
  outright, and of the buck: `U3-PWR2.5 (PG)` floats while its intended pull-up R75-PWR2 sits on a
  one-pin net whose wire is at **negative y** — drawn off-sheet. For a board whose stated mission is
  to maximise observability, three unobservable power-good signals is a coherent gap rather than
  three separate slips.

---

## U2-PWR1 — INA226 current and voltage monitor

`INA226AIDGSR`, TI SBOS547C. Shunt is `RSH1-PWR1`, 10 mΩ WSHP2818R0100FEA.

Sense topology is right: IN+ (pin 10) on `5V_PROTECTED`, IN− (pin 9) on `5V_SYS`, and RSH1 bridges
exactly those two nets, so the part measures across the shunt. VBUS (pin 8) on `5V_SYS` for bus
voltage; VS+ (pin 6) on 3V3 decoupled by C3-PWR1 100 nF, which meets the datasheet's §8.3 request
for 0.1 µF. At the 2.08 A peak the shunt develops 20.8 mV and dissipates 43 mW against an INA226
full scale of 81.92 mV — comfortable, with 2.5 µV LSB giving 250 µA resolution.

### Defect: the No-Connect flags on A0/A1 bless a state TI forbids

`U2-PWR1.1 (A1)` and `U2-PWR1.2 (A0)` are floating **and carry No-Connect flags** — two of the
twelve NC marks on the sheet. TI SBOS547C Table 4-1, for both pins verbatim:

> Address pin. **Connect to GND, SCL, SDA, or VS.** Table 6-2 shows pin settings and corresponding
> addresses.

Four permitted connections are enumerated. Floating is not among them, and §6.5.5.1 adds that the
device samples A0/A1 on every bus transaction and requires the states to be established before any
interface activity. **The I²C address is undefined.** The board will not reliably enumerate its own
current monitor.

This is worth naming as a class, not just an instance: a No-Connect flag is an assertion that the
open state is *correct*. Here it has been used to silence a DRC warning about a pin that the vendor
requires to be driven — the annotation now certifies the defect. Tie A1 and A0 to GND (address
1000000) or to whichever pair Table 6-2 gives a free address, and remove the flags.

### Gap: no input filter

TI SBOS547C §6.4.2 asks for series resistance of **10 Ω or less** on IN+ and IN− with a **0.1 µF to
1 µF** capacitor across the shunt (Figure 6-3). Neither is present. This is a schematic-level
omission, not a layout one, and matters more here than usual because the shunt sits in a rail that
sees eFuse hot-swap slew and LED switching.

### Kelvin: not yet true, and mostly a VAL-G3 obligation

The brief asks about Kelvin sensing. At schematic level IN+/IN− join `5V_PROTECTED` and `5V_SYS`,
which are the same nets that carry C2-PWR1, D1-PWR1, R65-PWR1 and U1-PWR1.6 on one side and
C5-PWR2, C14-PWR2, FB3-PWR2, R7-PWR2, U3/U4/U5-PWR2 on the other. So the measurement currently
includes whatever copper drop layout puts between those nodes. TI SBOS547C §8.4.1 is explicit:

> Connect the input pins (IN+ and IN−) to the sensing resistor using a Kelvin connection or a
> 4-wire connection.

Enforcing that is a VAL-G3 layout constraint and is out of scope here. What *is* in scope: the
schematic can carry the intent by breaking out dedicated `RSH1_KELVIN_P` / `RSH1_KELVIN_N` nets
from the shunt pads to the INA226 inputs (through the 10 Ω filter resistors above), so that layout
inherits a constraint rather than a hope. Recommended, not required.

---

## Device-binding defect on the two eFuse ILIM resistors

Raised by the BOM audit as a `BLOCKER` (`bom-audit.json`) and **re-derived here independently
from the frozen source**, because it lands on the two most safety-relevant passives in the power
tree and I am the one holding the eFuse context.

### What the frozen source actually says

EasyEDA device UUID `e1b1f220e40a4edea589adfa05a5d8c7` is bound to **24 components**:

| Drawn value | Count |
| --- | --- |
| `10k` | 15 |
| `DNP` | 7 |
| **`1.33k`** | **1 — R1-PWR1** |
| **`3.48k`** | **1 — R8-PWR2** |

Nineteen of the 24 carry supplier part `RC0402FR-0710KL.1` — a 10 kΩ 0402. So the shared device
is a 10 kΩ device, and the two eFuse current-limit resistors are minority values riding on it.

`R1-PWR1.1 -> USB_EFUSE_ILIM` and `R8-PWR2.1 -> LED_EFUSE_ILIM`, both with pin 2 on GND. These
two resistors *are* the overcurrent protection thresholds for the whole board.

### The record contradicts itself, which is why nothing catches it

The instance-level supplier codes are **correct**, verified against the LCSC catalogue:

| Part | Instance supplier code | Actual part | Matches drawn value? |
| --- | --- | --- | --- |
| R1-PWR1 | `C276261` | YAGEO RC0402FR-071K33L, **1.33 kΩ** ±1 % 0402 | yes |
| R8-PWR2 | `C185418` | YAGEO RC0402FR-073K48L, **3.48 kΩ** ±1 % 0402 | yes |

So the schematic displays the right value, the instance supplier code names the right part, and
the device binding says 10 kΩ. Which value reaches the assembler depends entirely on which field
the BOM exporter reads — and that is not a property anyone should be relying on. ERC and DRC
cannot see it, because both check connectivity, and this is a data defect in a field neither
inspects. It is the same class as the No-Connect flags on the INA226 address pins: the artefact's
own annotation certifies something the underlying record contradicts.

### What 10 kΩ would actually do

Both fail **low**, not high — TI SLVSFC9C Eq. 5 is `R_ILM = 3334 / I_LIM`, so a larger resistor
means a *smaller* limit:

    R_ILM = 10 kohm  ->  I_LIM = 3334 / 10000 = 0.333 A typ,  0.300 - 0.367 A over +/-10 %

| eFuse | Programmed limit at 10 kΩ | Required | Outcome |
| --- | --- | --- | --- |
| U1-PWR1 trunk | 0.300 A guaranteed | 2.08 A peak, 1.15 A sustained | **Board cannot power up.** The 3V3 branch alone draws 0.480 A at peak — 1.6x the limit — so the eFuse trips during the buck's own start-up |
| U4-PWR2 LED | 0.300 A guaranteed | up to 1.05 A | LED branch trips on the first bright frame |

This is fail-safe in the electrical sense — nothing is over-stressed — but it is a total build
failure, and one that would present at bring-up as "the board is dead" with no obvious cause.

### The rest of the family verifies clean

The same check was run against **every** programming resistor, divider and timing component in the
power-entry blocks — comparing each part's drawn value against the value census of the device it
is bound to:

| Part | Drawn | Binding verdict |
| --- | --- | --- |
| R63-PWR1 1.05 M, R64-PWR1 324 k, R65-PWR1 274 k, R6-PWR2 32.4 k, L1-PWR2 2.2 µH, RSH1-PWR1 10 mΩ | — | **Clean** — each on a device unique to that part |
| R2-PWR1, R5-PWR2, R7-PWR2, R66-PWR1, R71-ESP, R72-ESP | 100 k | **Clean** — shared device, all 8 members are 100 k |
| R21-ESP, R22-ESP | 5.1 k | **Clean** — shared device, both members 5.1 k |
| R73-ESP, R74-ESP | 22 R | **Clean** — shared device, all 15 members 22 R |
| R3-PWR1, R67-PWR1, R75-PWR2 | 10 k | **Clean** — legitimately on the 10 kΩ device |
| R56-VAL | `DNP` | **Clean** — a 10 kΩ part deliberately not populated; flagged by the check, cleared on inspection |

**The buck feedback divider is clean.** The team lead flagged `R5-PWR2` / `R6-PWR2` as a possible
instance of the same defect because a wrong divider would bring 3V3 up at the wrong voltage. It is
not: R5 sits on the all-100 k device with seven siblings, and R6 (32.4 k) has a device of its own.
That is a positive verification, not an inference from absence. The 3V3 rail's *value* remains
A2-RAILS' question; its BOM binding is sound.

**So the defect is exactly two parts**, both of them eFuse ILIM resistors, and the fix is bounded.

### The repair, and why the value comes from the envelope

The repair is **not** "correct the device binding to match the drawing." The drawn values were
chosen against the inherited 2.35 A / 0.95 A figures, which this audit was asked to re-derive
rather than inherit. So the sequence is:

1. Derive the required current limit for each eFuse from the re-derived envelope.
2. Convert to a resistance via TI SLVSFC9C Eq. 5, `R_ILM(Ω) = 3334 / I_LIM(A)`.
3. Make the device binding, MPN, supplier code **and** displayed value all agree on that value.

Step 1 and 2 are done in `power-envelope-rederivation.md` §7. The results:

| eFuse | Present | Required | Verdict |
| --- | --- | --- | --- |
| **U1-PWR1** trunk | 1.33 kΩ -> 2.507 A typ, **2.26 A min** | **1.24 kΩ** -> 2.689 A typ, 2.42 A min, 2.96 A max | **Change.** 1.33 kΩ trips below the 2.40 A design point |
| **U4-PWR2** LED | 3.48 kΩ -> 0.958 A typ, 1.054 A max | **3.48 kΩ — keep** | **Keep the value, fix the binding only.** 1.054 A max sits safely under the repaired trunk's 2.42 A guaranteed trip |

R8's value is correct and should not be disturbed; only its device binding is wrong. R1 needs
both a new value and a corrected binding.

---

## Protection chain — verified correct

The chain from F1 to 5V_SYS is topologically sound and every pin is accounted for:

    J1.B4 --5V_USB--> F1-PWR1 --5V_USB_FILTERED--> U1-PWR1 (eFuse) --5V_PROTECTED--> RSH1-PWR1 --> 5V_SYS
                                    |                    |                    |
                                 C1 22uF          C2 22uF, D1, R65      U2-PWR1 INA226 (VIN+ / VIN-)

Downstream of `5V_SYS`, all four branches are correctly formed:

| Branch | Path | Ceiling |
| --- | --- | --- |
| 3V3 | U3-PWR2 TPS62913, L1 2.2 µH, R5/R6 feedback | 3 A device |
| LED | U4-PWR2 TPS259474L -> `5V_LED_COMMON` -> FB1/FB2 -> `+5V_LED_L` / `+5V_LED_R` -> J2/J3 | **0.958 A**, set by R8 = 3.48 kΩ |
| NFC | FB3-PWR2 -> `NFC_5V` -> U12-NFC.10 (VDD_TX) | 0.5 A peak |
| Mic | U5-PWR2 TLV75533 -> `3V3_MIC_REG` -> Q1-PWR2 DMG2305UX -> `3V3_MIC` | 500 mA device |

Two observations on this chain that belong to other lanes but were found here:

- **U4-PWR2 EN/UVLO is tied hard to `5V_SYS`.** The LED eFuse has no undervoltage programming and
  cannot be commanded off. On a board whose LED branch is its largest and least predictable load,
  and whose source may only advertise 500 mA, the inability to shed that load in firmware is a
  design limitation worth a decision rather than an accident. See
  `power-envelope-rederivation.md`.
- **ST25R3916B supply-domain conflict.** `U12-NFC.8 (VDD)` is on **3V3** while `U12-NFC.10
  (VDD_TX)` is on **NFC_5V**. ST DS13541 Rev 5 requires **VDD and VDD_TX to track within ±0.2 V**.
  A 1.7 V split violates that. VDD_IO is genuinely independent and may stay at 3.3 V. This is
  outside my brief and is handed to whoever owns the NFC block — flagged because it was found while
  deriving the FB3 branch budget, and because it invalidates part of the NFC 5 V current
  assumption.

---

## Defect register

| # | Pin(s) | Defect | Severity | Repair |
| --- | --- | --- | --- | --- |
| 1 | D1-PWR1.5 | VBUS clamp node floats — the TVS clamps nothing | **P0** | Redeploy D1 to J1 D+/D-, pin 5 to protected VBUS |
| 2 | D1-PWR1.3/4/6 | Unused halves of a misapplied part | **P0** | As above |
| 3 | — | No input transient protection anywhere on `5V_USB` | **P0** | Add a rail TVS upstream of F1, clamping below 28 V |
| 4 | F1-PWR1.1/2 | 2.0 A bead carrying a 2.08–2.40 A trunk | **P0** | Re-rate ≥ 3 A / ≤ 20 mΩ, or remove from the trunk |
| 5 | U1-PWR1.2 | OVLO 5.46 V, inside the 4.75–5.50 V VBUS band | **P0** | Re-derive the divider for ≥ 6.0 V |
| 5b | R1-PWR1, R8-PWR2 | Both eFuse ILIM resistors bound to a shared **10 kΩ** device; a BOM emitting 10 kΩ limits both eFuses to 0.300 A guaranteed and the board cannot power up | **P0** | Bind each to its own device; make binding, MPN, supplier code and drawn value agree |
| 6 | U1-PWR1.9 | ILIM minimum 2.26 A below the 2.40 A design point | **P1** | R1 1.33 k -> **1.24 k (E96)**, coupled to the J1 VBUS bonding fix |
| 7 | U2-PWR1.1/2 | NC flags certify a state TI forbids; I²C address undefined | **P1** | Tie A1/A0 per SBOS547C Table 6-2, remove flags |
| 8 | U2-PWR1.9/10 | No 10 Ω / 0.1 µF input filter per SBOS547C §6.4.2 | **P2** | Add filter; break out Kelvin nets while doing so |
| 9 | U1-PWR1.3, U4-PWR2.3, U3-PWR2.5 | Three unobservable power-good signals | **P2** | Route at least the trunk PG to an RT1062 GPIO |
| 10 | U1-PWR1.10 | ITIMER open is correct but unflagged | **P3** | Add No-Connect flag |
| 11 | R75-PWR2 | Buck PG pull-up stub drawn at negative y, off-sheet | **P2** | Redraw onto U3-PWR2.5 |
| 12 | U12-NFC.8/10 | VDD 3V3 vs VDD_TX 5 V breaks ST's ±0.2 V tracking rule | **P1, other lane** | Hand to the NFC owner |

---

**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:usb-power-audit | Created. 94 pins adjudicated across the power-entry and protection chain against frozen hash 489736:464c27d4; 31 defects; every disposition carries a vendor citation. |
| 2026-08-28 | agent:usb-power-audit | Added the device-binding section after the BOM audit raised a BLOCKER on R1-PWR1 and R8-PWR2. Re-derived the binding from the frozen source, quantified the 10 kohm failure mode, cleared the remaining 14 programming components including the buck feedback divider, and pointed the repair value at the envelope rather than at the drawing. |
