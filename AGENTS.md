# AGENTS — K1-CORE-VAL-R0 operating doctrine

**K1-CORE-VAL-R0 is a hardware validation platform.** Experimental capability, observability,
electrical correctness and future flexibility outrank PCB compactness and BOM cost.

EasyEDA Pro is the final EDA authority.

Before any EasyEDA work, read `docs/agent/EASYEDA-EXECUTION-CANON.md`. It is the durable execution
and evidence contract for this repository.

**There shall be exactly one electrical schematic sheet. Separate or hierarchical schematic
sheets are forbidden.** All electrical components, nets, power paths, option circuits and real
schematic wiring live on that one sheet, separated visually by domain of concern.

**`dcd7e3cab2a24b9aa6e531d2b62e1b6f` is not canonical.** That disposable project
(`K1-Core-Val-R0-G2.1-BULK-CANDIDATE`) is historical G2.1 electrical-reference
evidence (D-048, **AMENDED_BY_D-052**). Do not promote it. Do not mutate it.

**D-052: every existing K1-CORE-VAL-R0 EasyEDA project is ARCHIVE / EVIDENCE /
DO NOT MUTATE / DO NOT FABRICATE.** That includes product canonical
`64325d0e55e0435abd018defb0089a9b`, G2.2 HOLD `55ed9ee948734a0e903f37744b51f3b8`,
G2.1 `dcd7e3ca…`, and every hub disposable. They may answer “what value did we
previously use?” They must not answer how the new schematic is wired.

The next implementation lives in **`/Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R1`**
(D-053). EasyEDA project **`K1-Core-VAL-R1`**: new UUID, no ancestry, not a
clone, not Save As, not imported JSON. Component #1 waits on
`architecture/GREENFIELD-BUILD-SPEC.md`. `JLC-SCH-READY` attaches there, not
to G2.2. Leave a hung EasyEDA window alone; no Force Quit.

This R0 repository is **knowledge and archive**. Do not draw the new board here.

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
- **Screenshot and inspect every EasyEDA mutation.** After each one-off API/MCP write or each
  visually atomic `mcp_batch` transaction, wait for the canvas to settle, capture the affected
  sheet/PCB at a scale that exposes the requested delta, and inspect it granularly before the next
  mutation. Preserve the screenshot under the active evidence directory. A batch may not conceal
  multiple visual stages that need separate inspection.
- **The EasyEDA mutation gate is mandatory.** Every EasyEDA write in this repository must begin,
  record semantic read-back and close visual evidence through
  `harness/easyeda_mutation_gate.py`. Missing/stale state or any state other than `READY` forbids a
  normal write. Direct mutation calls that bypass the gate are forbidden.
- Run `python3 harness/easyeda_mutation_gate.py validate` before actuation. The state file and
  append-only ledger own the live transaction phase; static status prose does not.
- All state transitions must use the gate so its OS-level file lock serialises competing agents.
- `FROZEN_INCIDENT` is an absolute stop with no automatic release path. Do not reinterpret it as a
  request to reconcile. Use it after live-session ownership is genuinely unresolved; another
  active agent is not sufficient evidence. Never obstruct a Captain-authorised operator.
  **D-052 programme-archive freeze of retired EasyEDA lanes is an authorised use of the same
  state.** It is not a D-040 ownership incident and has no reconcile-then-continue path.
- Placement, designation and wiring are separate visual transactions. The fixture executor may
  perform exactly one stage for one complete source-derived circuit block per invocation. A
  multi-stage convenience mode is forbidden.
- A missing, empty, distant, cropped, unreadable or failed screenshot is missing evidence. Semantic
  read-back cannot substitute for it. Stop before another write.
- Decorative frames, role-count grids, generic symbol fallbacks and arbitrary count tranches are
  forbidden. Circuit topology defines composition.
- API success is not evidence of board correctness.
- Do not weaken DRC rules to make errors disappear.
- Do not silently consume reserved signals.
- The board may grow east-west whenever more area produces a materially more robust design.
- **G2.2 / HOLD USB schematic writes are terminated (D-052).** The USB session
  canon and `.cursor/skills/g22-usb-schematic-wiring` remain **knowledge** for the
  greenfield USB block. They are not a licence to mutate HOLD or canonical.
  Two Type-C origins within 80 units, a USB2422 west-column signal on `3V3`,
  `XTALOUT` on `GND`, or RBIAS sharing XTALIN remain STOPs when that block is
  drawn. `add_schematic_wire` is a net-join. Never MCP-move symbols.

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

For every EasyEDA mutation, evidence includes both semantic read-back and the immediately
following screenshot with a recorded visual verdict. If either disagrees with the intended delta,
stop, quarantine the execution, and repair or roll back before any further write.
