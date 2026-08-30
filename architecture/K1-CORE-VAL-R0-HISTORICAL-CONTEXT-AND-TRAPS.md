---
title: K1-CORE-VAL-R0 — Historical Context and Traps
purpose: Institutional memory export. What a technically strong fresh agent cannot learn from datasheets or the stale EDA export.
status: RECOVERY PASS — not a design document, not an architecture proposal, not authority.
authority_class: Level 6 (architecture/). Nothing here supersedes authority/01-DECISION-REGISTER.md or authority/05-SUPERSESSIONS.md.
date: 2026-08-30
---

# K1-CORE-VAL-R0 — Historical Context and Traps

## How to use this file

This is not a design document. It exists because roughly three weeks of K1 hardware reasoning —
architectures tried and abandoned, questions closed twice, figures that turned out to be circular,
control-system failures that produced written mandates — sits in conversation history and scattered
evidence directories rather than in the authority layer where a fresh agent would look.

Read `authority/00-AUTHORITY-PRECEDENCE.md` first. Then this file. Then the live repo.

**G2.2 USB EasyEDA wiring (2026-08-30)** is not in this traps file. It is
`docs/agent/SESSION-CANON-2026-08-30-G22-USB-WIRING.md` plus executable gates
`harness/check_g22_usb_hub.py` and `harness/check_g22_schematic_drawing.py`.
Do not re-derive Type-C pin maps or USB2422 keepouts from this document.

**Precedence discipline for everything below.** Where my recollection and written authority disagree,
I flag the conflict and let the written authority stand. Conflicts are marked **⚠ CONFLICT**.
Nothing in this file promotes, supersedes or amends any decision.

---

## 0. INPUT GAP — declared before anything else

The brief names three inputs. **Only two arrived.**

| Input | Status |
| --- | --- |
| Live K1-CORE-VAL-R0 repository and authority documents | ✅ Read this pass |
| Opus 5 Support Architecture Investigation | ✅ In context; also on disk at `architecture/SUPPORT-ARCHITECTURE-INVESTIGATION.md` |
| **Grok 4.6 Heavy Electrical Architecture Report R0-ARCH-2** | ❌ **NOT SUPPLIED AND NOT PRESENT** |
| Stale `K1CoreValR0.epro2` | ✅ Present, treated as non-authoritative throughout |

Searched for the Grok report: `grep -rl -iE "grok|R0-ARCH-2|R0_ARCH_2"` across the whole repo returns
**zero files**; the session upload directory contains only `f47abb4f-K1CoreValR0.epro2`; nothing in
`architecture/`, `evidence/`, `docs/` or `archive/` matches.

**Consequence for section G:** the Grok half of the conflict audit **cannot be performed** and has not
been guessed at. Section G audits the Opus report fully and leaves every Grok row as
`GROK NOT SUPPLIED`. Attach `R0-ARCH-2` and section G can be completed as a bounded follow-up — it is
the only part of this brief left open, and it is left open deliberately rather than fabricated.

---

## A. CURRENT AUTHORITY — what each subsystem actually is, right now

Source column gives the highest-precedence document that establishes the item.

### A.1 Compute and ownership

| Item | Current state | Source |
| --- | --- | --- |
| Architecture class | Dual-MCU. RT1062 application/audio/visualisation + ESP32-S3 radio/control | D-001, D-003 |
| Compute location | **Option C** — RT1062 and ESP32-S3 both on K1-CORE. VAL-G1 CLOSED | D-024 |
| Option B (carrier + SSCM-1 module) | **DEFERRED, not rejected.** Interface feasibility **UNPROVEN** — the earlier "B2 59/67 PASS" was **withdrawn** | D-025 → **D-033** |
| RT1062 package | **FROZEN**: `MIMXRT1062DVJ6B`, 196-ball MAPBGA, 12 × 12 mm, 0.8 mm pitch, 600 MHz. The **A revision is NRND** | D-028 |
| Ownership: capture, AP, GDFT, tempo/onset/saliency, VP, render, pixels, FastLED, LED output | RT1062 | D-001, `authority/03-OWNERSHIP-MATRIX.csv` |
| Ownership: radio, wireless control, NFC host, service USB | ESP32-S3 | D-001, D-007, ownership matrix |
| ESP32-S3 extra role on this board | **Validation-only** debug/service endpoint. Product role unchanged; no RT1062 real-time function moves | D-018, D-019, supersession 2026-08-27 |
| Third MCU | **Forbidden** | D-019 |
| Inter-MCU link | SPI, K1BR v1 framing frozen. Command / state / telemetry **only** | D-002, `contracts/k1br-bridge.md` |
| K1BR forbidden payloads | RAW_PCM, RAW_PDM, AUDIO_FEATURES, RENDER_BUFFER, PIXEL_BUFFER, CRGB | `contracts/k1br-bridge.md` |
| Wireless control plane | **BLE-MIDI only.** Wi-Fi / REST / WebSocket **parked** | D-007, reaffirmed 2026-08-27 |
| Wi-Fi exception | Raw Wi-Fi/TCP permitted **for VAL Debug Fabric instrumentation only** — does not unpark the product plane | supersession 2026-08-27 |
| RF zone | Mandatory regardless of protocol — BLE and Wi-Fi share radio and antenna | D-008 |

### A.2 USB

| Item | Current state | Source |
| --- | --- | --- |
| Receptacle count | **ONE.** `J1-PWR1`. Second forbidden, third forbidden | **D-049** |
| J1 MPN | **BOUND**: `GT-USB-7005A` / `C5250872` | **D-050** |
| J1 role | Type-C **sink**, 5 V inlet, Rd 5.1 kΩ, CC current-advertisement sense, **and hub upstream** | D-049, `contracts/usb-interface.md` |
| Hub | Microchip **USB2422**, strap mode, `NON_REM[1:0] = 10`, both DN ports non-removable | D-049 |
| DN1 | RT1062 USB OTG1, HS device | D-049 |
| DN2 | ESP32-S3 native USB GPIO20/19, FS device | D-049 |
| VBUS validity | **F6-B**: TPS2052B. `F6_VALIDITY_SOURCE` = `5V0_USB_VALID` from `U22-USB` TPS7A2550DRVR / C2876265 — **explicitly not `5V_PROTECTED`** | D-049, `H0f-CLOSE.md` |
| Host-unplug kill | **KILL-B** — TLV7031 comparator + dual AND. `PRTPWR`/`OCS` may assist but are **not** the kill | GO-NO-GO H0e |
| Downstream power islands | **FORBIDDEN.** Neither TPS2052B output powers a processor | D-049 |
| S3 brick-proof path | `J6-ESP` UART0 + EN + GPIO0 + 3V3 + GND — **mandatory** | D-049, `contracts/debug-fabric.md` |
| S3 USB XOR recovery header | `J12-USB` + `R94` (FIT, DN2) / `R95` (DNP, J12). True XOR | GO-NO-GO H10 |
| USB audio | `EXPERIMENT_ONLY`, terminates hub DN1 → RT OTG1, never across K1BR | D-049, ownership matrix |
| SuperSpeed / SBU | **NC. Do not route "for later"** | D-050 |
| Differential impedance | 90 Ω on three pairs: hub UP, DN1, DN2 | `contracts/usb-interface.md` |

### A.3 Power

| Item | Current state | Source |
| --- | --- | --- |
| Inlet | `J1-PWR1` is the only USB-C and the 5 V inlet | `architecture/POWER-ARCHITECTURE.md`, D-049 |
| Protection chain | `5V_USB` → eFuse `U1-PWR1` TPS259474L → `5V_PROTECTED` → `RSH1-PWR1` → `5V_SYS` | POWER-ARCHITECTURE, live graph |
| 3V3 | `U3-PWR2` TPS62913 low-noise buck | POWER-ARCHITECTURE |
| TPS62913 mandatory support | PG open-drain **must** have a pull-up (`R75-PWR2` 10 k); NR/SS **must** have its cap (`C10-PWR2`) | **D-045(a)** |
| LED branch protection | `U17-PWR2` **TPS2561** dual current-limited switch, `RILIM-LED` ≈ 59 kΩ, separate `LED_PWR_L_EN` / `LED_PWR_R_EN`, separate `LED_FAULT_L_N` / `LED_FAULT_R_N` | live graph. **Replaced a previous TPS2594-class `U4-PWR2` — see C.6** |
| Mic rail | `U5-PWR2` TLV75533 → `3V3_MIC_REG` → `Q1-PWR2` P-FET → `3V3_MIC`; enable `MIC_PWR_EN_N` from `U6-RTC.J11` | live graph, `contracts/microphone-interface.md` |
| RT power switching | **`remote_rt_power_switch: NOT_BASELINE`** | **D-021** ⚠ see G.1 |
| Board | 1.60 mm, **six layers**. 8 is evidence-triggered escalation; 10 rejected | D-012, D-022 |
| Stackup | `JLC06161H-3313` — **PREFERRED CANDIDATE, NOT ORDER-FROZEN** | `project.yaml` |
| Thickness change | **No agent may set the board to 0.8 mm.** Only a D-012 amendment can change thickness | D-050 |

### A.4 Audio

| Item | Current state | Source |
| --- | --- | --- |
| Architecture | **DUAL-INPUT**: switched stereo 3.5 mm AUX **plus** IM69D130 PDM room mic, both through one `U11-AUD` TLV320ADC6120 | **D-051** |
| Simultaneity | AUX-L + AUX-R + ROOM-MIC captured **simultaneously** | D-051 |
| Bus | 48 kHz, four 32-bit TDM slots: 0 = AUX_L, 1 = AUX_R, 2 = ROOM_MIC, 3 = reserved | D-051 |
| PDM XOR | Microphone-lane alternate **only**. `R38`/`R39` 0R FIT → ADC; `R40`/`R41` DNP → RT1062 | D-051, live graph |
| Direct-PDM host | **RT1062**, not ESP32-S3. The EVAL board's ESP32 route is not copied | D-051 |
| Clock master | RT1062 default; **external override REQUIRED** with isolation on MCLK/BCLK/FSYNC | D-013 |
| PDM decimation | **RT1062 has no MICFIL and no hardware PDM decimator.** SAI + DMA + software decimation. 3.072 MHz → 48 kHz full-width is an **experiment**, not a datasheet feature | **D-017** |
| Jack MPN | **UNBOUND.** `PJ-3537S-SMT` / `C2689709` is EVAL reference only, status PINOUT-VERIFY | D-051 |
| **Live sheet state** | **PDM-only. AUX is ABSENT from the electrical graph.** This is a migration gap, not a rejection | D-051, `STATUS.md` |

### A.5 NFC

| Item | Current state | Source |
| --- | --- | --- |
| Part | ST25R3916B, 27.12 MHz crystal | `contracts/nfc-interface.md` |
| Front-end location | **K1 carrier-side, frozen independent of B/C.** Only I2C_SDA / I2C_SCL / NFC_IRQ may cross SSCM-1 | D-009 |
| Host | ESP32-S3 | ownership matrix |
| I2C_EN strap | **High selects I2C. Floating is not a valid strap.** `R76-NFC` 10 k to 3V3. No-connect **forbidden** | **D-046** |
| Internal regulator rails | `VDD_A`, `VDD_D`, `VDD_RF`, `VDD_AM`, `VDD_DR`, `AGDC` are **OUTPUTS**. Never drive them. Each carries 2.2 µF (`C92`–`C97`) | **D-047** ⚠ see G.4 |
| Matching | Fixed. Values `TUNE_TBD` until the real antenna, lead and installation are characterised | `contracts/nfc-interface.md` |
| Antenna | External, remote, on a U.FL coaxial lead (`J10-NFC`) | live graph, memory |

### A.6 LED

| Item | Current state | Source |
| --- | --- | --- |
| Channels | **Two, electrically and logically independent** | `contracts/led-interface.md` |
| Owner | **RT1062.** `J2-LED` / `J3-LED` belong electrically to RT1062, not the S3 | D-001, `contracts/led-interface.md` |
| Level shift | Required 3.3 V → 5 V. `U14-LED` / `U15-LED` SN74AHCT1G125 | `contracts/led-interface.md` |
| Data path per channel | `U6-RTC.D7` → `LED_D0_3V3` → U14 → `LED_D0_5V` → `R51` 33 Ω → `LED_D0_J` → `J2-LED.2`. Mirror for D1/U15/R52/J3 | live graph |
| Series R value | `R51`/`R52` **must be re-stamped `TUNE_TBD`** — 33 Ω is a donor-circuit number, not derived (RQ-054) | REPAIR-QUEUE |
| Thermal feedback | `RT1-LED` / `RT2-LED` NCP15XH103 NTC + `RNTC_L/R-LED` bias to 3V3 → `U6-RTC.L12` / `K12` | live graph |
| High-current copper | Deliberate regions with via arrays, **never router-default traces** | `contracts/led-interface.md` |
| **LED part** | **WS2816C, 1313 body, 160 per channel, two channels. Never full white.** Captain, 2026-08-30 | ⚠ **not yet in any repo document** — see F.9 and J.2 |

### A.7 Motion, debug, validation

| Item | Current state | Source |
| --- | --- | --- |
| IMU | LIS2DH12. Default owner **RT1062**; explicit 0R/DNP ownership matrix (`R44`–`R49-MOT`) so it can be assigned to either MCU but **never both as masters** | `contracts/motion-interface.md` |
| Mount | Rigid section near the assembled structural centre — not board edge, connector tongue or cantilever | `contracts/motion-interface.md` |
| Debug fabric | D13.1. **REQUIREMENTS ONLY** — no circuit, no MPN, no final GPIO | **D-018** |
| RT boot | Passive default is Internal Boot via external straps, no firmware. `BOOT_MODE[1:0] = 10` | D-020, debug-fabric |
| RT recovery line | **One logical line** (`OPT_BOOT_REC_RT`), decoded target-side into both boot-mode bits. **Raw boot-mode bits are never exported across a connector** | debug-fabric |
| POR_B | Wired-OR of supervisor + manual + S3 request. **S3 may assert low or release high-Z. It must NEVER drive POR_B high** | debug-fabric |
| SWD | Fitted 10-pin 1.27 mm Cortex header (`J4-RTDBG`). **Never proxied through the ESP32-S3** | debug-fabric |
| GPIO | **No GPIO assigned anywhere.** Pinmux is not frozen (D-031). K1 firmware is GPIO-agnostic and always has been | D-031, memory |

### A.8 Process and execution (governs how any agent may act)

| Item | Current state | Source |
| --- | --- | --- |
| Schematic sheets | **Exactly one.** Hierarchical or per-domain sheets **forbidden**. If one sheet fails, the response is **not** to add sheets — stop and report | **D-010**, AGENTS.md |
| Net labels | Identification and long-distance readability only. **Must never conceal the power tree.** No "net-label schematic" | AGENTS.md, memory |
| Canonical project | `64325d0e55e0435abd018defb0089a9b` (`spectrasynq/K1-Core-Val-R0`) | project.yaml |
| EasyEDA host | **3.2.149** (`.epro2`, V3 typed-record grammar). Archived 2.2.40.8 client opens **pre-migration backups only** and must never be pointed at the migrated project | **D-045(b)** |
| Source parsers | All positional (V2) parsers are **OUT OF SERVICE** and fail closed. Use `harness/easyeda_source_format.parse_records_any_format` for read-only analysis | D-045(b) |
| Mutation gate | **Mandatory.** Every EasyEDA write begins, records semantic read-back and closes visual evidence through `harness/easyeda_mutation_gate.py`. Direct calls that bypass it are forbidden | **D-038**, **D-039** |
| Per-write evidence | Snapshot + semantic read-back + **settled, granular screenshot** before the next write. **A source/count PASS cannot override a failed screenshot** | D-037, D-038 |
| Transaction granularity | One complete circuit block, one visual stage. Placement, designation and wiring are **separate transactions** | D-038 |
| `FROZEN_INCIDENT` | Absolute stop, **no automatic release path**. Another active agent is **not** sufficient evidence of an ownership incident | **D-040**, **D-041** |
| Harness doctrine | Create a check when the artefact it checks first exists. **A checker that inspects nothing must never print PASS** | **D-015**, AGENTS.md |
| Gates open | `JLC_SCH_READY = OPEN` · `G2_1_OFFICIAL_FREEZE = BLOCKED_BY_HUB_ERC_PHASE_K` · `JLCPCB_LAYOUT = BLOCKED_BY_SCHEMATIC_PRESENTATION` | STATUS.md |

---

## B. SUPERSEDED / STALE — must not be resurrected

Everything here **used to be true**. A fresh agent reading an old file, an old render or the stale
`.epro2` will find these and may reasonably think they are current. They are not.

### B.1 Tombstoned — never valid, must not be recreated

| Item | Why it is a tombstone |
| --- | --- |
| **`15 × 7 mm` ESP32-S3 antenna keepout rectangle** | Espressif's 15 mm is an **end-product clearance recommendation** in free space between antenna and enclosure/metal. Converting a one-dimensional clearance into a two-dimensional PCB keepout **invented a second dimension no source states**. Do not recreate it, and do not replace it with a different invented rectangle |
| **Four-screw mounting default** | Adopted as habit, never derived from a load case. Replaced by a three-point determinate triangle plus a **passive** fourth support (not a screw) |
| **Short-edge USB-C placement** | Inherited assumption, never tested against escape pressure, the RF zone or the insertion-load path |
| **"Six layers preserves JLCPCB Economic PCBA eligibility"** | Factually void. Economic is single-sided placement only; authorised double-sided placement commits the board to Standard PCBA at any layer count |
| **The `800 − 350 = 450 µm` BGA channel calculation** | The 350 µm PCB land was **invented from a solder-ball specification**, and 450 µm is exact-fit with zero surplus |
| **"Single USB owned by ESP32-S3, RT1062 data only across K1BR"** | Tombstoned. D-049 explicitly states it does **not** revive this |

### B.2 Superseded architectures

| Was | Now | Note for a fresh agent |
| --- | --- | --- |
| Monolithic ESP32-S3 | Dual-MCU RT1062 + S3 | S3-monolithic survives **only as the legacy parity oracle** for firmware diffing |
| SSCM-1 pin map v1.0 "frozen" | **UNRECOVERED_UNFROZEN**; v2 is a requirements-driven replacement | A contract that cannot be located is not frozen. Bounded recovery is **COMPLETE_NOT_FOUND**; no further recovery is authorised while Option B is deferred |
| `J7-ESP` second USB-C | Deleted by D-049 | **Present in the stale `.epro2` and in the D01 designator list as `J1-USB4105-RETIRED`.** Its presence proves nothing |
| `J1` = USB4105-GF-A | `GT-USB-7005A` / C5250872 | The retired USB4105 symbol is **still on the sheet, still on legacy nets, 0/28 wired on the new part** |
| Two USB-C receptacles (D-044) | One (D-049) | D-044 stays in the register as history |
| Option B "interface budget PASSES B2 59/67" | **WITHDRAWN** (D-033) | The study used an invalid carrier/module power boundary, inconsistent signal counts, carrier-local B1 crossings and heuristic return/shield allocations with no physical pin assignment |
| "Option C escapes cleanly on six layers" | `OPTION_C_BGA_ESCAPE = OPEN` | Ring capacity is **not** an escape proof |
| `MIMXRT1062DVJ6A` | `DVJ6B` | A revision is NRND |
| 1.00 mm board | 1.60 mm, six layers | The 1.0 mm assumption is dead; **no agent may infer 1.0 mm from the presence of a MEMS microphone** |
| Three parallel envelope studies (105/115/125 mm) | One contraction study | |
| 21-script bootstrap harness | Two non-vacuous checks at VAL-G0 | Checks written before their artefacts exist become stubs, and stubs pass |
| `check_architecture_ownership.py` ported from firmware | `check_authority_consistency.py` | The firmware scanner finds **no source files** in a hardware repo, iterates over nothing and **passes vacuously**. Do not port it |

### B.3 Retired components and nets still visible on the sheet

| Artefact | Status |
| --- | --- |
| `J1-USB4105-RETIRED` | Parked, still bound to legacy nets. Not the connector |
| `J7-ESP` (USB4105) | Deleted by D-049. Present only in the stale `.epro2` |
| `U4-PWR2` (TPS2594-class LED eFuse) + `R8-PWR2` 3.48 kΩ | **Deleted.** Replaced by `U17-PWR2` TPS2561 + `RILIM-LED`. Every audit written before 2026-08-29 that discusses "U4-PWR2" or "R8-PWR2 = 3.48 kΩ" is describing a part that is no longer on the board |
| `CS35`, fixture orphans, padding primitives | Removed during the canonical takeover |
| Qualification project `09e9c541fd3d404082d4b92e55ae5336` | Destroyed, empty shell, **receives no further mutation** |
| Everything from the rejected fixture — primitives, topology, generators, layout | **May not be reused in any form** |

### B.4 Terminology traps

| Trap | Rule |
| --- | --- |
| `AP` | **Audio Processing only.** Wi-Fi access point is `WIFI_AP` / `SOFTAP` / `ACCESS_POINT`. The bare phrase "AP-only radio bridge" is forbidden in every authority document and guard |
| "the processor" / "the MCU" / "the chip" | Forbidden where ownership matters. Write `RT1062` or `ESP32_S3`. **Ownership language that does not name a part is not authority** |
| "dual audio" | Means **AUX + PDM**, the D-051 dual-input architecture. It does **not** mean the PDM ADC-vs-direct XOR, which is a microphone-lane implementation comparison |
| `[quoted-superseded]` | A line legitimately quoting banned text. `check_terminology.py` honours the marker and reports the count so an exemption cannot hide a violation |

---

## C. FAILED ATTEMPTS AND REVISION LESSONS

These are the expensive ones. Each cost real time and produced a written rule.

### C.1 The K1-CORE geometry that was declared finished and then abandoned

**Tried.** `k1_core` was declared design-finalised on 2026-08-18, then converted to six layers /
1.60 mm on 2026-08-27.

**Failed.** Captain judged the routing "disgusting"; schematic pages were effectively empty — it was
a **board-only artefact** with copper but no schematic authority; copper was only partially re-widened.

**Learned.** A PCB whose schematic is empty cannot be reasoned about, reviewed, or corrected — only
redrawn. Layout-first is how you end up with a board nobody can defend.

**Decision.** `k1_core` archived as `LEGACY_SNAPSHOT_DO_NOT_FAB` / `DO_NOT_IMPORT_COPPER`. K1-CORE-VAL-R0
is **schematic-authoritative**: no PCB-only electrical component may exist without schematic authority.
**Do not import legacy K1 copper** (AGENTS.md hard rule).

### C.2 KiCad — abandoned twice

**Tried.** Migrating the design to KiCad; then importing EasyEDA → KiCad.

**Failed.** Converter failures; and more decisively, **Captain cannot operate KiCad at all** and needs
to personally move components and tighten routing.

**Learned.** Tool choice is constrained by who does the work, not by tool quality.

**Decision.** EasyEDA Pro is the final EDA authority (AGENTS.md). This is not reopenable on technical
merit.

### C.3 The VAL-G2.0 qualification fixture — rejected twice, then destroyed

**Tried (attempt 1).** A generated single-sheet fixture to prove EasyEDA could hold the whole design:
200 symbols, 120 unique net names, 10 repeated rails, one page.

**Failed.** It optimised the **thresholds** rather than representing the architecture. 132 of 200 symbols
were passives; four ADCs, four USB-C connectors, two NFC controllers, four accelerometers — quantities
tied to nothing. The 120 "unique nets" were **one-endpoint dangling stubs** attached to passive pin 1.
The 10 "high-fanout rails" were round-robin passive attachments with **no source and no real load**.
Neither processor appeared in the net-generation set.

**Tried (attempt 2), after a Captain-ordered destructive reset.** An automatic role-count placement.

**Failed identically** at 81/353 components — repeated symbol grids, bottom-loaded composition, no
circuit topology. Stopped by its first mandated screenshot and fully removed.

**Learned — and this is the deepest lesson in the project.** The root cause was **not** a bad agent
judgement and **not** an EasyEDA defect. It was a **control-system defect**: VAL-G2.0 had no
fail-closed, executable fixture-definition gate, so an unresolved Option-C estimate was silently
replaced by the numeric floor, and the available evidence oracle measured **persisted primitive counts**
rather than electrical representativeness. *"A source read-back could prove that 200 symbols and 240
wire stubs persisted while remaining unable to prove that a single signal had two meaningful endpoints."*

**Decisions.** D-035 (split fixture definition from EDA execution), D-036 (destructive reset), D-037,
D-038 (executable mutation gate), plus the standing rules: an unresolved estimate is a **hard stop**,
never defaulted; one-endpoint named nets, passive-only fanout, unpowered major ICs and stub-only wiring
plans all **fail**; a whole-sheet visual checkpoint precedes bulk population; **API success is not
evidence of board correctness**.

### C.4 Building agent graded its own homework — the DualMCU firmware audit

**Tried.** A DualMCU firmware harness reporting "3 PASSING / on track".

**Failed.** An independent second review returned **REQUEST CHANGES**. There was **no integrated
production firmware at all** — the harness built separate probes and printed a collective PASS. The
microphone fed **zeros** into GDFT (window filled forwards, GDFT read backwards). The 82-byte SPI slot
**violated the ESP32-S3 64-byte non-DMA limit** and was physically invalid but invisible to
cross-compilation. The FastLED adapter never emitted. Every prior green inherited a false signal.

**Learned.** Green gates decoupled from working artefacts — a map/territory failure. **Permanently
separate build-role from verify-role.**

**Decision.** This is the ancestor of the whole VAL evidence doctrine: builder and verifier roles stay
separate (AGENTS.md CopperPilot section), self-asserted gates are replaced by differential, mutation,
post-link and provenance gates, and **CopperPilot's PASS claims are proposals until independently
reproduced**.

### C.5 CopperPilot's ten domain renders

**Tried.** A CopperPilot.ai agent produced 10 per-domain schematic renders of K1-CORE-VAL-R0.

**Failed.** An independent audit judged **all ten electrically faulty or stale**.

**Learned.** A rendering agent will faithfully draw a broken source.

**Decision.** Captain had the accurate versions reproduced **directly from the `.epro2` source**, and
established the standing rule now in `/preferences.md`: *"reproduce the accurate versions"* of a faulty
design means produce the **corrected** version — never a faithful re-render of the broken source.
CopperPilot is a geometry/architecture reasoning agent, **not** a PCB execution agent, and may never be
both builder and verifier.

### C.6 The LED protection part changed mid-audit

**Tried.** A single TPS2594-class eFuse (`U4-PWR2`, `R8-PWR2` = 3.48 kΩ) feeding `5V_LED_COMMON`, which
split through `FB1`/`FB2` into both branches.

**Failed / superseded.** Replaced on 2026-08-29 by `U17-PWR2` **TPS2561** — a dual-channel
current-limited switch with **separate enables** (`LED_PWR_L_EN` / `LED_PWR_R_EN`), **separate fault
flags** (`LED_FAULT_L_N` / `LED_FAULT_R_N`) and a **single shared ILIM** (`RILIM-LED` ≈ 59 kΩ).

**Learned.** Every power audit written before 2026-08-29 — `PIN-AUDIT-PWR1.md`, `PIN-AUDIT-PWR2.md`,
`power-envelope-rederivation.md`, `REPAIR-QUEUE.md` items RQ-046/047 — reasons about **U4-PWR2 and a
3.48 kΩ ILIM that no longer exist**. Their arithmetic is sound for a part that is gone.

**Decision.** Not yet in the register. The change happened, the audits were not re-run. **This is the
single largest stale-analysis trap in the repo.**

### C.7 Three rulings that lived only in Python string literals

**Found.** Three real design rulings — PG must not be tied off; I2C_EN high selects I2C; ST25R3916B
regulator rails are outputs — existed **only as prose inside `schematic/repair_pullup.py` and
`schematic/repair_nfc_regulator_caps.py`**.

**Failure mode.** *"A ruling stored in executable prose sits at precedence level 6 while carrying
level-2/level-4 authority, so it is invisible to every authority check, cannot be superseded by the
documented mechanism, and dies with the script that quotes it."*

**Decision.** Promoted to D-045(a), D-046, D-047 and written into `architecture/POWER-ARCHITECTURE.md`
and `contracts/nfc-interface.md`.

**Standing lesson for a fresh agent:** when you find a design fact in a script, a comment or a commit
message, **it is not authority and it is about to be lost.** Promote it.

### C.8 The concurrency incident — containment was wrong

**Tried.** A second EasyEDA agent was observed mutating the live project. It was classified as an
unowned ownership incident and the lane was frozen.

**Failed.** The operator was **Captain-authorised**. The containment decision was wrong.

**Learned.** Concurrency alone does not establish unauthorised ownership.

**Decision.** D-041. `FROZEN_INCIDENT` is reserved for genuinely unresolved live-session ownership, has
**no automatic release path**, and **must never obstruct a Captain-authorised operator** (AGENTS.md).

### C.9 The mezzanine / B2B joint iteration (mechanical, K1 FE lineage)

**Tried, in order.** A 12-pin board-to-board connector between the USB-C breakout and main board →
rejected (too tall, collides with the rear cover, under-side placement makes assembly extremely hard).
Then a through-hole mezzanine joint. Then a 7.00 mm seat drop.

**Failed.** The 7.00 mm drop was invalid — the V-hull is too narrow there; it broke the bracket blocks
and the centre bolt tower.

**Learned.** Mechanical envelope constraints kill electrical/connector ideas late and expensively. The
enclosure is a first-class input, not a downstream consumer.

**Decision.** B2B joint LOCKED as Option A (1 × 12 THT pin strip, soldered both ends, permanent, 6 mm
overlap); USB-C reach solved by a recessed well + interior plinth in the cover, seat back at V13-native
Z 12.94. **This lineage belongs to K1 FE, not to VAL-R0** — recorded so a fresh agent does not
rediscover the mezzanine idea and re-propose it.

### C.10 The separate microphone breakout board

**Tried.** A dedicated dual-IM69D130 microphone daughterboard with a cabled connector; PCB3 was built
and bench-tested.

**Failed / retired.** Three PCBs is avoidable BOM cost; and first PDM bring-up under music read raw_i16
peaks of ~31 (sub-SSL) — the initial IM69D PDM firmware was judged not up to the task.

**Learned.** The acoustic path and the firmware gain ladder are coupled; a breakout does not remove the
firmware problem.

**Decision.** Mic architecture locked 2026-08-14: IM69D130 **on the main PCB**, top face, Ø0.8 port
through the board, gasket + cover pedestal. On VAL-R0 it arrives on a flex (`J9-AUD`, FH12-10S) with
`3V3_MIC_FLEX`.

### C.11 The calibration poisoning incident (firmware, but it explains hardware intent)

**Happened.** An agent ran `start_noise_cal` **during music**, poisoning `SWEET_SPOT_MIN_LEVEL`
281 → 745.

**Decision.** The Calibration Command Policy and the Phase-B admission gates exist because of this.

**Why it matters to hardware.** It is the origin of the design instinct that **calibration must be
armed, bounded, and disarmable** — and it is why `TMP1826`-class board-local calibration storage with
an explicit revision is attractive: a poisoned coefficient must be identifiable and replaceable, not
silently inherited.

---

## D. REPEATEDLY CLOSED QUESTIONS — do not reopen without new evidence

Each of these has been argued to a conclusion at least once, several of them twice or three times.
Reopening any of them costs a day and, historically, has produced the same answer.

| # | Question | Closed as | Closed | Reopen only if |
| --- | --- | --- | --- | --- |
| D.1 | Monolithic S3 vs dual-MCU | Dual-MCU | **Twice** (2026-08-24, D-003) | Fresh **current-silicon measurement** disproves the compute wall. Note: shipping headroom has **never actually been measured** post int64-GDFT — see J.6 |
| D.2 | Option B vs C | Option C, B deferred | D-024; B re-litigated and its PASS withdrawn by D-033 | Option B is revived by Captain, and then the interface budget must be **re-derived from scratch** |
| D.3 | USB receptacle count and ownership | **One**, hub-based | **Three times**: D-014 → D-044 → D-049 | Nothing short of a Captain ruling. The S3-owns-the-only-USB variant is separately tombstoned |
| D.4 | Board thickness | 1.60 mm | D-012, defended against D-050 connector pressure | A **D-012 amendment**. No agent may set 0.8 mm |
| D.5 | Layer count | 6 baseline | D-022 | Evidence triggers escalation to 8. 10 is rejected |
| D.6 | RT1062 package | `DVJ6B` FROZEN | D-028 | — |
| D.7 | Schematic sheet count | Exactly one | D-010, D-011 | **Never by adding sheets.** If one sheet fails, stop and report |
| D.8 | Wireless control plane | BLE-MIDI only | D-007, reaffirmed 2026-08-27 | A later ownership list is **not** a superseding ruling |
| D.9 | RT1062 PDM decimation | No MICFIL. SAI + software | D-017, NXP primary source | — |
| D.10 | `AP` meaning | Audio Processing only | D-006 | — |
| D.11 | Voice PE as a K1 mapping | Patterns-only specimen | D-043 | — |
| D.12 | Third MCU | Forbidden | D-019 | — |
| D.13 | Antenna keepout rectangle | Tombstoned | 2026-08-28 | Never. It was never valid |
| D.14 | **Power envelope / current budget** | Re-derived twice; **third pass 2026-08-30** | See D.15 | Only with a **measured** figure |

### D.15 The power-envelope question specifically — the four-way distinction

This has been argued three times and each pass found the previous one circular or incomplete. The
distinction the brief asks for, stated so it cannot collapse again:

| Class | Value | Status | Where it comes from |
| --- | --- | --- | --- |
| **Theoretical electrical maximum** | **4.000 A** LED (both channels, 160 × WS2816C-1313 at 11.5 mA combined + 1.0 mA IC each) **+ 0.947 A** non-LED coincident peak = **4.95 A** | Datasheet-bounded worst case | Worldsemi WS2816C-1313-4P V1.1 max column; Opus report §0.1, §3 |
| **Credible validation workload** | The same 4.95 A, **deliberately commanded**, from a bench supply, to characterise the LED system at full output | This is a **required experiment**, not an accident. It is why the bench path exists | Opus report §3.5, E-11 |
| **Normal product workload** | **Never full white on either or both channels** (Captain, 2026-08-30). Realistic duty is **unmeasured** | ⚠ **The actual number does not exist yet.** E-11 is the experiment that produces it | Captain ruling; Opus E-11 |
| **Intentionally prohibited operating states** | Full white on USB power; LED rails enabled below the 3.0 A source tier; NFC and radio TX on a Default-USB source | Enforced in **hardware**, default-deny, before firmware runs | Opus §J, §3.6 |
| **Source-policy limits** | Type-C advertises exactly three at 5 V: **Default 500 mA · 1.5 A · 3.0 A**. Board must **enumerate and stay diagnostically alive on Default** | Captain ruling 2026-08-30: "anything, degrade gracefully" | Captain; USB Type-C R2.0 |

**The historical trap, stated so it is not repeated:** the inherited figures were `2.35 A trunk /
0.95 A LED / 0.60 A 3V3`. The 2026-08-28 re-derivation found that **the 0.95 A "LED branch" was the
eFuse ILIM setting read back**, not a load derivation — *"the design input and the thing it was
supposed to constrain are the same number."* That circularity survived because nothing on the board
determines the LED load: the strips are off-board on 3-pin XH headers. **The only way to break the
circle was to ask what is actually on the strip**, which happened on 2026-08-30 and moved the LED
ceiling by **4.2×**.

**Rule:** never again state an LED current figure without naming which of the five classes above it
belongs to.

---

## E. NON-OBVIOUS DESIGN INTENT

Decisions whose rationale is invisible in the electrical graph.

| Element | Looks like | Actually is |
| --- | --- | --- |
| `R44`–`R49-MOT` 0R/DNP pairs | Redundant option resistors | The **ownership XOR**. The IMU may be assigned to RT1062 or ESP32-S3 during validation but must **never be electrically enabled to both as uncontrolled masters**. The XOR is the enforcement |
| `R40`/`R41-AUD` DNP + `R38`/`R39` 0R | Unpopulated parts | The **PDM route XOR**. FIT default is ADC-PDM; direct-RT is the DNP alternate. The XOR exists so both routes can **never load the PDM bus simultaneously** |
| `R34`–`R36`, `R56`/`R57-VAL` 0R/DNP around `AUDIO_MCLK` | Series resistors | The **external audio clock override** (D-013). The validation board must be able to accept a laboratory clock with RT1062 outputs isolated. `J8-AUD` is the external clock entry |
| `TP7-AUD` "BCLK TP", `TP8-AUD` "FSYNC TP" | Random test points | Deliberate clock observation for the audio-interference matrix |
| `SW1-RTC`, `SW2`/`SW3-ESP`, `SW4-VAL` | Buttons | Reset / boot / recovery controls destined for a **recessed side service bay** so they cannot be actuated accidentally on a board that will be handled repeatedly |
| `OPT_BOOT_REC_RT` — one net, D10 → D03 | An unremarkable control line | The **single logical recovery request**. Raw `BOOT_MODE[1:0]` bits are deliberately **never** exported across a connector; the target decodes one line into two bits locally |
| `POR_B` with three sources | Over-engineering | Wired-OR of supervisor + manual + S3. **S3 may pull low or release high-Z; it must never drive high**, because the supervisor must be able to hold reset until supplies are stable and nothing may override that |
| `F6_VALIDITY_SOURCE = 5V0_USB_VALID`, not `5V_PROTECTED` | An arbitrary rail choice | The eFuse OVLO sits near 6 V while NXP's `USB_OTG1_VBUS` **absolute maximum is 5.50 V**. Feeding F6 from `5V_PROTECTED` would put a legal post-eFuse voltage above an absolute maximum. `U22-USB` TPS7A2550 exists to close that gap |
| KILL-B (TLV7031 + dual AND) | Extra logic | `VBUS_DET` falling does **not** guarantee `PRTPWR` falling. An **independent `5V_USB`-presence kill is mandatory** — the hub's own signalling is not a host-unplug detector |
| `NON_REM[1:0] = 10` via **resistors** | A strap detail | Sampled at reset. It changes **descriptors** and **does not remove the need for a VBUS circuit** — it is not the self-powered/embedded-device argument, and D-049 says so explicitly |
| USB2422 in **strap** mode | A configuration convenience | In SMBus mode the hub *"waits indefinitely for the SMBus code load"* — no USB for **either** processor until S3 firmware is healthy. Strap mode is chosen to keep USB access independent of firmware |
| `C43`/`C44-ESP` 100 pF DNP | Spare filter positions | USB2422 **errata Anomaly 2**'s stated workaround (downstream DP/DM loading against FS adjacent-port disconnect corruption) |
| `RUSB_S3_DP_TUNE` / `_DM_TUNE` | Series terminations | S3 PHY tuning at GPIO20/19. **XOR 0R is path-select only and is not a substitute for TUNE** |
| `J12-USB` + `R94` FIT / `R95` DNP | An unused header | The S3 USB XOR recovery path, **mutually exclusive with DN2**. True XOR — never fit both |
| `J6-ESP` 1 × 6 | A debug header | **Mandatory brick-proof path.** Espressif states USB recovery can become unavailable depending on application configuration. A dead or misconfigured hub must not brick the S3 |
| `RSH1-PWR1` + `RINA_P` / `RINA_N` / `CINA_DIFF` | A shunt and some filtering | The **reference measurement** the whole board's telemetry will be calibrated against. Kelvin routing is a stated requirement, not a nicety |
| `C92`–`C97-NFC` 2.2 µF ×6 | Generous decoupling | Six **internal regulator outputs**, each requiring its own decoupling, matching the STEVAL reference. Driving any of them back-drives a regulator |
| `L4-RTC` 4.7 µH + `1V15_CORE` | An external buck | The RT1062's **internal** DC-DC. `DCDC_PSWITCH` sequencing (≥1 ms delay, 5–15 ms RC) is an NXP **"must"** |
| `RNTC_L/R-LED` bias resistors | Pull-ups | Without them the NTC divider has **no excitation** and firmware reads a plausible-looking number that means nothing. Added by RQ-042 after the failure was found to be **silent** |
| Board may grow east-west | Sloppiness about size | Deliberate. Area is explicitly subordinate to correctness; the board grows wherever more area materially improves RF, SI, PI, EMI, thermal, routing, measurement access or experimental flexibility |
| Single schematic sheet | A stylistic preference | The board exists to reason about **domain interactions**, which sheet ports and hierarchy conceal |
---

## F. KNOWN STALE ARTEFACTS

Files and sections that lag current architecture. Each carries the condition under which it may be
trusted.

| # | Artefact | Lags what | Trust condition |
| --- | --- | --- | --- |
| F.1 | **`K1CoreValR0.epro2`** (the supplied export) | Everything from D-049 onward | **NON-AUTHORITATIVE. Establishes nothing.** It still contains `J7-ESP`, no USB2422, no CC ADC tap, no INA input filter, no NTC bias, no `U17-PWR2`, no hub support, and 229 symbols against a live 287. Useful only as a symbol/value cache |
| F.2 | `schematic/visual-reference/**` (SVG/PNG sheets, `REGISTERS.md`, `domains.json`, `inventory.json`, `reconciliation.json`) | Nothing — it is the **freshest machine-readable capture** (`G2.2-HOLD-REOPEN.source.txt`, hub-era) | Self-declared **`STATUS = STUDY_INPUT / BINDING = NO`**. It is a **visual construction reference, not an EasyEDA schematic**, nothing in it is importable, and **the Captain is the sole EasyEDA schematic author**. Trust its **net data**; never treat its sheets as drawing authority |
| F.3 | `architecture/POWER-ARCHITECTURE.md` power tree diagram | Shows a single "LED eFuse → +5V_LED_L / +5V_LED_R" split; the board now has `U17-PWR2` TPS2561 with two independently-enabled switched outputs. Also still carries the inherited `2.35 / 0.95 / 0.60 A` figures as "design input to be re-derived" | The **D-045(a) TPS62913 section is current**. The tree diagram and the current figures are stale |
| F.4 | `evidence/.../power-envelope-rederivation.md` §2, §4, §5, §6, §7 | Written against `U4-PWR2` + `R8-PWR2` 3.48 kΩ (**deleted parts**) and before the LED spec existed. Its 0.958 A LED ceiling is **4.2× below** the real load | **§2's finding that the 0.95 A figure was self-referential is permanently valid and important.** Its numeric conclusions are superseded |
| F.5 | `evidence/.../PIN-AUDIT-PWR1.md`, `PIN-AUDIT-PWR2.md`, `PIN-AUDIT-LED.md`, `PIN-AUDIT-*` | All written against frozen hash `489736:464c27d4` — **pre-hub, pre-`U17`, pre-CC-tap** | Their **defect findings** remain valid unless the part changed. Their **arithmetic** on `U4-PWR2`/`R8-PWR2` describes deleted parts |
| F.6 | `evidence/.../REPAIR-QUEUE.md` | Same vintage. RQ-046/047 concern `R8-PWR2`, now gone | Items not tied to deleted parts (RQ-022 INA filter, RQ-024 buck R2, RQ-042 NTC bias, RQ-054 `TUNE_TBD`, RQ-057/060 displacement) are **live and mostly still open** |
| F.7 | `evidence/.../canonical-core-val-r0/TAKEOVER-RECEIPT.md` | Explicitly **historical**; its "remaining DRC" list is closed by D-045/D-047 | Left unedited **on purpose** as the record of what was true at takeover |
| F.8 | `experiments/val-g1-study/P2-B-VS-C-STUDY.md` | Its B2 59/67 PASS is **withdrawn by D-033** | Evidence only |
| F.9 | The **entire repo** on the subject of the LED part | **No document anywhere in K1-CORE-VAL-R0 names WS2816C as the LED.** The only WS2816C mentions are D-043 and its supersession, both listing it as **non-authoritative Voice-PE mapping material** | ⚠ A fresh agent reading D-043 could reasonably conclude WS2816C is **retired**. It is not — see I.7 |
| F.10 | `authority/01-DECISION-REGISTER.md` | ⚠ **Contains two different decisions both numbered `D-045`** — the TPS62913 support components (2026-08-28) and the EasyEDA 3.2.149 host migration (2026-08-28) | Both are RATIFIED and both are real. Cite them as **D-045(a)** and **D-045(b)** until renumbered. **This is an authority-layer defect that should be fixed** |
| F.11 | `contracts/debug-fabric.md` front-matter `remote_rt_power_switch: NOT_BASELINE` and `project.yaml` `remote_rt_power_switch: NOT_BASELINE` | The 2026-08-30 CTO position asks for RT hard power-cycling | ⚠ See **G.1** — this is the live conflict, not a stale file |
| F.12 | `STATUS.md` | Current as of 2026-08-30 and **explicitly says** the live sheet is PDM-only and `JLC-SCH-READY` is OPEN | Trustworthy. Read it before anything |
| F.13 | `archive/` | Anything in it | **Evidence only, never authority** (precedence level 8) |
| F.14 | `docs/agent/VOICE-PE-SPECIMEN-VAL-R0.md` | Voice PE extraction | Patterns-only under D-043. Its §5 mapping is historical |
| F.15 | Amended/superseded register entries: **D-014, D-025, D-026, D-027, D-030, D-032, D-035, D-036, D-044** | Each carries its successor in the Status column | Read the Status column **before** quoting any decision |

### F.16 — Live defects visible in the current capture, unclosed

These are in the **current** graph, not stale artefacts, and neither architecture report caught them
because both worked from rail-level views rather than the full pin map.

| Defect | Evidence | Severity |
| --- | --- | --- |
| **`U1-PWR1.9` (eFuse ILM) is bound to `USB_DP_UP`**, while `R1-PWR1` dangles alone on `USB_EFUSE_ILIM` | **CONFIRMED 2026-08-30 by independent geometric re-derivation — see Addendum K.** **REPAIRED 2026-08-30** on live HOLD `55ed9ee9` (`g22-pwr1-ilm-repair-2026-08-30`). Canonical `64325d0e` was never defective and was not mutated. The HOLD-REOPEN dump remains the pre-repair witness. | **P0, scoped to G2.2.** This ILM blocker is cleared on HOLD; other G2.2 construction gaps remain. Do not write “K1-CORE has ILM on USB D+” without naming the candidate. |
| `U23`/`U25-USB` supply pins deviate from H0f — V+/GND swapped, PRTPWR2 path grounded | `usb_delta.json` | P0-class |
| USB2422 support unwired: `Y3` crystal, `RBIAS` (R77 12 k), `CRFILT` (C100 1 µF), `PLLFILT` (C101 100 nF), VDD33 pin 1; `NON_REM` straps orphaned | `usb_delta.json`, README | The hub is **placed but not wired** |
| `J1` GT-USB-7005A placed **0/28 wired**; `J1-USB4105-RETIRED` still on legacy nets | README | Connector migration incomplete |
| Same-net series elements a router can bypass: `R85`, `R94`, `R90`, `C123` | `usb_delta.json` | Routing hazard |
| `LED_PWR_L_EN` / `LED_PWR_R_EN` bind only `U17` + a pulldown — **no driver** | `domains.json` | LED enables cannot be commanded |
| `LED_FAULT_L_N` / `LED_FAULT_R_N` bind **only `U17` pins** — no consumer | `domains.json` | Faults go nowhere |
| `LED_OE_L` / `LED_OE_R` bind only the buffer + a pulldown — no controller | `domains.json`, PIN-AUDIT-LED | Boot state indeterminate was the original finding; a pulldown now exists but nothing drives OE |
| `NVCC_PLL_1V1` carries `C72`/`C73` and `U6-RTC.P10` and **has no source** | `domains.json` | ⚠ Unresolved. See J.1 |
| 8 net labels meeting fewer than two pins; ~25 wires meeting no pin | RQ-060 | Drawing-level, tracked |

---

## G. REPORT CONFLICT AUDIT

Classifications: **OPUS HISTORICAL CONFLICT** · **GROK HISTORICAL CONFLICT** · **BOTH** ·
**CURRENT AUTHORITY UNCLEAR**.

> **Grok 4.6 Heavy R0-ARCH-2 was not supplied and is not in the repo (§0).** Every Grok row below reads
> `GROK NOT SUPPLIED`. I have not inferred its contents. This section is complete for Opus and
> **explicitly incomplete for Grok**.
>
> **Re-checked 2026-08-30, second pass — still absent.** Searched: session uploads (one file, the
> `.epro2`); `grep -rl -iE "grok|R0-ARCH-2|ARCH-2"` repo-wide; every file modified in the preceding
> three hours; every path matching `*report*`, `*arch-2*`, `*R0-ARCH*`. The only Grok-related material
> on disk is `_scratch/claude-mem-grok-export/` and `harness/export_claude_mem_for_grok.py` — a
> claude-mem slice exported **to** Grok for browser upload (`generated_at_utc 2026-08-30T08:44:18Z`;
> 324 project observations, 112 deduped query hits, 22 session summaries; queries USB2422 / D-044 /
> D-049 / D-050 / D-051 / NFC I2C). **That is input to Grok, not Grok's report.** The Grok lane of this
> section remains open.

I wrote the Opus report. It gets audited harder than it would if someone else had, not softer.

| # | Issue | Class | Detail |
| --- | --- | --- | --- |
| **G.1** | **RT1062 independent power cycling** | **OPUS HISTORICAL CONFLICT** — the most important one in this audit | **D-021 (RATIFIED, 2026-08-27): "Independent remote RT power switching stays out of baseline R0."** `contracts/debug-fabric.md` states the reasoning: *"once one domain can be powered while the other is not, every cross-domain signal becomes a back-power path and the board stops behaving like the product power architecture. A lab supply or fixture performs cold cycles."* `project.yaml` carries `remote_rt_power_switch: NOT_BASELINE`. **The Opus report ADOPTs it (register #20, #21) and never cites D-021.** The 2026-08-30 CTO position asks for it, and a direct Captain ruling is precedence level 1 — but **no supersession entry exists and the register still says NOT_BASELINE**. **Resolution required: a Captain ruling plus a `05-SUPERSESSIONS.md` entry, or the feature is out of baseline.** Do not implement it on the strength of the report alone |
| G.2 | **Second 5 V inlet (`J-BENCH`)** | **CURRENT AUTHORITY UNCLEAR** | D-049 forbids a second and third **Type-C receptacle**; `architecture/POWER-ARCHITECTURE.md` says *"J1 is the only USB-C and the 5 V inlet."* A bench inlet is not a Type-C receptacle, so D-049 is not literally violated — but the POWER-ARCHITECTURE sentence reads as a **sole-inlet** claim. **A fresh agent could read the split inlet as violating D-049.** Needs one sentence of clarification in POWER-ARCHITECTURE or a register entry |
| G.3 | **NFC `VDD` on 3V3 while `VDD_TX` on `NFC_5V`** | **NOT a conflict — a re-discovery.** See H.3 | Opus flags it as a hard defect. It **is** one. But it was already found on 2026-08-28 (`PIN-AUDIT-PWR1.md` defect #12, `power-envelope-rederivation.md` §3) and handed to "the NFC owner", where it stopped. The Opus report presents it as newly surfaced; it is **previously known and not carried forward** |
| G.4 | **NFC `VDD_AM` XOR pads (2.2 µF ↔ 22 nF for AWS)** | **OPUS HISTORICAL CONFLICT (minor, and correct)** | **D-047 (RATIFIED) specifies 2.2 µF on all six internal-regulator rails including `VDD_AM`**, matching STEVAL. ST AN5806 §1 forbids 2.2 µF on `VDD_AM` **when AWS is used**. Both are true; they describe different modes. The Opus XOR proposal is the right answer but it **amends D-047** and must be recorded as such, not slipped in |
| G.5 | **TPS2561 "contradicts two electrically and logically independent LED channels"** | **OPUS OVERSTATED — partial correction** | TPS2561 has **separate enables** (`LED_PWR_L_EN` / `LED_PWR_R_EN`) and **separate fault flags** (`LED_FAULT_L_N` / `LED_FAULT_R_N`), both present as distinct nets. **Logical independence is satisfied.** What is genuinely shared is the **die, the IN pins and the ILIM resistor** — so a thermal or ILIM fault is common-mode, and the per-channel limit cannot differ. The Opus arithmetic (per-channel 826/949/1067 mA against a 2.000 A load; 2 × max = 2.14 A) **stands and is decisive**. The independence argument should be narrowed to shared-die/shared-ILIM |
| G.6 | **BOM baseline "~250 placements"** | **OPUS FACTUAL ERROR** | The live capture is **287 designators** (`REGISTERS.md` §1). The "≈ +90 on a base of ~250 → ~340" line should read **≈ +90 on 287 → ~377** |
| G.7 | **INA226 moving to a service bus** | **CURRENT AUTHORITY UNCLEAR (no conflict, a gap)** | `U2-PWR1` is currently on the **functional** `I2C_SDA`/`I2C_SCL` (D01 endpoints in the cross-domain register). Nothing forbids moving it, but **no authority document contains a "service plane" concept** — the ownership matrix has no such row. The two-plane split is a **new architectural concept** and needs a decision entry, not just a report section |
| G.8 | **`TPS2052B` EN gated by `RT_PWR_EN`** | **CURRENT AUTHORITY UNCLEAR — integration constraint** | D-049 and GO-NO-GO H0e fix F6-B's control as **KILL-B: TLV7031 + dual AND from `5V0_USB_VALID`**. Adding `RT_PWR_EN` as a third AND term is plausible but **must not weaken KILL-B**, which is a ratified host-unplug safety mechanism. Any implementation must re-prove H0e |
| G.9 | **CC tap topology change (delete `RCC1B`/`RCC2B`)** | **OPUS CORRECT, and the current state is worse than described** | `USB_CC1_ADC_TAP` binds `RCC1B-PWR1.1` + `RCC1S-PWR1.2`, and `RCC1B-PWR1.2` is on **GND** — so it **is** a divider to ground, exactly as Opus says. Additionally the tap node is **dangling** (there is no ADC on the board), which `README.md` lists under "dangling-by-pinmux (D-031, expected)". Both facts are compatible; the divider should still go |
| G.10 | **`TPD4E05U06` replacing `USBLC6-2SC6`** | **CONSISTENT** | D-050 sets `cc_protection: IEC_ESD_ONLY` and specifies "low-C ESD" **without binding an MPN**. No conflict |
| G.11 | **USB2422 strap mode, SMBus DNP** | **CONSISTENT** | Matches D-049 and `contracts/usb-interface.md` ("Strap mode. No EEPROM required.") exactly |
| G.12 | **Rejecting TPS389006 and TPS3435** | **CONSISTENT** | Matches D-015 harness doctrine (don't build a gate before its artefact) and the CTO position. No authority requires either part |
| G.13 | **AAT rejected on ST's coaxial-cable statement** | **CONSISTENT and closes an open item** | `contracts/nfc-interface.md` keeps fixed matching as default with values `TUNE_TBD`. Opus supplies the primary-source reason AAT can never be an option for K1's remote U.FL antenna. This should become a register entry so it is not re-proposed |
| G.14 | **Arrays rejected wholesale** | **CONSISTENT** | D-043 explicitly leaves the LED eFuse 0402 0R bypass **not frozen**; nothing mandates arrays |
| G.15 | **Bidirectional reset `RT → S3_EN`** | **CURRENT AUTHORITY UNCLEAR** | The ownership matrix has `rt_reset_request: ESP32_S3` and `rt_recovery_request: ESP32_S3` — **one direction only**. A net named `S3_POR_REQ` exists (D05 → D10) but is S3-sourced. Adding an RT→S3 reset **reverses a documented ownership direction** and needs a matrix row, not just a report line |
| G.16 | **`NVCC_PLL_1V1` unsourced** | **CONSISTENT — correctly escalated** | Opus flags it as blocking. Confirmed: `domains.json` shows `C72`, `C73`, `U6-RTC.P10` and no source. Genuinely open |
| G.17 | **`R6-PWR2` 32.4 kΩ vs TI's 5 kΩ maximum** | **NOT a conflict — a re-discovery.** See H.4 | Already filed as **RQ-024** on 2026-08-28 with the same SLVSFP4B citation and the same "6.5× over the vendor maximum" phrasing. Opus re-derived it independently, which is a useful confirmation, but it is **not new** |
| G.18 | **Opus report placed in `architecture/`** | **PROCESS NOTE** | `architecture/` is precedence level 5. The report's own front matter says PROPOSAL / not authority, which is correct. **It must not be cited as authority** until entries land in the register |
| G.19–G.40 | *(every Grok claim)* | **GROK NOT SUPPLIED** | Cannot be audited. Supply `R0-ARCH-2` and this section can be completed |

### G.41 — What neither report caught

Recorded because it is the point of this pass.

| Missed item | Why both reports would miss it |
| --- | --- |
| **`U1-PWR1.9` eFuse ILM bound to `USB_DP_UP`** | Both worked from rail registers and contracts. This is a **pin-level** binding error visible only in the full pin→net inventory |
| **The hub is placed but its support network is unwired** (Y3, RBIAS, CRFILT, PLLFILT, VDD33 pin 1, NON_REM straps) | Both treated D-049 as describing a working hub. It describes an **intended** hub |
| **`LED_PWR_*_EN` have no driver; `LED_FAULT_*_N` have no consumer** | Both reasoned about what the enables *should* do |
| **The board has 2 LED data lines; the firmware lane expects 4** | Cross-repo. See J.2 |
| **`D-045` is used twice** | Nobody re-reads a register they are citing from |
| **287 designators, not ~250** | Both anchored on the stale `.epro2`'s 229 |

---

## H. NEW DISCOVERY vs OLD KNOWLEDGE — Opus report claims classified

Honest classification. "Previously known but not carried forward" is not a criticism of the report —
it is the exact failure mode this whole recovery pass exists to prevent, and it means the finding is
**older and better-evidenced** than the report implies.

| # | Opus claim | Classification | Evidence |
| --- | --- | --- | --- |
| H.1 | LED load is 2.000 A/channel, 4.000 A both | **GENUINELY NEWLY SURFACED** | The number could not exist before Captain supplied the strip spec on 2026-08-30. Nothing on the board determines the LED load |
| H.2 | The inherited 0.95 A LED figure was circular | **PREVIOUSLY KNOWN, correctly re-stated** | `power-envelope-rederivation.md` §2 said so on 2026-08-28 in almost the same words. Opus **inherited this finding correctly**; the value of the new pass is that it finally broke the circle |
| H.3 | NFC VDD/VDD_TX ±0.2 V violation | **PREVIOUSLY KNOWN, NOT CARRIED FORWARD** | Found 2026-08-28: `PIN-AUDIT-PWR1.md` defect #12 ("P1, other lane"), `power-envelope-rederivation.md` §3 ("the NFC block cannot operate as drawn"). Handed to the NFC owner. **Never entered the register, never fixed.** Opus re-found it independently. **This is the clearest case in the project of a real defect dying in an evidence directory** |
| H.4 | TPS62913 `R2` 32.4 kΩ vs TI's 5 kΩ max | **PREVIOUSLY KNOWN, IN THE QUEUE, NOT ACTIONED** | RQ-024, 2026-08-28, same citation, same 6.5× figure, priority P2 |
| H.5 | TPS2561 per-channel ILIM ≈ 1.07 A max against a 2.000 A load; 2 × max overruns a 3 A source | **GENUINELY NEWLY SURFACED** | The part landed 2026-08-29, after every power audit. Nobody had re-run the arithmetic |
| H.6 | ≈0.55 A of back-power into an unpowered `3V3_RT`; 22 Ω is not isolation | **REASONING PREVIOUSLY KNOWN, QUANTITY NEW** | `contracts/debug-fabric.md` already stated the qualitative reason for D-021 in 2026-08-27. **Opus supplies the number that was missing** — which is exactly what would justify revisiting D-021, if Captain chooses to |
| H.7 | `DCDC_PSWITCH` RC must drain between power cycles or NXP's ≥1 ms sequencing is violated from cycle 2 | **GENUINELY NEWLY SURFACED** | Not in any repo document. Would have made the feature silently unreliable |
| H.8 | ADS7138 source-impedance limit derived (≈2.86 kΩ) because TI publishes none | **GENUINELY NEWLY SURFACED** | No prior work on this device |
| H.9 | FRAM must be on SPI (829 µs hold-up vs 630 µs I²C write) | **GENUINELY NEWLY SURFACED** | |
| H.10 | AAT impossible with a single-ended antenna on a coaxial cable | **GENUINELY NEWLY SURFACED (ST primary source)** | `contracts/nfc-interface.md` kept fixed matching as default but never gave this reason. **Closes the question permanently** |
| H.11 | AWS requires 10–50 nF on `VDD_AM`, forbidding the ratified 2.2 µF | **GENUINELY NEWLY SURFACED** | Conflicts with D-047 — see G.4 |
| H.12 | USB2422 SMBus mode blocks enumeration until S3 code-loads | **CONSISTENT WITH EXISTING DECISION** | `contracts/usb-interface.md` already specified strap mode. Opus supplies the *reason* |
| H.13 | USB2422 Anomaly 3 caps USB audio | **CONSISTENT** | Already a named hold in D-049 and `ERRATA-HOLD.md`. `usb_audio: EXPERIMENT_ONLY` in the ownership matrix |
| H.14 | Anomaly 2's 100 pF workaround explains `C43`/`C44-ESP` | **PREVIOUSLY KNOWN, UNDOCUMENTED** | The parts exist with the right value and DNP status. Nobody had written down **why** |
| H.15 | `WSHP2818R0100FEA` is two-terminal, not four-terminal | **GENUINELY NEWLY SURFACED** | `POWER-ARCHITECTURE.md` shows "RSH1 ---- INA226 (Kelvin)" — Kelvin was **intended**; the part cannot deliver it. RQ-022 asked for Kelvin **nets** without questioning the part |
| H.16 | Split power inlet | **GENUINELY NEW, and see G.2** | |
| H.17 | Automatic priority muxing destroys the brownout sweep | **GENUINELY NEWLY SURFACED** | |
| H.18 | RT power cycling ADOPT | **CONFLICTS WITH D-021** | See G.1. The technical work is sound; the authority is not in place |
| H.19 | Hardware power-permission gate, default-deny | **GENUINELY NEW as a mechanism; the need was previously known** | `power-envelope-rederivation.md` §5 already stated "the board cannot read the advertisement" and "the board cannot shed its largest load", and offered options (a)/(b)/(c) with a recommendation of (a). **Opus's tiering and TUSB320 decode is the implementation of a previously-identified requirement** |
| H.20 | Two-plane (functional / service) I²C separation | **NEW ARCHITECTURAL CONCEPT, no authority row** | See G.7 |
| H.21 | 287 vs "~250" baseline | **FACTUAL ERROR in the report** | See G.6 |
| H.22 | TMP1826 is the only single-package UID + local temp + ≥256 B NVM | **GENUINELY NEWLY SURFACED** | |
| H.23 | Rejecting resistor/capacitor arrays on placement physics | **CONSISTENT with doctrine** | Matches the mission document's area-is-cheap stance and D-043's refusal to freeze the 0R bypass |

---

## I. DO-NOT-INFER RULES

Written for a fresh architecture agent. Each is a mistake that has actually been made in this project
or is one step away from one.

**I.1 — Stale EDA presence does not establish current architecture.** `J7-ESP` is in the `.epro2`.
`J7-ESP` does not exist. D-049 deleted it. The export predates the decision.

**I.2 — Absence from a stale schematic does not mean a locked subsystem was removed.** The analogue
AUX lane is **absent from the live sheet** and is **RATIFIED by D-051**. The supersession entry says it
explicitly: unused ADC analogue pins and the PDM XOR are **not** a ratification that AUX was rejected.
Same class of error: no ADS7138, INA4235 or FRAM appears anywhere — because they have never been
proposed into the graph, not because they were rejected.

**I.3 — A theoretical component maximum is not a product workload.** 4.000 A is what 320 WS2816C
devices can draw at full white. Captain has ruled full white will **never** be commanded. The design
must **survive** the maximum and **be dimensioned for** the workload, and the workload figure **does not
yet exist** (E-11 produces it). Never collapse these.

**I.4 — An eFuse ILIM setting is not a load derivation.** This exact circularity survived two design
passes. If a current figure's only provenance is a component value on the sheet, it is a **ceiling you
chose**, not a load you measured. Say which.

**I.5 — A 22 Ω series resistor is not an isolation mechanism.** It is a termination. At 3.3 V into a
clamp diode it passes ~118 mA. Isolation means Ioff, a high-impedance switch, open-drain, a level
translator or removing the driver — named per signal, in a matrix.

**I.6 — API success is not evidence of board correctness.** A source read-back can prove 200 symbols
and 240 wire stubs persisted while being unable to prove one signal has two meaningful endpoints.
Screenshot and inspect. **A source/count PASS cannot override a failed screenshot.**

**I.7 — D-043 does not retire WS2816C.** D-043 makes *Voice-PE→K1 mappings written against* WS2816C
non-authoritative. **The LED part itself is WS2816C**, confirmed by Captain on 2026-08-30 and by the
firmware repo's G0.1 dual-DIN ruling. Do not read the tombstone as a part retirement.

**I.8 — A decision that "mentions" a topic does not supersede a ruling on it.** Superseding requires an
entry in `authority/05-SUPERSESSIONS.md`. This is written into the precedence file because it has been
violated.

**I.9 — A contract that cannot be located is not frozen.** SSCM-1 v1.0 was described as frozen for two
weeks and could not be found. Search before citing.

**I.10 — Do not port a checker from the firmware repository.** `check_architecture_ownership.py` scans
firmware source. In a hardware/docs repo it finds nothing, iterates over nothing, and **passes
vacuously**. A checker that inspects nothing must never print PASS; every check reports the count of
files, records and contracts it actually parsed and fails closed when any count is zero.

**I.11 — Do not infer 1.0 mm board thickness from the presence of a MEMS microphone.** That inference
was made once. The board is 1.60 mm, six layers, and only a D-012 amendment changes it.

**I.12 — Do not convert a clearance recommendation into a keepout rectangle.** Espressif's 15 mm is a
free-space end-product clearance. The `15 × 7 mm` PCB keepout was an invention. Do not recreate it and
do not invent a different rectangle.

**I.13 — Ring capacity is not a BGA escape proof.** Signals cannot be freely assigned to balls; NXP
fixes pad positions and their legal alternate functions. K1 may choose among legal IOMUX alternatives,
and escape, pinmux and orientation are co-optimised **at VAL-G3, against a completed schematic**.

**I.14 — Do not treat the visual-reference package as drawing authority.** It self-declares
`STATUS = STUDY_INPUT / BINDING = NO`, it is not an EasyEDA schematic, nothing in it is importable, and
**the Captain is the sole EasyEDA schematic author**. Its *net data* is the freshest machine-readable
truth; its *sheets* are a construction reference.

**I.15 — Do not treat an import/save/reopen survival as schematic readiness.** D-048: `dcd7e3ca…`
proves what EasyEDA thinks the repaired archive is. It is not product canonical, not JLCPCB handoff,
not drawing authority. `JLC-SCH-READY` attaches to **G2.2**, not G2.1.

**I.16 — Do not write a design ruling into a script.** It sits at precedence level 6 while carrying
level-2 authority, is invisible to every authority check, cannot be superseded by the documented
mechanism, and dies with the script.

**I.17 — Do not assume a part named in an audit still exists.** `U4-PWR2` and `R8-PWR2` are quoted
across four evidence documents and were deleted on 2026-08-29. Check the current designator inventory
in `schematic/visual-reference/REGISTERS.md` before trusting any audit's arithmetic.

**I.18 — Do not add a schematic sheet.** If one sheet cannot hold the design, **stop and report**. The
correct response is to optimise the one-sheet implementation, never to fork it.

**I.19 — Do not resolve an EasyEDA concurrency observation by freezing.** Verify operator authority
first. A Captain-authorised operator must never be obstructed. `FROZEN_INCIDENT` has no automatic
release path — using it wrongly is expensive.

**I.20 — Do not read `2.35 A / 0.95 A / 0.60 A` anywhere and treat it as current.** Those are the
inherited figures. Two re-derivations have replaced them. `POWER-ARCHITECTURE.md` still carries them
labelled "to be re-derived" — that label is the only thing keeping them honest.

**I.21 — Do not assign GPIO.** Pinmux is not frozen (D-031). The firmware is GPIO-agnostic and always
has been. GPIO assignment happens at VAL-G3 against escape pressure, not in an architecture document.

**I.22 — Do not treat `NON_REM` as the self-powered argument.** It changes descriptors. It does not
remove the need for a VBUS circuit. D-049 says this explicitly because the inference was available.

---

## J. TRUE OPEN QUESTIONS

Only items genuinely unresolved after using both history and the live repository. Everything that
could be closed above has been.

| # | Question | Why it is open | Blocks | Who can close it |
| --- | --- | --- | --- | --- |
| **J.1** | **`NVCC_PLL_1V1` has two capacitors, one ball (`U6-RTC.P10`) and no source.** Is it an internal-regulator output (like `VDD_HIGH_CAP`) or does it need a 1.1 V supply that does not exist on this board? | NXP's accessible datasheet and reference manual do not state the pin's nature. Not resolvable from documents on hand | **Schematic freeze** | NXP directly, or the RT1062 pin-audit lane |
| **J.2** | **LED data-line count.** The board provides **two** data lines (`LED_D0_3V3`, `LED_D1_3V3`) and two 3-pin XH connectors. The firmware lane's ruling G0.1 (2026-08-28, Captain direct) is **WS2816 dual-DIN**, and its WP1 gate requires **four LED pins — 2 channels × dual-DIN**. Nothing in K1-CORE-VAL-R0 mentions WS2816 or dual-DIN at all | Cross-repo. The hardware repo and the DualMCU firmware repo have diverged on the LED interface, and neither knows it | **LED interface contract, connector selection, `J2`/`J3` pin count, RT1062 pin budget** | Captain. This is a **genuine architectural conflict**, not a documentation gap |
| **J.3** | **D-021 vs RT hard power-cycling.** The register says NOT_BASELINE; the CTO position asks for it; the Opus report designs it | Precedence 1 (a live Captain ruling) beats the register, but no supersession entry exists | The entire `3V3_RT` segmentation, 2 × TMUX1511, load-switch selection, back-power matrix | Captain ruling + `05-SUPERSESSIONS.md` entry |
| **J.4** | **Real LED duty envelope.** What percentile does the actual visualiser workload reach on each channel? | Cannot be derived. Depends on effect content, palette, brightness policy | Trunk sizing for a production derivative; the firmware duty cap; whether 3.0 A is genuinely sufficient | Bench measurement (Opus E-11) |
| ~~J.5~~ | ~~`U1-PWR1.9` eFuse ILM on `USB_DP_UP` — real defect or parser artefact?~~ | **CLOSED 2026-08-30. CONFIRMED in the G2.2 hub candidate; canonical `64325d0e` is CLEAN.** Derivation in Addendum K. **Repair executed** on HOLD `55ed9ee9` (`g22-pwr1-ilm-repair-2026-08-30`). HOLD-REOPEN dump is the pre-repair witness. | This ILM blocker no longer blocks G2.2 promotion; other gates still do | Closed by independent geometric re-derivation; implementation on HOLD 2026-08-30 |
| **J.6** | **Shipping ESP32-S3 headroom, post int64-GDFT.** The compute-wall premise rests on a 2026-07-13 capture that predates the promotion; estimated remaining headroom ≈22 µs of a 7500 µs budget, **never measured** | Recorded as open risk R2 in `VALIDATION-ARCHITECTURE.md` and in `sources/SOURCE-REGISTER.md` | Does **not** reopen Q0-A (render/radio coexistence is independent) — but the RT1062 port target cannot be sized without it | Current-S3 baseline lane, which is unblocked and NOT STARTED |
| **J.7** | **Option C six-layer BGA escape.** Unproven | D-026 → D-031. Land diameter, clearance, via geometry, mask expansion, fab rules and pinmux must all be sourced | VAL-G3 | VAL-G3, against a completed schematic |
| **J.8** | **`TPS25947x` LED-switch fault-response suffix** (if the Opus LED architecture is adopted). Latch-off would turn an LED transient into a dead channel; auto-retry is required | Not yet read off TI's device-comparison table | BOM freeze | Bounded datasheet step |
| **J.9** | **`GRM155R60J106ME44D` suffix.** Absent from Murata's own product database; four sibling suffixes exist; distributors list it as active | Procurement | BOM freeze | Murata |
| **J.10** | **NFC single-ended vs differential antenna topology** (DEC-04 in the repair queue). Single-ended-with-cable is what the board *is*, and ST's AN5592 §2.3 is the topology for a coaxial lead — but it halves output power, is more noise-prone, gives up part of the receive path, and **requires a second matching network at the antenna end that does not exist in any BOM** | Never ratified. The device default is differential, so `single = 1` / `rfo2 = 0` is required for the as-built board either way | NFC performance envelope; possibly the antenna assembly | Captain ruling |
| **J.11** | **Duplicate `D-045`.** Two ratified decisions share an ID | Authority-layer defect | Any citation of D-045 | Register renumber |
| **J.12** | **Grok 4.6 Heavy R0-ARCH-2 conflict audit** | The report was not supplied | Section G completeness | Supply the file |
| **J.13** | **`JLC06161H-3313` order freeze.** Construction verified from JLC's live impedance page; still `PREFERRED_CANDIDATE_NOT_ORDER_FROZEN` | Layer count, copper weights and impedance config must be selected in JLC's live order workflow | Controlled-impedance dimensions, and therefore final USB/RF geometry | VAL-G5 |
| **J.14** | **Hub support network is unwired** (Y3, RBIAS, CRFILT, PLLFILT, VDD33 pin 1, NON_REM straps) and `J1` GT-USB-7005A is 0/28 wired | The hub-era capture is a work-in-progress, not a finished block | `G2_1_OFFICIAL_FREEZE`, which additionally waits on hub ERC Phase K **and** on AUX being present | The authorised EasyEDA lane |

---

---

## ADDENDUM K — bounded read-only verification of the `U1-PWR1.9` finding

**Date:** 2026-08-30 · **Class:** read-only forensic verification · **Mutations:** none · **Scope:** the
one question asked, nothing else.

### K.1 Verdict

> ## **CONFIRMED LIVE DEFECT — scoped to the G2.2 hub candidate. The canonical project is CLEAN.**

Not a parser artefact. The original flag in `schematic/visual-reference/README.md` was correct about the
binding and silent about the scope; the scope is the part that matters.

| Project | `U1-PWR1.9` (ILM) lands on | Verdict |
| --- | --- | --- |
| **Canonical `64325d0e…`** (`live-source-2026-08-28-2232.json`) | **`USB_EFUSE_ILIM`** | ✅ **CORRECT** |
| **G2.2 hub candidate** (`G2.2-HOLD-REOPEN.source.txt`, updateTime 1787976488933 — the freshest capture) | **`USB_DP_UP`** | ❌ **DEFECT** |

### K.2 Why the original evidence was not sufficient on its own

`G2.2-HOLD-REOPEN.graph.json` reports `role: IDENTITY_AND_NC_ONLY`, `bound_pin_count: 0`,
`pin_membership.pins: {}` — **it contains no pin-to-net binding at all.** The pin map used by the
visual-reference package came from a separate geometric coincidence parser whose own `inventory.json`
records `landing_rate: 0.8149` (18.5 % of pins land on nothing) and `transform_proof: "oracle U6
agreement 55/60"` (5 disagreements on the one component cross-checked). A P0 claim resting on that
parser needed independent confirmation. It now has it.

### K.3 Method

Independent re-derivation, not a re-reading of the same inventory:

1. Pin geometry taken from the **symbol library**, not the parser: symbol `76f01ceafa6a4cf682bb611206e2286f`
   (`TPS259474LRPWR.1`), read from the `.epro2` symbol documents. Pin 9 = **`ILM`**, root offset
   `(65, 55)` in the symbol frame.
2. Component transform read from the source: `U1-PWR1` at `(690, −4110)`, `rotation 180`, `isMirror false`.
3. Wire geometry rebuilt from `LINE` records grouped by `lineGroup`; net names from `ATTR key="NET"`
   whose `parentId` is the wire id. (In V3, a net name belongs to a **wire**, not to a coordinate.)
4. All ten pins transformed and tested for coincidence at tolerance 0.

### K.4 The transform validates itself

Nine of ten pins land at **tolerance 0** on exactly the net the inventory claims, including the three
that admit no ambiguity:

| Pin | Name | Absolute | Net at tol=0 |
| --- | --- | --- | --- |
| 1 | EN/UVLO | (775, −4110) | `USB_EFUSE_EN` ✅ |
| 2 | OVLO | (775, −4130) | `USB_EFUSE_OVLO` ✅ |
| 3 | PG | (600, −4130) | `PWR_ENTRY_PG_RT_IOMUX_TBD` ✅ |
| 4 | PGTH | (600, −4110) | `USB_EFUSE_PGTH` ✅ |
| 5 | **IN** | (775, −4090) | **`5V_USB`** ✅ |
| 6 | **OUT** | (600, −4090) | **`5V_PROTECTED`** ✅ |
| 7 | DVDT | (705, −4165) | `USB_EFUSE_DVDT` ✅ |
| 8 | **GND** | (665, −4165) | **`GND`** ✅ |
| **9** | **ILM** | **(625, −4165)** | **`USB_DP_UP`** ❌ |
| 10 | ITIMER | (740, −4165) | *(nothing — open, which is correct)* ✅ |

A transform that places IN on `5V_USB`, OUT on `5V_PROTECTED` and GND on `GND` is not misplacing pin 9.

### K.5 Pin 9 sits on a wire **vertex**, not near one

`USB_DP_UP` wire `w154290` segment list:

```
(600, −4225) → (600, −4165)
(600, −4165) → (625, −4165)      ← vertex at the ILM pin
(625, −4165) → (640, −4165)
(575, −4165) → (600, −4165)
```

`(625, −4165)` is a **segment endpoint shared by two segments**. That is a drawn connection point, not
a coincidental overlap. Other members of the net: `RUSB_DP-PWR1.2` and `U20-USB.20` — the upstream D+
series resistor and the hub's D+ input. **The eFuse current-limit programming node is on the USB 2.0
upstream D+ line, between the series resistor and the hub.**

### K.6 `USB_EFUSE_ILIM` — one endpoint, confirmed

In the G2.2 candidate the net survives only as an orphan stub:

```
wire w1000 : (325, −4420) → (345, −4420)          20 units long, adjacent to R1-PWR1 at (365, −4420)
wire e8070 : (5275.7, −29.5) → (5335.7, −29.5)    isolated, in the legend region, connects nothing
```

Confirmed: **exactly one component endpoint, `R1-PWR1.1`.** `R1-PWR1`'s current-limit resistor
programmes nothing.

### K.7 How the defect was introduced — provable from the two captures

The canonical project carries the correct wiring:

```
CANONICAL e1012 "USB_EFUSE_ILIM" : (605, −4220) → (605, −4160) → (630, −4160)
                                    U1-PWR1 at (695, −4105) → pin 9 abs (630, −4160)  ✅
```

The G2.2 candidate has the **same corridor, shifted by exactly 5 units in x and y, under a different
name**:

```
G2.2   w154290 "USB_DP_UP"      : (600, −4225) → (600, −4165) → (625, −4165) → (640, −4165)
                                    U1-PWR1 at (690, −4110) → pin 9 abs (625, −4165)  ❌
```

`U1-PWR1` moved `(695, −4105) → (690, −4110)`; the ILIM wire moved by the same delta and **came back
named `USB_DP_UP`**. The hub-era rework either renamed that wire or deleted it and drew a D+ wire along
the identical path. Either way the ILM pin was carried onto the USB upstream pair and `R1-PWR1` was
orphaned.

Corroborating detail: pin 5 reads `5V_USB_FILTERED` in canonical and `5V_USB` in G2.2 — the known
hub-era rename after `F1` left the trunk. The two captures are the same circuit at two epochs, which is
what makes the delta readable.

### K.8 Consequences

1. **D-052 terminated G2.2 promotion.** `JLC-SCH-READY` attaches to GREENFIELD,
   not G2.2. This ILM delta remains evidence of a fracture, not a repair queue.
2. **Do not mutate `64325d0e`.** D-052 archives it. The historical ILM
   connectivity there is knowledge, not a write licence.
3. **`R1-PWR1` is 1.24 kΩ** (`RNCF0402BTC1K24` / `C2491273`, on its own device
   `263cdab6e3341f4ea8fd57ccc688e923`). The 2026-08-28 value and binding repair **was completed**.
   RQ-046/RQ-047's binding defect is closed for R1. ⚠ **Trap:** its `partId` string is still
   `RC0402FR-0710KL.1` — the symbol/footprint id, not the value. **Reading `partId` would tell you
   10 kΩ. Read the `Manufacturer Part` / `Name` attributes instead.**
4. The `USB_EFUSE_ILIM` value question is therefore **not** open. The **connectivity**
   question was open at the time of this addendum and is now closed on live HOLD
   (see K.10). Canonical connectivity was already correct.

### K.9 What this verification does not establish

- It does **not** run EasyEDA GUI DRC. Per the project's own evidence hierarchy, exported Gerber >
  GUI DRC > source read-back. This is source read-back on two captures, independently re-derived from
  symbol geometry — strong, and one rank below a GUI DRC witness.
- It does **not** cover any other pin on any other part. Scope was one question.
- `G2.2-HOLD-REOPEN` is the forensic capture this addendum measured (2026-08-29 04:08). It is
  **not** the live HOLD after K.10.

### K.10 Implementation stamp (2026-08-30)

Not a re-derivation. The forensic tables above stay as the pre-repair record.

| Item | State |
| --- | --- |
| Canonical `64325d0e…` | Untouched. ILM already correct. |
| G2.2 HOLD `55ed9ee9…` | `g22-pwr1-ilm-repair-2026-08-30`: U1-PWR1.9 → `USB_EFUSE_ILIM` → R1-PWR1.1. USB_DP_UP retains RUSB D+. |
| R1-PWR1 | Electrical 1.24 kΩ / `RNCF0402BTC1K24` / `C2491273`. Stale `partId` `RC0402FR-0710KL.1` retained; checker reports `METADATA_MISMATCH`. |
| Gate | `harness/check_g22_pwr1_ilm.py` on the G2.2 oracle path. HOLD-REOPEN dump must still FAIL. Repaired HOLD must PASS this check. `JLC-SCH-READY` remains OPEN for unrelated gates. |


## Definition of done — self-check

A fresh agent reading this file plus the live repo now knows:

- what every subsystem currently is, and which document says so (§A);
- which architectures, parts, nets and assumptions look current but are dead, including the six
  tombstones that must never be recreated (§B);
- the eleven expensive failures and the rule each produced — most importantly that the qualification
  fixture failed twice for a **control-system** reason, not a judgement reason, and that a building
  agent grading its own homework is the project's recurring failure mode (§C);
- which fourteen questions are closed and what evidence would be needed to reopen them, with the
  power-envelope question decomposed into five non-collapsible classes (§D);
- why twenty-odd circuit elements exist whose purpose the schematic does not show (§E);
- which sixteen artefacts lag, under what condition each may be trusted, and ten live defects in the
  current capture (§F);
- where the Opus report conflicts with, re-discovers, or overstates against written authority — and
  that its RT power-cycling recommendation sits against a ratified decision (§G);
- which of its major claims are new, which were already known and lost, and which are simply wrong
  (§H);
- twenty-two things not to infer (§I);
- fourteen genuinely open questions, two of which — `NVCC_PLL_1V1` and the LED data-line count —
  block schematic freeze (§J).

**What this file does not do:** it does not ratify anything, does not supersede anything, does not
propose an architecture, and does not complete the Grok half of §G.
