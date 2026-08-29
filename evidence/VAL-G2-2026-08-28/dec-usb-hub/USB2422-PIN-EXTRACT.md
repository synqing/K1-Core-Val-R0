# USB2422 Pin Extract — DS00001726B

Source: `datasheets/D1-USB2422-DS00001726B.pdf`  
Captured: 2026-08-29  
Package: SQFN-24 (4 mm × 4 mm, exposed pad VSS)

---

## 2.1 All 24 Pins — by Number

| Pin # | Symbol | Buffer Type | Function Summary |
|-------|--------|-------------|-----------------|
| 1 | VDD33 | PWR | 3.3 V supply. Requires 0.1 µF low-ESR cap to VSS as close as possible to pin. |
| 2 | USBDM_DN2 / PRT_DIS_M2 | IO-U | Downstream port 2 D−; strap tie to VDD33 (with pin 5) to disable port 2. |
| 3 | USBDM_DN1 / PRT_DIS_M1 | IO-U | Downstream port 1 D−; strap tie to VDD33 (with pin 4) to disable port 1. |
| 4 | USBDP_DN1 / PRT_DIS_P1 | IO-U | Downstream port 1 D+; strap tie to VDD33 (with pin 3) to disable port 1. |
| 5 | USBDP_DN2 / PRT_DIS_P2 | IO-U | Downstream port 2 D+; strap tie to VDD33 (with pin 2) to disable port 2. |
| 6 | NC | IPD | No connect (internal pull-down). Treat as NC or tie to GND. No signal routing to this pin. |
| 7 | PRTPWR1 / BC_EN1 | O12 / IPD | Port 1 power enable (active-high output). Strap: sampled at RESET_N negation — pull high (10 kΩ) to enable BC on port 1. |
| 8 | OCS1_N | IPU | Over-current sense port 1. Active-low input; internal pull-up to VDD33. |
| 9 | VDD33 | PWR | 3.3 V supply. **Critical:** requires 1.0 µF low-ESR cap to VSS as close as possible to pin 9. |
| 10 | CRFILT | — | VDD core regulator filter. Requires 1.0 µF low-ESR cap to VSS. |
| 11 | PRTPWR2 | O12 | Port 2 power enable (active-high output). |
| 12 | OCS2_N | IPU | Over-current sense port 2. Active-low input; internal pull-up to VDD33. |
| 13 | SMBDATA / NON_REM1 | I/OSD12 | SMBus data. Strap (NON_REM1): sampled at RESET_N negation — see NON_REM table. |
| 14 | SMBCLK / CFG_SEL | I/OSD12 | SMBus clock. Strap (CFG_SEL): latched on rising edge of RESET_N; determines hub config method (SMBus vs strap). |
| 15 | RESET_N | IS | Active-low reset input (Schmitt). Minimum active-low pulse: 1 µs. |
| 16 | VBUS_DET | I | Upstream VBUS detection. Monitors VBUS to assert internal D+ pull-up (connect event). Detachable: connect via 2×100 kΩ voltage divider. Self-powered + permanent host: connect to VDD33. |
| 17 | SUSP_IND / LOCAL_PWR / (NON_REM0) | I/O12 | Multi-function: NON_REM0 at reset (strap); SUSP_IND after reset (hub active indicator). LOCAL_PWR via SMBus config. **Never tie directly to VDD33.** |
| 18 | VDD33 | PWR | 3.3 V supply (third rail pad). |
| 19 | USBDM_UP | IO-U | Upstream USB D−. |
| 20 | USBDP_UP | IO-U | Upstream USB D+. |
| 21 | XTALOUT / CLKIN_EN | OCLKx | Crystal output (1.2 V p-p, weak drive). Leave unconnected if using external clock source. |
| 22 | XTALIN / CLKIN | ICLKx | Crystal input or external 24 MHz clock. |
| 23 | PLLFILT | — | PLL regulator filter. Up to 0.1 µF low-ESR cap to VSS; may be left unconnected. |
| 24 | RBIAS | I-R | USB transceiver bias. Connect 12.0 kΩ ±1% resistor from this pin to GND. |
| ePad | VSS | GND | Exposed pad. **Only VSS for the device.** Must be connected to ground with multiple vias. |

---

## D9 — RBIAS

Value: **12.0 kΩ ±1%** from RBIAS (pin 24) to GND. Sets internal transceiver bias. Tolerance is critical.

---

## D10 — CRFILT / PLLFILT Decoupling

| Pin | Requirement |
|-----|------------|
| CRFILT (pin 10) | 1.0 µF low-ESR cap to VSS. Required for proper operation. |
| PLLFILT (pin 23) | Up to 0.1 µF low-ESR cap to VSS; may be left unconnected. |

---

## D11 — Crystal

XTALIN/CLKIN (pin 22) and XTALOUT (pin 21). **24 MHz** crystal resonator or external 24 MHz clock input.  
If external clock drives XTALIN/CLKIN, leave XTALOUT unconnected (or use with appropriate caution).

---

## D12 — VBUS_DET

Pin 16. Hub monitors VBUS_DET to determine when to assert the internal D+ pull-up (connect event).

- **Detachable hub:** connect to upstream VBUS via 2:1 voltage divider (2×100 kΩ suggested).
- **Self-powered, permanently attached host:** connect to dedicated host control output, or to VDD33.

Loss of VBUS_DET transitioning low is **not listed** in the datasheet as a PRTPWRx PORT OFF condition (see D17 below). VBUS_DET controls the USB D+ pull-up, not the downstream power switch state.

---

## D13 — NON_REM Table

Pins 13 (NON_REM1) and 17 (NON_REM0), sampled together at RESET_N negation:

| NON_REM[1:0] | Meaning |
|-------------|---------|
| 00 | All ports are removable |
| 01 | Port 1 is non-removable |
| 10 | Ports 1 and 2 are non-removable |
| 11 | Reserved |

Strap resistor values: 47–100 kΩ pull-up/pull-down for I/O type buffers; 10 kΩ for IPD type.

---

## D14 — CFG_SEL

Pin 14 (SMBCLK/CFG_SEL). The logic state is internally latched on the rising edge of RESET_N. Determines the hub configuration method (strap vs SMBus — see Table 4-1 of DS00001726B).  
SMBus slave address: 0101100b.

---

## D15 — Buffer Type Descriptions

| Code | Description |
|------|-------------|
| I/O | Input/Output |
| IPD | Input with internal weak pull-down resistor |
| IPU | Input with internal weak pull-up resistor |
| IS | Input with Schmitt trigger |
| I/O12 | Input/Output, 12 mA sink and 12 mA source |
| ICLKx | Crystal clock input |
| OCLKx | Crystal clock output |
| I-R | RBIAS (analog) |
| IO-U | Analogue Input/Output per USB specification |

---

## D16 — Strap Pin Configuration Summary

| Strap | Pins | Buffer | Resistor |
|-------|------|--------|----------|
| NON_REM[1:0] | 17 (NON_REM0), 13 (NON_REM1) | I/O | 47–100 kΩ |
| BC_EN1 | 7 (PRTPWR1/BC_EN1) | IPD | 10 kΩ (built-in pull-down; external pull-up for BC_EN1=1) |
| PRT_DIS | 2,3,4,5 | IO-U | Tie both D+/D− to VDD33 to disable port |
| CFG_SEL | 14 | I/OSD12 | 47–100 kΩ |

---

## D17 — PRTPWR OFF Conditions (from DS00004196 Hardware Checklist)

PRTPWRx is in PORT ON state and will transition to **PORT OFF only if:**
1. An overcurrent event is sensed on OCSx_N pin.
2. A command from the USB host is received which instructs the hub to disable power.
3. The hub is reset or experiences a POR event.

**Explicitly NOT listed:** loss of VBUS_DET does not appear as a PRTPWRx PORT OFF condition in the checklist or datasheet. VBUS_DET controls USB device attachment signalling (D+ pull-up), not the downstream power switch.

---

## D18 — ESD and Supply Current Notes

**ESD:** "ESD protection up to 6 kV on all USB pins" (DS00001726B features list). This is the on-chip protection rating. The standard referenced is **not** IEC 61000-4-2 (which uses a different test circuit and waveform). External ESD protection devices (see DS00004196 §4.2) may be required for IEC 61000-4-2 compliance.

**IHCH2 supply current (Hi-Speed host, 2 downstream ports):**
- Minimum: 70 mA
- Maximum: 89 mA
- Note: "Current measured during peak USB traffic and does not reflect the average current draw." (Note 5-8)

**Other supply currents for reference:**
| Symbol | Min | Max | Condition |
|--------|-----|-----|-----------|
| ICCINTHS | 40 | 45 mA | Unconfigured, HS host |
| IHCH1 | 47 | 58 mA | HS host, 1 downstream port |
| IHCH2 | 70 | 89 mA | HS host, 2 downstream ports |
| ICSBY | — | 425 µA | Suspend (commercial); 1000 µA industrial |
