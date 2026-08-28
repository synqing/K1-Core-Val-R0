---
abstract: "Build receipt, 2026-08-28: label-to-pin binding oracle (transform audited differentially, pins keyed by primitive id, full 881-pin coverage), DRC log parser, and repairs to THREE independent green-lights-wired-to-nothing in one harness. Records what each checker measures, every fault-battery case with observed RED/GREEN, ten mutation tests proving each guard load-bearing, and the finding that the ESP32-S3 block is wired to coordinates that miss its pins — and that BUCK_PG binds one pin, not the two D-045 asserts, on a wire that is both sign-flipped and 10 units short at each end."
---

# Oracle build receipt — a DRAWING oracle, DRC parsing, three false-green repairs

> **Scope of the connectivity oracle, stated first because it bounds every number below.**
> It measures **whether wires visually meet their pins in the drawing**. It is **NOT a
> netlist oracle** and must never be quoted as one. Disproof on the record: `U9-ESP` was
> displaced by a rejected-but-never-rolled-back transaction at `474325:91295516`, and the
> DRC — run 46 s after the accepted repair that followed, displacement already present —
> reported **19** floating pins there, not the 41 the geometry sees. EasyEDA's netlist does
> not require exact endpoint coincidence.
>
> The property is still real and still required: `SINGLE-SHEET-CONTRACT.md` demands visible
> wiring — *"A page of hundreds of floating components joined only by global names is not a
> schematic"* — so a sheet whose wires miss their pins fails the contract whatever the
> netlister salvages. Violation names are drawing language accordingly:
> `net_labels_meeting_fewer_than_two_pins`, `wires_not_meeting_any_pin`,
> `pins_met_by_multiple_net_labels`, `off_sheet_wires`.
>
> Also confirmed independently: only **9 of 1359** wire endpoints are shared, so all 675
> wires are isolated labelled stubs and there is no geometric graph to traverse.

## Why the DRC-anchored per-component fit was DECLINED

A per-component translation fitted to reproduce the DRC verdict (reported: 221/228 exact)
was proposed as the registration method. It is declined as the measurement path, and the
residual offsets are reported as a **diagnostic** instead. Three reasons:

1. **It is self-defeating against the reframe above.** The oracle exists because the netlist
   and the drawing disagree. Fitting geometry until it reproduces the netlist verdict makes
   *"the wires do not meet the pins"* unreportable by construction — the one thing the
   contract needs checked.
2. **It fits the model to the answer.** Two free parameters per component chosen to maximise
   agreement with a target verdict *will* agree with it; 221/228 is what the method produces,
   not evidence it is right. It also forfeits the DRC as an **independent** witness, which is
   its more valuable role — and with `run_schematic_drc` and `get_schematic_netlist` both
   absent from this host build, the parsed log is the only netlist-grade evidence there is.
3. **Measured counterexample.** `C10-PWR2` was cited as needing `(0,-5)`. Its pin cloud sits
   at delta **(0.0, 0.0)** from its own source anchor — the pin data is right and the *wire*
   is 5 units off. That offset would move good pin data onto a badly drawn wire and erase the
   defect. `U9-ESP` does show **(5, -20)**, matching the known rejected-transaction
   displacement — a real uncorrected defect, and cancelling it would blind the oracle to
   exactly the event class the mutation gate exists to catch.

Co-registration is not broken in general: **214 of 229** components have their pin-cloud
bbox centre within 10 u of their own source anchor.

**The displacement diagnostic is deliberately NOT a violation.** It finds 15 components,
but 14 are `(-20, 0)` on single-pin test points and connectors — symbol asymmetry from a
20-unit pin length, not displacement. Separating the two needs symbol definitions this
oracle does not have, so it reports the offsets and declines the verdict.

Date: 2026-08-28 · Lane: `evidence/VAL-G2-2026-08-28/canonical-core-val-r0`
Read-only build. No EasyEDA session, bridge, CDP port or MCP tool was touched.

**The finding is not any one repair. It is that this harness contained three
independent green lights wired to nothing, and all three reported OK.**

| # | Checker | How it was green while blind |
| --- | --- | --- |
| 1 | `close_visual_from_census.py` | Wrote its own four `"result": "OK"` checks and `"verdict": "ACCEPTED"` — nobody read the canvas |
| 2 | `easyeda_mutation_gate.py` (bare `validate`) | Defaulted to the **retired** lane; both lanes read READY, so the wrong green was indistinguishable |
| 3 | `check_single_schematic.py` | Measured a **static read-back file** two revisions stale; would have passed forever, including on an emptied sheet |

---

## 1. What was built or changed

| File | Role |
| --- | --- |
| `harness/check_schematic_connectivity.py` | **NEW** — measures label-to-pin binding, abstains where pin geometry is missing |
| `harness/parse_drc_log.py` | **NEW** — structured DRC findings, reconciled against the log's own census, waiver register |
| `harness/check_single_schematic.py` | Staleness gate added; hardcoded constants deliberately **not** re-baselined |
| `harness/easyeda_mutation_gate.py` | Lane resolution added; gate semantics otherwise unchanged |
| `schematic/single-sheet-qualification/close_visual_from_census.py` | Rewritten — structurally cannot auto-accept |
| `harness/test_single_schematic.py` | Repaired: five tests had begun passing for the wrong reason |
| `harness/test_connectivity_and_drc_oracles.py` | **NEW** — runs all four batteries under pytest |
| `harness/fixtures/{connectivity,drc,single-schematic}/` | The deliberately-broken fixtures |
| `evidence/.../DRC-WAIVERS.json` | Canonical waiver register, seeded with `J7-ESP` SBU1/SBU2 |
| `evidence/VAL-G2-2026-08-28/LANE-RETIRED` | Retirement marker excluding the dead lane from gate discovery |

Full harness suite: **74 passed**.

---

## 2. The connectivity oracle measures label-to-pin binding — NOT fragmentation

### The property this started with was wrong, and the number it produced was noise

The first version counted, per named net, how many disjoint geometric islands
carried that name. On the frozen denominator it reported **142 of 143 nets
fragmented**, GND at 186 islands, 3V3 at 90 — islands == wire count for
essentially every net.

That is not 142 defects. It is the sheet's **construction method**:
`schematic/wire_led_efuse_support.py:37-48` emits a 20-unit stub outward from
each pin and hangs a `NET` ATTR on it. Pins share a net by sharing a NAME, never
by touching. A checker flagging that goes RED on 142/143 — as useless as one
that always passes.

It also contradicted doctrine. `schematic/SINGLE-SHEET-CONTRACT.md` says
verbatim: *"Long global rails and major shared buses may use labelled trunks."*
GND and 3V3 are exactly that.

The same mistake had been made a second time, in `dangling_wire_endpoints`: it
counted 722 free stub far-ends, when by construction **every** stub has exactly
one free end. Both are now statistics, never violations.

### The property that actually carries the electrical claim

> For each named net, how many distinct **component pins** does it actually touch?

This is what `K1E-016` means by *"a named one-ended stub is not an electrical
connection"*, and what EasyEDA's own DRC reports as *"The wire X is a single
network connected to only one component pin."*

Three violation classes: `nets_reaching_fewer_than_two_pins` (K1E-016),
`wires_touching_no_pin`, `pins_on_multiple_nets` (K1E-018).

### Coverage is measured and abstained on, never assumed

Pin coordinates are not in the schematic source — they live in the symbol
library — so they are reconstructed from on-disk read-backs. The transform is
`(x, y) -> (x, -y)`, audited differentially in **§6a**.

A wire touching no known pin is attributed to its nearest component anchor:

- nearest component's pins **are** measured → **VIOLATION** (it really touches nothing)
- nearest component's pins are **not** measured → **UNKNOWN**, the oracle abstains

**Final coverage: 228/228 designators, 229/229 component parts, zero
abstentions**, using `jobs/full-pin-harvest.results.json` (231 records,
881 pins). Pin data is keyed by `componentPrimitiveId`, so the two parts of the
`U6-RTC` MIMXRT1062 (`e3295` + `e3673`, 98 pins each) are both retained.

The interim run was coverage-starved: designator-keyed loading held 783 of 881
pins, the missing 98 being exactly one RT1062 part, which forced 9 nets into
UNKNOWN. Full coverage removed six nets from the violation list
(`AUDIO_BCLK_RT`, `BOOT_MODE1`, `LED_D0_3V3`, `LED_D1_3V3`, `SWD_SWCLK`,
`SWD_SWDIO`) — they were artefacts of the missing part, exactly the false
"reaches fewer than two pins" class the gap could manufacture. The abstention
count rides on the headline line so a GREEN can never quietly mean "skipped".

### What this oracle cannot see

It can only measure nets that **exist**. Confirmed on the real sheet: `NFC_RFO1`
exists and binds 2 pins, while **`NFC_RFO2`, `NFC_RFI1` and `NFC_RFI2` do not
exist at all** — invisible to this checker. Completeness against a design
authority is a different checker with an external denominator; claiming this one
covers it would be a false denominator.

---

## 3. `parse_drc_log.py`

Four scripts had hand-transcribed this log into Python dict literals — a second,
undocumented parser with no denominator. This ends that.

- Ten classified kinds; anything unmatched becomes `unclassified` and turns the run RED.
- **The denominator is external**: the log's own `Fatal Error: N, Error: N, Warning: N, Info: N`
  line. Counts that do not reconcile FAIL CLOSED rather than reporting a tidy subset.
- **Waivers never delete a finding** — they move it to a printed, counted `waived` bucket,
  and a waiver matching nothing is reported STALE and turns the run RED.

**The unclassified guard earned its keep on the first real run.** It reported 7
unclassified lines, caused by a **non-breaking space** (U+00A0) inside
`components\xa0Pins floating` — invisible in a terminal, and exactly what a hand
transcription normalises away without noticing. The parser now normalises exotic
spaces, counts how many lines needed it (7), keeps the raw message, and carries
fixture `nbsp-floating-pins` so it cannot regress.

---

## 4. Fault batteries — observed results

```bash
python3 harness/check_schematic_connectivity.py --self-test
python3 harness/parse_drc_log.py --self-test
python3 harness/check_single_schematic.py --self-test
python3 schematic/single-sheet-qualification/close_visual_from_census.py --self-test
```

### 4.1 Connectivity — 12 cases, 3 RED, 3 FAIL-CLOSED observed

| Case | Expected | **Observed** | What fired |
| --- | --- | --- | --- |
| `joined-net` | GREEN | **GREEN** | one label binding two real pins |
| `t-junction` | GREEN | **GREEN** | T-junction stub, three pins bound |
| `disjoint-same-name` | GREEN | **GREEN** | **POSITIVE CONTROL** — disjoint stubs sharing a name must NOT be flagged |
| `one-pin-net` | RED | **RED** | `nets_reaching_fewer_than_two_pins: 1` |
| `stub-to-nowhere` | RED | **RED** | `wires_touching_no_pin: 1` |
| `pin-on-two-nets` | RED | **RED** | `pins_on_multiple_nets: 1` |
| `unmeasured-part` | GREEN | **GREEN** | **ABSTENTION CONTROL** — `nets_unknown: 1`, not a defect |
| `rotated-component` | GREEN | **GREEN** | **TRANSFORM CONTROL** — 90°/270° parts; RED if rotation is composed |
| `multi-part-designator` | GREEN | **GREEN** | **KEYING CONTROL** — RED if keyed by designator (`pins_loaded: 2`) |
| `empty-source` | FAIL-CLOSED | **FAIL-CLOSED** | `zero source records` |
| `no-wires` | FAIL-CLOSED | **FAIL-CLOSED** | `zero WIRE records` |
| `no-pin-data` | FAIL-CLOSED | **FAIL-CLOSED** | `no pin geometry loaded` — property unmeasurable |

### 4.2 DRC parser — 10 cases, 4 RED, 4 FAIL-CLOSED observed

| Case | Expected | **Observed** | What fired |
| --- | --- | --- | --- |
| `clean` / `waived-warn` | GREEN | **GREEN** | — |
| `unwaived-warn` | RED | **RED** | `open_warn_or_worse=1` |
| `stale-waiver` | RED | **RED** | `stale_waivers=1` |
| `unclassified` | RED | **RED** | `unclassified_lines=1` |
| `nbsp-floating-pins` | RED | **RED** | RED **with** `unclassified=0`, `nbsp_normalised=1` |
| `empty` / `garbage` | FAIL-CLOSED | **FAIL-CLOSED** | `parsed zero DRC findings` |
| `no-summary` | FAIL-CLOSED | **FAIL-CLOSED** | `no external denominator` |
| `count-mismatch` | FAIL-CLOSED | **FAIL-CLOSED** | `Warn declared=7 observed=1` |

### 4.3 Single-schematic staleness gate — 7 cases, 6 REFUSE observed

| Read-back | Gate state | Expected | **Observed** |
| --- | --- | --- | --- |
| current | matching | PASS | **PASS** |
| current | advanced | REFUSE | **REFUSE** (`STALE READ-BACK`) |
| missing | matching | REFUSE | **REFUSE** (`read-back file missing`) |
| no `source` record | matching | REFUSE | **REFUSE** (`no 'source' record`) |
| empty | matching | REFUSE | **REFUSE** (`zero read-back records`) |
| current | no hash | REFUSE | **REFUSE** (`no current_source_hash`) |
| current | missing | REFUSE | **REFUSE** (`cannot prove currency`) |

### 4.4 `close_visual_from_census.py` — 11 cases, 10 REFUSED observed

Well-formed block inspection ACCEPTED; the **historical auto-accept** (the exact
record the old script wrote) REFUSED, plus readability-OK-at-whole-sheet,
boilerplate detail, no checks supplied, unanswered declared check, undeclared
extra check, ACCEPTED-over-DEFECT, no inspector named, thin observed delta, and
REJECTED-naming-no-defect — all REFUSED.

---

## 5. Mutation tests — proving each guard load-bearing

A passing battery proves the fixtures match the code. It does not prove the code
does the work. Each guard was neutered in a scratch copy and the battery re-run.

| Mutation | Battery result | Verdict |
| --- | --- | --- |
| Connectivity: K1E-016 `<2 pins` check disabled | `one-pin-net` RED → **GREEN** | killed |
| Connectivity: pin-less-stub violation dropped | `stub-to-nowhere` RED → **GREEN** | killed |
| Connectivity: abstention removed | `unmeasured-part` GREEN → **RED** | killed |
| Connectivity: **fragmentation reinstated as a violation** | `disjoint-same-name` GREEN → **RED** | killed |
| Connectivity: no-pin-data vacuity guard removed | `no-pin-data` FAIL-CLOSED → **GREEN** | killed |
| Connectivity: **identity transform** (no y negation) | 8 of 12 cases flip | killed |
| Connectivity: **rotation composed** into transform | `rotated-component` GREEN → **RED** | killed |
| Connectivity: **designator keying** restored | `multi-part-designator` — **survived**, then killed | fixed, then killed |
| Connectivity: **half-pitch tolerance refusal** removed | `snap-tolerance=5` FAIL-CLOSED → **GREEN** | killed |
| Connectivity: **empty-DRC differential guard** removed | reports `agreed 0 / drc_only 0` = false agreement | killed |
| Connectivity: **off-sheet-wire rule** removed | `off-sheet-wire` positive control `off_sheet_wires 1 -> 0` | killed |
| DRC: NBSP normalisation removed | still RED, but **positive control failed** (`unclassified 0→1`) | killed |
| DRC: summary reconciliation disabled | `count-mismatch` FAIL-CLOSED → **RED** | killed |
| DRC: stale-waiver detection removed | `stale-waiver` RED → **GREEN** | killed |
| Staleness: hash comparison disabled | `state-advanced` REFUSE → **PASS** | killed |
| Staleness: gate-hash presence guard removed | **survived**, then killed — see below | fixed, then killed |

Three mutants survived their first attempt, and each exposed the same failure —
**a case reaching the right verdict for the wrong reason**:

- **Connectivity zero-records guard.** An empty source also has zero wires, so
  deleting the zero-**records** guard still failed closed via the zero-**wires**
  guard. Fixed by pinning the required fail-closed reason per case.
- **Staleness gate-hash presence guard.** A gate state with no
  `current_source_hash` also fails the hash comparison, so deleting the presence
  guard left the battery green with a misleading `STALE READ-BACK` message.
  Fixed the same way; the mutant now reports `WRONG GUARD FIRED`.
- **`close_visual` boilerplate rule.** It sat only on the CLI parse route; a
  direct call to `build_visual_record` sailed past it. Moved into the core
  builder. A guard on one route is not a guard.
- **The multi-part keying control.** Reverting to designator keying left it
  GREEN, because dropping a part also made every part look unmeasured and the
  ABSTENTION path absorbed the bug. The control now asserts `pins_loaded`, so
  the dropped pin itself is the failure regardless of what abstention does.

---

## 6. The three false-green repairs

### 6.1 `close_visual_from_census.py` — wrote its own OK

The previous version hardcoded four checks, every one `"result": "OK"`, and
`"verdict": "ACCEPTED"`, filling the mandatory `detail` strings from the semantic
census — derived from `get_document_source`, not from anybody looking. Verbatim,
its third check:

```
{ "name":   "changed labels pins and geometry readable",
  "result": "OK",
  "detail": "Pin glyphs are not readable at whole-sheet zoom. Named-net ATTR census
             in the semantic read-back is the electrical proof." }
```

The detail says the thing the check is named after could not be seen. The result
says OK anyway. That satisfied `easyeda_mutation_gate.py close` and moved the
gate to READY with nobody having read the canvas. The gate was measuring the
**shape** of the evidence record; the script manufactured a correctly shaped one.
It also read state from the **retired** lane, so it could report the wrong phase too.

Preserved at the same path with that mechanism quoted in its header. It now
cannot produce an OK: every result and detail must be supplied on the command
line, check names are validated against the transaction's `expected_checks`, an
`--inspected-by` attestation is mandatory, the census is attached as
clearly-labelled context only, and a readability check marked OK at
`scale=whole_sheet` is refused outright.

### 6.2 `easyeda_mutation_gate.py` — bare `validate` hit the retired lane

`DEFAULT_STATE`/`DEFAULT_LEDGER` pointed at the retired lane (project
`09e9c541…`) while the live lane is `canonical-core-val-r0/` (project
`64325d0e…`). `AGENTS.md:39` tells every agent to run a bare `validate` before
actuation. **Both lanes read READY**, so the wrong green was indistinguishable
from the right one.

**Gate semantics unchanged** — explicit `--state`/`--ledger` behaves exactly as
before, verified against the retired lane. Only the bare invocation changed: it
discovers lanes, resolves the single non-retired one, prints
`EASYEDA_MUTATION_LANE_RESOLVED` and `..._PROJECT`, and **refuses** on zero or
multiple live lanes. New `lanes` subcommand lists them. Verified: bare validate →
canonical lane, 170 ledger records; marker removed → `BLOCKED: 2 live mutation
lanes found`, exit 2; restored → green; 21 existing gate tests still pass.

### 6.3 `check_single_schematic.py` — measured a memory of the schematic

It printed `SINGLE_SCHEMATIC_CHECK=OK` and exited 0 while measuring nothing
current. `DEFAULT_READBACK` is a static file nothing refreshes:

| | source_hash | designators | wires | nets |
| --- | --- | --- | --- | --- |
| checker's input (`jobs/final-readback-results.json`) | `389936:080d43fd` | 181 | 517 | 125 |
| frozen denominator | `489736:464c27d4` | 228 | 675 | 143 |
| **live gate** | `497055:82c17c12` | — | — | — |

It would have passed forever regardless of what happened to the canvas,
including if the sheet were emptied. Both ends were dead: it also validates the
designator set against `FIXTURE-PLAN.json`, which is `RETIRED_BY_D_042` — a
retired plan checked against a stale read-back, reporting OK.

**Fix:** the read-back's `sourceHash` must equal `current_source_hash` in the
live lane's `MUTATION-STATE.json`, or the run refuses. The live lane is resolved
through the gate's own `resolve_lane()`, never hardcoded. Today's real state is
therefore a **live RED case**, not a synthetic one:

```
SINGLE_SCHEMATIC_CHECK=ERROR STALE READ-BACK: this check would measure
source_hash 389936:080d43fd, but the live gate holds 497055:82c17c12. ... exit 1
```

The hardcoded `181 designators` / `U6-RTC` duplicate / `389936:080d43fd`
constants are **deliberately not re-baselined** — the writer updates those once
the repair queue lands, against a sheet that has stopped moving.

**Its test file was part of the false green too.**
`test_current_canonical_readback` asserted the checker PASSES on the stale
read-back. Worse, once the gate was in front, all five `run_mutant` tests began
raising `CheckError` from the *staleness gate* before reaching the mutation under
test — five tests passing while testing nothing. They now supply a matching gate
state and **assert on the rejection reason**, so they exercise what they claim.

---

## 6a. The coordinate transform — the load-bearing, formerly unaudited step

Everything this oracle concludes rests on mapping read-back pin coordinates into
source coordinates. That step is now stated exactly and established
**differentially**, not asserted.

    THE TRANSFORM IS:   (x, y)  ->  (x, -y)

`list_schematic_component_pins` returns **absolute page coordinates** in a
y-down screen frame. Component `(x, y, rotation)` is **NOT composed**, and must
not be — rotation is already baked in by the host. Evidence: component `e3673`
has `rotation=90` and its pins read (2010, 4040), (2020, 4040) — absolute page
positions, not anchor-relative offsets awaiting rotation.

Against the 881-pin harvest and 1359 wire endpoints:

| candidate | pins landing | rate |
| --- | --- | --- |
| identity `(x, y)` | 0/881 | **0.0%** |
| **negate y `(x, -y)`** | **654/881** | **74.2%** |
| negate x `(-x, y)` | 0/881 | 0.0% |
| negate both `(-x, -y)` | 0/881 | 0.0% |
| swap `(y, x)` | 0/881 | 0.0% |
| swap+negate `(-y, x)` | 2/881 | 0.2% |

**A wrong transform does not degrade gracefully — it lands ~0%.** Anyone
re-deriving this with the identity transform gets exactly 0% and will conclude
the frames are unrelated. They are not; negate y. `pin_landing_rate` is now
reported beside every verdict, so if it ever collapses it is the transform, not
the board, that broke.

Two battery cases guard this, and both were watched failing under mutation:

- `rotated-component` — 90°/270° parts whose read-back pins are absolute. Adding
  any rotation composition turns it RED.
- `multi-part-designator` — two parts sharing a designator. Reverting to
  designator keying turns it RED.

The keying control initially passed under mutation **for the wrong reason**:
dropping a part also made every part look unmeasured, so the *abstention* path
absorbed the bug. The control now asserts `pins_loaded`, which makes the dropped
pin itself the failure. Same class as the three earlier survivors.

### The 227 non-landing pins: unconnected, not a transform gap

| attribution | count |
| --- | --- |
| EasyEDA's own DRC independently calls them floating | **190** |
| DRC floating but waived (`J7-ESP` SBU1/SBU2) | 2 |
| carry a `NO_CONNECT` mark in the source | 12 |
| unexplained by either | 24 |

A coordinate error cannot correlate 190/193 with an independent instrument. And
23 of the 24 "unexplained" are `U9-ESP` pins — the *other half* of the 23
pin-less stubs clustered around `U9-ESP`/`R73-ESP`. Both halves of that pair are
the same defect: **the ESP32-S3 block is wired to coordinates that miss its
pins.** The DRC does not flag them only because it predates that work.

---

## 6b. Snap tolerance — measured, guarded, and shown

A tolerance changes the findings, so it cannot be chosen by taste. Measured on the
frozen denominator, pin-to-nearest-wire-endpoint distance is **quantised, not
noisy**:

| distance | 0 | 5 | 10 | 20 | >20 |
| --- | --- | --- | --- | --- | --- |
| pins | **654** | 15 | 81 | 47 | 84 |

There is no continuum, so there is no grid-noise band to absorb. All 15 pins at
distance 5 belong to **one component, `U9-ESP`, which has zero pins at distance 0**
— a systematic drawing offset on one part, not measurement error.

**The decisive test.** Bind at tol=5 and compare each wire's NET name against the
PIN's name. It produces **0 correct bindings and 14 wrong ones**:

```
GND        -> U9-ESP.3  (pin name EN)     I2C_SDA  -> U9-ESP.37 (pin name TXD0)
3V3        -> U9-ESP.4  (pin name IO4)    I2C_SCL  -> U9-ESP.36 (pin name RXD0)
ESP_EN     -> U9-ESP.5  (pin name IO5)    NFC_IRQ  -> U9-ESP.6  (pin name IO6)
```

A tolerance that manufactures 14 false connections is not a tolerance; it is a
net-swap. Pin pitch is 10, so tol=5 is exactly half-pitch — a point at distance 5
is **equidistant between two adjacent pins** and the binding is ambiguous by
construction.

**So the oracle uses tol=0, refuses tol >= half the measured pin pitch, and prints
the sensitivity every run:**

```
     tol  <2 pins  no-pin wires  inexact  WRONG pin
       0        7            23        0          0
       5        4             9       16         15  <- AMBIGUOUS, refused by default
      10        4             8       44         42  <- AMBIGUOUS, refused by default
```

The `<2 pins` count does drop from 7 to 4 at tol=5 — bought with 15 wrong-pin
bindings. `--allow-ambiguous-tolerance` overrides the refusal and records every
wrong-pin binding as a violation, so the cost is never hidden.

Battery: fixture `half-pitch-offset` (pin pitch 10) asserts tol=0 RED, tol=4 RED,
tol=5 FAIL-CLOSED, tol=10 FAIL-CLOSED. Deleting the refusal turns tol=5 GREEN —
mutant killed.

---

## 6c. Differential oracle — geometry vs EasyEDA's own DRC

`--drc-report` runs the geometry against `parse_drc_log.py` output as an
independent second implementation of the same question. It fails closed if the
DRC report yields zero floating pins, so an empty second oracle cannot masquerade
as agreement (mutant killed: without the guard it reports `agreed 0 / drc_only 0`,
which reads as perfect agreement).

```
agreed_floating   192   both oracles say unconnected — high confidence, actionable
geometry_only      35   geometry says unconnected, DRC does not
drc_only            3   DRC says floating, geometry says bound — suspect the geometry
```

**`drc_only` is 3, and all three are explained**: `C10-PWR2.1`, `C10-PWR2.2`,
`U12-NFC.20` were rewired by the buck-SS and NFC-decoupling transactions **after**
the 12:17 DRC ran. There is no case where the geometry claims a binding that the
DRC contradicts on comparable evidence.

**`geometry_only` is 35, and it resolves to two real items:**

| attribution | count |
| --- | --- |
| carry a `NO_CONNECT` mark in the source (deliberate) | 11 |
| `U9-ESP` | 22 |
| `U3-PWR2.5` | 1 |
| page-frame pin | 1 |

---

## 6d. The two items resolved

### `U9-ESP` pins 1 (GND), 2 (3V3), 41 (GND) — geometry is right, the DRC is stale

Measured distances to the nearest wire endpoint: **pin 1 = 20, pin 2 = 10,
pin 41 = 20**. None is at 5, so no tolerance reaches them; they are far from any
wire. The mechanism is visible in the whole block: `U9-ESP`'s pins sit at
x=4175/4345 while its wires are drawn at x=4170/4340 — a uniform **5-unit x
offset** — and the wires are additionally on the **wrong pin rows**, which is why
snapping binds `GND` to `EN` and `3V3` to `IO4`.

That offset cannot have existed when the DRC saw 22 of 41 pins connected, and the
wires carrying it (`e103594`, `e103600`, `e103602`) have primitive ids in the
103,000 range — created late. The ESP wiring was redrawn after the DRC ran.

**Conclusion: the ESP32-S3's supplies are unwired — canon `K1E-020`, a major IC
without supply connectivity blocks actuation.** This is the highest-value finding
on the sheet after `BUCK_PG`.

### `BUCK_PG` — unconnected, and not a tolerance artefact

```
BUCK_PG binding vs snap tolerance:
  tol= 0 -> ['R75-PWR2.1']
  tol= 5 -> ['R75-PWR2.1']
  tol=10 -> ['R75-PWR2.1']
  tol=20 -> ['R75-PWR2.1']
```

Completely tolerance-insensitive. `U3-PWR2.5` is confirmed as the power-good pin
(read-back `pinName` = `PG`, matching D-045), and its nearest wire endpoint of any
net is a **GND** wire 10 units away. No `BUCK_PG` wire is near it.

**Scope limit, stated plainly:** the brief asked me to resolve this "directly
against the live sheet". **I cannot and did not** — this agent has no EasyEDA
authority, and a live operator owns the canvas (`K1E-065`, `F-20A`). Everything
above is measured on the frozen `489736` dump plus the on-disk pin harvest. If the
live sheet has moved since, the live check still has to be run by whoever holds
the canvas. On the evidence available, `BUCK_PG` reaches one pin, not the two
D-045 asserts.

---

## 7. What the corrected oracle found on the real sheet

Source `frozen-denominator-489736/source.txt` (`489736:464c27d4`), pins from
`jobs/all-pins-nc-audit.results.json`. Report: `connectivity-report.json`.

Run against the **full pin harvest** (`jobs/full-pin-harvest.results.json`,
231/231 components, 881 pins) — no coverage starvation, **zero abstentions**:

```
CONNECTIVITY=RED
  6631 source records · 230 component records · 228 designators
  675 wires · 143 named nets · 881 pins loaded
  coverage: designators 228/228 · component parts 229/229 · abstentions 0
  pin landing rate                 = 74.2%  (654/881)
  wires bound to >=1 pin           = 652
  wires touching no pin            = 23     <- violations
  nets_reaching_fewer_than_two_pins = 7
  pins_on_multiple_nets             = 0
```

**23 labelled stubs bind no pin at all**, and they are not scattered: they
cluster on `U9-ESP` and the `R73-ESP` K1BR group. Read together with the 23
`U9-ESP` pins that carry no wire, both halves describe one defect — **the
ESP32-S3 block is wired to coordinates that miss its pins**: `ESP_EN`,
`ESP_GPIO0`, `ESP_UART0_RX/TX`, `ESP_USB_VBUS_SENSE`, `USB_DM_S3`, `USB_DP_S3`,
`I2C_SDA`, `I2C_SCL`, `NFC_IRQ`, `MOTION_INT_S3`, `S3_POR_REQ`,
`K1BR_SCK/MOSI/MISO/CS/IRQ`, plus `3V3` and `GND` stubs.

**Seven nets bind fewer than two pins:** `BUCK_PG`, `ESP_UART0_RX`,
`K1BR_IRQ_S3`, `K1BR_MISO_S3`, `K1BR_MOSI`, `MOTION_INT_S3`, `S3_POR_REQ`.

Under coverage-starved data this list had 13 entries and 9 abstentions. Full
coverage removed `AUDIO_BCLK_RT`, `BOOT_MODE1`, `LED_D0_3V3`, `LED_D1_3V3`,
`SWD_SWCLK` and `SWD_SWDIO` — those were artefacts of the missing RT1062 part.
The seven that remain are measured against complete pin geometry.

### The single most important finding — `BUCK_PG` survives full coverage

Decision **D-045** (ratified 2026-08-28) asserts `R75-PWR2` pulls `BUCK_PG` to
3V3 and `U3-PWR2` pin 5 drives it. Measured against complete pin geometry, with
no abstentions:

```
BUCK_PG binds: ['R75-PWR2.1']          <- one pin, not two
  R75-PWR2.1  at (1010, 4480)   bound by wire e146317
  U3-PWR2.5   at (1140, 4535)   BOUND BY NOTHING
```

The wire meant to carry it, `e146347`, is broken **two independent ways**:

```
e146347 = [[1000, -4535, 1130, -4535], [1000, -4480, 1000, -4535]]
```

1. **Wrong coordinate frame.** Every other wire on the sheet uses positive `y`
   (range `0 … 4680`). This one is at **negative** `y` — the pin read-back's
   screen frame — putting it ~9000 units off-sheet, nearest component 7085 units
   away. It is the only wire in the source with negative coordinates, so this is
   a sign-flip in whichever script wrote it, not a convention.
2. **Ten units short at both ends, even if the sign were corrected.** Mirroring
   `y` gives endpoints (1130, 4535) and (1000, 4480). `U3-PWR2.5` is at
   (1140, 4535) and `R75-PWR2.1` at (1010, 4480) — **10 units away in each
   case**. Every endpoint of `e146347` binds nothing in either frame.

**This is not a keying artefact and not a coverage artefact.** It was found
under 228/228 designator and 229/229 part coverage with zero abstentions, and
`U3-PWR2.5` independently appears in the set of pins carrying no wire.

**A transaction closed ACCEPTED while its net did not connect.** That is the
finding that changes what we trust, and it is the reason the `close_visual`
auto-accept in §6.1 mattered: the gate was moved to READY on a record nobody
had looked at.

Nothing else in the repository catches it. `check_single_schematic.py`
bounds-checks COMPONENT anchors against the ten domain boxes but never wire
coordinates, and EasyEDA's DRC did not flag `BUCK_PG` at all.

### One correction to the brief

`RT_RESET_REQ_N` was flagged for use as a real-sheet RED case, on the grounds of
being a single-endpoint net. **Measured, it is the opposite.** It is carried by
exactly one wire — that part is right — but that wire spans two distinct points
and binds **two real pins, `SW1-RTC.2` and `U7-RTC.3`**:

```json
"RT_RESET_REQ_N": {"status": "GREEN", "wire_count": 1, "geometric_islands": 1,
                   "pins_reached": ["SW1-RTC.2", "U7-RTC.3"]}
```

It is the healthiest net on the sheet — one wire, one island, two pins, a
genuinely drawn connection. It has **not** been encoded as a RED fixture; a
fixture asserting a false expectation would make the oracle wrong.

---

## 8. DRC cross-check — and a staleness finding

```
DRC_PARSE=RED
  422/422 lines parsed · 0 unparseable · 0 unclassified · 7 nbsp-normalised
  reconciliation: Fatal 0/0 · Error 0/0 · Warn 22/22 · Info 398/398  (all ok)
  waived 2 (J7-ESP.A8, J7-ESP.B8) · stale_waivers 0 · open_warn_or_worse 22
  floating_pins 193 · single_pin_net 7 · supplier_standardisation 209
  designator_style 221 · empty_value 171 · pad_without_pin 2
```

**The DRC log predates the frozen source snapshot.** Three confirmations:

1. It names `$1N2873` as a `BUCK_SS` wire; wire `e2873` **does not exist** in the
   frozen source (`BUCK_SS` there is `e2945` + `e145984`).
2. Reconciling its 193 floating pins against frozen geometry: 117 still floating,
   **3 now carry a wire** (`C10-PWR2.1`, `C10-PWR2.2`, `U12-NFC.20` — the
   `repair_buck_ss_cap` work landed after the DRC run), 73 have no pin coordinate
   (the `U6-RTC` multi-part gap).
3. Its 12:17 local timestamp maps to 04:17Z, before the lane's last reconciliation
   at 05:52:30Z.

The waiver register must not be used to paper over this. **Re-run DRC against the
current sheet before treating those 22 warnings as the live picture.**

---

## 9. Still out of scope

All PCB geometry, and any G3 RF/mechanical checker (D-015 — no checker before its
artefact exists). `FIXTURE-PLAN.json` unmodified. `check_single_schematic.py`
constants unmodified.

---

## 10. Reproduce

```bash
python3 harness/check_schematic_connectivity.py --self-test
python3 harness/parse_drc_log.py --self-test
python3 harness/check_single_schematic.py --self-test
python3 schematic/single-sheet-qualification/close_visual_from_census.py --self-test
python3 harness/easyeda_mutation_gate.py lanes
python3 -m pytest harness/ -q                      # 74 passed

python3 harness/check_single_schematic.py          # exit 1 = STALE READ-BACK, expected

D=evidence/VAL-G2-2026-08-28/canonical-core-val-r0
python3 harness/check_schematic_connectivity.py \
  --source $D/frozen-denominator-489736/source.txt \
  --pins   $D/jobs/all-pins-nc-audit.results.json \
  --json-out $D/connectivity-report.json           # exit 1 = RED, expected

python3 harness/parse_drc_log.py \
  --log ~/Downloads/schDrcLog_2026-08-28.txt \
  --waivers $D/DRC-WAIVERS.json \
  --json-out $D/drc-parse-report.json              # exit 1 = RED, expected
```

---

**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:harness | Created — connectivity oracle, DRC parser, two false-green repairs, fault batteries and mutation tests |
| 2026-08-28 | agent:harness | Reframed as a DRAWING oracle (not a netlist oracle); violation classes renamed to drawing language; `off_sheet_wires` rule added with fixture; DRC-anchored per-component fit declined with a measured counterexample; displacement reported as a diagnostic, not a violation |
| 2026-08-28 | agent:harness | Snap tolerance measured and guarded at half-pitch with sensitivity table; DRC differential oracle added; U9-ESP and BUCK_PG disagreements resolved |
| 2026-08-28 | agent:harness | Connectivity oracle re-pointed from geometric fragmentation to label-to-pin binding, with coverage abstention; third false green (`check_single_schematic.py` stale-input) repaired; `RT_RESET_REQ_N` fixture claim corrected against measurement |
