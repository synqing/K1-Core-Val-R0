# F6_VALIDITY_SOURCE — candidate comparison and bind

Authority for the close, netlist, clocks and BOM is **`H0f-CLOSE.md`**.
This file is the comparison appendix.

```text
F6_VALIDITY_SOURCE = 5V0_USB_VALID
GENERATOR = U22-USB TPS7A2550DRVR / C2876265
TOPOLOGY = high-Vin 5.0 V LDO from raw 5V_USB
KILL_B_COMPARATOR = U23-USB TLV7031DBVR / C2869832
KILL_B_AND = U24-USB + U25-USB SN74LVC1G08DBVR / C7666
ENVELOPE = CLOSED_NAMED
H0f = H0f-CLOSE.md
```

No existing G2.1 rail qualifies. That remains true.

## Why a regulator, not an OVP cutoff

Legal Type-C vSafe5V DC reaches **5.50 V**. NXP `USB_OTG1_VBUS` recommended
and absolute maximum is also **5.50 V**. A hard OVLO at or below 5.50 V
would drop a legal host. An OVLO above 5.50 V (TPD1S514 class, NCP349 5.68 V,
or the existing eFuse at 6.01 V) would pass a voltage the RT pin must not
see. Cutoff cannot close both boxes. The rail must **regulate**.

## Candidates (real LCSC hits, 2026-08-29)

| MPN / topology | LCSC | Vin | Iout | VDO / trip | Verdict |
| --- | --- | --- | --- | --- | --- |
| **TPS7A2550DRVR** | C2876265 | 2.4–**18 V** | 300 mA | **105 mV max @ 50 mA** (340 mV @ 300 mA) | **WIN** |
| AP2204K-5.0TRG1 | C112031 | 24 V | 200 mA | 3.3 V sibling 420–500 mV; 5.0 V not proved | FAIL vs 4.40 V |
| XC6216B502MR-G | C2962429 | 28 V | 150 mA | **1.3 V @ 100 mA** | FAIL |
| AMS1117 / NCP1117-5.0 | — | — | — | ~1.1–1.3 V | FAIL |
| AP7361C-50 | — | **6 V** | 1 A | low | FAIL (SMF clamp ≈ 9 V) |
| NCP718AMT500TBG | — | 24 V | 300 mA | 380 mV max @ 300 mA; stock 5 | lose to TPS7A25 |
| AP7375Q-50 | — | 45 V | 300 mA | 350 mV typ @ 100 mA | lose to 105 mV @ 50 mA |
| TPD1S514 / NCP349 | — | — | — | OVP 5.7–6.2 V | FAIL (passes 5.50 V to N6) |
| TPS229xx / AP2280 | — | often 5.5–6 V | — | no regulation | FAIL |
| Comparator + PFET | — | — | — | still a cutoff | FAIL |
| `5V_PROTECTED` | existing | follows OVLO **6.01 V** | — | — | FAIL |
| `5V_USB` raw | existing | unbounded transient | — | — | FAIL as switch IN |

## Winner — TPS7A2550DRVR

Authority: `datasheets/D5i-TI-TPS7A25.pdf` SBVS372C, SHA-256
`d0116d16cb8e86050457b4a158b2837ecc378bd818ebef713f699e7d74028a5e`.
LCSC C2876265, WSON-6-EP 2×2, Extended, stock **147** (LCSC 2026-08-29).

Fixed DRV pin 2 is **NC** (tie GND). It is not NR/SS and not FB.

C1-PWR1 1.0 µF **is** CIN. C121 is 100 nF HF only. C122 2.2 µF on OUT.

KILL-B: R81 = **169 kΩ**, R82 = 100 kΩ, VTH nom **4.439 V** (worst
4.252–4.630 V). R80 = **4.7 kΩ**. GPIO15 ← `USB_5V_VALID`, not OUT2.

Clocks (5.50 V start, C_raw 1.2 µF): **1.45 ms / 28 ms / 2.60 ms**.
See `H0f-CLOSE.md`.
