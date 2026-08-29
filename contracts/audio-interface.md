---
contract: audio
status: RATIFIED
authority: D-051
capture_owner: RT1062
tdm_ingress_owner: RT1062
clock_master_default: RT1062
external_clock_override: REQUIRED
rt1062_native_pdm_decimator: false
evaluation_part: TLV320ADC6120
input_families:
  - AUX_STEREO_ANALOG
  - IM69D130_PDM
aux_connector: SWITCHED_3P5MM_TRS
aux_channels: [AUX_L, AUX_R]
aux_jack_mpn: CANDIDATE_NOT_BOUND
aux_jack_candidate: PJ-3537S-SMT
aux_jack_candidate_lcsc: C2689709
pdm_channel: ROOM_MIC
simultaneous_adc_capture: REQUIRED
simultaneous_channels: [AUX_L, AUX_R, ROOM_MIC]
audio_bus: TDM_48K_4X32
tdm_slots:
  0: AUX_L
  1: AUX_R
  2: ROOM_MIC
  3: RESERVED
pdm_adc_path: FIT_DEFAULT
pdm_direct_rt_path: DNP_ALTERNATE
pdm_route_population: XOR
live_sheet_aux: ABSENT
---

# Audio interface contract

RT1062 owns microphone capture, ADC and TDM ingress, and everything downstream
through Audio Processing, VP and render (D-001). This contract is **dual-input**.
It is not a PDM-only contract.

The intended validation architecture, migrated from K1-AUDIO-EVAL-R0 and
ratified for this board by D-051, is:

    switched stereo 3.5 mm AUX  -->  analogue CH1 + CH2 of U11-AUD / TLV320ADC6120
    IM69D130 PDM room-mic       -->  digital PDM input of the same U11-AUD (FIT)

    simultaneous ADC capture: AUX_L + AUX_R + ROOM_MIC

    U11-AUD -- 48 kHz / 4-slot / 32-bit TDM --> RT1062 SAI + DMA
      slot 0 = AUX_L
      slot 1 = AUX_R
      slot 2 = ROOM_MIC
      slot 3 = reserved / diagnostic

The live EasyEDA sheet still shows only the PDM portion. That is a migration
gap, not a decision that analogue AUX is unused. Do not freeze the
post-D049/D050 electrical graph while AUX is absent from that graph.

## Dual-input versus the PDM XOR

Two PDM paths are compared for the **microphone lane only**. They are not
equivalent mechanisms, and they are not the meaning of “dual audio”:

    IM69D130 -> TLV320ADC6120 PDM input -> hardware decimation -> 24/32-bit TDM -> RT1062 SAI + DMA
    IM69D130 -> RT1062 SAI capture -> DMA -> software decimation -> full-width PCM

The second path at 3.072 MHz into 48 kHz full width is a custom clock, DMA and
filter experiment that must be proven. It is not a datasheet feature. RT1062
has no MICFIL and no dedicated hardware PDM decimation peripheral
(D-017; NXP IMXRT1060CEC).

A 0R / DNP matrix enforces the XOR so both PDM routes can never load the bus
at once. FIT default is ADC-PDM. Direct-RT is the DNP alternate. The XOR does
**not** replace, disable or redefine the stereo AUX lane.

The EVAL daughterboard sent the direct-PDM branch to ESP32. That host map is
not copied. On K1-CORE-VAL-R0 the experimental branch terminates at RT1062.

## Analogue AUX lane

Physical connector: switched stereo 3.5 mm TRS.

    TIP    = AUX_L
    RING   = AUX_R
    SLEEVE = AUX_RETURN
    switch / detect contacts = AUX_PRESENT / JACK_DETECT implementation

K1-AUDIO-EVAL-R0 selected `PJ-3537S-SMT` / `C2689709` as a candidate with
status `PINOUT-VERIFY`. That part is a **reference**, not a bound mainboard
MPN. The manufacturer pinout, switch contacts, courtyard and insertion axis
must be proven before schematic freeze. The VAL-R0 designator is not `J1`
(`J1-PWR1` is the USB-C receptacle).

Do not connect a consumer TRS jack straight to the ADC pins. The EVAL
electrical design is the starting architecture, not a finished VAL-R0
network:

- low-capacitance ESD immediately behind the jack (EVAL candidate
  TPD4E05U06DQAR, AVL-OPEN — not bound here);
- consumer stereo single-ended / pseudo-differential attenuation and return
  as the FIT baseline (EVAL start: four matched 10 kΩ 0.1 % series/return
  resistors, EVT-tunable);
- differential laboratory population as four DNP 0 Ω links, mutually
  exclusive with the consumer path;
- four AC-coupling capacitors into IN1P / IN1M / IN2P / IN2M (EVAL start:
  1 µF low-distortion).

Recalculate attenuation, input impedance, corner frequency, capacitor
distortion, common-mode behaviour and source loading from TI authority
(TLV320ADC6120 datasheet and *Working With Analog Inputs*, SBAA583). Meet
the EVAL PRD intent of a **2.0 Vrms** consumer source without clipping. Do
not simply ground `IN1M` and `IN2M`, or tie the TRS sleeve straight to the
negative ADC pins, without verifying the chosen single-ended /
pseudo-differential topology. Use matched L/R values.

Keep the analogue path in the audio quiet enclave, away from USB, buck
switch nodes, LED power and NFC RF.

## ADC pin use (migrated from EVAL)

K1-AUDIO-EVAL-R0 `docs/04-ELECTRICAL-DESIGN.md` assigned:

| U11 pins | EVAL use | VAL-R0 net |
| --- | --- | --- |
| 1 / 2 | line-left IN1P / IN1M | AUX_L |
| 3 / 4 | line-right IN2P / IN2M | AUX_R |
| 11 | GPIO1 = PDMCLK | PDM clock, FIT default |
| 19 | MICBIAS_GPI2 = PDMDIN | PDM data, FIT default |

The live PDM-only sheet uses `IN2P` as PDM data and pin 19 as `AUDIO_MCLK`.
That assignment cannot survive once both analogue channels are used. D-013
still requires an external MCLK / BCLK / FSYNC override with isolation.
Pin 19 cannot be both PDMDIN and MCLK. Re-derive the override landing at
schematic restore. This contract does **not** assign GPIO.

## Operating profiles

| Profile | AUX-L/R | IM69D130 | Notes |
| --- | --- | --- | --- |
| `LINE_REF_FIXED` | yes | no | DRE off |
| `LINE_DRE` | yes | no | DRE on |
| `LINE_PLUS_ROOM` | yes | via ADC | simultaneous; normal line-plus-room |
| `LINE_PLUS_ROOM_DRE` | yes | via ADC | simultaneous; DRE experiment |
| `MIC_ADC` | no | via ADC | microphone-lane ADC path |
| `MIC_DIRECT` | no | direct RT1062 | microphone-lane DNP alternate |
| `LINE_HPF_PROBE` | yes | optional | EVAL-retained probe; not a substitute for `LINE_PLUS_ROOM` |

AGC and DRC stay off in reference profiles. DRE is a measured A/B variable,
not a shipping assumption.

## Clocks

Default clock master is RT1062. The validation board must not hard-wire
RT1062 as the only possible source. Provide isolation, series options and
test access on `AUDIO_MCLK`, `AUDIO_BCLK` and `AUDIO_FSYNC`. The
TLV320ADC6120 supports master or slave operation, so an external laboratory
clock must be able to drive the interface with RT1062 outputs isolated.

Baseline bus: 48 kHz, four 32-bit slots, BCLK 6.144 MHz when that family is
used. PDM clock target remains 3.072 MHz.

## Measurement constraint

Any capture path used to evaluate converter dynamic range must preserve full
sample width. A 16-bit application-level audio path cannot resolve a 113 dB
against 123 dB question.

## Test access

Provide access at jack-side L/R, post-ESD, post-conditioning, ADC input
pairs, jack detect and ADC TDM output. Dedicated pads, option-jumper pads
and series-resistor pads count. Do not invent a probe stub on every net.

## What this contract does not copy

- K1-AUDIO-EVAL-R0 daughterboard form: 30-pin host FPC, card LDO, PCA9306,
  `CARD_EN`, or the EVAL GPIO list.
- DualMCU AIC3204 / other-codec jack circuits.
- A second schematic sheet. AUX lives on the one existing sheet, in the
  audio domain, when Captain authorises EasyEDA work.
- A bound jack MPN, a bound ESD MPN, or frozen resistor/capacitor values.

## Schematic restore (not this turn)

Later EasyEDA work must remove “unused / NC” treatment from the analogue
input pins, wire both analogue channels, add the physical jack and local
front end, retain the IM69D130 flex and PDM XOR, and keep RT1062 as ingress
owner. That pass waits until USB-C 3D seating is off the live canvas and
Captain issues an EasyEDA GO.
