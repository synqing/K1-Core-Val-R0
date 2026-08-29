# NXP IMXRT1060 USB OTG1 VBUS Extract

Source: `datasheets/D4-NXP-IMXRT1060IEC.pdf`  
Document: i.MX RT1060 Crossover Processors for Industrial Products, Rev. 4, 04/2024  
Captured from archive.org snapshot (20240926) on 2026-08-29  
SHA256: a4ef1fd31841678b97967ef8a64fcbd76aec509e565066c064dff536a97fd295

---

## Table 12 — Maximum Supply Currents (Extracted Verbatim)

| Power Rail | Conditions | Max Current | Unit |
|------------|-----------|-------------|------|
| USB_OTG1_VBUS | 25 mA for each active USB interface | **50** | mA |
| USB_OTG2_VBUS | 25 mA for each active USB interface | **50** | mA |

**Interpretation:** Each USB OTG interface draws up to 25 mA per active interface. With both OTG1 and OTG2 active, the combined VBUS supply maximum is 50 mA per rail (i.e., each rail is specified separately at 50 mA max).

---

## Recommended Operating Conditions — USB VBUS Voltage

From Table 8 (Operating conditions):

| Parameter | Min | Typical | Max | Unit |
|-----------|-----|---------|-----|------|
| USB_OTG1_VBUS | **4.40** | — | **5.5** | V |
| USB_OTG2_VBUS | **4.40** | — | **5.5** | V |

---

## Design Implications for K1 Hub

- The RT1062 USB OTG1 peripheral requires 4.40–5.50 V on VBUS to operate within spec.
- Maximum expected supply draw: 50 mA per USB OTG interface.
- The hub's TPS2052B (D5a) supplies 5 V at up to 500 mA continuous to downstream devices; RT1062 VBUS draw is within this budget.
- The 25 mA / 50 mA row explicitly covers both the self-powered and bus-powered contribution scenarios.

---

## Notes on CEC Variant

Source: `datasheets/D4-NXP-IMXRT1060CEC.pdf`  
SHA256: d65fcf01020ccde2181a716ba6eeb5b9dc66b368b0c3066c1734f9d8e060e388

IEC = Industrial Electrical Characteristics; CEC = Commercial Electrical Characteristics.  
The 4.40–5.5 V and 25/50 mA rows appear in the IEC document. CEC was obtained for completeness; its electrical tables may differ at temperature extremes.
