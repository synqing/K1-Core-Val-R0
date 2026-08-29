# H0f-CLOSE — F6 validity source named

```text
H0f                 = CLOSED
F6_VALIDITY_SOURCE  = 5V0_USB_VALID
F6_VALIDITY_IC      = TPS7A2550DRVR / C2876265
TOPOLOGY            = high-VIN 5.0 V LDO from raw 5V_USB
                        + KILL-B (TLV7031 AND dual 1G08)
                        + TPS2052B on the regulated rail
EASYEDA             = not this file
LIVE_64325d0e       = not mutated
```

What happened. H0f was still a letter with `TBD` as the only honest
end-state until a rail was named from physics. No existing G2.1 net
survives the inlet envelope and the NXP / TPS2052B boxes at once, so a
new regulator was specified.

What is true now. The validity source is **`5V0_USB_VALID`**, made by
**U22-USB TPS7A2550DRVR**. TPS2052B IN sits on that rail, not on
`5V_PROTECTED` and not on raw `5V_USB`. Inlet capacitance is contracted:
**1.0 µF** on raw `5V_USB` (C1 retarget; this *is* the LDO CIN), bulk
behind the eFuse (C2 keep + C120 add).

What is left. EasyEDA on a disposable hub project, never live
`64325d0e`. This file is the schematic-level netlist for that later
work.

## Why a regulator, not a cutoff

Legal Type-C vSafe5V DC reaches **5.50 V**. NXP `USB_OTG1_VBUS`
recommended *and* absolute maximum is **5.50 V** (IMXRT1060IEC Table 7
and Table 8). A hard OVLO at or below 5.50 V drops a legal host. An
OVLO above 5.50 V (TPD1S514 class, NCP349 ≈ 5.68–6.2 V, or today’s
eFuse at **6.008 V**) passes a voltage N6 must not see.

Cutoff cannot close both boxes. The rail must **regulate**.

G2.1 eFuse OVLO (U1 TPS259474L, Vth = 1.20 V):

```text
R63 = 1.05 MΩ    5V_USB → EN
R2  = 100 kΩ     EN → OVLO
R64 = 287 kΩ     OVLO → GND
Rtot = 1.437 MΩ
V_IN(OV) = 1.20 × 1437 / 287 = 6.008 V
```

`5V_PROTECTED` therefore follows inlet DC up to ≈ 6.01 V. TPS2052B
recommended VIN max is **5.5 V** (SLVS514P §6.3). Naming
`5V_PROTECTED` because it “sounds safe” is the forbidden habit.

## Candidates (physics, then LCSC)

| Topology / MPN | Why considered | Why it lost |
| --- | --- | --- |
| Raw `5V_USB` into TPS2052B | Fewest parts | Inlet clamp is SMF5.0A, Vc ≈ 9 V under surge. Recommended VIN 5.5 V not proved. KILL-A rejected. |
| `5V_PROTECTED` / `5V_SYS` | Already “protected” | Follows OVLO **6.01 V**. Fails TPS2052B rec max and NXP 5.50 V abs max. |
| OVP switch (TPD1S514, NCP349/NCP360) | Survive over-voltage | Trip 5.7–6.2 V class. Passes legal 5.50 V straight to N6. Same cutoff paradox. |
| Protected load switch (TPS229xx, AP2280) | Fast EN, reverse-block | No regulation. VIN often 5.5–6 V. Same 5.50 V problem. |
| Comparator-controlled PFET pass | UV + OV in hardware | OV still cannot sit on both 5.50 V legal and 5.50 V abs max. Without a regulator this *is* a cutoff. |
| Precision shunt / 5.1 V clamp | Hold N6 at 5.0 V | A 5.50 V host into a 5.1 V shunt is a heater. Needs a series limiter; that limiter is an LDO. |
| High-dropout high-VIN LDO (XC6216B502, AMS1117-5.0) | Cheap, 24–28 V | VDO ≈ 1.1–1.3 V. At 4.75 V host, N6 ≈ 3.5 V. Fails 4.40 V min. |
| AP2204K-5.0TRG1 C112031 | 24 V, high stock | 5.0 V sibling dropout not published on the hit; 3.3 V sibling 420–500 mV @ 100–150 mA. 4.75 − 0.45 = 4.30 V < 4.40 V. |
| AP7361C-50 | Low dropout | VIN max **6.0 V**. SMF clamp ≈ 9 V. Fail. |
| NCP718ASN500 / NCP718AMT500TBG | 24 V, 300 mA | VDO max **380 mV** @ 300 mA (worse than TPS7A25 340 mV). LCSC stock of the WDFN was 5 on 2026-08-29. No win. |
| AP7375Q-50 / AP7370-50 | 45 V / wide VIN, LCSC alt | AP7375 VDO **350 mV typ @ 100 mA** — worse than TPS7A25 **105 mV max @ 50 mA**. |
| Buck 5.0 V | Regulate and survive 18 V | 80 mA does not justify an inductor next to USB analogue. Lose on EMI and parts. |
| **TPS7A2550DRVR C2876265** | 18 V, 300 mA, 5.00 V ±1 % | **WIN.** |

Winner authority: `datasheets/D5i-TI-TPS7A25.pdf` SBVS372C, SHA-256
`d0116d16cb8e86050457b4a158b2837ecc378bd818ebef713f699e7d74028a5e`.
LCSC C2876265, WSON-6-EP 2×2, Extended, **147** ship-now (LCSC
2026-08-29 fetch). VAL accepts the Extended feeder.

## Winner limits (used in the proofs)

| Limit | Value | Source |
| --- | --- | --- |
| VIN recommended | 2.4–**18 V** | TPS7A25 §6.3 |
| VIN abs max | **20 V** | §6.1 |
| VOUT fixed | 5.00 V **±1 %** | §6.5 → 4.95–5.05 V in regulation |
| VOUT abs max (fixed) | **5.5 V** | §6.1 |
| IOUT | 0–300 mA | §6.3 |
| VDO @ 50 mA | 64 typ / **105 mV max** | §6.5 (NXP 50 mA row) |
| VDO @ 150 mA | 120 typ / 180 mV max | §6.5 |
| VDO @ 300 mA | 210 typ / 340 mV max | §6.5 — **not** the current we draw |
| CIN / COUT | 1 µF nom / 1–100 µF (2.2 µF typ) | §6.3; 50 % derate assumed by TI |
| Active overshoot pulldown | yes | Features |
| TPS2052B VIN rec | 2.7–**5.5 V** | SLVS514P §6.3 |
| TPS2052B VIN abs | **6.0 V** | §6.1 |
| TPS2052B rDS(on) D-pkg | 70 typ / **135 mΩ max** | §6.5 |
| TPS2052B tf @ 1 µF | 0.05–**0.50 ms** | §6.5 |
| TPS2052B toff @ 100 µF | **10 ms max** | §6.5 — different load; do not own S3 with this |
| Fig 6-18 toff @ 1 µF | delay ≪ 50 µs, fall < 0.5 ms | SLVS514P typical, 500 µs/div |
| NXP USB_OTG1_VBUS rec | **4.40–5.5 V** | IEC Table 8 |
| NXP USB_OTG1_VBUS abs | **5.5 V** | IEC Table 7 |
| NXP current | 25 mA / interface, **50 mA max** | IEC Table 12 |
| USB2422 upstream C | **≤ 10 µF** | Checklist §5.1 |
| USB2422 VBUS_DET | VILI **0.8 V**, VIHI **2.0 V** (I-buffer) | DS Table 5-1 |
| Espressif | valid > 4.75 V, invalid < 4.35 V, GPIO low in **3 ms** | `ESP-USB-SELF-POWERED-EXTRACT.md` |

### Dropout / high-line proofs (80 mA design, 50 mA NXP)

Design current: RT 50 mA + S3/KILL-B resistors + TPS2052B Iq + margin
= **80 mA**. LDO is a 300 mA part.

Linear interpolate VDO max between 50 mA (105 mV) and 150 mA (180 mV):
**128 mV at 80 mA**. Switch drop 135 mΩ × 80 mA = **11 mV**.

| Host `5V_USB` | LDO | TPS2052B IN | N6 (`RT_USB_VBUS`) |
| --- | --- | --- | --- |
| 4.75 V (USB-IF / Type-C min) | dropout, ≥ 4.75 − 0.105 = **4.645 V** @ 50 mA | same | ≥ 4.645 − 0.007 = **4.638 V ≥ 4.40 V** |
| 4.75 V @ 80 mA | ≥ 4.75 − 0.128 = **4.622 V** | same | ≥ **4.611 V ≥ 4.40 V** |
| 5.09–5.50 V | regulate **4.95–5.05 V** | ≤ 5.05 V ≤ 5.5 V rec | ≤ 5.043 V **< 5.50 V abs** |
| 6.01 V (eFuse OVLO, if it reached IN) | regulate 5.05 V | 5.05 V | 5.04 V |
| SMF clamp ≈ 9 V on raw | VIN 18 V rec / 20 V abs | still 5.05 V | still 5.04 V |

No series input diode: BAT54 Vf ≈ 0.3 V would put 4.75 − 0.3 − 0.105
= 4.345 V on N6, under 4.40 V. `D4-USB` stays **DNP**.

`D3-USB` SMF5.0A is a **new** inlet clamp, not a revival of census
`DVBUS-PWR1` (Convert-to-PCB = no). It keeps U22 VIN inside 18 V. It
does **not** make raw `5V_USB` legal as TPS2052B IN.

## Capacitor correction (contracted inlet)

Census E1.8: C1-PWR1 is **22 µF on `5V_USB`** today. That is an H12
fail (checklist ≤ 10 µF) and it holds `VBUS_DET` / KILL-B alive.

```text
USB-C VBUS
  ├── C1-PWR1  RETARGET 22 µF → 1.0 µF 16 V X7R 0805 on 5V_USB
  │              this IS U22 CIN — do not add a second microfarad
  ├── C121-USB ADD 100 nF 16 V at U22 IN (HF only; in the 1.2 µF worst C)
  ├── R78/R79  100 k / 100 k  VBUS_DET
  ├── R80-USB  4.7 kΩ         F8 bleeder (not 10 kΩ — see clocks)
  ├── R81/R82  KILL-B sense
  ├── D3-USB   SMF5.0A        new clamp
  └── U1 eFuse
        ├── C2-PWR1  KEEP 22 µF on 5V_PROTECTED
        └── C120-USB ADD  22 µF on 5V_PROTECTED   (C1’s energy, moved)
```

| Designator | Today | Contract |
| --- | --- | --- |
| C1-PWR1 | 22 µF on `5V_USB` | **1.0 µF** on `5V_USB` (U22 CIN) |
| C2-PWR1 | 22 µF on `5V_PROTECTED` | **KEEP** |
| C120-USB | absent | **ADD 22 µF** on `5V_PROTECTED` |
| C121-USB | — | **100 nF** at U22 IN, not 1 µF |
| C122-USB | — | **2.2 µF** on `5V0_USB_VALID` (does **not** sit on raw VBUS) |
| DVBUS-PWR1 | SMF5.0A, PCB = no | **DELETE**; replace with **D3-USB** |

Worst-case raw C used in the clocks: **1.2 µF** = C1 × 1.20 + C121.
Still ≪ 10 µF.

## KILL-B (coexists with F6-B)

APX803S-31 rejected: 240 ms reset delay misses 3 ms. LDO PG rejected:
low in dropout at legal 4.75 V.

Threshold is set for a **5.50 V** unplug, not a 5.00 V habit.

```text
R81-USB  169 kΩ 1%   5V_USB → TAP_VBUS
R82-USB  100 kΩ 1%   TAP_VBUS → GND          k = 100/269 = 0.3717
R83-USB  100 kΩ 1%   3V3 → TAP_REF
R84-USB  100 kΩ 1%   TAP_REF → GND           Vref = 1.65 V
U23 IN+  = TAP_VBUS
U23 IN−  = TAP_REF
U23 OUT  = USB_5V_VALID
VTH nom  = 1.65 / 0.3717 = 4.439 V
```

Tolerance (resistors ±1 %, `3V3` ±3 %):

| | k | Vref | VTH |
| --- | --- | --- | --- |
| min | 0.3764 | 1.6005 V | **4.252 V** |
| nom | 0.3717 | 1.650 V | **4.439 V** |
| max | 0.3671 | 1.6995 V | **4.630 V** |

VTH max **4.630 V < 4.75 V**. Low legitimate VBUS still attaches
(120 mV worst-case). SMF 9.2 V × 0.372 = 3.42 V on IN+ < 7 V abs.

```text
U24: USB_PRTPWR1  AND  USB_5V_VALID  → U21 EN1
U25: USB_PRTPWR2  AND  USB_5V_VALID  → U21 EN2
```

### S3 GPIO15 does **not** wait on OUT2

TPS2052B `toff` max is **10 ms** at 100 µF. That number cannot own
Espressif’s 3 ms. Figure 6-18 at 1 µF is fast, but OUT2 also waits on
PRTPWR (chicken-and-egg with hub configure) and grows if anyone later
adds bulk.

**GPIO15 ← `USB_5V_VALID`** through R85 470 Ω. That is the 3 ms owner.
OUT2 `S3_USB_VBUS_VALID` stays as the F6-B switched copy (bleeder only;
test / optional). It is not the attach pin.

F3 leakage (sense present, S3 unpowered): `USB_5V_VALID` is a 3.3 V
push-pull from U23, which is itself unpowered if `3V3` is down. No 5 V
into GPIO15. Closed: **0 µA from VBUS into GPIO15**.

## Three independent clocks (contracted inlet)

Start voltage for unplug is **5.50 V** (legal max), not 5.00 V.
C_raw worst = **1.2 µF**. R80 = **4.7 kΩ** is the contracted bleeder;
other paths are bonus.

### Clock 1 — S3 GPIO15 low within 3 ms

Owner: KILL-B on `5V_USB`. Independent of hub `VBUS_DET`. Independent
of TPS2052B.

```text
t = R80 × C_raw × ln(5.50 / VTH_min)
  = 4.7e3 × 1.2e-6 × ln(5.50 / 4.252)
  = 1.45 ms
TLV7031 tpd ≤ 3 µs
AND tpd  ≪ 1 µs
GPIO15  = USB_5V_VALID
CLOCK 1 = 1.45 ms  ≤  3 ms
```

Nominal (5.00 V, C = 1.0 µF, all parallel 4.50 kΩ, VTH 4.439 V):
**0.54 ms**.

### Clock 2 — hub `VBUS_DET` below VIL, declared 100 ms

Owner: R80 + C1 on `5V_USB`. Independent of KILL-B. Independent of
TPS2052B. Microchip gives no millisecond number; reconnect budget is
the contract’s **100 ms**.

100 k / 100 k tap. VILI = 0.8 V ⇒ `5V_USB` must reach **1.60 V**.

```text
t_VIL = 4.7e3 × 1.2e-6 × ln(5.50 / 1.60) = 6.96 ms
5τ     = 5 × 4.7e3 × 1.2e-6                 = 28.2 ms
CLOCK 2 = 28 ms (5τ)  ≤  100 ms
```

At 4.75 V host, tap = 2.375 V > 2.0 V VIHI. Attach holds.

### Clock 3 — RT `USB_OTG1_VBUS` below 4.40 V within 10 ms

Owner: KILL-B + U21 EN fall + OUT1 + `CUSBVBUS-RTC` 1 µF + R86 bleeder.
Independent of hub `VBUS_DET`. NXP’s 25 mA is a **supply** requirement,
not a guaranteed sink during collapse, so R86 is fitted.

```text
KILL-B trip (clock 1)                     1.45 ms
tf max @ 1 µF (SLVS514P §6.5)             0.50 ms
R86 4.7 kΩ × 1 µF × ln(5.05 / 4.40)       0.65 ms
CLOCK 3 = 2.60 ms  ≤  10 ms
```

Full dump 5.05 V → 0.80 V through R86 alone is 8.7 ms after EN; still
inside 10 ms once added to 1.45 + 0.50 = **10.6 ms** to *empty*, which
is why the contract defines collapse as **below 4.40 V** (no longer a
valid VBUS). Empty-to-ground is a bonus, not the stamp.

## Reverse / backfeed

- U22 IN is only `5V_USB`. `5V_SYS` has no path into it.
- Row 2 (bench `5V_SYS` only): `5V_USB` down → U22 down →
  `5V0_USB_VALID` down → KILL-B low → OUT1/OUT2 down. No fake attach.
- TPS2052B reverse leakage IN=0, OUT=5.5 V: **0.2 µA typ** (§6.5).
- C122 2.2 µF into ≥ 50 mA: 2.2e-6 × 5 / 0.05 = **220 µs** if the
  load is present; pulldown also active. No series diode.
- D4-USB BAT54: **DNP**, unfitted, never in series with IN.

## Four-row behaviour

| Row | Condition | `5V0_USB_VALID` | EN | OUT1/OUT2 | GPIO15 |
| --- | --- | --- | --- | --- | --- |
| 1 | Host on J1 | 5.0 V or dropout ≥ 4.62 V | PRTPWR AND high | follow EN | high |
| 2 | Bench `5V_SYS` only | **down** | forced low | **down** | **low** in 1.45 ms |
| 3 | Bench forced onto J1 VBUS | up (named J1 hazard) | may be ON | up if PRTPWR | high |
| 4 | Unpowered | down | down | down | down |

## Schematic-level netlist (EasyEDA later)

Nets introduced or owned here: `5V0_USB_VALID`, `USB_5V_VALID`,
`TAP_VBUS`, `TAP_REF`, `RT_USB_VBUS`, `S3_USB_VBUS_VALID`,
`USB_PRTPWR1`, `USB_PRTPWR2`, `USB_OCS1_N`, `USB_OCS2_N`,
`USB_VBUS_DET`.

### U22-USB — TPS7A2550DRVR / C2876265 — WSON-6 DRV **fixed**

| Pin | Name | Net |
| --- | --- | --- |
| 1 | OUT | `5V0_USB_VALID` |
| 2 | NC | `GND` (thermal; do not treat as NR/SS — that is the adjustable die) |
| 3 | PG | no-connect (or GND). **Not** KILL-B |
| 4 | EN | `5V_USB` (tied to IN; do not float) |
| 5 | GND | `GND` |
| 6 | IN | `5V_USB` |
| EP | thermal | `GND`, vias |

### U21-USB — TPS2052BDR / C130049 — SOIC-8

| Pin | Name | Net |
| --- | --- | --- |
| 1 | GND | `GND` |
| 2 | IN | `5V0_USB_VALID` |
| 3 | EN1 | `USB_EN1` (U24.Y) |
| 4 | EN2 | `USB_EN2` (U25.Y) |
| 5 | OC2 | `USB_OCS2_N` |
| 6 | OUT2 | `S3_USB_VBUS_VALID` |
| 7 | OUT1 | `RT_USB_VBUS` |
| 8 | OC1 | `USB_OCS1_N` |

EN is **active-high** (TPS205xB). Do not gang OUT1/OUT2. Do not power
an MCU core from either output.

### U23-USB — TLV7031DBVR / C2869832 — SOT-23-5 (North-West; not S/L)

| Pin | Name | Net |
| --- | --- | --- |
| 1 | OUT | `USB_5V_VALID` |
| 2 | V− | `GND` |
| 3 | IN+ | `TAP_VBUS` |
| 4 | IN− | `TAP_REF` |
| 5 | V+ | `3V3` |

### U24-USB / U25-USB — SN74LVC1G08DBVR / C7666 — SOT-23-5

| Pin | Name | U24 net | U25 net |
| --- | --- | --- | --- |
| 1 | A | `USB_PRTPWR1` | `USB_PRTPWR2` |
| 2 | GND | `GND` | `GND` |
| 3 | B | `USB_5V_VALID` | `USB_5V_VALID` |
| 4 | Y | `USB_EN1` → U21.3 | `USB_EN2` → U21.4 |
| 5 | VCC | `3V3` | `3V3` |

### Passives and diodes

| Ref | Value / MPN | Pin 1 | Pin 2 |
| --- | --- | --- | --- |
| C1-PWR1 | **RETARGET** 1.0 µF 16 V X7R 0805 (JLC Basic; same land as today’s 22 µF) | `5V_USB` | `GND` |
| C2-PWR1 | KEEP 22 µF / C86816 | `5V_PROTECTED` | `GND` |
| C120-USB | ADD 22 µF 16–25 V X5R/X7R 0805 / C86816 | `5V_PROTECTED` | `GND` |
| C121-USB | 100 nF 16 V X7R 0402 | `5V_USB` | `GND` (at U22.6) |
| C122-USB | 2.2 µF 10–16 V X7R 0402/0603 | `5V0_USB_VALID` | `GND` (at U22.1) |
| C123-USB | 100 nF | `3V3` | `GND` (U23.5) |
| C124-USB | 100 nF | `3V3` | `GND` (U24.5) |
| C125-USB | 100 nF | `3V3` | `GND` (U25.5) |
| CUSBVBUS-RTC | KEEP 1 µF / C76999; **RETARGET net** | `RT_USB_VBUS` | `GND` |
| R78-USB | 100 kΩ 1 % | `5V_USB` | `USB_VBUS_DET` (U20.16) |
| R79-USB | 100 kΩ 1 % | `USB_VBUS_DET` | `GND` |
| R80-USB | **4.7 kΩ** 1 % | `5V_USB` | `GND` |
| R81-USB | 169 kΩ 1 % | `5V_USB` | `TAP_VBUS` |
| R82-USB | 100 kΩ 1 % | `TAP_VBUS` | `GND` |
| R83-USB | 100 kΩ 1 % | `3V3` | `TAP_REF` |
| R84-USB | 100 kΩ 1 % | `TAP_REF` | `GND` |
| R85-USB | 470 Ω | `USB_5V_VALID` | U9.8 GPIO15 |
| R86-USB | 4.7 kΩ 1 % | `RT_USB_VBUS` | `GND` |
| R87-USB | 10 kΩ | `S3_USB_VBUS_VALID` | `GND` |
| D3-USB | SMF5.0A / C2758488 (new des; not DVBUS-PWR1) | `5V_USB` (K) | `GND` (A) |
| D4-USB | BAT54 | DNP — do not fit | — |
| DVBUS-PWR1 | SMF5.0A leftover | **DELETE** | |

U20 pin 16 `VBUS_DET` ← `USB_VBUS_DET` (already in PIN-CONTRACT G2).
U6 N6 ← `RT_USB_VBUS`. U9.8 ← R85.

## BOM delta (validity island only)

| Ref | MPN | LCSC | Class | Note |
| --- | --- | --- | --- | --- |
| U22-USB | TPS7A2550DRVR | C2876265 | Extended | 147 stock 2026-08-29 |
| U21-USB | TPS2052BDR | C130049 | Extended | already reserved |
| U23-USB | TLV7031DBVR | C2869832 | Extended | push-pull, 3 µs |
| U24, U25 | SN74LVC1G08DBVR | C7666 | Extended, high stock | |
| D3-USB | SMF5.0A | C2758488 | — | new clamp |
| D4-USB | BAT54 | any Basic | DNP | |
| C1-PWR1 | 1.0 µF 16 V X7R 0805 | JLC Basic | RETARGET | |
| C120-USB | 22 µF (same family as C2) | C86816 | Basic | |
| C121–C125 | 100 nF / 2.2 µF ceramics | Basic | | |
| R78, R79, R82–R84 | 100 kΩ 1 % 0402 | Basic | | |
| R80, R86 | 4.7 kΩ 1 % 0402 | Basic | | |
| R81 | 169 kΩ 1 % 0402 | Basic | | |
| R85 | 470 Ω 0402 | Basic | | |
| R87 | 10 kΩ 0402 | Basic | | |

No consigned-only part.

## Ship path

1. **Already named in this repository:** `F6_VALIDITY_SOURCE = 5V0_USB_VALID`,
   MPN, nets, clocks, capacitor correction.
2. Agent: place the netlist on the disposable hub EasyEDA project
   (never `64325d0e`), one visual stage at a time, through the mutation
   gate.
3. Agent: retarget C1 to 1.0 µF, add C120, delete DVBUS-PWR1, add D3.
4. Captain: no part-pick remains. Captain acts only if a later lane
   wants to shave F6-A (omit the switch) — that is a different letter.
5. Shipped stamp: EasyEDA semantic read-back shows U22 OUT =
   `5V0_USB_VALID` = U21 IN, and the three clocks still match this
   file.
