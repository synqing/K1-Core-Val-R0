# VAL-G2.0 invalid fixture — root-cause analysis

Status: **REJECTED BEFORE QUALIFICATION**

```text
PROJECT_UUID = 09e9c541fd3d404082d4b92e55ae5336
PROJECT_STATE = ABANDONED_INVALID_FIXTURE
VAL_G2_0_RESULT = NOT_RUN
MUTATION_AFTER_REJECTION = NONE
```

## Problem statement

The disposable EasyEDA project reached 200 electrical symbols, 120 generated unique signal names,
10 repeated rail names and one schematic page, but the rendered sheet was not a representative,
electrically coherent Option-C schematic. It was therefore incapable of proving that the real
single-sheet design would remain usable.

## Direct evidence

- `sources/SOURCE-REGISTER.md` still recorded the Option-C symbol estimate as unresolved.
- `invalid-fixture-generator.mjs` hard-coded the outcome to exactly 200 symbols without consuming
  an Option-C estimate or a source-derived component-role inventory.
- The generated population contained 132 resistors/capacitors (66% of all symbols), four ADCs,
  four USB-C connectors, two NFC controllers and four accelerometers. No record tied those
  quantities to the selected architecture.
- `invalid-net-generator.mjs` selected 120 passive components with `slice(0, 120)`. For each
  passive it attached one unique `*_QUAL_*` name to pin 1 and one of ten repeated rail names to
  pin 2.
- The 120 unique names therefore had one component-pin endpoint each. They were named dangling
  stubs, not electrical connections.
- The ten claimed high-fanout nets were produced by round-robin attachment to passive pins. The
  generator did not require a regulator/source endpoint, a processor power pin or a real load.
- Neither processor nor the main peripheral symbols appeared in the net-generation job set.
- `create-schematic/SKILL.md` already required a complete pin-to-net plan before placement and
  a clean validation boundary between stages. No durable plan artefact or executable pre-write
  gate made those requirements unavoidable for a disposable qualification fixture.

## Five Whys Plus

### Why 1 — Why did the sheet look like count padding?

Because the generator optimised the literal count thresholds: 200 symbols, 120 unique names and
10 repeated names.

Evidence: the two preserved generators calculate those values directly.

### Why 2 — Why were the thresholds treated as the product being tested?

Because no source-derived Option-C topology or component-role inventory was required as input to
the generation step. Counts were available; topology was not.

Evidence: the source register marked the Option-C symbol estimate unresolved, while the generator
accepted no estimate or topology input.

### Why 3 — Why could work proceed with the defining input unresolved?

Because the test plan gave `max(200, ceil(1.20 × N_estimated_symbols_option_C))` but did not state
that an undefined estimate is a hard stop. It also described “representative” and “electrically
coherent” qualitatively, with no falsifiable connectivity criteria.

### Why 4 — Why did the normal EasyEDA workflow not stop it?

Because the router and read-back gates protected project identity, mutation safety, counts and
persistence. They did not require a machine-checked fixture plan before the first EDA write.
The more specific schematic skill contained a planning rule, but compliance depended on agent
discipline and was not connected to a qualification preflight.

### Why 5 — Why was agent discipline the last line of defence?

Because no executable semantic gate existed for the qualification fixture. A source read-back
could prove that 200 symbols and 240 wire stubs persisted while remaining unable to prove that a
single signal had two meaningful endpoints.

## Root cause

**VAL-G2.0 lacked a fail-closed, executable fixture-definition gate.** The undefined Option-C
estimate and topology were silently replaced by the numeric floor, and the available evidence
oracle measured persisted primitive counts rather than electrical representativeness.

This is a control-system defect, not an EasyEDA capability defect and not adequately explained by
“the agent made a bad judgement”.

## Contributing factors

- The first whole-sheet visual review occurred after bulk population rather than before the first
  electrical write tranche.
- Wire-stub fallback was treated as representative visible wiring instead of a net-label transport
  mechanism.
- Duplicated functional ICs were allowed without an architecture-backed quantity basis.

## Alternatives considered and rejected

- **EasyEDA API defect:** rejected. Project creation, placement, annotation and source read-back
  behaved consistently.
- **Library-symbol defect:** rejected. The symbols rendered; the selected quantities and topology
  were wrong.
- **Canvas-size or zoom defect:** rejected. The full-sheet render exposed the semantic failure.
- **Merely poor visual composition:** incomplete explanation. Better spacing would still leave
  dangling processors and one-endpoint nets.

## Source-level prevention

1. Split VAL-G2.0 into fixture definition and EDA execution. EDA execution waits on a validated
   fixture-definition PASS.
2. Treat an unresolved Option-C estimate as a hard stop; never default it to 200.
3. Require a machine-readable component-role and endpoint-level net plan before project creation.
4. Fail one-endpoint named nets, passive-only high-fanout nets, unpowered major ICs, synthetic
   count-padding roles and stub-only wiring plans.
5. Require a whole-sheet visual checkpoint before responsiveness measurements.

## Evidence files

- `invalid-fixture-render.png`
- `invalid-fixture-generator.mjs`
- `invalid-net-generator.mjs`
- `invalid-net-manifest.json`
