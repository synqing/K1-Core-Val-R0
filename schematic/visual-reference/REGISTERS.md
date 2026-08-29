# K1-CORE-VAL-R0 — Visual Schematic Reference Package · Registers

```text
STATUS   = STUDY_INPUT / BINDING=NO — visual construction reference, NOT an EasyEDA schematic
AUTHOR   = the Captain is the sole EasyEDA schematic author; nothing here mutates the project
SOURCES  = g22/G2.2-HOLD-REOPEN.source.txt (SCH_PAGE, updateTime 1787976488933)
           anchors/hub-export-v3.epro2 (symbol library) · PIN-CONTRACT.md · H0f-CLOSE.md
PARSER   = V3 typed records; log-replay (max ticket, tombstone=delete); pins bound to
           labelled stubs at exact coincidence; rotation composes CW per 90 in the stored
           frame (oracle-proven: 55/60 U6 agreement; all 5 disagreements are hub-era renames
           or the M8 hub rewire); isMirror unused on the page (0 instances)
VERDICT  = reconciliation PASS (0 fails) — Phase B generated
DATE     = 2026-08-29
```

## 1. Component count per domain

| Domain | Title | Components |
|---|---|---:|
| D01 | POWER ENTRY + PROTECTION | 71 |
| D02 | POWER CONVERSION | 27 |
| D03 | RT1062 CORE + POWER | 42 |
| D04 | RT1062 BOOT + CLOCK + DEBUG | 21 |
| D05 | ESP32-S3 RADIO + SERVICE + K1BR | 21 |
| D06 | AUDIO | 32 |
| D07 | NFC | 27 |
| D08 | MOTION | 10 |
| D09 | LED | 19 |
| D10 | DEBUG / RECOVERY / VALIDATION | 17 |
| **Total** | | **287** |

## 2. Reference-designator inventory (assignment + overrides)

**D01** (71): C1-PWR1 C100-USB C101-USB C102-USB C103-USB C104-USB C105-USB C106-USB C107-USB C108-USB C109-USB C110-USB C120-USB C121-USB C122-USB C123-USB C124-USB C125-USB C2-PWR1 C3-PWR1 C4-PWR1 C67-PWR1 CINA_DIFF-PWR1 D1-PWR1 D3-USB J1-PWR1 J1-USB4105-RETIRED R1-PWR1 R2-PWR1 R3-PWR1 R4-PWR1 R63-PWR1 R64-PWR1 R65-PWR1 R66-PWR1 R67-PWR1 R77-USB R78-USB R79-USB R80-USB R81-USB R82-USB R83-USB R84-USB R85-USB R86-USB R87-USB R88-USB R89-USB R90-USB R91-USB RCC1-PWR1 RCC1B-PWR1 RCC1S-PWR1 RCC2-PWR1 RCC2B-PWR1 RCC2S-PWR1 RINA_N-PWR1 RINA_P-PWR1 RSH1-PWR1 RUSB_DN-PWR1 RUSB_DP-PWR1 U1-PWR1 U2-PWR1 U20-USB U21-USB U22-USB U23-USB U24-USB U25-USB Y3-USB

**D02** (27): C10-PWR2 C11-PWR2 C12-PWR2 C13-PWR2 C14-PWR2 C15-PWR2 C16-PWR2 C17-PWR2 C5-PWR2 C6-PWR2 C7-PWR2 C8-PWR2 C9-PWR2 CMICREG-PWR2 FB1-PWR2 FB2-PWR2 FB3-PWR2 L1-PWR2 Q1-PWR2 R5-PWR2 R6-PWR2 R7-PWR2 R75-PWR2 R9-PWR2 U17-PWR2 U3-PWR2 U5-PWR2

**D03** (42): C18-RTC C19-RTC C20-RTC C21-RTC C22-RTC C23-RTC C24-RTC C25-RTC C26-RTC C27-RTC C28-RTC C29-RTC C30-RTC C31-RTC C32-RTC C33-RTC C34-RTC C69-RTC C70-RTC C71-RTC C72-RTC C73-RTC C74-RTC C75-RTC C76-RTC C77-RTC C78-RTC C79-RTC C80-RTC C81-RTC C82-RTC C83-RTC C84-RTC C85-RTC C86-RTC C87-RTC C88-RTC C89-RTC CUSBVBUS-RTC L4-RTC R70-RTC U6-RTC

**D04** (21): C35-RTDBG C36-RTDBG C37-RTDBG C38-RTDBG J4-RTDBG J5-RTDBG R10-RTC R11-RTC R12-RTC R13-RTDBG R14-RTDBG R15-RTDBG R16-RTDBG R17-RTDBG R18-RTDBG R68-RTDBG R69-RTDBG SW1-RTC U7-RTC U8-RTDBG Y1-RTDBG

**D05** (21): C39-ESP C40-ESP C41-ESP C42-ESP C45-ESP FB6-ESP J6-ESP R19-ESP R20-ESP R23-ESP R24-ESP R25-ESP R26-ESP R27-ESP RUSB_S3_DM_TUNE RUSB_S3_DP_TUNE SW2-ESP SW3-ESP TP1-ESP TP2-ESP U9-ESP

**D06** (32): C46-AUD C47-AUD C48-AUD C49-AUD C50-AUD C51-AUD C52-AUD C53-AUD C90-AUD C91-AUD FB5-AUD J8-AUD J9-AUD R28-AUD R29-AUD R31-AUD R32-AUD R33-AUD R34-AUD R35-AUD R36-AUD R37-AUD R38-AUD R39-AUD R40-AUD R41-AUD TP3-AUD TP4-AUD TP5-AUD TP7-AUD TP8-AUD U11-AUD

**D07** (27): C54-NFC C55-NFC C56-NFC C57-NFC C58-NFC C59-NFC C60-NFC C61-NFC C910-NFC C911-NFC C912-NFC C92-NFC C93-NFC C94-NFC C95-NFC C96-NFC C97-NFC C98-NFC C99-NFC CVDR1-NFC CVDR2-NFC J10-NFC L2-NFC R42-NFC R76-NFC U12-NFC Y2-NFC

**D08** (10): C62-MOT C63-MOT CMOT-BULK R44-MOT R45-MOT R46-MOT R47-MOT R48-MOT R49-MOT U13-MOT

**D09** (19): C64-LED C65-LED J2-LED J3-LED R51-LED R52-LED R53-LED R54-LED RILIM-LED RLED_ENL_PD-LED RLED_ENR_PD-LED RLED_PD0-LED RLED_PD1-LED RNTC_L-LED RNTC_R-LED RT1-LED RT2-LED U14-LED U15-LED

**D10** (17): C66-VAL J11-VAL J12-USB Q2-VAL R55-VAL R56-VAL R57-VAL R58-VAL R59-VAL R60-VAL R61-VAL R62-VAL R94-USB R95-USB SW4-VAL TP6-VAL U16-VAL

Overrides (function over suffix, each with cause):

| Designator | Domain | Cause |
|---|---|---|
| R10-RTC | D04 | BOOT_MODE0 strap |
| R11-RTC | D04 | BOOT_MODE1 strap |
| R12-RTC | D04 | POR_B pull-up |
| SW1-RTC | D04 | RT_RESET_REQ_N reset switch |
| U7-RTC | D04 | reset supervisor: POR_B / RT_RESET_REQ_N |
| J12-USB | D10 | G6 XOR recovery header |
| R94-USB | D10 | G6 XOR 0R FIT hub DN2 path |
| R95-USB | D10 | G6 XOR 0R DNP to J12 |
| CMOT-BULK | D08 | U13-MOT bulk decoupling, 3V3/GND at the sensor |
| RUSB_S3_DP_TUNE | D05 | G5 S3 DP series tune at GPIO20 |
| RUSB_S3_DM_TUNE | D05 | G5 S3 DM series tune at GPIO19 |

## 3. Cross-domain port register (48 nets — every port appears on every touching sheet)

| Net | Class | Driver | Kind | Domains (endpoints) |
|---|---|---|---|---|
| AUDIO_BCLK_RT | clock | D03 | out | D03(1) · D06(1) |
| AUDIO_DOUT | audio | D06 | out | D03(1) · D06(1) |
| AUDIO_FSYNC_RT | audio | D03 | out | D03(1) · D06(1) |
| AUDIO_MCLK | clock | D10 | bidi | D06(5) · D10(1) |
| AUDIO_MCLK_RT | clock | D03 | out | D03(1) · D06(1) |
| BOOT_MODE0 | ctl | D04 | out | D03(1) · D04(1) · D10(1) |
| BOOT_MODE1 | ctl | D04 | out | D03(1) · D04(1) |
| ESP_UART0_TX | sig | D05 | out | D05(2) · D10(1) |
| FLEXSPI_D0 | sig | D03 | bidi | D03(1) · D04(1) |
| FLEXSPI_D1 | sig | D03 | bidi | D03(1) · D04(1) |
| FLEXSPI_SCLK | i2c | D03 | out | D03(1) · D04(1) |
| FLEXSPI_SS0 | sig | D03 | out | D03(1) · D04(1) |
| I2C_SCL | i2c | D05 | bidi | D01(1) · D05(1) · D06(2) · D07(1) · D08(3) |
| I2C_SDA | i2c | D05 | bidi | D01(2) · D05(1) · D06(2) · D07(1) · D08(3) |
| K1BR_CS_RT | k1br | D03 | out | D03(1) · D05(1) |
| K1BR_IRQ_RT | k1br | D05 | out | D03(1) · D05(1) |
| K1BR_MISO_RT | k1br | D05 | out | D03(1) · D05(1) |
| K1BR_MOSI_RT | k1br | D03 | out | D03(1) · D05(1) |
| K1BR_SCK_RT | k1br | D03 | out | D03(1) · D05(1) |
| LED_D0_3V3 | led | D03 | out | D03(1) · D09(2) |
| LED_D1_3V3 | led | D03 | out | D03(1) · D09(2) |
| LED_PWR_L_EN | ctl | D09 | out | D02(1) · D09(1) |
| LED_PWR_R_EN | ctl | D09 | out | D02(1) · D09(1) |
| LED_THERM_L | led | D09 | out | D03(1) · D09(2) |
| LED_THERM_R | led | D09 | out | D03(1) · D09(2) |
| LPUART1_RX | sig | D04 | out | D03(1) · D04(1) |
| LPUART1_TX | sig | D03 | out | D03(1) · D04(1) |
| MIC_PWR_EN_N | audio | D03 | out | D02(2) · D03(1) |
| MOTION_INT_RT | ctl | D08 | out | D03(1) · D08(1) |
| NFC_5V | nfc | D02 | out | D02(3) · D07(4) |
| NFC_IRQ | ctl | D07 | out | D05(1) · D07(1) |
| OPT_BOOT_REC_RT | ctl | D10 | out | D03(1) · D10(1) |
| PDM_CLK_RT | audio | D03 | out | D03(1) · D06(1) |
| PDM_DAT_RT | audio | D06 | out | D03(1) · D06(1) |
| POR_B | ctl | D04 | out | D03(1) · D04(3) · D10(1) |
| RT_PWR_VALID | ctl | D10 | out | D05(1) · D10(2) |
| RT_USB_VBUS | sig | D01 | out | D01(3) · D03(2) |
| S3_POR_REQ | ctl | D05 | out | D05(1) · D10(1) |
| SWD_SWCLK | clock | D04 | out | D03(1) · D04(1) |
| SWD_SWDIO | sig | D04 | bidi | D03(1) · D04(1) |
| TPS2561_ILIM | test | D09 | out | D02(1) · D09(1) |
| USB_5V_VALID | ctl | D01 | out | D01(5) · D05(1) |
| USB_DM_DN1 | usb | D01 | bidi | D01(1) · D03(1) |
| USB_DM_DN2 | usb | D01 | bidi | D01(1) · D05(1) |
| USB_DP_DN1 | usb | D01 | bidi | D01(1) · D03(1) |
| USB_DP_DN2 | usb | D01 | bidi | D01(1) · D05(1) · D10(2) |
| XTALI | clock | D04 | out | D03(1) · D04(3) |
| XTALO | clock | D03 | out | D03(1) · D04(1) |

## 4. Rail register (23)

| Rail | Domains | Endpoints |
|---|---|---:|
| +5V_LED_L | D02 D09 | 5 |
| +5V_LED_R | D02 D09 | 5 |
| 1V15_CORE | D03 | 18 |
| 3V3 | D01 D02 D03 D04 D05 D06 D07 D08 D09 D10 | 101 |
| 3V3_MIC | D02 D06 | 3 |
| 3V3_MIC_FLEX | D06 | 3 |
| 3V3_MIC_REG | D02 | 4 |
| 3V3_S3_FILTERED | D05 | 2 |
| 5V0_USB_VALID | D01 | 4 |
| 5V_LED_L_SW | D02 | 2 |
| 5V_LED_R_SW | D02 | 2 |
| 5V_PROTECTED | D01 | 7 |
| 5V_SYS | D01 D02 | 13 |
| 5V_USB | D01 | 14 |
| GND | D01 D02 D03 D04 D05 D06 D07 D08 D09 D10 | 249 |
| NVCC_PLL_1V1 | D03 | 3 |
| USB_CC1 | D01 | 3 |
| USB_CC1_ADC_TAP | D01 | 2 |
| USB_CC2 | D01 | 3 |
| USB_CC2_ADC_TAP | D01 | 2 |
| VDD_HIGH_CAP | D03 | 3 |
| VDD_SNVS_CAP | D03 | 3 |
| VDD_USB_CAP | D03 | 3 |

## 5. Net reconciliation summary

- named nets with pins: 172 · cross-domain: 48 · rails: 23 · single-domain: 101
- mechanical FAIL checks run: PORT_DIR coverage both ways, driver-touches-net, domain-set drift, count integrity — **PASS**

## 6. Orphan list

Named wires reaching no pins: USB_NON_REM0 · USB_NON_REM1

Single-endpoint nets (dangling by design or by capture gap): LED_FAULT_L_N · LED_FAULT_R_N · MOTION_INT_S3 · RT_I2C_SCL · RT_I2C_SDA · RT_USB_AUD_STRAP_IOMUX_TBD · S3_I2C_SCL · S3_I2C_SDA · USB_EFUSE_ILIM · USB_XTALIN

## 7. Unresolved / TBD register

| # | Item | Authority | Status |
|---|---|---|---|
| T1 | U20-USB support pins UNWIRED in capture: 1 VDD33, 10 CRFILT, 22 XTALIN, 23 PLLFILT, 24 RBIAS | PIN-CONTRACT G2 specifies R77/C100/C101/Y3 wiring | TBD |
| T2 | Y3-USB crystal fully unwired (0/4); C102/C103 stubs dangle near it | PIN-CONTRACT G2: Y3 24 MHz + C102/C103 | TBD |
| T3 | J1-PWR1 GT-USB-7005A placed, 0/28 pins wired; J1-USB4105-RETIRED still holds 5V_USB/CC/USB_DP_J1/USB_DN_J1 | PIN-CONTRACT G3 retarget mid-migration; D050_BOUND = GT-USB-7005A | TBD |
| T4 | USB_NON_REM0 / USB_NON_REM1 named wires reach no pins (strap wiring pending; R88/R89 half-wired) | PIN-CONTRACT G2 pins 13/17 straps | TBD |
| T5 | J12-USB recovery header unwired (0/4); R95-USB 0R DNP unwired | PIN-CONTRACT G6 XOR default | TBD |
| T6 | U6-RTC ball N5 (VSS) unbound in capture — GND stub missing (was bound in pre-hub oracle) | oracle disagreement N5 | VERIFY |
| T7 | U22-USB pin 3 PG unwired — MATCHES contract (PG = NC by design) | PIN-CONTRACT G4c | VERIFIED-NC |
| T8 | C105-USB one side unwired (1/2) | VDD33 decoupling set G2 | TBD |
| T9 | U1-PWR1.9 ILM bound to USB_DP_UP; R1-PWR1 ILIM resistor dangles on USB_EFUSE_ILIM | net_pins scan — eFuse ILM node on the USB HS pair | VERIFY |
| T10 | RT_I2C_SDA / RT_I2C_SCL single-endpoint (R44/R46 RT side dangles — no U6 ball bound) | net_pins scan; RT I2C bridge default expects a bound ball | TBD |
| T11 | IOMUX-TBD strap nets dangle by design: PWR_ENTRY_PG_RT_IOMUX_TBD, RT_USB_AUD_STRAP_IOMUX_TBD, MOTION_INT_S3, USB_CC*_ADC_TAP RT side | D-031: pins after placement freeze | TBD |
| T12 | Single-endpoint status/fault nets: LED_FAULT_L_N, LED_FAULT_R_N, BUCK_PG(R75 far side), USB_EFUSE_ILIM | net_pins single-endpoint scan | VERIFY |

## 8. Capture-vs-contract deltas (USB island, machine-diffed)

| Ref | Contract | Capture |
|---|---|---|
| U20-USB.1 | 3V3 | None |
| U20-USB.10 | CRFILT(C100 1uF) | None |
| U20-USB.11 | USB_PRTPWR2 | GND |
| U20-USB.22 | XTALIN(Y3) | None |
| U20-USB.23 | PLLFILT(C101 100nF) | None |
| U20-USB.24 | RBIAS(R77 12k->GND) | None |
| U23-USB.2 | GND | USB_EN2 |
| U23-USB.5 | 3V3 | GND |
| U25-USB.1 | USB_PRTPWR2 | GND |
| U25-USB.5 | 3V3 | USB_EN2 |
| R85-USB.2 | GPIO15 side (distinct node through 470R) | USB_5V_VALID |
| R87-USB.1 | S3_USB_VBUS_VALID | None |
| R87-USB.2 | GND | None |
| C123-USB.1 | 3V3 | GND |
| C125-USB.1 | 3V3 | USB_EN2 |
| Y3-USB.1 | USB_XTALIN | None |
| Y3-USB.2 | GND | None |
| Y3-USB.3 | USB_XTALOUT | None |
| Y3-USB.4 | GND | None |

Same-net series elements (router can bypass): R94-USB · R85-USB · R90-USB · C123-USB

## 9. Per-domain port tables

### D01 · POWER ENTRY + PROTECTION

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| I2C_SCL | i2c | bidi | D05/D06/D07/D08 | U2-PWR1.5 |
| I2C_SDA | i2c | bidi | D05/D06/D07/D08 | R4-PWR1.1, U2-PWR1.4 |
| RT_USB_VBUS | sig | driver | D03 | C109-USB.2, R86-USB.1, U21-USB.7 |
| USB_5V_VALID | ctl | driver | D05 | R85-USB.1, R85-USB.2, U23-USB.1, U24-USB.3, U25-USB.3 |
| USB_DM_DN1 | usb | driver | D03 | U20-USB.3 |
| USB_DM_DN2 | usb | driver | D05 | U20-USB.2 |
| USB_DP_DN1 | usb | driver | D03 | U20-USB.4 |
| USB_DP_DN2 | usb | driver | D05/D10 | U20-USB.5 |

Rails touched: 3V3 · 5V0_USB_VALID · 5V_PROTECTED · 5V_SYS · 5V_USB · GND · USB_CC1 · USB_CC1_ADC_TAP · USB_CC2 · USB_CC2_ADC_TAP

### D02 · POWER CONVERSION

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| LED_PWR_L_EN | ctl | consumer | D09 | U17-PWR2.4 |
| LED_PWR_R_EN | ctl | consumer | D09 | U17-PWR2.5 |
| MIC_PWR_EN_N | audio | consumer | D03 | Q1-PWR2.1, R9-PWR2.1 |
| NFC_5V | nfc | driver | D07 | C16-PWR2.1, C17-PWR2.1, FB3-PWR2.2 |
| TPS2561_ILIM | test | consumer | D09 | U17-PWR2.7 |

Rails touched: +5V_LED_L · +5V_LED_R · 3V3 · 3V3_MIC · 3V3_MIC_REG · 5V_LED_L_SW · 5V_LED_R_SW · 5V_SYS · GND

### D03 · RT1062 CORE + POWER

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| AUDIO_BCLK_RT | clock | driver | D06 | U6-RTC.G12 |
| AUDIO_DOUT | audio | consumer | D06 | U6-RTC.H12 |
| AUDIO_FSYNC_RT | audio | driver | D06 | U6-RTC.H11 |
| AUDIO_MCLK_RT | clock | driver | D06 | U6-RTC.J14 |
| BOOT_MODE0 | ctl | consumer | D04/D10 | U6-RTC.F11 |
| BOOT_MODE1 | ctl | consumer | D04 | U6-RTC.G14 |
| FLEXSPI_D0 | sig | driver | D04 | U6-RTC.P3 |
| FLEXSPI_D1 | sig | driver | D04 | U6-RTC.N4 |
| FLEXSPI_SCLK | i2c | driver | D04 | U6-RTC.L4 |
| FLEXSPI_SS0 | sig | driver | D04 | U6-RTC.L3 |
| K1BR_CS_RT | k1br | driver | D05 | U6-RTC.J3 |
| K1BR_IRQ_RT | k1br | consumer | D05 | U6-RTC.K11 |
| K1BR_MISO_RT | k1br | consumer | D05 | U6-RTC.K1 |
| K1BR_MOSI_RT | k1br | driver | D05 | U6-RTC.J1 |
| K1BR_SCK_RT | k1br | driver | D05 | U6-RTC.J4 |
| LED_D0_3V3 | led | driver | D09 | U6-RTC.D7 |
| LED_D1_3V3 | led | driver | D09 | U6-RTC.E7 |
| LED_THERM_L | led | consumer | D09 | U6-RTC.L12 |
| LED_THERM_R | led | consumer | D09 | U6-RTC.K12 |
| LPUART1_RX | sig | consumer | D04 | U6-RTC.L14 |
| LPUART1_TX | sig | driver | D04 | U6-RTC.K14 |
| MIC_PWR_EN_N | audio | driver | D02 | U6-RTC.J11 |
| MOTION_INT_RT | ctl | consumer | D08 | U6-RTC.L11 |
| OPT_BOOT_REC_RT | ctl | consumer | D10 | U6-RTC.M12 |
| PDM_CLK_RT | audio | driver | D06 | U6-RTC.J13 |
| PDM_DAT_RT | audio | consumer | D06 | U6-RTC.L13 |
| POR_B | ctl | consumer | D04/D10 | U6-RTC.M7 |
| RT_USB_VBUS | sig | consumer | D01 | CUSBVBUS-RTC.1, U6-RTC.N6 |
| SWD_SWCLK | clock | consumer | D04 | U6-RTC.F12 |
| SWD_SWDIO | sig | bidi | D04 | U6-RTC.E14 |
| USB_DM_DN1 | usb | bidi | D01 | U6-RTC.M8 |
| USB_DP_DN1 | usb | bidi | D01 | U6-RTC.L8 |
| XTALI | clock | consumer | D04 | U6-RTC.P11 |
| XTALO | clock | driver | D04 | U6-RTC.N11 |

Rails touched: 1V15_CORE · 3V3 · GND · NVCC_PLL_1V1 · VDD_HIGH_CAP · VDD_SNVS_CAP · VDD_USB_CAP

### D04 · RT1062 BOOT + CLOCK + DEBUG

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| BOOT_MODE0 | ctl | driver | D03/D10 | R10-RTC.1 |
| BOOT_MODE1 | ctl | driver | D03 | R11-RTC.1 |
| FLEXSPI_D0 | sig | bidi | D03 | U8-RTDBG.5 |
| FLEXSPI_D1 | sig | bidi | D03 | U8-RTDBG.2 |
| FLEXSPI_SCLK | i2c | consumer | D03 | U8-RTDBG.6 |
| FLEXSPI_SS0 | sig | consumer | D03 | U8-RTDBG.1 |
| LPUART1_RX | sig | driver | D03 | R18-RTDBG.1 |
| LPUART1_TX | sig | consumer | D03 | R17-RTDBG.1 |
| POR_B | ctl | driver | D03/D10 | J4-RTDBG.10, R12-RTC.2, U7-RTC.1 |
| SWD_SWCLK | clock | driver | D03 | R15-RTDBG.1 |
| SWD_SWDIO | sig | driver | D03 | R16-RTDBG.1 |
| XTALI | clock | driver | D03 | C35-RTDBG.1, R68-RTDBG.1, Y1-RTDBG.1 |
| XTALO | clock | consumer | D03 | R13-RTDBG.1 |

Rails touched: 3V3 · GND

### D05 · ESP32-S3 RADIO + SERVICE + K1BR

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| ESP_UART0_TX | sig | driver | D10 | J6-ESP.3, U9-ESP.37 |
| I2C_SCL | i2c | driver | D01/D06/D07/D08 | U9-ESP.38 |
| I2C_SDA | i2c | driver | D01/D06/D07/D08 | U9-ESP.39 |
| K1BR_CS_RT | k1br | consumer | D03 | R26-ESP.1 |
| K1BR_IRQ_RT | k1br | driver | D03 | R27-ESP.2 |
| K1BR_MISO_RT | k1br | driver | D03 | R25-ESP.2 |
| K1BR_MOSI_RT | k1br | consumer | D03 | R24-ESP.1 |
| K1BR_SCK_RT | k1br | consumer | D03 | R23-ESP.1 |
| NFC_IRQ | ctl | consumer | D07 | U9-ESP.4 |
| RT_PWR_VALID | ctl | consumer | D10 | U9-ESP.7 |
| S3_POR_REQ | ctl | driver | D10 | U9-ESP.6 |
| USB_5V_VALID | ctl | consumer | D01 | U9-ESP.8 |
| USB_DM_DN2 | usb | bidi | D01 | RUSB_S3_DM_TUNE.1 |
| USB_DP_DN2 | usb | bidi | D01/D10 | RUSB_S3_DP_TUNE.1 |

Rails touched: 3V3 · 3V3_S3_FILTERED · GND

### D06 · AUDIO

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| AUDIO_BCLK_RT | clock | consumer | D03 | R32-AUD.1 |
| AUDIO_DOUT | audio | driver | D03 | R37-AUD.2 |
| AUDIO_FSYNC_RT | audio | consumer | D03 | R33-AUD.1 |
| AUDIO_MCLK | clock | bidi | D10 | C52-AUD.1, J8-AUD.1, R34-AUD.2, TP3-AUD.1, U11-AUD.19 |
| AUDIO_MCLK_RT | clock | consumer | D03 | R31-AUD.1 |
| I2C_SCL | i2c | bidi | D01/D05/D07/D08 | R29-AUD.2, U11-AUD.13 |
| I2C_SDA | i2c | bidi | D01/D05/D07/D08 | R28-AUD.2, U11-AUD.12 |
| PDM_CLK_RT | audio | consumer | D03 | R40-AUD.2 |
| PDM_DAT_RT | audio | driver | D03 | R41-AUD.2 |

Rails touched: 3V3 · 3V3_MIC · 3V3_MIC_FLEX · GND

### D07 · NFC

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| I2C_SCL | i2c | bidi | D01/D05/D06/D08 | U12-NFC.30 |
| I2C_SDA | i2c | bidi | D01/D05/D06/D08 | U12-NFC.32 |
| NFC_5V | nfc | consumer | D02 | C57-NFC.1, C58-NFC.1, U12-NFC.10, U12-NFC.8 |
| NFC_IRQ | ctl | driver | D05 | U12-NFC.27 |

Rails touched: 3V3 · GND

### D08 · MOTION

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| I2C_SCL | i2c | bidi | D01/D05/D06/D07 | R46-MOT.2, R47-MOT.2, U13-MOT.1 |
| I2C_SDA | i2c | bidi | D01/D05/D06/D07 | R44-MOT.2, R45-MOT.2, U13-MOT.4 |
| MOTION_INT_RT | ctl | driver | D03 | R48-MOT.2 |

Rails touched: 3V3 · GND

### D09 · LED

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| LED_D0_3V3 | led | consumer | D03 | RLED_PD0-LED.1, U14-LED.2 |
| LED_D1_3V3 | led | consumer | D03 | RLED_PD1-LED.1, U15-LED.2 |
| LED_PWR_L_EN | ctl | driver | D02 | RLED_ENL_PD-LED.1 |
| LED_PWR_R_EN | ctl | driver | D02 | RLED_ENR_PD-LED.1 |
| LED_THERM_L | led | driver | D03 | RNTC_L-LED.2, RT1-LED.1 |
| LED_THERM_R | led | driver | D03 | RNTC_R-LED.2, RT2-LED.1 |
| TPS2561_ILIM | test | driver | D02 | RILIM-LED.1 |

Rails touched: +5V_LED_L · +5V_LED_R · 3V3 · GND

### D10 · DEBUG / RECOVERY / VALIDATION

| Net | Class | Role | Counterpart | Local endpoints |
|---|---|---|---|---|
| AUDIO_MCLK | clock | driver | D06 | R57-VAL.2 |
| BOOT_MODE0 | ctl | consumer | D03/D04 | R61-VAL.2 |
| ESP_UART0_TX | sig | consumer | D05 | R58-VAL.2 |
| OPT_BOOT_REC_RT | ctl | driver | D03 | R55-VAL.2 |
| POR_B | ctl | consumer | D03/D04 | R59-VAL.2 |
| RT_PWR_VALID | ctl | driver | D05 | R62-VAL.2, U16-VAL.1 |
| S3_POR_REQ | ctl | consumer | D05 | R60-VAL.1 |
| USB_DP_DN2 | usb | bidi | D01/D05 | R94-USB.1, R94-USB.2 |

Rails touched: 3V3 · GND
