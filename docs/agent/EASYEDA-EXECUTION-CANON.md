# EasyEDA execution canon

Use this canon before any EasyEDA schematic or PCB write in this repository. It captures the durable
lessons from the VAL-G2.0 failure sequence and converts them into an operating contract.

## Core principle

An EasyEDA mutation is unfinished until the saved semantic artefact and the settled canvas both show
the intended delta. Neither the API response nor either observation alone is sufficient.

```text
authority -> plan -> snapshot -> one bounded write -> semantic read-back
          -> settled screenshot -> comparison -> record -> next write
```

If any arrow is missing, stop.

## System diagnosis

### Reinforcing failure loop: delayed observation

```text
slow tool calls
  -> pressure to batch more work
  -> later visual inspection
  -> larger hidden defect
  -> more sunk cost
  -> reluctance to discard
  -> even larger repair batch
```

Break the loop at its leverage point: observe after the smallest visually meaningful transaction,
not after a convenient quantity of calls.

### Reinforcing failure loop: metric substitution

```text
numeric floor
  -> generator targets the floor
  -> counts appear compliant
  -> confidence rises
  -> semantic review is deferred
  -> fake topology survives longer
```

Break the loop before generation: the architecture-derived plan is the input; numeric floors are
only lower bounds on a representative design.

### Reinforcing failure loop: governance displacement

```text
bad artefact
  -> more prose/checkers
  -> less time on source-derived circuit work
  -> no valid artefact
  -> more frustration
  -> still more governance
```

Break the loop by adding only the smallest control that directly prevents the observed mechanism,
then return to the electrical deliverable.

### Reinforcing failure loop: net-join treated as a pen

```text
add_schematic_wire ok
  -> assume only the requested polyline exists
  -> skip that symbol’s pin-net dump
  -> EasyEDA merged a pin column or shared corridor
  -> USB overall-red excused as “later transactions”
  -> next batch
```

Break the loop at the first add: dump pin nets for the touched symbol; **new**
errors versus the pre-transaction set are a STOP; never delete a returned
`3V3`/`GND` primitive id without a segment census. Durable record:
`docs/agent/SESSION-CANON-2026-08-30-G22-USB-WIRING.md`.

## Recurring system archetypes

| Archetype | Session manifestation | Durable response |
| --- | --- | --- |
| Drifting goals | Representative fixture became “reach 200 symbols and 120 nets” | Derive architecture first; treat floors only as floors |
| Shifting the burden | Checker work substituted for circuit design | Separate prevention work from delivery and time-box the former |
| Fixes that fail | First semantic checker still allowed role-count grids | Test the historical bad mechanism, not only schema shape |
| Success to the successful | Count-based generation appeared productive, so more generation followed | Reward plan-to-territory agreement, not object throughput |
| Escalation | Slow per-call transport encouraged ever-larger batches | Use one transport session but keep visual transactions small |
| Eroding goals | Empty or distant screenshots were accepted because read-back existed | Screenshot usefulness is binary; unusable evidence closes the lock |
| Shifting the burden (USB) | USB checker staying red “until T6” hid new T2 shorts (DN on 3V3) | Diff this transaction’s error set; new shorts are a STOP |
| Fixes that fail (USB) | West 3V3 dogleg 30 units off the pin column still auto-filled pins 2–5 | Keepout ≥40; electrical 3V3-on-signal checker; no parallel vertical |
| Success to the successful (USB) | T1 geometric wires on J1 (pitch 32) were reused on U20 (pitch 10) | Pin pitch is part of the plan; J1 success is not a U20 method |

## Steel-manned explanation of the failed approach

The count-based approach was not irrational on its face. The qualification contract had explicit
symbol and net floors; EasyEDA transport had significant per-call overhead; repeated parts created
editor load; domain frames made a large sheet easier to scan; and batching reduced execution time.

That strongest case still fails because the property under test was usability of the eventual K1
single-sheet architecture. Repeated symbols, one-ended stubs and passive-only rails load the editor
without reproducing the topology, visual density, cross-domain wiring or editing tasks of the real
design. The approach optimised a proxy after severing it from the thing it was meant to approximate.

## Canonical lessons inventory

### Authority, scope and identity

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-001 | Inherited prose is not measurement | Re-read current authority and primary sources before implementation claims |
| K1E-002 | Live repository state beats conversational assumptions | Run `git status`, branch, remote and HEAD checks before Git claims |
| K1E-003 | A missing typed MCP method is not proof that EasyEDA lacks the capability | Inspect official API declarations and the live host surface before declaring a blocker |
| K1E-004 | Project names are safety boundaries | Use the exact disposable name; abandon a wrong project UUID rather than rename it through unsupported behaviour |
| K1E-005 | Project creation may provision documents automatically | Inventory the new project before creating another schematic or PCB |
| K1E-006 | No documented rename/delete API means no invented wrapper | Record abandoned identities and continue through supported lifecycle calls |
| K1E-007 | Identity can change after reconnect, open or GUI action | Re-read project and document UUIDs before every mutation transaction |
| K1E-008 | A product project and a disposable fixture are different safety domains | Never place scratch content inside the product project |

### Fixture definition and electrical meaning

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-009 | An unresolved architecture estimate is a hard stop | Never substitute the contract minimum for an unknown estimate |
| K1E-010 | Minimum counts are not generation targets | Include every meaningful planned component/net even when already above the floor |
| K1E-011 | Role counts are not a circuit | Every component belongs to a source-derived circuit block with endpoints and placement intent |
| K1E-012 | Source provenance must be locatable | Record document, revision, locator and URL/path for each required circuit role |
| K1E-013 | Approximate device identity creates fake diversity and false pin maps | Record MPN, value, exact EasyEDA device/library identity and live pin mapping |
| K1E-014 | Generic symbol fallback is prohibited | Missing library identity blocks placement; never substitute a convenient resistor, connector or IC |
| K1E-015 | Functional duplication needs architecture evidence | Stress load may add passives but not duplicate processors, power stages, clocks, connectors or functional ICs |
| K1E-016 | A named one-ended stub is not an electrical connection | Every non-intentional named net has at least two distinct component-pin endpoints |
| K1E-017 | Passive-only fanout is not a rail | High-fanout nets require a real source/active endpoint and real loads |
| K1E-018 | A pin cannot silently belong to two nets | Plan and live netlist both enforce exclusive pin membership |
| K1E-019 | Generated chain names reveal metric padding | Reject numbered `QUAL`, `LINK`, `SIG`, `FUNC`, `NODE` or equivalent count-farming topology |
| K1E-020 | Major ICs require both supply and functional connectivity | Unpowered or functionally isolated processors/peripherals block actuation |
| K1E-021 | The plan must have an external denominator | Completion is measured against authority/primary-source inventory, never against objects already generated |

### Composition and placement

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-022 | Decorative organisation can hide missing circuits | Do not draw domain frames or presentation scaffolds before complete circuit blocks exist |
| K1E-023 | Uniform grids are component landfills, not schematic composition | Place by signal/power flow, adjacency, option topology and editability |
| K1E-024 | A block is the smallest useful placement unit | Place a complete source-derived block, not an arbitrary number of roles |
| K1E-025 | Placement, designation and wiring are visually different states | Execute and inspect them as separate transactions |
| K1E-026 | A convenience `all` mode hides evidence boundaries | Multi-stage mutation modes are prohibited |
| K1E-027 | Board or sheet area is cheaper than ambiguity | Grow the canvas when separation materially improves readability and debugging |

### Mutation, observation and evidence

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-028 | Snapshot before every write | Persist source/project state and hash before the mutation starts |
| K1E-029 | The write return is not evidence | Re-query the document source, inventory and net membership after mutation |
| K1E-030 | A source hash proves change, not correctness | Diff expected components/nets/endpoints, not only the hash |
| K1E-031 | A screenshot proves appearance, not topology | Pair it with semantic read-back |
| K1E-032 | Semantic read-back proves topology, not composition | Pair it with a settled screenshot |
| K1E-033 | Screenshot scale must expose the requested delta | Empty space, unreadable pins, cropped blocks and distant whole-sheet views are unusable |
| K1E-034 | Screenshot failure is a stop condition | A hung zoom/capture or missing image cannot be replaced by semantic evidence |
| K1E-035 | Canvas settling is part of the transaction | Capture only after rendering and autosave state stabilise |
| K1E-036 | Every transaction needs a granular inspection record | State intended delta, observed delta, unexpected changes and named checks |
| K1E-037 | No later write may precede evidence closure | The write lock remains closed while evidence is absent, weak or contradictory |
| K1E-038 | Batching is a transport optimisation only | One session may carry many calls, but one visual transaction cannot hide multiple stages |
| K1E-039 | Measure transport before choosing batch size | Use timing evidence, then retain the visual boundary regardless of speed |

### Failure, repair and recovery

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-040 | A rejected mutation changes the allowed action set | Only a declared repair/rollback transaction may follow |
| K1E-041 | Partial mutation is more dangerous than a clean failure | Preserve post-failure census and block normal work until reconciled |
| K1E-042 | Deletion is proven by absence | Re-query inventories/source after delete; do not trust the boolean alone |
| K1E-043 | Save is proven by persistence | Check the save result, source hash and reopened inventory |
| K1E-044 | The same mechanism may not be retried with new numbers | Change the model/abstraction or stop; cosmetic variation is not a new approach |
| K1E-045 | Rejected work remains evidence, never seed material | Preserve generators/renders for diagnosis but prohibit reuse in replacement design |
| K1E-046 | Unknown live state is not ready state | Initialise the write lock as blocked and reconcile read-only before actuation |

### Qualification and claims

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-047 | An invalid fixture says nothing about EasyEDA capability | Record qualification as not run rather than tool failure |
| K1E-048 | Editor timing starts only after fixture admissibility | Do not measure responsiveness on semantically rejected content |
| K1E-049 | Source and live netlist must agree exactly on endpoint membership | Compare membership, not only counts or names |
| K1E-050 | A valid disposable fixture proves only its qualification contract | It does not prove the canonical design, PCB routability or fabrication readiness |
| K1E-051 | Canonical schematic work remains gated | Do not begin VAL-G2.1 until the required disposable measurements and inventories close |
| K1E-052 | PCB work remains separately gated | Do not place, fan out or route canonical PCB geometry during schematic qualification |

### Agent and harness behaviour

| ID | Lesson | Enforced behaviour |
| --- | --- | --- |
| K1E-053 | Prose-only discipline is bypassable under pressure | Put mechanical constraints in executable gates |
| K1E-054 | A checker that has never rejected the historical bad case is unproven | Retain known-bad fixtures and mutation tests |
| K1E-055 | Zero parsed records must never produce an affirmative result | Every checker reports counts and rejects vacuity |
| K1E-056 | The evaluator cannot be rewritten mid-run and reused for self-certification | Lock the checker for an execution; rerun controls after changes |
| K1E-057 | A fluent agent report is the weakest evidence layer | Cite files, UUIDs, hashes, net membership and screenshots |
| K1E-058 | Report theatre can consume the delivery budget | Add the smallest effective guard, then return to the circuit |
| K1E-059 | Captain is not the visual test harness | Agents capture and inspect the screenshots; Captain receives decisions and evidence |
| K1E-060 | Durable state must survive agent/session replacement | Keep plans, ledgers, rejected attempts and current lock state on disk |
| K1E-061 | Atomic file replacement is not a multi-writer lock | Serialise state transitions with an OS-level file lock and test simultaneous begins |
| K1E-062 | Static prose drifts from live transaction state | Runtime phase belongs only to the validated state file and append-only ledger |
| K1E-063 | A timing-dependent test can report a false contradiction | Test durable invariants; query mutable runtime state separately |
| K1E-064 | Every committed mutation must extend one continuous source-hash chain | An unexplained pre-hash change means an unrecorded write and forces quarantine |
| K1E-064A | A host upgrade re-serialises every page, so the hash chain breaks ONCE at that boundary without any unrecorded write | Before invoking K1E-064/F-20/D-040, check the source FORMAT: if the pre-hash is V2 (`easyeda_source_format.detect_format` -> `V2_TAGGED_ARRAY`) and live is `V3_TYPED_RECORD`, the discontinuity is the 2026-08-28 EasyEDA 2.2.40.8 -> 3.2.149 migration. Resolve it with `easyeda_mutation_gate.py reconcile`, NEVER with `FROZEN_INCIDENT` |
| K1E-065 | One live EasyEDA canvas requires one explicit operator | Competing agents must not share actuation ownership even when the gate serialises calls |
| K1E-066 | Quarantine is a new trust boundary, not historical erasure | Preserve the bad ledger epoch, close actuation and reconcile the live territory afresh |
| K1E-067 | Reconciliation-capable quarantine cannot stop a genuinely unowned continuation loop | Use `FROZEN_INCIDENT` after ownership is actually unresolved, never merely because another authorised agent is active. D-052 programme-archive freeze of dead EasyEDA lanes is K1E-078, not this rule |
| K1E-068 | Concurrency is not evidence of unauthorised ownership | Identify the live operator before containment; do not obstruct Captain-authorised execution |
| K1E-069 | `add_schematic_wire` is a net-join, not a pen | The returned primitive may be the whole merged net; dump pin nets after every add; never delete a `3V3`/`GND` id from an add result without a segment census |
| K1E-070 | A parallel vertical inside a pin-column keepout auto-shorts the column | No vertical within 40 units of a pin column; U20 west column (source x=230 at origin 400,−800) is forbidden for power doglegs |
| K1E-071 | Crystal and RBIAS corridors that share an x, or a run along a crystal pin row, merge nets | Distinct east corridors; never route through another pin of the same symbol |
| K1E-072 | Two Type-C origins within 80 units is a stacked drawing even if USB `j1_wired` is green | Drawing checker `check_g22_schematic_drawing.py`; delete `J1-USB4105-RETIRED`; do not reinstate it on top of J1-PWR1 |
| K1E-073 | MCP `modify_schematic_component` x/y leaves wires behind | Native drag or delete+replace; never MCP-move a connected symbol |
| K1E-074 | EasyEDA restamps DOCHEAD without an electrical change | Body SHA for electrical identity; restamp the gate before `begin`; a recovery payload hash is not live identity |
| K1E-075 | Overall USB FAIL is not this-transaction FAIL | Diff the USB error set against the pre-write dump; new shorts stop the lane |
| K1E-076 | EasyEDA selection hatch and dark IC fill are not DNP or a deprecated sub-sheet | DNP is `Add into BOM=no`; click empty canvas; do not delete U1/U20 with a Type-C stack |
| K1E-077 | OCS/EN picture-frame segments ≥ 400 units are drawing failures, not ghost sheets | Local stub + net label; `check_g22_schematic_drawing.py` on `USB_OCS1_N` / `USB_OCS2_N` / `USB_EN1` / `USB_EN2` only |
| K1E-078 | Archived EasyEDA is not the design | After D-052, canonical / HOLD / G2.1 / hub UUIDs are ARCHIVE. GREENFIELD is the only implementation canvas. Hashes fingerprint a known semantic state; they are not identity. Programme-archive freeze is not a D-040 ownership incident |

## Failure-to-control traceability

| Incident | What failed | Durable control |
| --- | --- | --- |
| F-01 | Stale decisions looked current beside superseding decisions | Decision status and supersession records must agree |
| F-02 | “VAL-G2 unblocked” was read as permission for canonical capture | VAL-G2.0 qualification and VAL-G2.1 capture are separate ordered gates |
| F-03 | A projected CopperPilot study was treated as B/C feasibility proof | Historical study quarantined; Option B interface and Option C escape remain unproven |
| F-04 | Connector current and crossing counts used the wrong module boundary | Re-derive boundaries from ownership and module-local loads if Option B is ever revived |
| F-05 | Missing typed MCP methods were mistaken for missing EasyEDA capability | Check official API plus live host surface before declaring a tool blocker |
| F-06 | A disposable project received a product-like wrong name | Exact project identity is asserted and wrong UUIDs are abandoned, not renamed by UI tricks |
| F-07 | The repository was described as having no remote without checking | Git claims require live branch, HEAD, dirty-state and remote inspection |
| F-08 | The first fixture targeted exactly 200 symbols and 120 nets | Architecture-derived inventory is the input; numeric thresholds are floors |
| F-09 | One-ended named passive stubs impersonated connectivity | Endpoint-level semantic checker requires real multi-pin topology |
| F-10 | Functional ICs and power stages were duplicated to create load | Functional quantities require source/contract provenance; stress load is passive-only |
| F-11 | The first useful screenshot arrived after a large bulk mutation | Screenshot and inspect after every visually atomic transaction |
| F-12 | Semantic read-back was used when the screenshot was absent or unreadable | Semantic and visual evidence are both mandatory and non-substitutable |
| F-13 | Placement, designation and wiring were hidden behind one convenience mode | The executor exposes exactly one visual stage per invocation |
| F-14 | A second rebuild repeated the same role-count/grid abstraction | Complete source-derived circuit blocks replace count tranches and uniform grids |
| F-15 | Decorative frames made weak content look organised | Circuit topology establishes composition before any presentation structure |
| F-16 | Execution continued after the visual log recorded a process failure | The state machine mechanically prevents a next normal write |
| F-17 | Partial mutations left the live sheet’s meaning uncertain | Unknown territory begins closed and requires read-only reconciliation |
| F-18 | Static status still named the installation phase after runtime advanced | State file plus ledger own the live phase; prose owns policy only |
| F-19 | Independent agent processes could race on an atomically replaced JSON file | OS-level file locking serialises every transition |
| F-20 | Reconciliation hash `222135:c6b343ed` was followed by begin hash `222137:a9bf996e` | Full ledger replay enforces hash continuity and quarantines unexplained changes |
| F-20B | The canonical gate hash `497055:82c17c12` is a V2 charcount; the live V3 page is ~2154721 chars. Read through K1E-064 alone this looks like a 4.3x unexplained write and invites an unreleasable freeze | A hash discontinuity must be classified by FORMAT before ownership: host migration first, rogue operator second |
| F-20A | I inferred that the continuing operator was unowned and froze it; Captain confirmed it was authorised and productive | Release the freeze immediately; operator identity must be established before containment |
| F-21 | Future/checker scaffolding risked becoming vacuous green theatre | Create checks only when their artefacts exist; zero parsed records is always rejected |
| F-22 | A fluent report or self-issued verdict displaced external evidence | Builder output remains a proposal until independent read-back, render and contract evidence agree |
| F-23 | T2 west 3V3 dogleg at x=200 auto-filled USB2422 pins 2–5 onto 3V3 | Electrical 3V3-on-west-pin errors in `g22_usb_hub.py`; keepout in the USB wiring skill |
| F-24 | RBIAS and XTALIN shared x=590; U20.24 became USB_XTALIN | RBIAS must not share a net with XTALIN |
| F-25 | Y3 OSC2 along y=−745 through pin 4 merged USB_XTALOUT into GND | U20.21 must be USB_XTALOUT, never GND |
| F-26 | `add_schematic_wire` returned the merged 12-seg 3V3 rail; deleting that id would depower the hub | Segment census before any delete of a power-net primitive |
| F-27 | Two Type-C symbols 43 units apart; T1 `j1_wired=18` while the drawing was a blob | Drawing origin-distance gate; USB4105 is deleted, not kept overlapping |
| F-28 | `USB_OCS1_N` / `USB_OCS2_N` 1 195-unit frames were read as a deprecated sub-sheet | Picture-frame checker scoped to OCS/EN nets |
| F-29 | Dark hatch / QFN fill treated as DNP | Selection overlay ≠ deprecated; DNP is a BOM attribute |
| F-30 | Continuous T2–T6 GO used to ignore **new** T2 shorts | Pre-existing gaps may stay red; new errors are a STOP |
| F-31 | `connect_schematic_pins_to_nets` reported 0 committed while geometric wires landed | Geometric vertex nets are the evidence; connect is not |
| F-32 | J1 pin table reconstructed as sx=−35 / A1 sy=+100 and missed every live pin end | `J1_PINS` from live MCP; never reconstruct Type-C from memory |
| F-33 | HOLD `.epro2` had 234 designators and no USB island while recovery treated 287 + U20 as known-good | Semantic census of the named artefact; hashes are not identity (D-052 / K1E-078) |

## Canonical execution workflow

### 0. Acquire authority

Read, in order:

1. repository `AGENTS.md`;
2. this canon;
3. current project status and decisions;
4. task contract and fixture plan;
5. applicable EasyEDA router and task skill;
6. for USB2422 / J1 / Type-C wiring on **GREENFIELD** (D-052 forbids HOLD/G2.2 writes):
   `docs/agent/SESSION-CANON-2026-08-30-G22-USB-WIRING.md` and
   `.cursor/skills/g22-usb-schematic-wiring/SKILL.md`.

### 1. Establish identity and ownership

Record and compare:

- repository path, branch, HEAD, remote and dirty files;
- live EasyEDA project UUID and exact friendly name;
- document UUID and type;
- project-tree inventory;
- active write-lock state; and
- whether another agent/driver owns the live session.

Any mismatch or ambiguity closes the write lock.

### 2. Validate the plan

The plan must identify every component, circuit block, endpoint, net, source and placement intent.
Run its checker before actuation. Review source meaning separately from schema conformance.

### 3. Reconcile current territory

If the write-lock state is missing, stale or blocked:

1. do not write;
2. capture current source and semantic census;
3. capture a settled useful-scale screenshot;
4. compare the canvas, source and evidence log;
5. record discrepancies; and
6. initialise `READY` only when the observed baseline is internally consistent.

### 4. Declare one visual transaction

Name:

- circuit block;
- stage (`place`, `designate`, `wire` or `repair`);
- exact intended objects/nets;
- expected visual delta;
- expected semantic delta; and
- inspection criteria.

No `all` stage and no arbitrary count tranche.

### 5. Snapshot and begin

Save the full pre-write source with project/document identity and hash. The gate records the
transaction as `IN_FLIGHT` before the actuator is called.

### 6. Act once

Run only the declared transaction. Do not opportunistically fix another block, add a frame, rename
unrelated objects or continue into the next stage.

### 7. Read the semantic result

Persist a post-write record containing:

- project/document identity;
- source hash;
- component/wire/net census;
- exact affected designators/primitive IDs;
- exact endpoint membership for affected nets;
- save result; and
- errors, rejections or unmapped pins.

### 8. Capture and inspect the canvas

Wait for settle, then capture:

- a block-scale image that makes the changed objects readable; and
- a whole-sheet image whenever composition or bounds can change.

Inspect duplication, omission, orientation, labels, pin visibility, wiring, collisions, out-of-bounds
content, dead space and unintended changes.

### 9. Close or reject

- **Accepted:** semantic and visual evidence both match intent; the gate returns to `READY`.
- **Rejected:** anything disagrees or is unobservable; the gate enters `REJECTED` and only repair is
  permitted.

### 10. Record before continuing

Append the event to the ledger and update the human-readable visual log. Only then may another
transaction begin.

## Visual evidence standard

An image is useful only if another agent can answer all applicable questions from it:

- Is the exact changed block visible?
- Are changed references and pin labels readable when relevant?
- Are there duplicate, placeholder or undesignated components?
- Does left-to-right/top-to-bottom signal or power flow remain understandable?
- Are wires visibly connected to intended pins without accidental crossings?
- Is any changed content clipped, off-sheet or colliding?
- Did unrelated content move or appear?
- Does the whole-sheet composition remain balanced and searchable?

If the answer to the first question is no, the screenshot is invalid. If any other applicable answer
is unknown because of scale, capture another image before disposition.

## Structured evidence contract

The visual evidence JSON must contain:

```json
{
  "schema_version": 1,
  "transaction_id": "POWER_ENTRY-place-001",
  "project_uuid": "exact live UUID",
  "document_uuid": "exact live UUID",
  "screenshot_path": "evidence/.../screenshots/...png",
  "captured_after_settle": true,
  "scale": "block",
  "intended_delta": "bounded declaration",
  "observed_delta": "what the image actually shows",
  "unexpected_changes": [],
  "checks": [
    {"name": "changed block visible", "result": "OK", "detail": "..."},
    {"name": "no duplicates", "result": "OK", "detail": "..."},
    {"name": "labels readable", "result": "OK", "detail": "..."},
    {"name": "no unrelated movement", "result": "OK", "detail": "..."}
  ],
  "verdict": "ACCEPTED"
}
```

The semantic read-back JSON must bind the same transaction, project and document and include both
pre/post source hashes plus the affected inventory/net membership.

## Rationalisation traps

| Rationalisation | Reality |
| --- | --- |
| “The API returned success.” | It reports the call path, not the saved electrical result. |
| “The hash changed.” | Something changed; it does not say the right thing changed. |
| “The counts match.” | Counts can describe padding, duplication or one-ended stubs. |
| “The screenshot tool hung, but read-back is enough.” | Topology cannot establish composition; stop. |
| “The screenshot exists.” | Empty, distant, cropped or unreadable images are missing evidence. |
| “This is one batch.” | A batch containing multiple visual stages is multiple uninspected states. |
| “I will designate and wire after placement.” | Each stage requires evidence closure before the next. |
| “The frame will help organise the sheet.” | Organisation follows circuit topology; decoration cannot define it. |
| “The generic symbol is close enough for qualification.” | Wrong pins and wrong visual density invalidate the model. |
| “I can clean up the duplicates later.” | Further writes increase ambiguity; reject and repair immediately. |
| “The checker accepted the JSON.” | Schema acceptance does not establish source truth or live execution. |
| “The previous attempt was different because the quantity changed.” | Same abstraction, same failure mechanism. |

## Immediate red flags

Stop before writing if any is true:

- estimate, source, MPN, library binding, pin mapping or block topology is unresolved;
- state file is missing, stale, blocked or names another project/document;
- prior transaction lacks a useful screenshot or semantic record;
- screenshot capture/zoom is unavailable;
- intended batch includes more than one visual stage;
- placement is described as a grid, tranche, padding or count target;
- a functional device is duplicated only to increase load;
- the plan and live source disagree on already placed content;
- placeholders or undesignated debris exist outside the declared repair scope;
- another agent or driver may own the session;
- two Type-C origins are within 80 units, or U20 west-column signals are on `3V3`,
  or U20.21 is `GND`, or RBIAS shares XTALIN;
- the next act is an MCP symbol move, or deleting a `3V3`/`GND` wire id returned
  by `add_schematic_wire` without a segment census.

## Current project boundary

D-052: every existing K1-CORE-VAL-R0 EasyEDA project is ARCHIVE. All mutation
lanes under `evidence/` are `LANE-RETIRED`. Bare `validate` must refuse. The
only future write target is `K1-Core-VAL-R0-GREENFIELD` once its UUID exists
and OPEN BEFORE BUILD is closed. This document never grants write permission
on archived UUIDs.

## Related evidence and machinery

- Complete session debrief:
  `evidence/VAL-G2-2026-08-28/SESSION-DEBRIEF-2026-08-28.md`
- Invalid fixture RCA:
  `evidence/VAL-G2-2026-08-28/INVALID-FIXTURE-RCA.md`
- Preserved bad generators:
  `evidence/VAL-G2-2026-08-28/invalid-fixture-generator.mjs` and
  `invalid-net-generator.mjs`
- Visual execution log:
  `evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-VISUAL-LOG.md`
- Fixture-plan checker:
  `harness/check_single_sheet_qualification_plan.py`
- Mutation state gate:
  `harness/easyeda_mutation_gate.py`
- Guardrail design:
  `docs/agent/2026-08-28-easyeda-execution-guardrail-design.md`
- G2.2 USB wiring session canon (2026-08-30):
  `docs/agent/SESSION-CANON-2026-08-30-G22-USB-WIRING.md`
- USB electrical gate:
  `harness/check_g22_usb_hub.py`
- USB / Type-C drawing gate:
  `harness/check_g22_schematic_drawing.py`
