---
abstract: "Pin-by-pin audit of the ESP32-S3 radio/service block on K1-CORE-VAL-R0 (U9/U10-ESP, J6/J7-ESP, SW2/SW3, TP1/TP2, C39-C45, R19-R27, R71-R74) against frozen denominator 489736:464c27d4. Answers: native USB Serial/JTAG retained and no USB-UART bridge exists anywhere on the board (PASS); J7 VBUS is sense-only with no back-feed into any system rail (PASS); K1BR carries no audio-class payload (PASS). Six defects, the load-bearing one being a 100k/100k VBUS divider that falls below the ESP32-S3 VIH minimum at USB-spec minimum VBUS. Verdicts for all 41 module pins including strapping and octal-PSRAM-reserved pins."
---

# PIN-AUDIT-S3 — ESP32-S3 radio, service and K1BR seam

**Status: PROPOSAL.** Findings are proposals against a frozen snapshot. A single writer must reconfirm
against live, which has moved past this hash.

| | |
|---|---|
| Frozen denominator | `frozen-denominator-489736/` · hash `489736:464c27d4` |
| Document UUID | `1435cb46f39e48c8a8aadbb84ca81603` |
| External denominator | `anchors/schDrcLog_2026-08-28.txt` (195 floating-pin entries, not derived from this audit) |
| Machine-readable | `pin-audit-s3-audio.json` |
| Scope A components audited | 28 of 28 · **120 pins, 100% classified, 0 unresolved** |

---

## 1. How connectivity was measured

**This sheet has no wire junctions at all.** All 675 wires are geometrically isolated 20-unit stubs,
each carrying a `NET` attribute; there are zero `NETLABEL` / `NETFLAG` / `NETPORT` primitives in the
source. Connectivity is therefore *entirely* by net name on a stub, and the only physical question
that can be asked is **does this pin's coordinate coincide with a stub endpoint** — which is the
question that catches a stub that is labelled correctly but attached to nothing.

**The pin readback is not co-registered with the frozen source.** `jobs/all-pins-nc-audit.results.json`
predates it for some components. Overlaid naively it reported 36 of U9-ESP's 41 pins floating and put
`RXD0` on `I2C_SCL` — all of it an artefact. A 2-parameter translation was fitted per component,
required to reproduce EasyEDA's own DRC floating-pin verdict for **every** pin of that component:

* 219 / 228 components fit at offset `(0,0)`
* **`U9-ESP` fits at `(-5,-20)`** — 41 pins, 2 free parameters, 22 correct and 0 wrong
* `C10-PWR2` at `(0,-5)`; 7 components do not fit exactly and are excluded (none in scope)

**The oracle was made to go red before it was trusted.** Fault battery, all observed:

| Injected fault | Expected | Observed |
|---|---|---|
| Delete the stub touching a pin | pin → FLOATING | RED ✓ |
| Displace a pin by 1 unit | pin → FLOATING | RED ✓ |
| Rename a stub's `NET` | pin's net membership changes | RED ✓ |
| Inject a known offset into a readback | fitter recovers it exactly | RED→GREEN ✓ |
| Remove a stub endpoint | registration fit → UNRESOLVED | RED ✓ |
| X-crossing wires (control) | not merged | GREEN ✓ |
| T-junction (control) | merged | GREEN ✓ |

Independent cross-check: the stub counts re-derived here reproduce every net count quoted in the
brief exactly (`ESP_EN` 5, `ESP_GPIO0` 4, `ESP_UART0_TX` 3, `ESP_UART0_RX` 2,
`ESP_USB_VBUS_SENSE` 3, `S3_VBUS` 6, `USB_DP_S3` 3, `USB_DM_S3` 3).

---

## 2. Headline answers

### 2.1 Native USB Serial/JTAG retained, and no USB-UART bridge exists — **PASS**

`GPIO19`/`GPIO20` (module pins 13/14) carry `USB_DM_S3`/`USB_DP_S3`, which is the ESP32-S3 native
USB Serial/JTAG pin pair per Espressif's Schematic Checklist. The full service surface is present:

| Service requirement | Realisation | Verdict |
|---|---|---|
| Native USB Serial/JTAG | pin 13 `IO19`→`USB_DM_S3`, pin 14 `IO20`→`USB_DP_S3`, via R74/R73 22 Ω and U10-ESP USBLC6-2SC6 to J7-ESP | PASS |
| UART0 TX/RX | pin 37 `TXD0`→`ESP_UART0_TX`, pin 36 `RXD0`→`ESP_UART0_RX`, both to J6-ESP 3/4 | PASS |
| `GPIO0` / BOOT | pin 27 → `ESP_GPIO0`, R20 10k pull-up to 3V3, SW2-ESP to GND, J6-ESP.6 | PASS |
| `CHIP_PU` / EN | pin 3 → `ESP_EN`, R19 10k pull-up, C42 1 µF to GND, SW3-ESP to GND, J6-ESP.5 | PASS |
| 3V3 | pin 2 → `3V3`; C39 100nF, C45 100nF, C40 10 µF, C41 47 µF | PASS |
| GND | pins 1, 40, 41 → `GND` | PASS |

**A full BOM scan for `CP210*`, `CH340`, `CH343`, `CH9102`, `FT23*`, `FT232`, `MCP2221` and `PL2303`
returns zero hits across all 228 designators.** No USB-UART bridge exists on this board for any
purpose. The requirement is met, not merely "no bridge for S3 access".

The 22 Ω series resistors R73/R74 with unpopulated caps C43/C44 are **not** a defect — they are
exactly Espressif's reference topology: *"It is recommended to reserve series resistors (initial value
can be 22/33 Ω) and capacitors to ground on the traces (initially can be unpopulated), and place them
close to the chip."*

### 2.2 J7-ESP VBUS is sense-only, with no back-feed — **PASS**

`S3_VBUS` reaches exactly six pins and nothing else:

```
J7-ESP.A4, J7-ESP.A9, J7-ESP.B4, J7-ESP.B9   (the four connector VBUS contacts)
R71-ESP.1                                     (top of the sense divider, 100k)
U10-ESP.5                                     (USBLC6-2SC6 VBUS clamp reference)
```

There is **no diode, no ideal-diode controller, no FET and no resistive path** from `S3_VBUS` to
`5V_SYS`, `5V_PROTECTED`, `5V_USB`, `5V_USB_FILTERED` or any other rail. The sense path is
R71 100k → `ESP_USB_VBUS_SENSE` → R72 100k → GND, tapped at module pin 8 (`GPIO15`). The sheet's own
annotation `e98363` — *"SELF-POWERED USB | VBUS SENSE -> GPIO15 | NO BACK-POWER"* — is truthful and
matches the measured topology.

`SBU1` (J7-ESP.A8) and `SBU2` (J7-ESP.B8) are confirmed floating — intentional opens, as recorded.
Both lack No-Connect flags, so EasyEDA DRC lists them (see **S3-04**).

**However the divider itself is defective — see S3-01.**

### 2.3 K1BR seam carries no audio-class payload — **PASS**

The seam is five signals, RT1062 master → ESP32-S3 slave, each through a 22 Ω series resistor:

| Signal | RT1062 side | Resistor | ESP32-S3 side | Test point |
|---|---|---|---|---|
| Chip select | `K1BR_CS_RT` → U6-RTC.J3 | R26 22 Ω | `K1BR_CS` → U9-ESP.18 (`IO10`) | TP2-ESP |
| Clock | `K1BR_SCK_RT` → U6-RTC.J4 | R23 22 Ω | `K1BR_SCK` → U9-ESP.20 (`IO12`) | TP1-ESP |
| MOSI | `K1BR_MOSI_RT` → U6-RTC.J1 | R24 22 Ω | `K1BR_MOSI` → U9-ESP.19 (`IO11`) | — |
| MISO | `K1BR_MISO` → U6-RTC.K1 | R25 22 Ω | `K1BR_MISO_S3` → U9-ESP.21 (`IO13`) | — |
| IRQ | `K1BR_IRQ` → U6-RTC.K11 | R27 22 Ω | `K1BR_IRQ_S3` → U9-ESP.22 (`IO14`) | — |

`IO10`–`IO13` are the ESP32-S3 default FSPI pins (FSPICS0 / FSPICLK / FSPID / FSPIQ), correct for
slave operation. **No `RAW_PCM`, `RAW_PDM`, `AUDIO_FEATURES`, `RENDER_BUFFER`, `PIXEL_BUFFER`, `CRGB`
or any `AUDIO_*`, `PDM_*` or `LED_*` net touches any U9-ESP pin.** The forbidden-payload list in
`contracts/k1br-bridge.md` is satisfied at the physical layer. There is no second wide path between
the two MCUs.

**But there is a second control path into an RT-owned peripheral — see S3-06, which is the finding
on this seam that matters most.**

---

## 3. Defects

### S3-01 — VBUS sense divider falls below VIH at USB-spec minimum VBUS · **HIGH**

R71 100k (`S3_VBUS` → sense) and R72 100k (sense → GND) form a 2:1 divider into `GPIO15`.

ESP32-S3 GPIO input high-level threshold, from the ESP32-S3 Series Datasheet DC Characteristics:
**VIH(min) = 0.75 × VDD**, absolute maximum input = VDD + 0.3 V.

| VBUS | Divider output | VIH(min) at VDD=3.3 V | Result |
|---|---|---|---|
| 5.25 V | 2.625 V | 2.475 V | high, 150 mV margin |
| **5.00 V nominal** | **2.500 V** | **2.475 V** | **high, 25 mV margin** |
| **4.75 V (USB 2.0 min at a downstream port)** | **2.375 V** | **2.475 V** | **reads LOW — USB reported absent while connected** |
| 4.35 V | 2.175 V | 2.475 V | reads LOW |

25 mV of margin at nominal is inside the tolerance of the resistors alone. At the bottom of the USB
voltage range the sense reads low, so the S3 will believe the service port is unplugged while it is
plugged in. The whole self-powered-USB detection story annotated on the sheet rests on this node.

**Fix:** change R72 to 150k (keep R71 at 100k). That gives 3.00 V at 5.0 V VBUS, 2.61 V at 4.35 V
(above VIH with 135 mV margin), and 3.30 V at 5.5 V — still inside the VDD + 0.3 V = 3.6 V absolute
maximum. Alternatively clamp with a small Schottky to 3V3.

### S3-02 — `IO16` and `IO17` (module pins 9, 10), and 11 further spare GPIO, have no No-Connect flags · **LOW**

The brief asked for these two specifically. Module pin 9 is `GPIO16` and pin 10 is `GPIO17`. Both are
**genuinely unconnected spare GPIO** — neither is a strapping pin, neither is reserved by the octal
PSRAM, and neither has an assigned function anywhere on the sheet. They are correctly unused; the only
issue is that no No-Connect flag is placed, so EasyEDA DRC lists them as floating and the sheet cannot
distinguish "deliberately spare" from "forgotten".

The same applies to `IO18` (11), `IO8` (12), `IO9` (17), `IO21` (23), `IO47` (24), `IO48` (25),
`IO38` (31), `IO39` (32), `IO40` (33), `IO41` (34), `IO42` (35) — 13 spare GPIO in total.

**Fix:** place No-Connect flags on all 13, or bring a subset to a spare header. Only 12 No-Connect
flags exist on the entire sheet today (`no_connect_parent_ids`).

### S3-03 — no LC on the module's 3V3 feed · **LOW**

Espressif's Schematic Checklist for the analogue supply: *"Add an LC circuit to the VDD3P3 power rail to
suppress high-frequency harmonics. The inductor's rated current is preferably 500 mA and above."*
U9-ESP pin 2 is fed directly from the board `3V3` net with C39/C40/C41/C45 but **no series inductor or
ferrite**. The mic rail has FB5-AUD; the radio, which is the part that draws transmit current bursts
and radiates, has none. Deviation from the vendor guideline on the one rail where it matters for RF.

### S3-04 — No-Connect flags missing on confirmed intentional opens · **LOW**

`J7-ESP.A8` / `.B8` (SBU1/SBU2) and `SW2-ESP.3/.4`, `SW3-ESP.3/.4` are all confirmed-intentional opens
but carry no No-Connect flag, so they appear in the DRC floating list alongside genuine omissions.
For the tact switches, the better fix is to parallel pins 3/4 onto 1/2 — that is the normal PTS645
treatment and it halves contact resistance and improves mechanical retention.

### S3-05 — K1BR net-naming convention is inconsistent, and three of five lines have no test point · **LOW**

Three nets use the `_RT` suffix for the RT1062 side (`K1BR_CS_RT`, `K1BR_SCK_RT`, `K1BR_MOSI_RT`)
while two use the `_S3` suffix for the ESP32-S3 side (`K1BR_MISO_S3`, `K1BR_IRQ_S3`), so the *bare*
name means "S3 side" for CS/SCK/MOSI and "RT side" for MISO/IRQ. **Electrically every line is correct
and consistent** — a 22 Ω series resistor between the two MCUs — but a reader or a netlist diff will
mis-attribute sides. Recommend `K1BR_<sig>_RT` / `K1BR_<sig>_S3` on all five.

Separately, TP1-ESP and TP2-ESP tap only `K1BR_SCK` and `K1BR_CS`. **MOSI, MISO and IRQ have no test
access**, so the seam cannot be fully observed on a scope or analyser — a gap against
`contracts/debug-fabric.md`'s purpose for a validation board.

### S3-06 — the ESP32-S3 is the sole I2C master and owns the audio ADC's control port · **HIGH — architecture, escalate**

Measured membership of the shared I2C bus:

```
I2C_SDA (8): R28-AUD.2, R4-PWR1.1, R44-MOT.2, R45-MOT.2,
             U11-AUD.12, U12-NFC.32, U2-PWR1.4, U9-ESP.39
I2C_SCL (7): R29-AUD.2, R46-MOT.2, R47-MOT.2,
             U11-AUD.13, U12-NFC.30, U2-PWR1.5, U9-ESP.36
```

**U6-RTC (the RT1062) is on neither net.** The RT1062 has no I2C access anywhere on this board.

`contracts/audio-interface.md` and the ownership matrix give the RT1062 ownership of audio capture,
ADC and TDM ingress. The RT1062 does own the ADC6120's *data and clock* pins. It does **not** own —
and cannot reach — the ADC6120's *control port*: sample rate, channel configuration, PDM mode, PLL
setup, gain and the GPIO1/GPI1/GPI2 function assignments all live behind I2C, which only the
ESP32-S3 can drive.

This is not a K1BR violation — the SPI seam is clean. But it means every audio experiment on this
validation board requires the ESP32-S3 to be alive and to configure the ADC on the RT1062's behalf,
with the configuration request crossing K1BR. On a board whose stated purpose includes resolving a
113 dB versus 123 dB converter question, the measurement chain now depends on the radio MCU and the
bridge being functional.

This is either a deliberate split (S3 = configuration master, RT = data master) that the ownership
matrix should be updated to state, or an oversight. **It is a decision, not a chore — it belongs to
D-AUTHORITY, and I am raising it rather than resolving it.**

---

## 4. Full pin table — U9-ESP (ESP32-S3-WROOM-1 N16R8), 41 / 41 classified

Registration offset `(-5,-20)`, exact fit to EasyEDA DRC across all 41 pins.

| Pin | Name | Net | Verdict |
|---|---|---|---|
| 1 | GND | `GND` | GND |
| 2 | 3V3 | `3V3` | POWER |
| 3 | EN | `ESP_EN` | CONNECTED |
| 4 | IO4 | `NFC_IRQ` | CONNECTED |
| 5 | IO5 | `MOTION_INT_S3` | CONNECTED |
| 6 | IO6 | `S3_POR_REQ` | CONNECTED |
| 7 | IO7 | `RT_PWR_VALID` | CONNECTED |
| 8 | IO15 | `ESP_USB_VBUS_SENSE` | CONNECTED (defect S3-01) |
| 9 | IO16 | — | INTENTIONAL_NC — spare GPIO (S3-02) |
| 10 | IO17 | — | INTENTIONAL_NC — spare GPIO (S3-02) |
| 11 | IO18 | — | INTENTIONAL_NC — spare GPIO |
| 12 | IO8 | — | INTENTIONAL_NC — spare GPIO |
| 13 | IO19 | `USB_DM_S3` | CONNECTED — native USB D− |
| 14 | IO20 | `USB_DP_S3` | CONNECTED — native USB D+ |
| **15** | **IO3** | — | **RESERVED** — strapping pin (JTAG source select) |
| **16** | **IO46** | — | **RESERVED** — strapping pin (boot mode); internal WPD ⇒ 0 = SPI Boot. Must not be pulled high |
| 17 | IO9 | — | INTENTIONAL_NC — spare GPIO |
| 18 | IO10 | `K1BR_CS` | CONNECTED — FSPICS0 |
| 19 | IO11 | `K1BR_MOSI` | CONNECTED — FSPID |
| 20 | IO12 | `K1BR_SCK` | CONNECTED — FSPICLK |
| 21 | IO13 | `K1BR_MISO_S3` | CONNECTED — FSPIQ |
| 22 | IO14 | `K1BR_IRQ_S3` | CONNECTED |
| 23 | IO21 | — | INTENTIONAL_NC — spare GPIO |
| 24 | IO47 | — | INTENTIONAL_NC — spare GPIO |
| 25 | IO48 | — | INTENTIONAL_NC — spare GPIO |
| **26** | **IO45** | — | **RESERVED** — strapping pin (VDD_SPI select); internal WPD ⇒ 0 = 3.3 V, correct for N16R8. Must not be pulled high |
| 27 | IO0 | `ESP_GPIO0` | CONNECTED — BOOT, 10k pull-up + SW2 |
| **28** | **IO35** | — | **RESERVED** — in-package **octal PSRAM** (N16R8). Must remain unconnected |
| **29** | **IO36** | — | **RESERVED** — in-package octal PSRAM |
| **30** | **IO37** | — | **RESERVED** — in-package octal PSRAM |
| 31 | IO38 | — | INTENTIONAL_NC — spare GPIO |
| 32 | IO39 | — | INTENTIONAL_NC — spare GPIO |
| 33 | IO40 | — | INTENTIONAL_NC — spare GPIO |
| 34 | IO41 | — | INTENTIONAL_NC — spare GPIO |
| 35 | IO42 | — | INTENTIONAL_NC — spare GPIO |
| 36 | RXD0 | `ESP_UART0_RX` | CONNECTED — UART0 on GPIO44, ROM default |
| 37 | TXD0 | `ESP_UART0_TX` | CONNECTED — UART0 on GPIO43, ROM default |
| 38 | IO2 | `I2C_SCL` | CONNECTED (see S3-06) |
| 39 | IO1 | `I2C_SDA` | CONNECTED (see S3-06) |
| 40 | GND | `GND` | GND |
| 41 | GND | `GND` | GND |

**Strapping pins are all correct.** `GPIO0` = 1 via R20 and `GPIO46` = 0 via internal weak pull-down
gives SPI Boot (Espressif Boot Mode Control table); pressing SW2 pulls `GPIO0` to 0 for Joint Download
Boot. `GPIO45` = 0 via internal weak pull-down selects 3.3 V VDD_SPI, correct for the N16R8's 3.3 V
in-package flash and PSRAM.

**The three PSRAM-reserved pins are correctly left unconnected.** Espressif's Schematic Checklist:
*"In cases where 1.8 V or 3.3 V, octal, in-package or off-package SPI flash/PSRAM is used, GPIO33 ~
GPIO37 are occupied and cannot be used for other functions."* The N16R8 carries 8 MB octal PSRAM, and
of that range the module exposes `IO35`, `IO36`, `IO37` on pins 28, 29, 30 — all three float. Correct
and must stay that way.

Remaining Scope A components (U10-ESP, J6, J7, SW2, SW3, TP1, TP2, C39–C45, R19–R27, R71–R74):
78 further pins, all classified, in `pin-audit-s3-audio.json`.

---

## 5. Cross-lane notes (not Scope A, passed on)

* `BUCK_PG` wire `e146347` sits at sheet y = **−4535**, i.e. negative Y, while all other geometry on
  this sheet is positive. It attaches to no pin in the readback. → A2-RAILS.
* `C10-PWR2` (100nF) has both pins floating per DRC, with a malformed 5-unit `GND` stub beside it
  where every other stub is 20 units. It also needed a `(0,-5)` registration offset. → A2-RAILS.
* `BUCK_SS` is a confirmed single-pin net in the DRC log. → A2-RAILS.
* `J7-ESP` triggers *"The pin of the component USB4105-GF-A does not correspond to the pad (Pad has no
  corresponding pin: 2、3、4)"*. Footprint/symbol mismatch on the USB-C receptacle. → B-BOM.
* `U9-ESP` and 29 further parts trigger *"Component attributes does not match the Supplier Part"*;
  `U9-ESP` carries `Name = 'FITTED'` and `supplierId = 'ESP32-S3-WROOM-1(N16R8).1'`, which is a part
  string rather than an LCSC code. → B-BOM.

---

## 6. Sources

Primary vendor documentation, which outranks CopperPilot, Voice PE, Teensy, old K1 and agent memory:

* [ESP32-S3 Schematic Checklist — ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html) — USB series resistors, strapping pins, boot mode control, GPIO33–37 octal PSRAM occupation, VDD3P3 LC, digital and analogue supply decoupling, per-pin internal WPU/WPD table
* [ESP32-S3 Series Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf) — DC characteristics, VIH = 0.75 × VDD, absolute maximum input VDD + 0.3 V
* [ESP32-S3-WROOM-1 / 1U Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) — module pinout
* [USB Serial/JTAG Controller Console — ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/usb-serial-jtag-console.html)

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:A4-S3-AUDIO | Created — Scope A pin audit against frozen denominator 489736:464c27d4 |
