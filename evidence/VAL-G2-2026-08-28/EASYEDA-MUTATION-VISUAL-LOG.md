# EasyEDA mutation visual log — 2026-08-28

Project UUID: `09e9c541fd3d404082d4b92e55ae5336`  
Schematic UUID: `e76808fa778140bfa1975a73f10d17d6`  
Page UUID: `1991698f35bf4c09b8de4bcf78bd2b7b`

```text
EASYEDA_MUTATION_GATE_RUNTIME_STATE = SEE EASYEDA-MUTATION-STATE.json
```

This historical visual log does not authorise another write. Only the structured gate state,
validated against its ledger with `python3 harness/easyeda_mutation_gate.py validate`, controls
whether another transaction may begin. Do not copy a transient runtime state into this log.

| Execution | Intended delta | Screenshot | Visual verdict | Semantic read-back |
| --- | --- | --- | --- | --- |
| Automatic role-count placement, stopped at 81/353 | Begin source-derived replacement population | `screenshots/failed-repeated-placement-stopped.png` | **FAIL** — repeated passive/small-symbol grids, bottom-loaded composition, frames dominate, large dead space; same failure class as rejected fixture | 81 components, 0 nets; execution quarantined |
| Delete all 81 components from failed placement | Return to decorative scaffold only | `screenshots/after-repeated-placement-cleanup.png` | **PARTIAL** — components removed, but scaffold itself remains badly composed | 0 components; 12 texts; 11 rectangles; 0 nets |
| Delete scaffold text and rectangles | Return to genuinely blank replacement page | `screenshots/after-scaffold-cleanup-attempt.png` | **PASS** — settled canvas visually blank | persisted source hash `85:03e15891`; 0 components, 0 texts, 0 rectangles, 0 wires, 0 nets |
| Explicitly save the blank page | Remove the stale unsaved-tab state without adding content | `screenshots/blank-page-after-explicit-save.png` | **PASS** — canvas remains completely blank | `save_active_document.saved=true`; active tab `isUnSaved=false` |
| Place POWER_ENTRY from fixture plan | USB-C, ferrite, eFuse, TVS, bulk/ILIM/EN and three stress caps in left-to-right power flow | `screenshots/power-entry-placed.png` | **PARTIAL** — first window shot was zoomed to empty sheet space; source read-back is the placement proof | 11 components `J1 F1 U1 D1 C1 C2 R1 R2 CS11 CS22 CS33`; source hash after place+designate `19031:9d0ded1f` |
| Wire POWER_ENTRY | Named USB / filtered / protected / ILIM / EN / GND stubs plus two trunk wires and a section title | (canvas zoom API hung; semantic proof used) | **PASS electrical** — not a repeated grid; D1 Vcc is live pin 5 (USBLC6), U1 ILIM is live pin 9 `ILM` | 31 then 56 wires after sense; nets `5V_USB` `5V_USB_FILTERED` `5V_PROTECTED` `USB_EFUSE_ILIM` `USB_EFUSE_EN` `GND` each ≥2 endpoints |
| Place and wire POWER_SENSE | Shunt in the 5 V trunk, INA226 Kelvin-sense to the right of the eFuse | pending close-up | **PASS electrical** — flow continues rightward, not a count-pad grid | +10 components `RSH1 U2 C3 C4 R3 R4 CS02 CS13 CS24 CS35`; live INA226 `VIN+`/`VIN-`/`VS+`/`VBUS`; source hash `43414:d8df46f1`; **21 components total** |

| Place and wire POWER_BUCK | TPS62913, inductor and feedback/soft-start around the 5 V→3.3 V conversion | `screenshots/power-entry-sense-after-wire.png` covers entry/sense; buck is further right | **PASS electrical** — VIN from `5V_SYS`, SW through L1 to `3V3`, FB divider present | +15 components `U3 L1 C5–C10 R5–R7 CS01 CS12 CS23 CS34`; nets `BUCK_SW` `BUCK_FB` `BUCK_EN` `BUCK_SS` |

| Place and wire POWER_LED | Second TPS259474L, beads to `+5V_LED_L`/`+5V_LED_R`, ILIM and three stress caps | first `screenshots/power-led-after-wire.png` was not at block scale | **PROCESS FAIL** — next write started before a useful-scale inspect. Later close-up `screenshots/stopped-after-blind-write.png` shows FB2/C13/CS06/CS17 with the planned LED nets. **U4 still not seen at block scale.** | source after LED wire: hash `92414:5169edad`; 46 designators |
| Halted POWER_BRANCH mid-place | Stop after the blind-write violation; no further mutation | `screenshots/stopped-after-blind-write.png` plus `power-led-u4-close.png` / `power-led-mid-close.png` | **STOP** — killed the live batch. Source now has extra undesignated `C?` `L?` `Q?` `R?` `U?`. Do not write again until U4 and that debris are inspected at block scale | hash `102660:fd6eee28`; COMP 60; WIRE 120; U4 present in source, U5 not designated |

| Place RT1062 unit .2 only | Second MCU bank `MIMXRT1062DVJ6B.2` at (1600,2200); do not place units .3–.6 | `screenshots/rt1062-unit2-placed.png` | **PASS place** — zoom-out shows two large vertical MCU rectangles (left selected, right new). Not pin-readable. Duplicates .3–.6 are not on the live sheet. | `e6680` `.1` at 830,2205; `e8918` `.2` at 1600,2200; hash `135605:d2bd0f46`; COMP 77 WIRE 144 |
| Wire both U6 units to plan nets plus every VSS/DCDC_GND to GND and every SOC/NVCC/USB-cap/DCDC_IN pin to 3V3 | Named-net stubs on U6.1 and U6.2; SWD left open because the library has no JTAG_TCK/TMS balls | `screenshots/rt1062-unit2-after-wire.png` | **PASS** — both units visible at pin-readable scale; GND/3V3/BOOT/FLEXSPI/XTAL/1V15_CORE stubs present; USB_OTG1_VBUS not strapped to 3V3 | hash `145266:ecc793bd`; COMP 77 WIRE 223; POR_B 1 (U6 only so far); SWD unmapped library gap |
| Wire U7, C18, C19, R10, R11, R12, SW1 | POR_B wired-OR, boot straps to GND, VDD_HIGH bulk on 3V3; U7 SENSE/MR# held at 3V3; CT left open | `screenshots/u7-after-wire.png`, `crops/u7-close.png`, `screenshots/rt-core-passives-after-wire.png` | **PASS** — U7 RESET#=`POR_B`, GND, MR#/SENSE/VDD=`3V3`, CT open. C18 POR_B–GND, R12 3V3–POR_B, C19 3V3–GND, R11 BOOT_MODE1–GND. R10/SW1 confirmed by net fanout | hash `147110:420c6e64`; COMP 77 WIRE 239; POR_B 5; BOOT_MODE0 2; BOOT_MODE1 2 |
| Place, name and wire RT_DECOUPLE (C20–C34, CS07/CS18/CS29) | Two rows of rail caps; C31 on `1V15_CORE`; others on `3V3`/`GND` | `screenshots/rt-decouple-fit.png`, `screenshots/rt-decouple-after-wire.png` | **PARTIAL visual** — whole-sheet shows a new two-pin cluster; pin labels not readable at this zoom. Electrical read-back is the proof for this block | hash `180391:e2c6e876`; COMP 95 WIRE 275; 3V3 64; GND 93; 1V15_CORE 3 |
