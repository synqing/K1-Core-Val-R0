<!-- british-english-guard: ignore — "analog" retained only inside the verbatim NXP IMXRT1060CEC Table 5 title -->
---
abstract: "D-044 conformance verdict for the two USB-C receptacles on the frozen canonical sheet (hash 489736:464c27d4), measured at pin level by geometric union-find over the sheet's own wire geometry. Verdict: J1-PWR1 FAILS D-044 on every clause (no Rd, no D+/D-, 3 of 4 VBUS and 3 of 4 GND contacts unwired); J7-ESP PASSES the VBUS-sense-only clause with back-feed proven absent, but its data pair lands 5 units short of the ESP32-S3 module, which has zero connected pins. Captain's read of R56-VAL is half-refuted: the RT-side endpoint is ball M8 USB_OTG1_DN, a dedicated analogue USB PHY pin, not an option GPIO. Contains the bounded repair specification for the missing RT1062 USB data path."
---

# USB topology audit — D-044 conformance

**Status: PROPOSAL, not an instruction.** Findings are measured against a frozen snapshot.
The single writer owns the live canvas and must reconfirm every item against live before acting.
Live has already moved past this hash.

## Denominator and method

| | |
| --- | --- |
| Frozen source | `frozen-denominator-489736/source.txt`, hash `489736:464c27d4` |
| Document UUID | `1435cb46f39e48c8a8aadbb84ca81603` |
| Project UUID | `64325d0e55e0435abd018defb0089a9b` |
| Wires parsed | 675 |
| Pins parsed | 782 across 228 designated components |
| Named nets | 143 |
| No-Connect marks | 12 |

Connectivity was derived from the sheet's **own wire geometry**, never from the net name written
on a wire. A union-find joins every wire-segment vertex, joins a vertex that lies on the interior
of another segment (T-junction), and deliberately does **not** join two segments that merely cross.
Pin primitives are unioned at their read-back coordinates. A second layer then merges geometric
clusters carrying the same `NET` label, because EasyEDA net labels do join by name — so a labelled
stub is legitimate connectivity, and the oracle would be wrong to call it a defect.

The oracle carries a 7-case fault battery, including two cases that **must go red**: a pure
crossing must not join, and a T-junction must join. Both behave correctly. Results are recorded in
`pin-audit-pwr1.json` under `self_test`.

### Reconciling against the DRC log

`/Users/spectrasynq/Downloads/schDrcLog_2026-08-28.txt` (12:17:37) is an independent instrument.
It agrees exactly with this oracle on the in-scope parts: **J1-PWR1 15 floating pins** (identical
list), **D1-PWR1 4**, **J7-ESP 2**, **U1-PWR1 1**.

It disagrees on `U9-ESP` (DRC 19 floating, this audit 41) and `U6-RTC` (DRC 111, this audit 38).
That disagreement is resolved, not averaged:

- Job read-backs contain **two distinct U9-ESP placements**. The earlier one puts pin 1 at
  `(4040, 4390)`; the later at `(4175, 4425)` — a shift of `(+135, +35)`.
- The frozen source's own `COMPONENT` record for `e8065` is at `(4255, 4360)`, which is the
  **later** placement.
- The pin read-back used here is the later placement, and lands exactly on wire endpoints for
  **227 of 228 components**. `U9-ESP` is the single exception, with **0 of 41** pins landing.

So the DRC log predates the move and describes an older sheet. The frozen sheet is the denominator.
This is also why U6-RTC improved from 111 floating to 38: wiring continued after the DRC ran.

---

## Verdict summary

| D-044 clause | Verdict |
| --- | --- |
| J1 VBUS -> protection -> 5V_PROTECTED -> RSH1/INA226 -> 5V_SYS | **PARTIAL** — the chain downstream of F1 is correct and complete; the connector end is not |
| J1 consumes VBUS | **FAIL** — 1 of 4 VBUS contacts wired, 1 of 4 GND contacts wired |
| J1 CC1/CC2 correct Type-C sink (Rd) | **FAIL** — both float. No Rd anywhere on J1 |
| J1 D+/D- -> low-C ESD -> series TUNE -> RT1062 USB_OTG1 | **FAIL** — absent entirely. All four data contacts float |
| J1 VBUS detect/sense per NXP USB OTG1 reference | **FAIL** — `USB_OTG1_VBUS` (ball N6) floats |
| J7 D+/D- -> ESP32-S3 native USB | **FAIL** — chain is correct up to `USB_DP_S3`/`USB_DM_S3`, then stops 5 units short of the module |
| J7 VBUS SENSE ONLY, never back-powers the board | **PASS** — proven absent, see below |
| K1BR control plane only | Not in scope of this document |

**Net verdict: the board as captured has no working power inlet and no USB data path to either
processor.** J7 cannot power the board by design (correctly), and J1 cannot power it by defect.

---

## 1. J1-PWR1 as a Type-C sink — FAIL

`USB4105-GF-A` (GCT, USB 2.0 16-contact receptacle). 17 symbol pins. **15 float.**

| Contact | Signal | As captured | Required |
| --- | --- | --- | --- |
| B4 | VBUS | `5V_USB` -> F1-PWR1.1 | keep |
| B1 | GND | `GND` | keep |
| A4, A9, B9 | VBUS | **float** | all to `5V_USB` |
| A1, A12, B12 | GND | **float** | all to `GND` |
| A5 | CC1 | **float** | Rd 5.1 kohm to GND |
| B5 | CC2 | **float** | Rd 5.1 kohm to GND |
| A6, B6 | DP1, DP2 | **float** | tie together -> ESD -> RT1062 L8 |
| A7, B7 | DN1, DN2 | **float** | tie together -> ESD -> RT1062 M8 |
| A8, B8 | SBU1, SBU2 | **float, no NC flag** | explicit No-Connect flag |
| 1 | EH (shell) | **float** | defined GND net |

### The two hard stops

**No Rd, so no power ever arrives.** USB Type-C Cable and Connector Specification R2.0 (August
2019) §4.5.1.3.1: a source presents Rp on CC1/CC2 and *"the presence of an Rd pull-down resistor on
either pin indicates that a Sink is being attached."* With no Rd on either pin, the source never
leaves its unattached state and **VBUS is never enabled**. Table 4-25 fixes the sink termination at
5.1 kohm (±20 %, or ±10 % if the sink needs to read the source's advertised current). J7-ESP already
implements this correctly with R21-ESP and R22-ESP; J1 does not implement it at all.

**One VBUS contact cannot carry the trunk.** GCT USB4105 Product Specification Rev A3 rates
**5.00 A collectively across the four VBUS contacts** and 6.25 A collectively across the four GND
contacts — 1.25 A and 1.56 A per contact respectively. The re-derived coincident trunk peak is
**2.08 A** (see `power-envelope-rederivation.md`), which is 1.7x the single-contact VBUS rating.

### Footprint defect: unbonded shell tabs

DRC line 421: *"The pin of the component USB4105-GF-A does not correspond to the pad (Pad has no
corresponding pin: 2、3、4)"*, reported for **both** `$1I339` (J1) and `$1I8334` (J7). The symbol
exposes a single shell pin (`EH`, pin 1); the footprint carries four shell/hold-down pads. Pads 2,
3 and 4 therefore have no net and will be left netless in layout. For a USB-C receptacle these are
the mechanical retention and shield-return tabs. Either the symbol gains pins 2-4 mapped to the
same shell node, or the footprint's pads 2-4 are explicitly bonded. This is a schematic-side
symbol/footprint mismatch, not a placement question, so it belongs to VAL-G2 rather than VAL-G3.

---

## 2. J1 D+/D- to RT1062 USB_OTG1 — the new P0

### Confirm / refute of Captain's re-derivation

Captain re-derived `OPT_USB_AUD -- R56-VAL -- OPT_USB_AUD_RT` as *a single option strap to an RT
option GPIO, not D+/D-*. Measured at pin level:

- **Confirmed:** it is a single strap, not a differential pair. `OPT_USB_AUD` has exactly two
  endpoints (`J11-VAL.2`, `R56-VAL.1`); `OPT_USB_AUD_RT` has exactly two (`R56-VAL.2`,
  `U6-RTC.M8`). There is no D+ counterpart anywhere on the sheet. R56-VAL is marked **DNP**.
- **Refuted:** the RT-side endpoint is **not an option GPIO**. It is **ball M8**, whose symbol pin
  name is `USB_OTG1_DN`. NXP IMXRT1060CEC Rev. 4 (04/2024) Table 87 confirms M8 = USB_OTG1_DN on
  the 12x12 mm package, and Table 86 gives that ball **no Power Group, no Ball Type, no Default
  Mode and no GPIO alternate** — it is a dedicated analogue USB PHY pin with no IOMUX function at
  all. It cannot serve as an option strap under any firmware configuration.

So the sheet routes a validation-header option line into the RT1062's USB D- ball through a DNP
10 kohm resistor. As drawn (R56 not fitted) it is inert; if R56 were ever fitted it would bias the
USB D- line to the header's logic level. Both the strap and the header pin need reassignment to a
real GPIO before this option is usable.

### What exists, what is missing

| RT1062 ball | Signal | As captured | Verdict |
| --- | --- | --- | --- |
| L8 | USB_OTG1_DP | **float** | must carry J1 D+ |
| M8 | USB_OTG1_DN | `OPT_USB_AUD_RT` | **wrong connection**; must carry J1 D- |
| N6 | USB_OTG1_VBUS | **float** | must be driven, see below |
| N12 | USB_OTG1_CHD_B | float, **no NC flag** | NC is correct, flag is missing |
| P7, N7, P6 | USB_OTG2_* | float, no NC flag | NC is correct, flags are missing |
| K8 | VDD_USB_CAP | C74 100 nF + C75 10 uF | value unresolved, see below |

### The bounded repair — do not invent the VBUS circuit

**D+/D- path.** `J1.A6+B6` (DP1/DP2 tied) and `J1.A7+B7` (DN1/DN2 tied) into a low-capacitance
ESD array, out to a series TUNE footprint, then to L8 and M8 respectively.

- The ESD array must be low-capacitance. The `USBLC6-2SC6` already in the library is 2.5 pF typ /
  3.5 pF max line-to-ground (ST Doc ID 11265 Rev 5), which is the correct class of part for this
  job — and is exactly the application it is designed for, unlike its present misuse at D1-PWR1
  (see `PIN-AUDIT-PWR1.md` §D1). Pass D+ in on pin 1 and out on pin 6; D- in on pin 3 and out on
  pin 4; pin 5 to the VBUS being protected; pin 2 to GND.
- The series TUNE footprint should be **0 ohm fitted by default**, not a populated resistor. NXP's
  Hardware Development Guide (MIMXRT105060HDUG Rev. 3, §7.5) specifies 90 ohm differential
  routing, matched skew under 5 mils, no vias or stubs on DP/DM, and **no series termination
  value** — the PHY provides its own. A fitted non-zero series resistor is a deviation that needs
  its own justification.
- Note the same reasoning applies to R73-ESP / R74-ESP on J7 (§3).

**VBUS detect/sense — cited, not invented.** NXP IMXRT1060CEC Rev. 4:

1. `USB_OTG1_VBUS` recommended operating range **4.40 V to 5.50 V**; **absolute maximum 5.50 V**.
2. §4.2.1.1: *"USB_OTG1_VBUS and USB_OTG2_VBUS are not part of the power supply sequence and may be
   powered at any time."*
3. NXP HDG MIMXRT105060HDUG Rev. 3 Table 2 (power-supply decoupling) requires **1 x 1 uF, 10 V
   rated** on USB_OTG1_VBUS to GND, and **specifies no divider**. Do not add one: the pin is
   designed to sit on VBUS directly, and a divider would defeat the session-valid detection it
   exists to perform.

There is one real design question this raises, and it must be surfaced rather than quietly
resolved: **absolute maximum on that ball is 5.50 V, and USB VBUS is specified to 5.50 V with
hot-plug overshoot on top.** The margin is zero. Two defensible answers, both for the writer to
choose: connect N6 to `5V_PROTECTED` (downstream of the eFuse's overvoltage lockout, which is where
the transient has already been clamped) rather than to raw `5V_USB`; or connect to raw VBUS and add
a dedicated low-clamp TVS at the inlet. The first is preferred because it reuses protection that
must exist anyway — but it does mean the RT sees "VBUS present" only after the eFuse has enabled,
which is the correct semantic for a self-powered device in any case.

**`USB_OTG1_CHD_B` (N12).** NXP IMXRT1060CEC Rev. 4 Table 5, recommended connections for unused
analog interfaces, and HDG §7.5: leave **not connected**. Same for the three OTG2 balls. Correct as
captured; each needs an explicit No-Connect flag so the intent is recorded rather than inferred.

**`VDD_USB_CAP` (K8) — unresolved.** Present decoupling is C74 100 nF + C75 10 uF. NXP publishes
**no capacitance value** for VDD_USB_CAP in IMXRT1060CEC Rev. 4 Table 82 (the "Remark" column is
empty) or in HDG Rev. 3 Table 2 — which is notable because the adjacent VDD_HIGH_CAP *is*
specified, at 0.22 uF + 4.7 uF. Only the general rule applies: HDG Table 3 requires ripple below
5 % Vp-p on VDD_xxx_CAP rails. Recorded as `TUNE_TBD` in the JSON rather than passed silently.

---

## 3. J7-ESP — service USB

### VBUS sense-only: PROVEN

`S3_VBUS` has exactly six endpoints and all six are accounted for:

    J7-ESP.A4, J7-ESP.A9, J7-ESP.B4, J7-ESP.B9   (all four VBUS contacts)
    U10-ESP.5                                     (USBLC6-2SC6 VBUS clamp node, shunt to GND)
    R71-ESP.1                                     (top of a 100k/100k divider to GND via R72-ESP)

There is **no diode, FET, load switch, ferrite or resistor** from `S3_VBUS` to `5V_SYS`,
`5V_PROTECTED`, `5V_USB` or `5V_USB_FILTERED`. Back-feed is proven absent, not assumed absent.
The divider produces `ESP_USB_VBUS_SENSE` at VBUS/2 = 2.5 V nominal, which is inside the
ESP32-S3's 3.3 V input range. Correct by design.

The consequence is worth stating plainly: **J7 cannot power the board.** Flashing, serial and
recovery over J7 all require J1 to be supplying power — and J1 currently cannot.

### CC1/CC2: correct

`USB_CC1` -> R21-ESP 5.1 kohm -> GND, `USB_CC2` -> R22-ESP 5.1 kohm -> GND. Independently
terminated, correct value per USB Type-C Spec R2.0 Table 4-25.

### SBU1/SBU2: not what the brief assumed

The brief records SBU1/SBU2 as *intentional opens*. Measured: `J7-ESP.A8` and `J7-ESP.B8` are
`FLOATING_NO_WIRE` and **neither carries a No-Connect flag**. The 12 NC marks on the sheet are:
three on U4-PWR2, one on e3619, five on e5134, one on e5635, and two on U2-PWR1. **None is on J1
or J7.** So SBU1/SBU2 are bare undocumented floats on both connectors. NC is the right disposition;
the flag has to be added for it to be a recorded decision rather than an omission.

### Data chain: correct up to the last 5 units, then broken

    J7.A6+B6 --USB_DP--> U10-ESP.1 |I/O1| U10-ESP.6 --USB_DP_ESD--> R73-ESP(22R) --USB_DP_S3--> [C43-ESP DNP] --> X
    J7.A7+B7 --USB_DM--> U10-ESP.3 |I/O2| U10-ESP.4 --USB_DM_ESD--> R74-ESP(22R) --USB_DM_S3--> [C44-ESP DNP] --> X

`USB_DP_S3` and `USB_DM_S3` each end in a lead-in wire that stops **5 units short in x and 20 short
in y** of `U9-ESP.14 (IO20)` and `U9-ESP.13 (IO19)`. Polarity intent is correct — ESP32-S3 native
USB is D- on GPIO19 and D+ on GPIO20 — the wires simply do not land.

**This is not isolated to USB. `U9-ESP` has 0 of 41 pins connected.** Every lead-in wire around the
module misses: `ESP_EN`, `ESP_GPIO0`, `K1BR_SCK`/`MOSI`/`MISO_S3`/`CS`/`IRQ_S3`, `I2C_SDA`,
`I2C_SCL`, `NFC_IRQ`, `MOTION_INT_S3`, `S3_POR_REQ`, `RT_PWR_VALID`, `ESP_USB_VBUS_SENSE`,
`ESP_UART0_RX`, `ESP_UART0_TX`, plus its `3V3` and `GND` stubs — 48 wire clusters on the sheet
carry a net name and touch no pin at all, and roughly half of them belong to this module. The
signature is a component move: the module was relocated by `(+135, +35)` and the lead-in wires
were redrawn to the new column but terminated one grid step short.

Whether the cause is a stale pin read-back or a genuine near-miss, **the repair is identical**:
re-anchor every U9-ESP lead-in onto its pin and re-verify by read-back, not by eye. This is a
single bounded transaction and it is the highest-value repair on the sheet.

### Two flagged concerns on the J7 data path

**R73-ESP / R74-ESP = 22 ohm in series with each leg.** ESP32-S3 native USB is Full Speed only.
44 ohm of added differential series resistance on a 90 ohm line is a real impedance discontinuity;
at FS the consequence is degraded rise time and eye rather than certain failure. I did not fetch
the Espressif *ESP32-S3 Hardware Design Guidelines*, so I am flagging this rather than asserting
it: **check that document for the specified D+/D- series value before keeping 22 ohm.** The default
expectation for a native-USB MCU is a direct connection or 0 ohm.

**C43-ESP / C44-ESP stamped `DNP / 100pF USB D+ TUNE`.** As DNP footprints they are harmless and a
tuning footprint is good practice. The stamped *value* is not: 100 pF of shunt capacitance on a USB
data line is an order of magnitude above what a tuning cap should be, and if anyone ever populates
the BOM value the line stops working. Change the stamped value to a few pF, or leave it blank.

---

## Defect register, in repair order

| # | Defect | Severity | Bounded repair |
| --- | --- | --- | --- |
| 1 | `U9-ESP` 0 of 41 pins connected | **P0** | Re-anchor all 41 lead-ins; read-back verify |
| 2 | J1 CC1/CC2 have no Rd — no Type-C source will ever enable VBUS | **P0** | 5.1 kohm from A5 to GND and from B5 to GND |
| 3 | J1 D+/D- absent; RT1062 L8 floats | **P0** | ESD array + 0 ohm TUNE -> L8 / M8 |
| 4 | J1 3 of 4 VBUS and 3 of 4 GND contacts float | **P0** | Bond A4, A9, B9 to `5V_USB`; A1, A12, B12 to `GND` |
| 5 | `USB_OTG1_DN` (M8) wired to a DNP validation strap | **P0** | Free M8; move `OPT_USB_AUD` to a real GPIO |
| 6 | `USB_OTG1_VBUS` (N6) floats | **P1** | Tie to `5V_PROTECTED` + 1 uF/10 V per NXP HDG Table 2 |
| 7 | USB4105 footprint pads 2-4 have no symbol pin (both J1 and J7) | **P1** | Symbol gains shell pins, or pads bonded |
| 8 | J1 shell (EH) floats | **P1** | Defined GND net |
| 9 | SBU1/SBU2 undocumented floats on both connectors | **P2** | Add No-Connect flags |
| 10 | `CHD_B` + three OTG2 balls float without NC flags | **P2** | Add No-Connect flags |
| 11 | 22 ohm series on J7 D+/D- | **P2, open** | Check Espressif ESP32-S3 HDG, then keep or zero |
| 12 | `VDD_USB_CAP` value unresolved against NXP | **P2, open** | No vendor value exists; record the choice |
| 13 | C43/C44 stamped 100 pF | **P3** | Restamp to a few pF or blank |

---

**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:usb-power-audit | Created. D-044 conformance verdict against frozen hash 489736:464c27d4; Captain's R56-VAL re-derivation confirmed in part and refuted in part; bounded repair specified for the RT1062 USB data path. |
