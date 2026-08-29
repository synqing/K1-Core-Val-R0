# Clock architecture

## Audio

Default master: RT1062, via SAI. Where SAI is master it generates BCLK and FSYNC, and MCLK where
required. That sets oscillator placement and clock routing toward the audio connector, and under
Option B it becomes a per-contact cost in the SSCM-1 budget.

External override is a requirement, not an option. The validation board must be able to accept a
laboratory or evaluation-module clock with RT1062 outputs isolated. See
`contracts/audio-interface.md` and `contracts/sscm1-v2/REQUIREMENTS.md`.

The audio bus is 48 kHz, four 32-bit TDM slots (D-051): AUX-L, AUX-R, room-microphone, reserved.
That map is the dual-input contract. The live sheet is still PDM-only until the AUX restore.

## PDM

Target 3.072 MHz for IM69D130 into the 48 kHz output family.

RT1062 has no MICFIL and no dedicated hardware PDM decimation block. Direct PDM is SAI capture
plus DMA plus software decimation, and the exact 3.072 MHz to 48 kHz full-width path is an
experiment to be proven rather than a datasheet feature.

## Inter-MCU

K1BR over SPI. RT1062 polls as master. No synchronous wait is permitted from RT1062 render or
audio work.
