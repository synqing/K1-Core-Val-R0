# AGENTS — K1-CORE-VAL-R0 operating doctrine

**K1-CORE-VAL-R0 is a hardware validation platform.** Experimental capability, observability,
electrical correctness and future flexibility outrank PCB compactness and BOM cost.

EasyEDA Pro is the final EDA authority.

**There shall be exactly one electrical schematic sheet. Separate or hierarchical schematic
sheets are forbidden.** All electrical components, nets, power paths, option circuits and real
schematic wiring live on that one sheet, separated visually by domain of concern.

## Hard rules

- Do not import legacy K1 copper.
- Do not create canonical PCB geometry, place, floorplan, fan out or route before VAL-G2 closes.
  The disposable PCB import required by VAL-G2.0 qualification is the only exception.
- Do not assign GPIO before ownership and physical requirements are understood.
- The RT1062 does not contain a dedicated MICFIL or hardware PDM decimation peripheral.
  Direct PDM is an SAI + DMA + software-decimation experiment.
- K1BR carries command, state and telemetry only. Never add PCM, feature or pixel transport.
- `AP` means Audio Processing only. Wi-Fi access point is `WIFI_AP`, `SOFTAP` or `ACCESS_POINT`.
- BLE-MIDI is the current wireless control plane. Wi-Fi, REST and WebSocket are parked.
- The ESP32-S3 2.4 GHz antenna zone stays mandatory regardless of which protocol is used.
- NFC RF circuitry stays carrier-side.
- DeepPCB is routing-only, never placement.
- Snapshot EasyEDA before every write.
- API success is not evidence of board correctness.
- Do not weaken DRC rules to make errors disappear.
- Do not silently consume reserved signals.
- The board may grow east-west whenever more area produces a materially more robust design.

## CopperPilot role

CopperPilot is a geometry and architecture reasoning agent. It is not a PCB execution agent.

**Authorised:** read-only board inspection; component-zone, orientation, pin-facing,
escape-density and routing-corridor analysis; outline synthesis; comparing and ranking
alternative placements; identifying congestion before routing; via-pressure reasoning;
conflicting domain adjacency; downstream-consequence analysis; proposing coordinates and
rotations; critiquing another agent's placement.

**Not authorised:** authoring the canonical schematic; mutating the canonical PCB; final
placement writes; routing canonical copper; altering rule expectations; running and certifying
its own acceptance gate; reporting DRC, routing or identity success as authoritative; claiming
fabrication readiness; acting as both builder and verifier.

Its coordinates, measurements and PASS claims are **proposals** until independently reproduced
through the normal project evidence path. Exploratory geometry may run against a disposable
clone, but the resulting geometry is imported conceptually and recreated independently — the
canonical board is never "CopperPilot says PASS".

Builder and verifier roles stay separate for CopperPilot-originated work.

Historical CopperPilot PCB lanes are evidence only unless explicitly reactivated. The
`SpectraSynq-K1-CORE-Final` lane is dead: historical design evidence, not a PCB source, not a
work target.

## Harness doctrine

> Create a check when the artefact it checks first exists.
> Do not create a future gate's harness merely because that gate will eventually exist.

A checker that inspects nothing must never print PASS. Every check reports the count of files,
records and contracts it actually parsed, and fails closed when any count is zero.

Two checks exist at VAL-G0:

- `harness/check_authority_consistency.py`
- `harness/check_terminology.py`

`check_single_schematic.py` is created when the first real EasyEDA schematic exists — not before.

**Do not port `check_architecture_ownership.py` from the DualMCU firmware repository.** It scans
firmware source. In a hardware and documentation repository it would find no source files,
iterate over nothing and pass vacuously. `check_authority_consistency.py` replaces it here and
inspects structured authority records instead.

## Evidence

Evidence directories are created when evidence exists, named `evidence/VAL-Gn-<YYYY-MM-DD>/`.
No empty future gate directories.
