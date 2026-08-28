---
abstract: "SSA-B2 evidence: the connectivity oracle now reads BOTH EasyEDA document-source grammars (V2 2.2.40.8 tagged arrays, V3 3.2.149 typed records) through one internal representation. Records the measured V3 grammar (wire geometry moved into LINE records; y axis negated), the 228/228 designator cross-check on the real differential pair, the new record-shape-drift fault cases with their RED output, and the four mutation runs proving each guard can go red. Read before trusting any connectivity verdict taken from a 3.2.x snapshot."
---

# SSA-B2 — V3 grammar for the connectivity oracle

**Date:** 2026-08-28 · **Lane:** SSA-B2 · **Verdict:** VERIFIED (offline, captured files only)

**Re-run command (one command, prints PASS/FAIL):**

```
python3 harness/run_v3_grammar_battery.py
```

Exit 0 = `V3_GRAMMAR_BATTERY=PASS`, exit 1 = FAIL. Read-only. No EasyEDA host, no
bridge, no `mcp__easyeda-mcp__*` call was made in this lane.

---

## 1. The V3 grammar, as measured

Source of truth for this section is the differential pair — the SAME schematic page
(`1435cb46f39e48c8a8aadbb84ca81603`), same board, captured minutes apart across the
2026-08-28 host upgrade:

| | file | records |
|---|---|---|
| V2 (2.2.40.8) | `/Users/spectrasynq/SpectraSynq-EDA/_archive/easyeda-backups/2026-08-28/schematic-P1-source-1305.json` | 6737 |
| V3 (3.2.149) | `…/schematic-P1-source-POST-V3.json` | 7397 |

V3 record types on the real page: `ATTR 5768 · LINE 688 · WIRE 676 · COMPONENT 231 ·
TEXT 22 · RECT 10 · DOCHEAD 1 · CANVAS 1`. All 7397 lines parse; 0 fail.

Two structural changes decide whether a connectivity oracle is right or
catastrophically wrong, and neither is visible from the brief's grammar sketch alone:

**(a) Wire geometry moved OUT of the WIRE record.** In V2 a wire carried its own
segments: `["WIRE","e968",[[80,4420,100,4420]],"st11",0]`. In V3 the WIRE payload is
only `{"zIndex":236,"locked":false}` — the geometry lives in separate `LINE` records
that point back with `lineGroup`:

```
{"type":"LINE",...}||{"startX":80,"startY":-4420,"endX":100,"endY":-4420,"lineGroup":"e968"}|
```

A parser that looks for coordinates in the V3 WIRE payload finds none and concludes
the sheet has no wiring. It has 676 wires and 688 segments.

**(b) The Y axis is NEGATED relative to V2.** V2 `[80,4420,…]` is V3 `startY:-4420`.
Verified across the whole page, not sampled: **all 676 wire ids match, all 676 segment
lists match after negation (0 mismatches), and 231 of 231 COMPONENT anchors match
after negation** (only `e1`, at the origin, matches without it).

This is the load-bearing step. `check_schematic_connectivity` maps pin read-backs into
the V2 source frame with its own `(x, y) -> (x, -y)`. Leave V3 coordinates un-negated
and every pin lands `2y` away from its wire: the pin landing rate collapses to ~0% and
the oracle reports an entire sheet of floating pins — confidently, and falsely. So V3
is normalised INTO the V2 frame once, at the parse boundary.

## 2. What changed on disk

| file | change |
|---|---|
| `harness/easyeda_source_format.py` | V3 record parser (`parse_v3_line`, `parse_v3_records`, `V3Record` named-field access), `assemble_v3_wire_segments` (LINE→WIRE fold + y-normalisation), `to_v2_shaped_rows`, dual-grammar entry point `parse_records_any_format`, the `V3_REQUIRED_PAYLOAD_FIELDS` / `V3_NUMERIC_PAYLOAD_FIELDS` shape contract, `topology_digest`, and an extended `--self-test` carrying the drift/truncation cases and the real-snapshot differential. `detect_format` / `describe` / `require_v2` behaviour unchanged. |
| `harness/check_schematic_connectivity.py` | `parse_records` now goes through `parse_records_any_format`, so ONE internal representation feeds the unchanged analysis; any parse-layer refusal is converted to `FailClosed`. Four V3 battery cases added plus a CROSS-GRAMMAR EQUALITY check. |
| `harness/run_v3_grammar_battery.py` | new — the single re-run command. |
| `harness/fixtures/connectivity/v3-joined-net/` | new — `joined-net` re-serialised as V3 (same `pins.json`). |
| `harness/fixtures/connectivity/v3-shape-drift/` | new — V3 COMPONENT payload renamed `x` → `posX`. |
| `harness/fixtures/connectivity/v3-truncated-record/` | new — last payload cut mid-object. |
| `harness/fixtures/connectivity/v3-no-wires/` | new — V3 components, zero WIRE records. |

**Out of scope, deliberately untouched and still refusing:** `easyeda_remove_source_records.py`,
`easyeda_repair_source_swap.py`, `extract_frozen_denominator.py`. They still call
`require_v2`, which still raises on a V3 snapshot — verified this run:

```
easyeda_remove_source_records: REFUSES (…refusing to parse — this snapshot is V3_TYPED_RECORD…)
easyeda_repair_source_swap:    REFUSES
extract_frozen_denominator:    REFUSES
```

Reading V3 is now a solved problem; **writing** it is not, and those three rewrite live
board source.

## 3. Cross-check — 228 designators from BOTH grammars

Run through the connectivity oracle's own parse layer (`parse_records` →
`extract_topology`), i.e. the exact path a verdict is taken on:

| | rows | components | **designators** | wires | named wires | nets |
|---|---|---|---|---|---|---|
| V2 | 6737 | 231 | **228** | 676 | 675 | 143 |
| V3 | 6709 | 231 | **228** | 676 | 675 | 143 |

**No discrepancy to report.** The designator count matches the brief's stated ground
truth on both grammars, and so do the wire, named-wire and net counts.

The row-count difference (6737 vs 6709) is fully accounted for and is not loss:
V3 folds its 688 `LINE` records into the 676 wires they belong to (7397 − 688 = 6709),
and V2 additionally carries 17 `FONTSTYLE` + 2 `LINESTYLE` records that V3 does not
emit. Neither class carries connectivity.

Stronger than counts, the `--self-test` differential compares the two parses
structurally on every run:

```
REAL-SNAPSHOT DIFFERENTIAL (V2 capture vs V3 capture of the same page):
      V2: 228 designators, 676 wires, 675 named wires, 143 nets
      V3: 228 designators, 676 wires, 675 named wires, 143 nets
PASS  designator SET identical across grammars
PASS  designator count is 228
PASS  wire id SET identical
PASS  wire SEGMENT GEOMETRY identical (this is the y-negation proof)
PASS  COMPONENT anchors identical
PASS  wire -> net map identical
```

Set equality, not count equality — two different sheets can share a count.

One measured difference between the captures, recorded for completeness because it is
NOT parser error: 100 `NO_CONNECT` ATTRs changed their parent-id spelling
(`e252e12` → `e252-e12`) and 9 V2-only `NO_CONNECT` ATTRs are absent from V3. These are
pin-level annotations; the connectivity oracle reads only `NET` and component attrs,
and `Designator`/`NET` values are identical across both captures.

## 4. Fault battery — including the cases that must go RED

`python3 harness/run_v3_grammar_battery.py` → `V3_GRAMMAR_BATTERY=PASS`.

### 4a. Record-shape drift and truncation (new this lane)

Every one of these is a case that DID NOT EXIST before and that goes RED:

```
PASS  DRIFT: ATTR parentId renamed -> parent_id                              <- went RED as required
PASS  DRIFT: COMPONENT x renamed -> posX                                     <- went RED as required
PASS  DRIFT: LINE lost startX                                                <- went RED as required
PASS  DRIFT: COMPONENT x present but null                                    <- went RED as required
PASS  DRIFT: lineGroup join key renamed — wires would silently lose all geometry  <- went RED as required
PASS  TRUNCATED: payload cut mid-object                                      <- went RED as required
PASS  TRUNCATED: header cut mid-object                                       <- went RED as required
PASS  TRUNCATED: '||' separator missing                                      <- went RED as required
```

("PASS" here means the guard fired. A `FAIL` line in this block means the guard stayed
silent on a broken record.)

At the oracle level the same faults surface as refusals, with the reason named:

```
[ok ] v3-shape-drift       expected=FAIL-CLOSED  observed=FAIL-CLOSED
        reason: … V3 COMPONENT record 'c1' (line 2) is missing required payload field(s)
        ['x'] — RECORD-SHAPE DRIFT. Present fields: ['attrs','partId','posX','rotation','y']
[ok ] v3-truncated-record  expected=FAIL-CLOSED  observed=FAIL-CLOSED
        reason: … V3 payload is not valid JSON (line 10) — TRUNCATED RECORD: Unterminated string
```

The battery asserts the REASON substring, not just the verdict — a case that fails
closed for the wrong reason is marked `[BAD]` (proved in mutation M3 below).

### 4b. Fail-closed behaviour survived the new grammar

```
[ok ] empty-source          FAIL-CLOSED   zero parseable records
[ok ] no-wires              FAIL-CLOSED   components present, zero WIRE records
[ok ] no-pin-data           FAIL-CLOSED   wires and nets present but NO pin geometry
[ok ] v3-no-wires           FAIL-CLOSED   V3 components, zero WIRE records
```

Zero named nets is likewise still a refusal (`analyse` raises before any verdict); it
is grammar-independent and sits below the parse boundary.

### 4c. Grammar-independence of the analysis

```
[ok ] v3-joined-net        expected=GREEN  observed=GREEN   V3 GRAMMAR CONTROL
CROSS-GRAMMAR EQUALITY (joined-net V2 vs v3-joined-net V3, same sheet):
[ok ] every report section identical
```

Matching verdicts would not be enough — two different sheets can both be GREEN. The
check asserts the two reports are identical section for section, which is what proves
the analysis did not fork on the host version.

Battery totals: `cases=17 red_observed=4 fail_closed_observed=6`.

## 5. Mutation runs — each guard proven able to go red

Each mutation was applied to a throwaway copy of `harness/`, never to the repo.

| # | mutation | result |
|---|---|---|
| M1 | `V3_Y_SIGN = -1` → `1` (drop the y-negation) | `FAIL v3 rows are V2-shaped AND y-normalised` · `FAIL wire SEGMENT GEOMETRY identical` · `FAIL COMPONENT anchors identical` · `[BAD] v3-joined-net expected=GREEN observed=RED` · `[BAD] every report section identical — DIFFERING SECTIONS: counts, diagnostics, nets, pin_coverage, snap_tolerance, verdict, violation_counts, violations` → `V3_GRAMMAR_BATTERY=FAIL` |
| M2 | `_check_payload_shape` neutered (`return` first) | 4 drift cases go `FAIL` (`guard did not fire`, and three `raised TypeError, wanted V3RecordError`) → `V3_GRAMMAR_BATTERY=FAIL` |
| M3 | `parse_v3_records` silently skips malformed lines | 6 cases `FAIL guard did not fire`; both V3 fixtures marked `[BAD]` **while still observing FAIL-CLOSED** — right verdict, wrong reason, caught by the reason assertion → `V3_GRAMMAR_BATTERY=FAIL` |
| M4 | LINE records ignored (wires lose geometry) | join-key guard fires: `676 WIRE record(s) declared but NOT ONE received any LINE geometry … refusing rather than reporting an unwired sheet`; differential `FAIL`; `v3-joined-net` `[BAD] observed=FAIL-CLOSED` → `V3_GRAMMAR_BATTERY=FAIL` |

M3 is the important one: without the reason assertion, both V3 fault fixtures would
have passed for the wrong reason under a parser that silently drops broken records.

The real-snapshot differential itself is also wired: with the snapshots absent it
prints `FAIL … refusing to report a green battery whose only external check did not
run` and exits non-zero. `K1_ALLOW_MISSING_SNAPSHOTS=1` downgrades it to a labelled
`NOT-RUN` for portability; `K1_V2_SNAPSHOT` / `K1_V3_SNAPSHOT` repoint it.

## 6. What this does NOT establish

- **No live-host validation.** Everything here is offline against captured files. The
  oracle has not been run against a 3.2.149 snapshot pulled through the bridge in this
  lane, and the pin read-backs it needs for a real verdict come from the host.
- **The pin transform is unchanged and unre-derived for V3.** `PIN_Y_SIGN = -1` was
  measured against V2 source coordinates. V3 is normalised into that same frame, so the
  transform still holds *by construction* — but a fresh V3-era pin read-back has not
  been landed against a V3 snapshot end to end. The `pin_landing_rate` is the witness
  to watch on the first real run: if it collapses, the frame is what broke.
- **No completeness claim.** This lane fixed the parse layer. The oracle still only
  measures nets that exist, still abstains on parts without pin geometry, and still is
  not a netlist oracle.
- **The three write-path tools remain out of service on V3**, by design.

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:SSA-B2 | Created — V3 grammar parser, dual-grammar connectivity parse layer, record-shape-drift fault battery, 228/228 cross-grammar designator check, four mutation runs |
