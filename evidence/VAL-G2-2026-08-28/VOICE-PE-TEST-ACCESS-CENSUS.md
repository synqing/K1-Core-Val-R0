# Test-access census — existing K1 mechanisms

Date: 2026-08-28. Documents **access**, not a request to add a TP per row.

Retired fixture refs are historical (`RETIRED_BY_D_042`). Live canonical designators use
suffix tags. A later G2.1 pass should bind each required node to one live mechanism.

## Dedicated TP strongly preferred

| Node class | Retired-plan access already present | Do not add |
| --- | --- | --- |
| 5V entry / protected / 5V_SYS / 3V3 | power-tree nets; INA on 5V_SYS | extra TP only if no pad/via is probeable |
| RT core / DCDC rails | `rt_dcdc_*`, `rt_vddhigh*` | — |
| 3V3_MIC / ADC rails | `mic_ldo*`, `adc_*` | — |
| NFC rail | `nfc_vdd`, `nfc_vsp_*` | no RF matching TP |
| LED_L / LED_R | LED eFuse + beads + connectors | — |
| INA alert / pwr_valid | `ina_alert`, `pwr_valid*` | — |
| POR / reset | `por_*`, `manual_reset`, `rt_reset` | — |
| BOOT_MODE0/1, S3 EN/GPIO0 | `boot_mode0/1`, `s3_boot`, `s3_en` | — |

## Access required — use existing doors, not extra stubs

| Node class | Existing mechanism | Extra dedicated TP? |
| --- | --- | --- |
| SWDIO / SWCLK / SWO | `debug_connector` (10-pin Cortex) + `swdio_series` / `swdclk_series` pads | **No** if header fitted |
| LPUART1 TX/RX | `rt_uart_header` + `uart_tx_series` / `uart_rx_series` | **No** if header fitted |
| S3 UART0 / USB service | `s3_uart0`, native USB connector | **No** USB-pair stubs |
| K1BR SCK/CS/MOSI/MISO | series resistors + existing `TP1`/`TP2` in retired plan | do not add more SPI TPs by default |
| PDM CLK/DATA | XOR 0R pads + retired `TP4`/`TP5`; live `TP*-AUD` | pads already access |
| AUDIO MCLK/BCLK/FSYNC/SDOUT | iso/series 0R/22R pads + retired `TP3` | pads already access |
| Ext clock select | `option_ext_mclk` DNP + `ext_audio_clk` | jumper/DNP pad is access |
| NFC IRQ / I2C | `nfc_irq_pu`, I2C pull-ups | no RF/tuning 0R |

## No casual TP stub

USB D+/D−, NFC RFO/RFI / matching, other controlled-impedance lines: connector pin or IC
node only. No mid-pair probe pad.

## Live sheet observation

Live TPs: `TP1-ESP` `TP2-ESP` `TP3-AUD` `TP4-AUD` `TP5-AUD` `TP6-VAL` `TP7-AUD` `TP8-AUD`.
This census does **not** add more symbols. Bind function names at G4 silk time.
