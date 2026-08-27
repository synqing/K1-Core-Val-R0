---
contract: debug_fabric
domain: D13.1
status: REQUIREMENTS_ONLY
scope: VAL_ONLY
service_endpoint: ESP32_S3
third_mcu: false
k1br_semantics_changed: false
rt_boot_uart: LPUART1
rt_boot_uart_tx_pad: GPIO_AD_B0_12
rt_boot_uart_rx_pad: GPIO_AD_B0_13
rt_boot_mode0_pad: GPIO_AD_B0_04
rt_boot_mode1_pad: GPIO_AD_B0_05
rt_boot_mode_internal_pull_kohm: 100
rt_boot_mode_serial_downloader: "01"
rt_boot_mode_internal_boot: "10"
remote_rt_power_switch: NOT_BASELINE
---

# D13.1 — K1-VAL Debug and Recovery Fabric

Subsystem of D13 (instrumentation and validation). **Requirements only.** No circuit, no
component selection, no final GPIO assignment. Implementation follows VAL-G1.

## Scope

An out-of-band engineering and recovery plane letting the ESP32_S3 observe, command and recover
the RT1062. It is **not** K1BR and does not change K1BR: that seam stays command, state and
telemetry, with the same forbidden payloads.

No third MCU. The existing ESP32_S3 is the service endpoint.

## Scoped authority exception

The product role of ESP32_S3 remains radio and control. K1-CORE-VAL additionally grants it a
**validation-only** debug and service role. No RT1062 real-time function moves: audio capture,
processing, VP, render, pixels and LED output stay where the ownership matrix puts them.

Raw Wi-Fi and TCP transport is permitted **for VAL Debug Fabric instrumentation only**. This
does not reactivate Wi-Fi, REST or WebSocket as a product control plane; that remains parked.
Implement the debug service as raw TCP first — a transparent binary tunnel needs less machinery
and suits ordinary serial tooling. WebSocket only if a browser tool actually requires it.

## Verified RT1062 facts

Verified against NXP IMXRT1060CEC and the MIMXRT1060-EVKB manual.

| Item | Value |
| --- | --- |
| Boot / console UART | LPUART1 |
| LPUART1 TX pad | `GPIO_AD_B0_12` |
| LPUART1 RX pad | `GPIO_AD_B0_13` |
| `BOOT_MODE0` pad | `GPIO_AD_B0_04` |
| `BOOT_MODE1` pad | `GPIO_AD_B0_05` |
| Internal pull-down on both boot-mode pads | 100 kohm |
| `BOOT_MODE[1:0]` = `01` | Serial Downloader |
| `BOOT_MODE[1:0]` = `10` | Internal Boot |

Boot-mode state is sampled around the `POR_B` transition, so strap-before-reset ordering matters.

## Requirements

### Boot and recovery

- Passive default is Internal Boot, established by external straps, with no firmware involved.
- RT1062 boot and recovery must remain fully functional with ESP32_S3 dead or absent.
- A single logical `RT_RECOVERY_REQ` is permitted **only** where target-local hardware decodes it
  into both boot-mode bits. Raw boot-mode bits are never exported across a module connector.
- A manual, ESP32_S3-independent path into Serial Downloader is required.

### Reset

- `POR_B` is driven by a wired-OR of: an external reset supervisor, a manual reset control, and
  an ESP32_S3 request.
- **ESP32_S3 may assert `POR_B` low or release it to high impedance. It must never actively
  drive `POR_B` high.** The supervisor keeps the target in reset until its supplies are stable,
  and nothing else may override that.
- NXP recommends an external reset IC; the specific part waits for the power architecture.

### UART arbitration

Freeze the requirement, not the implementation:

- exactly one active writer to RT RX at any time;
- a completely ESP32_S3-independent physical takeover path, electrically overriding any software
  selection;
- safe behaviour when either domain is unpowered — powered-off protection, Ioff or guaranteed
  high-Z;
- a hardware-defined default state that works before any firmware runs.

Active mux versus jumper or 0R selection is decided after VAL-G1. TMUX1574 is a **candidate,
not a requirement**.

RT TX is one driver into two receivers, so it needs fan-out rather than arbitration. Isolate it
only for powered-off backfeed, input capacitance or fault isolation — derived after the power
domains exist.

### Independent physical doors

Neither processor may be strandable by a network, firmware, mux or bridge failure.

- **RT1062:** a fitted direct SWD/JTAG connector, plus direct UART recovery access, both local to
  the RT1062 — on SSCM-1 under Option B, beside it on the Core under Option C. **SWD is never
  proxied through ESP32_S3.** Baseline is a standard 10-pin 1.27 mm Cortex header unless
  mechanics later argue otherwise. Trace/SWO may be reserved; a full TPIU connector is not
  escalated to without a proven need.
- **ESP32_S3:** native USB Serial/JTAG for console, flashing and debug, **plus** retained
  physical access to UART0 TX/RX, GPIO0/BOOT, CHIP_PU/EN, 3V3 and GND. Espressif recommends
  keeping UART download access because USB recovery can become unavailable depending on
  application configuration. No CP2102, CH340 or FTDI part is added for ESP32_S3 access.

No MAX3232 or equivalent. Both domains are 3.3 V logic.

### Target state

- An RT power-valid indication is available to ESP32_S3, sourced from the RT supervisor or power
  tree rather than inferred. The service endpoint refuses transmit and recovery operations while
  the target domain is invalid.

### Out of baseline

- Independent remote RT power switching is **not** in R0. Once one domain can be powered while
  the other is not, every cross-domain signal becomes a back-power path and the board stops
  behaving like the product power architecture. A lab supply or fixture performs cold cycles.
  Fixture-friendly power measurement and isolation links may be provisioned after VAL-G1 if cheap.
- An auxiliary ESP32_S3 UART is a **logical reservation only**, taken if the GPIO and floorplan
  cost is low and dropped if a higher-value peripheral needs the resource.

### Real-time hygiene

Electrical separation does not make logging free. The RT-side debug transport must be bounded,
non-blocking, ring-buffered or DMA-backed, droppable under overload, instrumentable, and fully
disable-able. A true off state is required when measuring real-time performance.

### Network semantics

Many clients may observe concurrently; exactly one holds a write lease at a time. The endpoint
adds identity, channel, monotonic timestamp, sequence, overflow count, connection state, reset
cause and bridge version **outside** the raw stream, while still offering a transparent raw
endpoint for ordinary tooling.

## Validation target, not a solved problem

The hardware provides an RT BootROM UART path, and NXP's BootROM supports serial download. But
host tooling expects a serial or USB transport. So: **the Debug Fabric shall expose a
transparent binary RT BootROM UART tunnel capable of supporting remote recovery tooling.
Automated network flashing is a validation target, not a hardware-complete assumption.** Prove it
with a host adapter or a virtual-serial bridge. Do not have ESP32_S3 reimplement NXP's bootloader
protocol without a discovered reason.
