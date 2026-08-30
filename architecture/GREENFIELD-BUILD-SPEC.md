# K1-CORE-VAL-R0 GREENFIELD BUILD SPEC

```text
STATUS     = AUTHORITY_FOR_GREENFIELD_DRAWING
DATE       = 2026-08-30
DECISION   = D-052
NOT        = a schematic, a netlist, or a licence to mutate archived EasyEDA
```

This is the one small specification of **what we are actually building**.
Existing EasyEDA projects are evidence only. If it is not in
`/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R1`
(EasyEDA `K1-Core-VAL-R1`), it is not on the new board (D-053).

Authority chain:

```text
CAPTAIN DECISIONS
        ↓
THIS SPEC + ratified contracts
        ↓
GREENFIELD SCHEMATIC (one sheet)
        ↓
SEMANTIC + VISUAL VERIFICATION
        ↓
BLANK PCB
```

Do not draw component #1 until **OPEN BEFORE BUILD** is closed or explicitly
waived in the decision register.

---

## COMPUTE

- RT1062 (`MIMXRT1062DVJ6B`, D-028) = Audio Processing, VP, capture, effects,
  render, pixels, LED output (D-001).
- ESP32-S3 = radio, wireless control (BLE-MIDI, D-007), NFC host, service USB,
  Debug Fabric endpoint (D-018, D-019).
- Inter-MCU: SPI, K1BR v1. Command, state and telemetry only. No PCM, feature or
  pixel transport (D-002).
- No third MCU (D-019).
- Exactly one schematic sheet (D-010).

## USB

- 1 × Type-C. No second. No third (D-049).
- Receptacle: GT-USB-7005A / C5250872 (D-050). Board stays 1.60 mm (D-012).
- Hub: USB2422. UP → J1. DN1 → RT1062 USB OTG1 (HS, non-removable).
  DN2 → ESP32-S3 native USB (FS, non-removable). `NON_REM[1:0] = 10`.
- J1 is 5 V inlet and Type-C sink. Hub does not replace source-policy.
- Brick-proof S3 path: `J6-ESP` UART0 + EN + GPIO0. USB-HID through the hub is
  not the brick path.
- USB audio remains `EXPERIMENT_ONLY`, DN1 → RT OTG1, not across K1BR.
- SuperSpeed and SBU: NC. Do not route SuperSpeed.
- When this block is drawn: session canon
  `docs/agent/SESSION-CANON-2026-08-30-G22-USB-WIRING.md` (keepouts, net-join,
  no stacked Type-C). That document is **knowledge**. HOLD is not the canvas.

## AUDIO

- TLV320ADC6120.
- Dual-input: switched stereo 3.5 mm AUX + IM69D130 PDM (D-051).
- Simultaneous AUX-L / AUX-R / room-mic on 48 kHz four-slot 32-bit TDM
  (slots 0/1/2; slot 3 reserved).
- Default clock master RT1062; external override required (D-013).
- PDM alternate path: XOR, ADC path FIT default, direct-RT DNP, terminates on
  RT1062 not S3 (D-017, microphone contract).
- Jack MPN unbound. No GPIO assigned yet.

## NFC

- ST25R3916B. S3 host. I2C. I2C_EN pulled high (D-046).
- RF front end carrier-side (D-009). Internal regulator rails are outputs
  (D-047). Matching values `TUNE_TBD` until the real antenna is characterised.
- Remote U.FL/coax antenna remains the intended installation style; exact
  connector and match are OPEN (see below).

## POWER

- 5 V ingress at J1. Type-C sink advertisement must bound load (D-049, D-050).
- Conversion: TPS62913 family as ratified (D-045: PG pull-up when used; NR/SS
  capacitor). Branch structure and instrumentation from
  `architecture/POWER-ARCHITECTURE.md` — as **calculations**, not as copied
  net geometry.
- eFuse ILIM ohmic identity 1.24 kΩ / RNCF0402BTC1K24 is **knowledge** from
  the ILM repair, not a copied wire.

## LED

- WS2816C. Two independent channels. RT1062 owner. Level shift required
  (led-interface contract).
- **OPEN:** dual-DIN physical interface (2 vs 4 data lines).

## MOTION

- Accelerometer on RT1062 by default (ownership matrix). Fit 0R/DNP so both
  masters cannot own it. Part not frozen here.

## VALIDATION / SERVICE / DEBUG

- D13.1 Debug and Recovery Fabric is a VAL requirement: remote reset and
  remote recovery. No third MCU. Requirements only until this spec’s OPEN
  item 4 closes (D-018, D-021).
- Independent remote RT **power switching** is out of baseline R0 unless
  D-021 is amended.

## MECHANICAL (carry into blank PCB later)

- 1.60 mm, six layers (D-012, D-022). 8-layer is evidence-triggered. 10 rejected.
- 0.8 mm board to fit a mid-mount Type-C is forbidden (D-050).
- Antenna zone stays mandatory (D-008).
- No imported K1 copper. Floorplan from the new electrical graph plus ratified
  keepouts (RF vendor, acoustic mic, connector access, mounting).

---

## Construction order (after OPEN closes)

One coherent block at a time. Build → inspect → semantic verify → visual
inspect → freeze that block. Then the next.

```text
PWR ENTRY
   ↓
3V3 / POWER TREE
   ↓
RT1062 CORE + PDN
   ↓
ESP32-S3
   ↓
USB2422 + TYPE-C
   ↓
AUDIO
   ↓
LED ×2
   ↓
NFC
   ↓
MOTION
   ↓
SERVICE / VALIDATION
   ↓
DEBUG / HIL
```

A fault in USB is a USB repair. It is not a whole-board snapshot restore.

---

## OPEN BEFORE BUILD

Architecture **stops moving** when these are closed in the decision register.

1. **LED physical interface:** 2 vs 4 data lines (two WS2816C channels are
   ratified; DIN/backup wiring is not).
2. **NVCC_PLL_1V1** electrical source requirement (not frozen in
   POWER-ARCHITECTURE.md).
3. **D-021:** independent remote RT hard power-cycle stays **out of baseline**
   unless Captain amends. Confirm for greenfield: keep D-021 or reopen.
4. Exact reconciled **validation / service / Debug Fabric** circuit (D-018 is
   requirements-only today).
5. Remaining **NFC** topology: antenna connector, coax/U.FL, matching numbers
   (`TUNE_TBD`).

When those five are closed, draw. Not before.

---

## Identity of the new board

Semantic, not a source hash:

- these components exist and are bound to verified LCSC/MPN identities;
- these pins connect to these nets;
- required pins are not open;
- forbidden connections do not exist.

A hash may fingerprint that state. The hash is not the design.
