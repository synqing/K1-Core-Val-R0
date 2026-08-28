# Reconcile receipt — 2026-08-28 (second operator)

Captain confirmed the Codex lane finished and handed the canvas over. This operator took
read-only territory. **No mutation was made, the gate was not restamped, and the document was
not saved.** The reason is stated below and it is not a small one.

## Identity — verified live

```text
project    64325d0e55e0435abd018defb0089a9b   "K1-Core-Val-R0"
schematic  cffcdb562c1b48d1a5214cfc263b6c90
page       1435cb46f39e48c8a8aadbb84ca81603   exactly one page, no hierarchy
pcb        59bef7e87cff4cd580561703b62d8c19   auto-provisioned, untouched
bridge     extension 1.5.9, preflight ok, 90/90 methods, gates enabled, no bypass
editor     tab reads "*P1.Schematic1" — unsaved changes present
```

## Stamp does not match live, and the census changed

```text
gate stamp    497055:82c17c12   (state READY, last close captain-nc-reconcile-2026-08-28)
live source   497700:31431188   (+645 characters)
live census   231 components · 677 wires · 228 designators · 143 named nets
frozen dump   230 components · 675 wires · 228 designators · 143 named nets
```

The ledger's recurring drift pattern is "hash moves, census unchanged". **This is not that.** A
component and two wires appeared, so it is a real content change, and the gate cannot see it —
`validate` replays the 170 ledger records and returns `READY` without ever querying the host.
That is a fourth blind spot in the harness: `AGENTS.md:39` presents `validate` as the
pre-actuation check, but it proves ledger self-consistency, never that the gate's belief matches
the canvas.

## What the drift actually is — identified exactly

Diffed live against the frozen dump:

```text
e153999  COMPONENT  GND power-flag symbol at (560,4515), no Designator (correct for a flag)
e154010  WIRE       5 segments around (560,4515), NET=GND — the flag's connection
e153914  WIRE       [[1475,3320,1390,3320]], NO NET ATTRIBUTE AT ALL
```

The first two are coherent work: a GND flag placed and wired. The third is the problem — the
frozen dump had `unnamed_wires: 0`, and on this sheet every wire carries a `NET` attribute by
construction. An 85-unit horizontal wire with no net is leftover debris or an unfinished stub.

It is not this operator's to silently delete. Removing another operator's object without seeing
it is the destructive scope-creep the doctrine exists to prevent. It needs a declared repair
transaction with its own visual evidence.

## Why nothing was saved or restamped

Closing this honestly needs a screenshot in which the object is visible. That screenshot cannot
currently be taken, and proving that took the rest of this pass.

## The evidence-capture failure — the real blocker

**Finding: the zoom path is dead on this host, and every gate close in this programme has been
made with whole-sheet images at which pin glyphs are unreadable.**

That is why `close_visual_from_census.py` exists at all. Its own docstring admits it: *"Whole-sheet
zoom cannot read pin glyphs on this host."* It then hardcodes four `OK` checks and
`verdict: ACCEPTED`. The weakness it papers over is real; the papering is the defect.

What was measured, in order:

1. The sibling tool `EasyEDA-MCP/tools/easyeda_zoom_shot.mjs` hard-pins `PAGE_TAB` to the
   **retired** project `1991698f…@09e9c541…` with no override. It cannot target this canvas.
2. A first tool written here reported `{ok:true, fired:true}` and produced a **byte-identical**
   PNG — same sha256 `1eda008ed720578c` before and after. The success flag meant "the call
   returned", not "the view moved". Cause: execution contexts arrive asynchronously, a 400 ms
   wait yielded no `contextId`, and the eval ran against the top frame.
3. Enumerating the API by walking the prototype chain — `Object.keys` returns `[]` for these
   class methods, a false negative that briefly suggested the methods were absent — gives the
   real surface in the canonical frame's context (ctx 7):
   ```text
   dmt_EditorControl : getCurrentRenderedAreaImage zoomToRegion zoomTo
                       zoomToAllPrimitives zoomToSelectedPrimitives activateDocument
                       generateIndicatorMarkers removeIndicatorMarkers …
   sch_SelectControl : doSelectPrimitives clearSelected getAllSelectedPrimitives_PrimitiveId …
   sch_Primitive     : getPrimitivesBBox getPrimitiveByPrimitiveId …
   ```
4. **The host promises never settle.** Evaluating any of them with `awaitPromise:true` hung
   until a two-minute timeout. They must be fired with `void` and `awaitPromise:false`.
5. With the context correctly bound to ctx 7 and the call fired correctly, **both
   `zoomToRegion(l,r,t,b,TAB)` and `doSelectPrimitives(ids,TAB)` + `zoomToSelectedPrimitives(TAB)`
   still leave the view byte-identical.** Unresolved after three attempts; handed to a dedicated
   lane rather than spiralling further.

## What was built

`harness/easyeda_canonical_zoom_shot.mjs` — targets the canonical page, binds the correct
execution context, fires without awaiting the non-settling promise, and **captures before and
after and refuses to report success unless the pixels changed**. It currently exits non-zero
with `stage: witness` — which is the correct answer, and the opposite of the auto-ACCEPT closer.
A tool that cannot report a false success is worth more than one that zooms.

`harness/extract_frozen_denominator.py` — one shared, faithful extraction of a source snapshot
into `index.json` / `bom_flat.csv` / `source.txt`, so parallel auditors never each re-parse
490 KB and never touch the live session. Fails closed on zero parsed records.

## State left behind

```text
gate            READY, stamp 497055:82c17c12, unchanged by this operator
live document   497700:31431188, unsaved, three undispositioned primitives
mutations made  none
open items      e153914 disposition · restamp · save-persistence proof
next allowed    fix evidence capture, then one declared repair transaction with a
                readable screenshot showing e153914 and what it touches
```

**Do not claim whole-sheet ERC clean, and do not claim this reconcile closed.** It is a recorded
read-only observation, not a closed transaction.

---

## Update — disposition of the three leftover primitives, established by measurement

The zoom is still broken, so these could not be *seen*. They could, however, be *measured*:
wire-to-wire endpoint comparison stays inside a single coordinate frame and needs no symbol
library, so it is reliable where pin snapping is not.

```text
e153914   NET = <NONE>   segment [[1475,3320,1390,3320]]
          endpoint (1475,3320) -> touches 0 other wires
          endpoint (1390,3320) -> touches 0 other wires
          nearest other endpoints, both ends, manhattan distance 10:
              (1390,3310) GND            (1475,3310) GND
              (1390,3330) NFC_VDD_DR     (1475,3330) NFC_VDD_DR
              (1390,3340) NFC_RFO1       (1475,3340) NFC_RFO1   (distance 20)
```

`e153914` sits in the NFC regulator decoupling cap row, exactly one grid step (10 units) below
the `GND` row and one step above the `NFC_VDD_DR` row — in the gap between two populated rows,
carrying no net and touching nothing at either end.

**Verdict: debris.** Almost certainly an aborted or mis-placed wire during the
`canonical-nfc-regulator-decouple-*` sequence, landing one grid step off. It connects nothing and
means nothing. It should be removed by a declared repair transaction — not silently, and not by
this operator without the visual evidence the canon requires.

```text
e153999   GND power-flag symbol at (560,4515), no Designator (correct for a flag)
e154010   NET = GND, 5 segments, all 10 endpoints touch no other WIRE
```

`e154010`'s endpoints touching no other wire is **not** evidence against it: one of its endpoints
is (560,4515), which is exactly where the flag component `e153999` sits. A wire-to-wire test
cannot see a wire-to-component-pin contact. These two are coherent as a placed-and-wired GND flag
and are **not** classified as debris on this evidence.

### Why this matters beyond these three objects

The measurement that settled it took seconds and needed no screenshot. The reason it worked is
that it compared like with like — wire geometry against wire geometry. The pin-level equivalent
does **not** hold: harvested pin coordinates from `list_schematic_component_pins` are not in the
source's coordinate frame. A naive snap of all 881 harvested pins onto wire endpoints landed
**zero**, while the connectivity oracle's transform lands about 80%. So any pin-level
connectivity claim depends entirely on a coordinate transform that is currently undocumented,
and must not be trusted until that transform is written down and given a fixture that can fail.

### Recorded for the repair queue

```text
e153914  DELETE   declared repair transaction, visual evidence required
e153999  KEEP     pending one look; coherent as a GND flag
e154010  KEEP     pending one look; carries NET=GND and meets the flag
```

---

## Orchestrator verification of the three false-green fixes

Re-derived directly rather than accepted from the building lane. A subagent's verification is a
hypothesis with a citation; these gate what the whole programme trusts, so they were re-run here.

### 1. `check_single_schematic.py` — was green while blind

```text
BEFORE  exit=0  SINGLE_SCHEMATIC_CHECK=OK
        measured jobs/final-readback-results.json, a static file written at 09:25 describing
        181 designators / 517 wires / hash 389936:080d43fd, while the live sheet held 228
        designators and hash 497055:82c17c12. It would have passed even if the sheet were emptied.

AFTER   exit=1
        SINGLE_SCHEMATIC_CHECK=ERROR STALE READ-BACK: this check would measure source_hash
        389936:080d43fd, but the live gate holds 497055:82c17c12. The read-back is a static file
        that nothing refreshes, so a pass here would say nothing about the current sheet.
```

The check is now bound to the gate's `current_source_hash`. It can only pass when it actually
inspected the current sheet — which is the property it was always supposed to have.

### 2. `easyeda_mutation_gate.py validate` — was validating the wrong project

`AGENTS.md:39` instructs every agent to run this before actuation. It defaulted to the **retired**
qualification lane, so the mandated pre-write check was reading a dead ledger.

```text
BEFORE  silently validated evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-STATE.json
        project 09e9c541fd3d404082d4b92e55ae5336  (terminated by D-042)

AFTER   EASYEDA_MUTATION_LANE_RESOLVED=evidence/VAL-G2-2026-08-28/canonical-core-val-r0
        EASYEDA_MUTATION_LANE_PROJECT=64325d0e55e0435abd018defb0089a9b
        EASYEDA_MUTATION_LEDGER_RECORDS=170
        EASYEDA_MUTATION_GATE_STATE=READY
```

It now announces which lane it used, so a wrong-lane validation can no longer be silent.

### 3. `close_visual_from_census.py` — was manufacturing consent

It hardcoded four `"result": "OK"` checks and `"verdict": "ACCEPTED"`, then called `gate close` —
satisfying the gate's schema without anyone reading the canvas, while its own check detail
admitted *"Pin glyphs are not readable at whole-sheet zoom."*

```text
BEFORE  exit=0, transaction closed ACCEPTED with four synthetic OK checks
AFTER   exit=2
        CLOSE_VISUAL=REFUSED missing required arguments:
          ['--screenshot', '--observed', '--scale', '--inspected-by', '--verdict']
        This script no longer supplies any of these on your behalf.
```

### What this changes

Three indicators that had never been seen to go red now can, and two of them went red on the
**real** current state rather than a synthetic fixture. That is the difference between a checker
and a decoration.

It also means the honest state of this programme is worse than the record previously showed, and
that is the point: `check_single_schematic.py` reporting `OK` was not evidence the sheet was
sound, and no past green from it should be cited as such.

## Correction to this receipt

An earlier section of the companion probe document claimed no `Add into BOM` attribute exists in
the schematic source. That was wrong — it exists on four records and ranks 44th of 213 attribute
keys, below the cut-off of the truncated list it was read from. The DNP exclusion mechanism is
schematic-level and demonstrably works on `C43-ESP`, `C44-ESP` and `C52-AUD`, which makes the
seven DNP-named resistors that lack it a measured defect rather than an inference. The correction
is recorded in `CANVAS-OWNERSHIP-PROBE-2026-08-28.md`.

---

## The pin-coordinate transform, solved — and its limit

The connectivity oracle's load-bearing unaudited step was how harvested pin coordinates map onto
source wire geometry. It is now solved, and the solving mattered as much as the answer.

**The rule is `page = (pin.x, -pin.y)`.** Y is negated; that is all. Verified exactly:

```text
C2-PWR1   pin 1 raw (200,-4420)  -> (200,4420)   = 5V_PROTECTED
          pin 2 raw (230,-4420)  -> (230,4420)   = GND
R75-PWR2  pin 1 raw (1010,-4480) -> (1010,4480)  = BUCK_PG
          pin 2 raw (1050,-4480) -> (1050,4480)  = 3V3
C10-PWR2  pin 1 raw (1000,-4295) -> (1000,4295)  = BUCK_SS
          pin 2 raw (1040,-4295) -> (1040,4295)  = GND
```

A plausible alternative — offsetting to the pin tip using each pin's `rotation` and `pinLength` —
was tested and rejected on measurement: it lands 10, 7 and 3 of 881 pins against 654 for raw.
Recorded so nobody re-derives it.

**The limit: raw lands 654/881 = 74%.** With a ±5 unit snap tolerance it reaches 669/881 = 76%,
and the count of nets reaching fewer than two pins falls from 7 to 4. `U9-ESP`'s wire endpoints
sit a uniform 5 units from its pins, against a 10-unit pin pitch. So a sub-grid mismatch exists on
some components, and **the tolerance chosen changes the findings** — which means any verdict must
state its tolerance and show the sensitivity, or it is not a verdict.

## Two wrong turns, both caught by an independent source

Recorded because the pattern matters more than the two instances.

**First: six false defects from a dropped symbol part.** The oracle reported 13 nets reaching
fewer than two pins. Six of them — `AUDIO_BCLK_RT`, `BOOT_MODE1`, `LED_D0_3V3`, `LED_D1_3V3`,
`SWD_SWCLK`, `SWD_SWDIO` — in fact reach two pins, the second being on `U6-RTC` at balls G12, G14,
D7, E7, F12 and E14. The oracle keyed pin data by **Designator**, so the two parts of the RT1062
multi-part symbol collided and one was silently dropped. The arithmetic pinned it exactly: the
oracle loaded 783 pins where the harvest holds 881, and the difference of 98 is precisely one
`U6-RTC` part. **Every one of those six is a signal terminating on the RT1062** — the component
whose pins were missing. A dropped symbol part manufactures defects concentrated in whatever that
part connects to, which is the shape most likely to look convincing.

**Second: a real finding nearly dismissed from a truncated excerpt.** All 41 `U9-ESP` pins read as
unconnected. That was checked against the DRC log — via a summary that showed `U9-ESP.9` and
`U9-ESP.10`, which read as "the DRC says only two pins float", so the geometry looked broken.
Reading the actual log gives a different answer: **7** batched floating-pin warning lines, using
the ideographic comma `、` as an intra-field separator, naming

```text
U6-RTC 111 floating pins ·  U9-ESP 19 ·  J1-PWR1 15 ·  U12-NFC 11
U13-MOT   6 ·  J9-AUD   6 ·  D1-PWR1  4 ·  U16-VAL  3
```

DRC 19 against geometry 26 on `U9-ESP` is an order-of-magnitude agreement, not a contradiction.
The near-miss came from trusting a summary of evidence instead of the evidence.

## What is genuinely open, stated as open

Both of these are unresolved and neither should be repeated as fact:

- **`U9-ESP` pins 1 (GND), 2 (3V3) and 41 (GND)** read unconnected in geometry at tol=5 yet are
  absent from the DRC's floating list. If the geometry is right, the ESP32-S3's supply pins are
  unwired — canon `K1E-020`, and serious. If the DRC is right, the tolerance or transform is short.
- **`BUCK_PG` reaches only `R75-PWR2.1`**; `U3-PWR2` pin 5 does not land. Decision **D-045** was
  ratified today asserting that connection exists. The DRC cannot settle it — it ran at 12:17,
  before the PG pull-up transaction was executed.

Also measured, and clean: **zero pins belong to more than one net** across all 881.

## Artefacts

```text
jobs/full-pin-harvest.json / .results.json   231 components, 881 pins, 0 failures, read-only
pin-net-map-489736.json                      transform, landing counts, net -> pins,
                                             nets reaching fewer than two pins
```

`pin-net-map-489736.json` is a **second implementation** for differencing against the oracle. It
is not truth; it is the one that has already been wrong twice today.

---

## Root cause found: one off-sheet wire, and the transaction that closed clean around it

The rails audit reported the TPS62913 `PG` pin unconnected with its wire "mirrored to negative y
off-sheet". That is confirmed, root-caused and bounded.

**Exactly one wire out of 675 has any negative y coordinate, and it is `BUCK_PG`:**

```text
e146347   NET=BUCK_PG   [[1000,-4535,1130,-4535], [1000,-4480,1000,-4535]]

all other wires        : 674 fully on-sheet
component anchor range : y 0 .. 4610   (page height 4800)
```

**The cause is the Y-negation trap, applied in reverse.** `list_schematic_component_pins` returns
pin coordinates with negative y; page coordinates are the negation. A repair script read a pin
coordinate and wrote a wire at that literal value instead of negating it, so the wire was drawn
off the bottom of the page. The wire starts at `(1000,-4480)`, and `R75-PWR2` pin 1 sits at raw
`(1010,-4480)` — the same frame error that made a naive pin-to-wire snap land 0 of 881 pins
earlier today.

### Why this is the most important finding of the pass

The transaction `canonical-power-buck-pg-pullup-wire-2026-08-28` **closed as ACCEPTED**. It has a
snapshot, a semantic read-back, a source-hash change, a 1800×1129 screenshot, four granular visual
checks and a `MUTATION_INSPECTED` ledger event. Every gate requirement was met.

And the wire it created connects nothing, because it is off the page — where no screenshot of the
page can show it.

Decision **D-045** was ratified today on the strength of that transaction, asserting that
`U3-PWR2` pin 5 drives `BUCK_PG` through a 10 k pull-up to 3V3. The pull-up half is real:
`R75-PWR2.1` does land on an on-sheet `BUCK_PG` wire. The regulator half does not exist. An
open-drain PG left floating reports nothing, which is exactly the condition D-045 was written to
prevent.

This is the concrete answer to why an evidence layer that cannot go red is worse than no evidence
layer. A hash changed, a screenshot existed, a census moved, four checks said OK — and the
electrical result was absent. Only geometry measured against the page boundary caught it.

### Bounded repair

```text
1. delete wire e146347 (off-sheet, NET=BUCK_PG)
2. draw BUCK_PG from the existing on-sheet R75-PWR2.1 node to U3-PWR2 pin 5,
   using PAGE coordinates — page = (pin.x, -pin.y)
3. re-verify: BUCK_PG must reach exactly two pins, R75-PWR2.1 and U3-PWR2.5
4. D-045 stands as a correct ruling but is NOT YET IMPLEMENTED; its status must say so
   until the repair closes
```

### Two confirmations this also delivers

- **The ESP32-S3 really is unwired.** The rails audit independently found a systematic **+5 unit**
  offset on `U9-ESP` wiring, and mapped the affected nets (`GND`, `3V3`, `ESP_EN`, `NFC_IRQ`,
  `MOTION_INT_S3`, `S3_POR_REQ`, `RT_PWR_VALID`). That matches the geometric finding of 26
  unconnected `U9-ESP` pins at tol=5 and explains the residual against the DRC's 19. The earlier
  hesitation about whether this was a measurement artefact is resolved: it is a real defect.
- **`RT_PWR_VALID` is decorative at both ends** — the TPS3808 supervisor's SENSE input floats, so
  it monitors nothing, and the net reaches only a pull-up. That is handover item P0-H, worse than
  the handover predicted.

---

## CORRECTION — the ESP32-S3 finding was overstated, and the reason matters

An earlier section of this receipt recorded the `U9-ESP` wiring offset as a confirmed electrical
defect. **That claim is withdrawn.** What is confirmed is a *drawing* defect. Whether it is an
electrical one is unresolved, and the evidence currently leans against it.

### The forensic timeline

`U9-ESP`'s anchor is stable at `(4125,4345)` across **38 consecutive snapshots**, then jumps to
`(4255,4360)` — while the `ESP_EN` wire moves only `(+20,+15)`. Component and wires moved by
different amounts, which is what breaks the coincidence.

The move lands inside one transaction, and the ledger tells its whole story:

```text
04:13:21Z  MUTATION_BEGAN      canonical-esp-service-label-visibility-repair  stage=repair
           intended_delta = "Restore visible endpoint net labels for ESP service USB support
                             parts WITHOUT CHANGING ELECTRICAL TOPOLOGY"
04:14:15Z  MUTATION_RECORDED   474399:c735a3f7 -> 474325:91295516
04:14:15Z  MUTATION_INSPECTED  verdict = REJECTED
04:14:40Z  MUTATION_BEGAN      kind=repair, repairs itself
04:15:41Z  MUTATION_ABORTED_NO_CHANGE -> REJECTED
04:15:53Z  MUTATION_BEGAN      kind=repair, repairs itself
04:16:51Z  MUTATION_RECORDED   474325:91295516 -> 474325:96bb5c36   (same length: metadata only)
04:16:51Z  MUTATION_INSPECTED  verdict = ACCEPTED
```

A transaction that promised not to change topology was **REJECTED**, its first repair aborted with
no change, and its second repair was **ACCEPTED** while changing only metadata. **The displacement
introduced at `474325:91295516` was never undone.** That is canon `K1E-041` — a partial mutation
left in place is more dangerous than a clean failure — and it is visible in the ledger as a
rejection that was closed without restoring the prior state.

### Why the electrical claim does not follow

Captain's DRC ran at **04:17:37Z — 46 seconds after** that ACCEPTED repair. So it inspected the
sheet *with* the displacement already present. It reported **19** floating pins on `U9-ESP`, not 41.

So EasyEDA considered the module connected after the move. Its netlist does not depend on exact
endpoint coincidence the way this geometric measure does.

### What that means for the connectivity oracle — the lesson turned around

The oracle measures **whether wires visually meet pins in the drawing**. That is a real and
required property: `schematic/SINGLE-SHEET-CONTRACT.md` demands visible wiring, and a sheet whose
wires do not touch their pins fails it. **But it is not EasyEDA's netlist**, and this receipt
briefly treated the two as the same thing.

That is the same error this programme keeps making, pointed the other way. The earlier finding was
that checks read the drawing's *annotations* instead of its geometry. The correction here is that
geometry is not automatically the electrical truth either — in this tool the netlist is the
authority, and geometry is a second, weaker witness that happens to be the one measurable from a
source dump.

### The one geometric finding that survives regardless

**A wire at negative y is off the page.** No snap tolerance recovers that, and no netlist should
bind through it.

```text
e146347   NET=BUCK_PG   [[1000,-4535,1130,-4535],[1000,-4480,1000,-4535]]
          the only wire of 675 with any negative coordinate
```

The PG pull-up transaction ran at ~04:56Z, **after** the 04:17:37Z DRC, so that DRC cannot clear
it. `BUCK_PG` remains a live concern and D-045 remains unproven.

### Status of the two open questions

```text
U9-ESP wiring   DRAWING DEFECT CONFIRMED (component displaced, wires not)
                ELECTRICAL STATUS UNRESOLVED - DRC after the move saw 19 floating, not 41
                Root cause dated and attributed; the rejected transaction was never rolled back

BUCK_PG         OFF-SHEET WIRE CONFIRMED, postdates the DRC, D-045 not demonstrated
```

Both are settled by one action that this host build cannot perform: **a fresh GUI DRC run.**
`run_schematic_drc` and `get_schematic_netlist` both return *"This EasyEDA runtime does not expose
sch_Drc / sch_ManufactureData"*, leaving `get_document_source` as the only programmatic oracle. The
GUI Check DRC panel is the certifying gate by doctrine anyway.

---

## A method the orchestrator pushed, a lane refused, and the lane was right

Recorded because the refusal is more valuable than the method would have been.

Faced with pin coordinates that would not land on wire geometry, one lane fitted a **per-component
translation constrained to reproduce EasyEDA's DRC verdict on every pin**, achieving an exact fit
on 221 of 228 components. The result looked authoritative, and the orchestrator propagated it to
two further lanes as the house method.

The oracle lane declined to implement it and wrote down why. The argument holds:

1. **It is self-defeating against the oracle's own purpose.** The checker exists precisely because
   the drawing and the netlist can disagree. Fitting the geometry until it reproduces the netlist
   verdict makes "the wires do not meet the pins" unreportable **by construction**.
2. **It fits the model to the answer.** Two free parameters per component, chosen to maximise
   agreement with a target verdict, will agree with that verdict. `221/228` is what the method
   *produces*, not evidence that it is correct. It also spends the DRC's most valuable property —
   being an **independent** witness — to calibrate the very thing it should be checking.
3. **A measured counterexample.** `C10-PWR2` was cited as needing a `(0,-5)` offset. Its pin cloud
   sits at delta **(0.0, 0.0)** from its own source anchor: the pin data is correct and the **wire**
   is 5 units off. Applying that "correction" moves good pin data onto a badly drawn wire and
   **erases the defect** — on the buck soft-start capacitor, one of the parts D-045 covers.

`U9-ESP`'s `(5,-20)` is the same trap in a different guise. It is not a registration error to
cancel; it is an uncorrected displacement from the rejected-never-rolled-back
`canonical-esp-service-label-visibility-repair` transaction. Fitting it away would blind the
oracle to exactly the event class the mutation gate exists to catch.

### What replaced it

Pins are measured against **their own component's source anchor**. 214 of 229 components sit within
10 units and need no correction at all; the residual is reported as
`components_displaced_from_their_wiring` — a finding in its own right rather than a nuisance to be
cancelled. The DRC stays an independent witness and is never a fitting target.

The checker also gained a guard nobody asked for and everybody needed: **it refuses any snap
tolerance greater than or equal to half the measured pin pitch**, because at that distance a wire
endpoint is equidistant between two adjacent pins and the tolerance silently resolves the tie. It
discovers the pitch from the data rather than assuming it.

### Current state of the checker, run against the real sheet

```text
CONNECTIVITY=RED
pins_landing_on_wire_geometry           = 654
net_labels_meeting_fewer_than_two_pins  = 7      (renamed - it is a LABEL finding, not electrical)
off_sheet_wires                         = 1      (e146347, BUCK_PG, no registration caveat)
self-test                               = 13 cases, 4 RED, 3 FAIL-CLOSED, all as expected
```

The rename matters. `nets_reaching_fewer_than_two_pins` read as an electrical claim the checker
cannot make on this host; `net_labels_meeting_fewer_than_two_pins` says what is actually measured.
The file now states in its own header that it is **not** a netlist oracle.

### The general lesson

A subagent's disagreement with the orchestrator is evidence, not friction. This one was resolved
by checking the counterexample rather than by seniority, and the orchestrator's instruction was
withdrawn from two other lanes as a result. Had it stood, the programme would have gained a
confident number and lost the ability to see the defect it was measuring.

---

## Fresh GUI DRC, 14:58:52 — the netlist-grade evidence, and what it settles

```text
archived  anchors/schDrcLog_2026-08-28T1458.txt   sha256 72b81f296a3af28c   432 lines
summary   Fatal Error: 0 · Error: 0 · Warning: 15 · Info: 414
prior run 12:17:37 was Warning: 22 · Info: 398
```

### Every open question, closed

| Question | Verdict | Evidence |
| --- | --- | --- |
| `BUCK_PG` connected? | **NO — confirmed broken** | *"The wire BUCK_PG is a single network connected to only one component pin"*, and `U3-PWR2.5` appears in the floating list. **D-045 is ratified but not implemented.** |
| `e153914` debris? | **YES — confirmed** | *"The wire $1N153914 is a single network connected to only one component pin"* |
| ESP32-S3 disconnected? | **NO — fully connected** | `U9-ESP` has **zero** floating pins, down from 19. The geometric alarm was entirely registration artefact. |
| `NFC_IRQ` reaches a host? | **YES — NFC-D2 refuted** | `NFC_IRQ` appears nowhere; only two single-pin nets exist on the whole board and it is not one of them. |
| RT unconnected balls? | **80, not 111** | The 111 was inflated by the same mis-registration. |

**Only two single-pin networks exist on the entire board: `BUCK_PG` and `$1N153914`.** Both were
found by geometry first — one as an off-sheet wire, one as an unnamed stub — and both are now
confirmed by EasyEDA's own netlist engine. That is the geometric oracle earning its place.

### A defect only the DRC found

```text
Component MIMXRT1062DVJ6B is a multi-part component, the properties of each part should be
the same. $1I3295、$1I3673 have different property Supplier Part, Add into BOM, supplierId.
```

EasyEDA independently confirms `U6-RTC` is **one** multi-part component — settling the
two-MCU question from the tool itself — while flagging that its two parts carry inconsistent
metadata. Real, small, bounded, and missed by every lane.

### Why this DRC is not a quality gate

It reports **Error: 0, Fatal: 0** on a board whose primary USB-C power inlet has **9 of 17
contacts floating**, including both CC pins and three of four VBUS. Nothing here is graded an
error.

The 414 Info lines are 98% known non-defects:

```text
229  "Designator doesn't match the suggestion rule"  <- the K1 -PWR1/-RTC suffix convention,
                                                        which the takeover receipt says not to fix
179  "has empty value of property Value"             <- value lives in `Name` on this sheet
  5  wires/buses not connected to netflag or netport
  1  USB4105-GF-A pad has no corresponding pin       <- the real one: J1 symbol/footprint mismatch
```

And its advice is actively unsafe where it matters most. It batches **101 distinct floating pins
into 4 lines** and gives all of them one recommendation — *"suggest placing No Connect Flag"*:

```text
80  U6-RTC    unused GPIO           -> advice correct
 9  J1-PWR1   VBUS, CC1, CC2, GND, shell -> advice catastrophic
 5  U13-MOT   incl. mode/address straps
 3  U16-VAL   2  Y2-NFC   1  U3-PWR2 (PG)   1  U12-NFC (RFI2)
```

Followed literally, this DRC instructs an operator to no-connect-flag the power inlet. It has no
severity model that distinguishes an unused GPIO from an unwired VBUS contact.

**Conclusion: useless as a pass/fail gate, valuable as an independent witness.** It confirmed two
defects, refuted two false alarms raised by geometry, and found one nobody else had. That is
exactly the role the differential approach assigns it — and the reason it must never be the thing
that certifies VAL-G2.

---

## Harness regression and mutation proof, run by the orchestrator

Every checker re-run after the day's changes, plus a mutation test on the one fix most likely to
have been made green by weakening it rather than by working.

```text
test_connectivity_and_drc_oracles.py        exit 0   OK
test_easyeda_mutation_gate.py               exit 0   OK
test_single_schematic.py                    exit 0   OK
test_single_sheet_qualification_plan.py     exit 0   OK
test_negative_suite.py                      exit 0   NEGATIVE_SUITE=PASS   21/21 CORRECTLY_FAILED
check_authority_consistency.py              exit 0   AUTHORITY_CONSISTENCY=PASS
check_terminology.py                        exit 0   TERMINOLOGY=PASS
```

The negative suite still rejects all 21 historical bad cases, so the day's edits did not soften
any pre-existing guard.

### Mutation test on the staleness gate

`check_single_schematic.py` was green-while-blind this morning and now refuses. Its test suite
also passes — which is exactly the shape a checker takes when someone makes the test agree with a
weakened check. So the guard was neutered and the suite re-run:

```text
mutation      staleness comparison forced inert
result        test_single_schematic.py -> FAILED (failures=2)
restored      bare checker still exits 1 with STALE READ-BACK
```

Two tests go red on the mutation, so the assertions are load-bearing rather than decorative. The
suite also carries a positive control — `test_content_checks_pass_when_readback_is_current` — so
the gate cannot pass by simply failing everything. Named assertions include
`test_on_disk_readback_is_refused_against_the_live_gate`, `test_advanced_gate_hash_is_refused`,
`test_missing_gate_state_is_refused` and `test_missing_source_record_fails_closed`.

Live proof, against the real current state rather than a fixture:

```text
SINGLE_SCHEMATIC_CHECK=ERROR STALE READ-BACK: this check would measure source_hash
389936:080d43fd, but the live gate holds 497055:82c17c12. The read-back is a static file
that nothing refreshes, so a pass here would say nothing about the current sheet.
```

---

## Readable capture proved possible — the blocker is one integer

The visual-evidence requirement is no longer theoretically blocked. A standalone read-only probe
established that the editor's own toolbar can reach gate-quality scale:

```text
mechanism   locate "Zoom In" by tooltip in the top-frame DOM -> {x:278,y:48}
            "Fit All in Window(K)" -> {x:340,y:48}
            fit-all, then 14 left-click pairs 160 ms apart, then settle
result      C62-MOT and C63-MOT rendered with their 3V3 / GND net labels and
            100nF values CLEARLY LEGIBLE — comfortably above the 1.0 px/unit floor
proof       zoomprobe-14clicks.png
```

`harness/easyeda_readable_capture.mjs` already implements the right contract — it refuses unless
the pixels changed, the measured scale clears the floor, and the target is in the final frame.
Its zoom loop is capped at **4** iterations while each click gains only ~1.2× and the gain decays,
so from a fit-all baseline it cannot reach the floor and always exits on the cap. Measured
progression: `0.0974 → 0.1234 → 0.1487 → 0.1683`, ratios `1.267, 1.205, 1.132`.

The refusal was correct behaviour throughout. The tool was never broken in the sense that
mattered — it declined to hand over an image it could not prove readable, which is exactly the
property `close_visual_from_census.py` lacked.

Incidental but useful: the probe capture also shows the DRC panel open on the 14:58:52 run —
`All 431 · Fatal Error 0 · Error 0 · Warn 15 · Info 416` — with `$1N153914` and `BUCK_PG` in the
first two warning rows. The panel itself is capturable, so it can corroborate the two lead
transactions alongside their block-scale images.
