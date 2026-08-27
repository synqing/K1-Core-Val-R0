---
contract: audio
status: RATIFIED
capture_owner: RT1062
tdm_ingress_owner: RT1062
clock_master_default: RT1062
external_clock_override: REQUIRED
rt1062_native_pdm_decimator: false
evaluation_part: TLV320ADC6120
---

# Audio interface contract

## Capture and ingress

RT1062 owns microphone capture, ADC and TDM ingress, and everything downstream through render.

The i.MX RT1060 and RT1062 feature list contains three SAI modules supporting I2S, AC97, TDM and
codec or DSP interfaces, with 8 to 32-bit words and up to 32 words per frame under DMA. It does
not contain MICFIL or any dedicated hardware PDM decimation peripheral (NXP IMXRT1060CEC).

Two PDM paths are therefore compared, and they are not equivalent mechanisms:

    IM69D130 -> TLV320ADC6120 PDM input -> hardware decimation -> 24/32-bit TDM -> RT1062 SAI + DMA
    IM69D130 -> RT1062 SAI capture -> DMA -> software decimation -> full-width PCM

The second path at 3.072 MHz into 48 kHz full width is a custom clock, DMA and filter experiment
that must be proven. It is not a datasheet feature.

## Clocks

Default clock master is RT1062. The validation board must not hard-wire RT1062 as the only
possible source. Provide isolation, series options and test access on `AUDIO_MCLK`, `AUDIO_BCLK`
and `AUDIO_FSYNC`. The TLV320ADC6120 supports master or slave operation, so an external
laboratory clock must be able to drive the interface with RT1062 outputs isolated.

## Measurement constraint

Any capture path used to evaluate converter dynamic range must preserve full sample width.
A 16-bit application-level audio path cannot resolve a 113 dB against 123 dB question.
