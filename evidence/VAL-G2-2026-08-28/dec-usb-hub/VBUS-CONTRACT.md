# VBUS-CONTRACT

If this file is hand-wavy, H is not GREEN. Letters are chosen, not blurred.

```text
F2 = F2-C
F6 = F6-B
F6_VALIDITY_SOURCE = 5V0_USB_VALID
F6_VALIDITY_IC = TPS7A2550DRVR / C2876265
F6_ENVELOPE = CLOSED_NAMED
F6_B_KILL = KILL-B
VBUS_DET_SOURCE = 5V_USB
RAW_5V_USB_C = 1.0 uF (C1-PWR1 retarget; this IS U22 CIN; no second 1 uF)
PROTECTED_BULK = C2-PWR1 22 uF KEEP + C120-USB 22 uF ADD
R80_USB = 4.7 kOhm
H0f = H0f-CLOSE.md
```

## F1 — sense sources

- Hub `VBUS_DET` ← divider from **`5V_USB` always**. Never 3V3. Never `5V_SYS`.
- F6-B (VAL default): RT `USB_OTG1_VBUS` from `RT_USB_VBUS` (OUT1).
  Switch IN = `F6_VALIDITY_SOURCE` = `5V0_USB_VALID` (U22-USB TPS7A2550DRVR
  from `5V_USB`; `H0f-CLOSE.md`). EN path is F6-B-KILL. OC → OCSx_N.
  S3 GPIO15 ← **`USB_5V_VALID`** (KILL-B comparator). Do not wait on
  OUT2: TPS2052B `toff` max is 10 ms at 100 µF and cannot own 3 ms.
  OUT2 `S3_USB_VBUS_VALID` stays as the switched copy (bleeder only).
- RT `USB_OTG1_VBUS` ← **no divider**, 1 µF 10 V to GND (`CUSBVBUS-RTC` exists;
  retarget net). Source must supply **25 mA typ / 50 mA max** copied from
  IMXRT1060IEC Rev. 4 Table 12 (`NXP-USB-OTG1-VBUS-EXTRACT.md`;
  `D4-NXP-IMXRT1060IEC.pdf` SHA
  `a4ef1fd31841678b97967ef8a64fcbd76aec509e565066c064dff536a97fd295`).

## F2 — RT 5.50 V / current — **F2-C**

NXP recommended 4.40–5.50 V. Abs max **5.50 V**. USB VBUS is specified to
5.50 V plus hot-plug overshoot.

- F2-A (`5V_USB` direct) — legal only under F6-A. Zero DC margin. **Not selected.**
- F2-B (`5V_PROTECTED` direct) — legal only under F6-A. **Not selected.**
- **F2-C** — N6 to F6-B `RT_USB_VBUS` + 1 µF. **VAL default with F6-B.**
  Host-unplug kill is F6-B-KILL, not an assumed PRTPWR drop. Do not write
  “`5V_PROTECTED` preferred”.

Hub `VBUS_DET` stays on `5V_USB` in every letter.

## F3 — S3 monitor

From `ESP-USB-SELF-POWERED-EXTRACT.md`: valid > **4.75 V**, invalid < **4.35 V**,
GPIO low within **3 ms**, divider option **0.75 × Vdd at 4.4 V**
(k = 2.475 / 4.4 = 0.5625 at Vdd = 3.3 V). GPIO VIH ≈ 2.475 V.

G2.1 census: today’s divider is **100 k / 10 k** (`R71`/`R72`), not the old-audit
100 k / 100 k. Still delete it. Do not copy either pair. GPIO15 is now
driven by `USB_5V_VALID` (R85), not a new divider from OUT2.

F6-B: the **3 ms** is owned by KILL-B `USB_5V_VALID` → GPIO15 (R85
470 Ω). Not owned by hub `VBUS_DET`. Not owned by PRTPWR. Not owned by
TPS2052B OUT2.

If the VIH window cannot be closed with resistors, specify a comparator to
GPIO15. That comparator is now named: U23-USB TLV7031. Still not an MCU
power island.

Leakage when the sense source is present and S3 is unpowered: **0 µA from
VBUS into GPIO15**. U23 is a 3.3 V push-pull; it is off when `3V3` is
down. No 5 V divider into the pin.

## F4 — hub VBUS_DET divider

Default: **100 k / 100 k** from `5V_USB` to GND, tap to pin 16. Separate from
the S3 divider.

Checklist §5.1 (verbatim extract): *“The upstream port VBUS line must have
no more than 10 μF of the total capacitance connected.”*

## F4b — raw `5V_USB` capacitance (from the G2.1 census, not instinct)

Census E1.8 / E1.2 / E1.10 (`CENSUS.md`) is the actual graph:

```text
J1 A4/A9/B4/B9  →  5V_USB
                     ├── C1-PWR1  22 µF          ← only raw bulk today
                     ├── R63-PWR1 1.05 MΩ        EN divider
                     ├── U1-PWR1.5 IN            eFuse
                     └── DVBUS-PWR1 SMF5.0A      Convert to PCB = no → DELETE
U1-PWR1.6 OUT   →  5V_PROTECTED
                     ├── C2-PWR1  22 µF          protected bulk (already)
                     ├── D1.5 USBLC6 VBUS ref
                     ├── RSH1 → 5V_SYS
                     └── CUSBVBUS-RTC 1 µF       today; retarget off this rail
```

Captain’s intended tree matches this graph **except** C1 is 22 µF on the
raw node (H12 fail) and there is no VBUS_DET / bleeder yet.

Contracted tree (prove against that census):

```text
USB-C VBUS
  ├── C1-PWR1 RETARGET 22 µF → 1.0 µF on 5V_USB     (this IS U22 CIN)
  ├── C121-USB 100 nF at U22 IN                     (HF only; not a second 1 µF)
  ├── VBUS_DET 100 k / 100 k
  ├── R80-USB F8 bleeder 4.7 kΩ
  ├── D3-USB SMF5.0A                                (new clamp; not DVBUS-PWR1)
  └── eFuse U1
        ├── C2-PWR1 KEEP 22 µF on 5V_PROTECTED
        ├── C120-USB ADD 22 µF on 5V_PROTECTED      (C1’s energy relocated)
        ├── INA / shunt → 5V_SYS
        └── F6 validity source                      (not this rail; see F6-B1)
```

| Designator | Today (census) | Contract | Why |
| --- | --- | --- | --- |
| C1-PWR1 | 22 µF on `5V_USB` | **RETARGET value to 1.0 µF**, stay on `5V_USB` | Checklist ≤ 10 µF; U22 CIN; do not keep `VBUS_DET` alive |
| C2-PWR1 | 22 µF on `5V_PROTECTED` | **KEEP** | Big energy already behind the eFuse |
| C120-USB | absent | **ADD** 22 µF on `5V_PROTECTED` | Relocate the energy C1 used to store on the raw node |
| C121-USB | absent | **ADD 100 nF** at U22 IN | HF only. A second 1 µF on raw VBUS would blow Clock 1 |
| C122-USB | absent | **ADD 2.2 µF** on `5V0_USB_VALID` | LDO COUT. Not on `5V_USB` |
| DVBUS-PWR1 | SMF5.0A, Convert to PCB = no | **DELETE** from placed island | Census leftover. Replacement clamp is **D3-USB** SMF5.0A |
| R80-USB | absent | **ADD** 4.7 kΩ `5V_USB`–GND | F8 + Clock 1 from a 5.50 V start; ~6.4 mW at 5.5 V |

Three clocks stay separate. TPS2052B does not discharge `5V_USB`.

## F5 — four-row state table (F2-C + F6-B + KILL-B)

| Row | Condition | `5V_USB` | `5V_SYS` | `VBUS_DET` | PRTPWR | `RT_USB_VBUS` | `S3_USB_VBUS_VALID` | S3 GPIO in 3 ms? | Hub enumerates? | J6 UART? | Firmware |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Host present, board from J1 | up | up | high (after divider) | host may set ON | follows KILL-B + EN | follows KILL-B + EN | n/a (still plugged) | yes if hub up | yes | normal attach |
| 2 | Host absent, bench 5 V on `5V_SYS` only | **down** | up | **low** | may stay ON (not specified to fall) | **down** (KILL-B) | **down** (KILL-B) | **yes** (KILL-B `USB_5V_VALID`) | no | yes | do not fake attach |
| 3 | Host absent, bench 5 V forced onto J1 VBUS | **up** | up | **high** | may be ON | **up** if EN true | **up** if EN true | no (still “plugged”) | maybe | yes | **named J1 hazard** — looks like a host |
| 4 | Board unpowered | down | down | down | down | down | down | n/a | no | no | none |

Row 2 is why F6-B exists. Row 3 is the existing J1 hazard. Do not invent a
new net to paper over it.

## F6 — F6-B selected (Captain 2026-08-29)

F6-A omit is the later shave path only. `NON_REM` is not this argument.

### F6-B1 — envelope closed; rail named

`F6_VALIDITY_SOURCE = 5V0_USB_VALID` generated by **U22-USB TPS7A2550DRVR**.

This is **not** a default to `5V_PROTECTED`. The inlet maths were run.
**No existing census rail qualifies.** A new 5.0 V / 18 V LDO was added
because cutoff cannot sit on both 5.50 V legal VBUS and 5.50 V NXP abs max.
Comparison, pin map, dropout proofs and KILL-B parts:
`H0f-CLOSE.md` (authoritative) and `F6-VALIDITY-SOURCE.md`.

Limits used (vendor files, not habit):

| Limit | Value | Source |
| --- | --- | --- |
| TPS2052B VIN recommended | 2.7–**5.5 V** | SLVS514P §6.3 (`D5a-TI-TPS2052B.pdf`) |
| TPS2052B VIN absolute max | **6.0 V** | SLVS514P §6.1 |
| NXP `USB_OTG1_VBUS` recommended | 4.40–**5.5 V** | IMXRT1060IEC Table 8 |
| NXP `USB_OTG1_VBUS` abs max | **5.50 V** | same band as recommended max |
| USB Type-C vSafe5V | up to **5.50 V** | legal host DC |
| G2.1 eFuse OVLO | **6.008 V** | below |

G2.1 census divider (U1 TPS259474L, TI SLVSFC9C, Vth = 1.20 V):

```text
R63 = 1.05 MΩ   5V_USB → EN
R2  = 100 kΩ    EN → OVLO
R64 = 287 kΩ    OVLO → GND
Rtot = 1.437 MΩ

V_IN(OV)  = 1.20 × 1437 / 287  = 6.008 V
V_IN(UV)  = 1.20 × 1437 / 387  = 4.456 V
```

(The pre-G2.1 324 kΩ lower leg gave OVLO ≈ 5.46 V, inside the USB band.
G2.1 RQ-020 moved it to 287 kΩ / ≈ 6.01 V so legal 5.50 V hosts pass.)

**Contradiction (why no existing rail can be named):**

1. A legal host may sit at **5.50 V DC**. The eFuse must **pass** that
   (OVLO > 5.50 V plus divider tolerance). Today it does: 6.01 V.
2. `5V_PROTECTED` therefore follows inlet DC up to the OVLO trip,
   i.e. up to **≈ 6.01 V**.
3. TPS2052B recommended VIN max is **5.5 V**. NXP abs max is **5.50 V**.
4. Therefore `5V_PROTECTED` (and `5V_SYS`, which is the same voltage
   minus ≈ 20 mV in the 10 mΩ shunt) **cannot** be proved to stay inside
   both recommended / abs-max boxes while the board still accepts legal
   USB. Naming `5V_PROTECTED` because it “sounds safe” is the forbidden
   habit.
5. `5V_USB` is worse: `DVBUS-PWR1` is not on the PCB. Hot-plug transient
   on the raw node is **unbounded** by a board clamp. KILL-A (IN tracks
   `5V_USB`) stays rejected.
6. A new 5.0 V LDO closes the box. **Named:** TPS7A2550DRVR / C2876265,
   VOUT 5.00 V ±1 %, VIN 18 V, VDO **105 mV max @ 50 mA** (datasheet row,
   not a 300 mA scale). 4.75 − 0.105 − 0.007 = **4.638 V ≥ 4.40 V**.
   At 80 mA design current, interpolated VDO 128 mV → N6 **4.611 V**.
   High-line 5.50 V host → VOUT 5.05 V max → N6 **5.043 V < 5.50 V**.
   Datasheet SHA
   `d0116d16cb8e86050457b4a158b2837ecc378bd818ebef713f699e7d74028a5e`.
   Full comparison: `H0f-CLOSE.md`.

Envelope status: **CLOSED**. Source name: **`5V0_USB_VALID`**.

### F6-B-KILL — **KILL-B**

Microchip does not specify `VBUS_DET ↓ ⇒ PRTPWR ↓`. Checklist OFF list:
overcurrent, host command, hub reset/POR. **VBUS_DET loss is not listed.**

- KILL-A (IN tracks `5V_USB`) — rejected; raw envelope unbounded and
  recommended 5.5 V not proved.
- **KILL-B — EN_AND_5V_USB_VALID.** EN1/EN2 = PRTPWRx **AND** a hardware
  `5V_USB`-valid (comparator/supervisor). Cable-out kills EN even if PRTPWR
  stays high. Independent of the undocumented `VBUS_DET → PRTPWR` path.
- KILL-C (trust PRTPWR on VBUS_DET fall) — **forbidden**.

### F6-B2

S3 3 ms is **Clock 1 in F8** (KILL-B `USB_5V_VALID` → GPIO15 = **1.45 ms**
worst-case). Do not use TPS2052B `toff` (10 ms max at 100 µF) as that
owner. OUT1 collapse is Clock 3 (**2.60 ms** to below 4.40 V).

Neither TPS2052B output powers an MCU.

## F7 — Anomaly 3

See `ERRATA-HOLD.md`. USB audio `EXPERIMENT_ONLY`. Hold stands.

## F8 — three clocks (do not share 3 ms)

Independent proofs. Unplug starts at **5.50 V**. C_raw worst = **1.2 µF**
(C1 × 1.20 + C121 100 nF). R80 = **4.7 kΩ**. Arithmetic in `H0f-CLOSE.md`.

1. **S3 GPIO15** low within **3 ms** (Espressif). Owner: KILL-B
   (`USB_5V_VALID` → R85 → GPIO15). VTH worst = 4.252 V.
   **Clock 1 = 1.45 ms ≤ 3 ms.**
2. **Hub `VBUS_DET`.** Microchip specifies host VBUS toggle as soft-reset /
   reconnect, **not a millisecond number**. Declared reconnect budget:
   **100 ms** to below divider VIL (tap 0.8 V ⇒ `5V_USB` = 1.60 V),
   **not** 3 ms. Owner: R80 on `5V_USB`.
   **Clock 2 = 28 ms (5τ) ≤ 100 ms.** Time to VIL = 6.96 ms.
   Do not assume TPS2052B fixes a sticky `5V_USB` node.
3. **RT `USB_OTG1_VBUS` / `RT_USB_VBUS`** below **4.40 V** within **10 ms**.
   Owner: KILL-B + U21 tf max 0.50 ms + R86 4.7 kΩ on the 1 µF.
   **Clock 3 = 2.60 ms ≤ 10 ms.**

Today’s G2.1 C1 = 22 µF is **superseded on paper** by F4b. H12 scores the
contract, not the unmutated sheet.

## F9 — inlet as one domain

| Advertisement | Allowed sink | Notes |
| --- | --- | --- |
| Default (USB2) | 500 mA | Pre-firmware startup must survive this |
| Type-C 1.5 A | 1.5 A | Throttle if advertisement falls |
| Type-C 3.0 A | 3.0 A | Still not PD |
| Connector 5 A | **not a grant** | Thermal headroom only |

Budget includes hub 70/89 mA 3V3 (from 5 V through the buck), F6-B 25–50 mA
RT VBUS, LED/NFC/audio as already carried. USB-PD steelman: **reject for R0**
(complexity, CC policy rewrite). Hold: formalise Default / 1.5 / 3 A
descriptor vs CC-throttle (amber from the UFP-powered-hub WP 0.9; **not a
certification basis**).

eFuse OVLO ≈ 6.01 V vs 5.50 V abs max is **closed as a contradiction on
existing rails**, and **closed as a named rail** by `5V0_USB_VALID`.
