---
abstract: "BOM/CPL semantic audit of all 228 designators (229 placed instances) in K1-Core-Val-R0 at frozen hash 489736:464c27d4. 14 BLOCKER parts would be built wrong: 2 resistors bound to a 10k device while drawn as 1.33k/3.48k, 7 DNP resistors carrying a fabricated MPN with no BOM exclusion, 2 USB-C connectors with unmapped shell pads, 3 undeclared stand-in binds. 160 MAJOR (supplier code is a device key, not an LCSC code), 55 hygiene-only. `Add into BOM` DOES exist in the schematic on 4 instances; its export semantics were measured against real EasyEDA BOM/CPL exports on disk — the flag omits a part from the BOM but the part is STILL written into the CPL. Every finding is a PROPOSAL against a frozen dump; live has moved on."
---

# BOM / CPL Semantic Audit — K1-Core-Val-R0

**Denominator:** `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/frozen-denominator-489736/`
**Source hash:** `489736:464c27d4`
**Date:** 2026-08-28

## Status of this document

Every finding below is a **proposal**, not an instruction. It was derived from a **frozen
dump**, and the live document has already moved past that hash. The single writer must
re-confirm each item against live before changing anything. Nothing in this audit was
obtained from, or applied to, the live EasyEDA canvas — the whole audit is on-disk.

## What was actually parsed

| Quantity | Count |
|---|---|
| `COMPONENT` records in `source.txt` | 230 |
| Sheet frame / title block (`e1`, not a part) | 1 |
| **Placed component instances** | **229** |
| **Distinct designators** | **228** |
| **Instances adjudicated** | **229** |
| Distinct bound library devices | 65 |

Zero parsed would never have been a pass. 229 of 229 instances were adjudicated; each
carries a record in `bom-audit.json` with every field, a verdict, a defect class list and a
bounded repair.

### Verdict distribution

| Severity | Meaning | Instances |
|---|---|---|
| **BLOCKER** | The part that gets fitted is not the part the schematic displays | **14** |
| **MAJOR** | Cannot be ordered or auto-matched as-is, or orders a part not wanted | **160** |
| **MINOR** | Metadata hygiene; the board still builds correctly | **55** |
| INFO | Conventional or cosmetic; not a defect | 0 |

**14 parts would ship wrong.** Those are the list in §1 and §5 and they are the whole
actionable set. The 160 MAJOR are not 160 independent mistakes — they are **one** finding
(the supplier code is an EasyEDA device key rather than an LCSC code) repeated across the
board, fixable as a single batch using a normalisation step this project has already run
once before (§3).

Severity is assigned per defect class, then each instance takes its worst. `NO_MPN` is
deliberately **MINOR**, not MAJOR: every one of the 229 instances carries either a direct
LCSC code or a device key that resolves to one, so **zero parts are unorderable** for want
of an MPN. `EMPTY_VALUE_FIELD` is **INFO** — see §6.3, where it is measured rather than
assumed.

## Cross-checks used

| Oracle | What it settles |
|---|---|
| LCSC/JLCPCB primary catalogue (`mcp__pcbparts__jlc_get_part`) | Whether an LCSC code is the part the schematic claims |
| Captain's `schDrcLog_2026-08-28.txt` | EasyEDA's own attribute-vs-device drift detector, pad/pin mismatch |
| `ProPrj_K1-Core-Val-R0_2026-08-28.epro`, independently decoded | Whether the frozen dump invented or lost designators |
| `evidence/VAL-G2-2026-08-28/jobs/library-bind-map.json` | Which binds are deliberate stand-ins |

## How the mis-bind finding was proved twice

"Is the displayed part the bound part?" was answered by two independent implementations:

1. Group all 229 instances by `Device` uuid, take each device's dominant
   `supplierId`/`Supplier Part` token, compare against the instance's displayed MPN.
2. Read the `COMPONENT` record's own library-reference string straight out of `source.txt`,
   with no grouping and no device uuids involved at all.

**Both return the same 20 designators, compared in emitted order.** A single implementation
checked against itself would have proved nothing; the two disagree nowhere. The 20 split into
2 true value mis-binds, 7 fabricated-MPN DNP resistors, 3 documented stand-ins and 8 test
points — classified in §1, §5 and §6.1.

The `DNP_NOT_EXCLUDED_FROM_BOM` detector was separately mutation-tested (§2).

**`.epro` differential.** SHA-256 verified as `06c5ac3800a5…04828`. 220 designators decoded
from the archive. **220 of 220 are present in the frozen dump; none are missing and none
were invented.** The 8 designators the frozen dump has in excess are
`C92-NFC, C93-NFC, C94-NFC, C95-NFC, C96-NFC, C97-NFC, R75-PWR2, R76-NFC` — all NFC
decoupling plus two resistors, and all 8 also appear in the small set that EasyEDA's DRC
does *not* flag for attribute drift. They are the newest, cleanest additions. The frozen
dump is a faithful superset of the anchor.

---

# 1. BLOCKER — parts that will be built wrong (11 of the 14)

## 1.1 Two resistors are bound to a 10 kΩ device while drawn as other values

`R1-PWR1` and `R8-PWR2` share bound device `e1b1f220e40a4edea589adfa05a5d8c7` with
**22 other resistors**. That device's dominant supplier identity across its 24 instances is
`RC0402FR-0710KL` — a **10 kΩ** part, confirmed against LCSC.

| | R1-PWR1 | R8-PWR2 |
|---|---|---|
| Displayed `Name` | `1.33k` | `3.48k` |
| `Manufacturer Part` | `RC0402FR-071K33L` | `RC0402FR-073K48L` |
| `supplierId` | `C60490` | `RC0402FR-0710KL.1` |
| `Supplier Part` | `C276261` | `C185418` |
| Bound `Device` | `e1b1f220…` (24 instances, 10 kΩ) | `e1b1f220…` (24 instances, 10 kΩ) |
| **`COMPONENT` library ref** | **`RC0402FR-0710KL.1`** | **`RC0402FR-0710KL.1`** |

The last row is the decisive one. Each `COMPONENT` record in `source.txt` carries its own
library-reference string, read directly with no inference:

```
["COMPONENT","e426","RC0402FR-0710KL.1",365,4420,0,0,{},0]     <- R1-PWR1, drawn as 1.33k
["ATTR","e24802","e426","Manufacturer Part","RC0402FR-071K33L",...]
["ATTR","e437","e426","Supplier Part","C276261",...]
```

Verified against the LCSC catalogue:

| Code | MPN | Actual value |
|---|---|---|
| `C60490` | RC0402FR-0710KL | **10 kΩ** |
| `C276261` | RC0402FR-071K33L | **1.33 kΩ** |
| `C185418` | RC0402FR-073K48L | **3.48 kΩ** |

The correct LCSC code for each part is already present in the file — it is sitting in
`Supplier Part`, the field EasyEDA does not use for ordering, while every field that carries
the actual binding names the 10 kΩ device.

Both are 1% precision values in the `PWR1`/`PWR2` domains. 1.33 kΩ and 3.48 kΩ are E96
values — a designer does not choose them unless the exact ratio matters, which in a power
block normally means a feedback or current-sense divider. **The circuit function was not
verified**: `index.json` records only endpoint and wire counts per net, not per-pin
membership, so this dump cannot say what either resistor does. What it does say with
certainty is that both are ordered and fitted as 10 kΩ. The writer should confirm the
function before deciding how urgently to act, but the mis-bind itself is not in doubt.

**Bounded repair.** Rebind each instance to the device for the MPN it already displays. The
bind map already resolves both: `RC0402FR-071K33L` → device `31e09015057d40e885a10cd7f4784b79`
(C276261), `RC0402FR-073K48L` → device `62850562b7904f11a759e60c3de20f54` (C185418). Do not
choose new parts — the displayed value already names the correct one. After rebinding, set
`supplierId` to the LCSC code.

## 1.2 Seven DNP resistors carry a fabricated MPN and still emit into BOM and CPL

`R40-AUD`, `R41-AUD`, `R45-MOT`, `R47-MOT`, `R49-MOT`, `R56-VAL`, `R57-VAL`.

All seven have `Name = DNP` and `Manufacturer Part = RC0402FR-07DNP`. **That part does not
exist** — the LCSC catalogue returns no result for it, and it is not a valid YAGEO RC0402
part number (the series encodes a resistance in that position, and `DNP` is not one).

The bind map confirms this was deliberate, not accidental:

```
"RC0402FR-07DNP": { "deviceUuid": "6593321c1e554b2f9070c57621ba8753",
                    "name": "RC0402FR-0710KL",
                    "note": "0402 DNP footprint stand-in" }
```

The fabricated MPN is a label pointing at the **real 10 kΩ device**. All seven
`COMPONENT` records confirm it directly — every one carries library ref
`RC0402FR-0710KL.1`. None of the seven carries `Add into BOM`. So each one emits into the
BOM as a populated line and into the CPL as a placement — and what gets fitted is a 10 kΩ
resistor at a location the schematic says must be empty.

**This confirms the handover's assertion: a part named DNP is currently NOT excluded from
BOM and CPL.** For these seven, it is a manufacturing failure, not a cosmetic one.

**Bounded repair.** Set `Add into BOM` = `no` on all seven. Clear the fabricated
`Manufacturer Part`. Non-population is a BOM state, never an MPN string.

## 1.3 Two USB-C connectors have unmapped shell pads

DRC line 421: *"The pin of the component USB4105-GF-A does not correspond to the pad (Pad has
no corresponding pin: 2、3、4)"* — naming instances `$1I339` and `$1I8334`, which are
**`J1-PWR1`** and **`J7-ESP`**. This is two connectors, not one.

`C3020560` = USB4105-GF-A is confirmed as a 12-position, right-angle, 5 A Type-C receptacle.
Pads 2/3/4 are the shell/mounting pads. They exist in the footprint and have no symbol pin,
so **they cannot be assigned a net** — the connector shield is unnettable on the primary
power inlet and on the ESP programming port. DRC also reports 15 floating pins on `J1-PWR1`.

**Bounded repair.** Rebind to a USB4105-GF-A symbol that exposes the shell pins, or add
shell pins to the current symbol, then net them (typically chassis/GND through the intended
shield strategy). Do not resolve this by deleting the pads.

---

# 2. Where BOM and CPL state actually lives

**The exclusion mechanism exists.** `Add into BOM` is present in the schematic source and is
counted 4 times in the frozen dump's own attribute census. The handover's premise that it is
absent is incorrect — it is present, and it is applied to exactly four instances:

| Designator | `Name` | `Add into BOM` | Correct? |
|---|---|---|---|
| `C43-ESP` | `DNP / 100pF USB D+ TUNE` | `no` | Yes |
| `C44-ESP` | `DNP / 100pF USB D- TUNE` | `no` | Yes |
| `C52-AUD` | `DNP / 100pF MCLK TUNE` | `no` | Yes |
| `U6-RTC` (2nd part, `e3673`) | `FITTED` | `no` | Yes — multi-part de-duplication |

So the answer to *"is a part named DNP in fact excluded from BOM and CPL?"* is:
**sometimes.** Three DNP capacitors are correctly excluded. Seven DNP resistors are not.
The mechanism is not missing — it was applied inconsistently, to 4 of the 11 instances that
need it.

This detector was mutation-tested: stripping `Add into BOM` from C43/C44/C52 makes all three
flag, and a `FITTED` part never flags. It is wired to the property, not to an annotation.

### How the flag was found, and how its behaviour was measured

Two separate questions, answered two different ways. Neither is an inference from the part
being named `DNP`.

**The flag itself — found in the schematic source.** Exact attribute key: `Add into BOM`.
It appears 4 times, which is why an attribute-key census of common fields does not surface
it. The frozen dump's own `attr_key_census` in `index.json` records `"Add into BOM": 4`, and
the raw source carries four literal rows:

```
["ATTR","<id>","<parent>","Add into BOM","no",null,null,null,null,null,"st4",0]
```

carried by `C43-ESP` (`e8224`), `C44-ESP` (`e8260`), `C52-AUD` (`e12082`) and `U6-RTC`
part 2 (`e3673`). Those are the four designators; each can be checked individually.

**The flag's export behaviour — measured at the artefact boundary, on real exports.**
Not from this board. Real EasyEDA BOM and CPL exports from a sibling SpectraSynq board sit
on disk and were read directly:

- `SpectraSynq-EDA/im69d130-stereo-mic/fab-final-2026-07-19/BOM_PCB3_2026-07-19.raw.csv`
- `SpectraSynq-EDA/im69d130-stereo-mic/fab-final-2026-07-19/PickAndPlace_PCB3_2026-07-19.raw.csv`

Reconciling the two by designator:

| | Count |
|---|---|
| Designators in the exported BOM | 33 |
| Designators in the exported CPL | 38 |
| **In the CPL but absent from the BOM** | **5** — `C5, C9, R11, R13, R9` |
| In the BOM but absent from the CPL | 0 |

So, measured:

1. `Add into BOM` = `no` **is honoured** — the part is **omitted from the exported BOM
   entirely**, not listed with a `no` flag. (No exported BOM row anywhere carries `no`.)
2. **The same part is still written into the CPL.** Exclusion does not propagate.
3. Absence of the attribute means **included** — all 33 exported BOM rows read
   `Add into BOM` = `yes` although the schematic omits the row when true.

This matches the independently-recorded finding in the EasyEDA-MCP failure ledger, F53
(*"DNP is the ATTR `Add into BOM`=`no` (its ABSENCE = FIT)"*, marked verified live 5/5) and
check C2 in `tools/verify_fab_package.py` (*"DNP parts are omitted from the BOM but EasyEDA
still writes them into the CPL; JLC flags a CPL row with no BOM line"*).

**The residual inference, stated plainly.** The mechanism above is measured on IM69D130,
not on K1-Core-Val-R0. Applying it to K1 is a **transfer between boards** in the same tool
and the same project pipeline. It is far stronger than reading a part's name, but it is not
an observation of K1's own export. Confirm by exporting this board's BOM and CPL.

### The CPL half of this is not fixed by the repair

`Convert to PCB` — the separate attribute that governs CPL inclusion (`addIntoPcb`, ledger
F92) — **does not appear anywhere in this schematic's source**, on any of the 229 instances.
Per F92 the row is omitted when true, so every part converts to PCB and every part lands in
the CPL.

That has a consequence worth stating before the repair is written: setting
`Add into BOM` = `no` on the seven resistors in §1.2 removes them from the BOM but leaves
them in the CPL, producing exactly the CPL-row-with-no-BOM-line that check C2 says JLC
flags. The three capacitors already correctly excluded (C43/C44/C52) are in that state now.
**The full repair for a DNP part is both flags, not one.**

### Contract vocabulary is not encoded as state

`SINGLE-SHEET-CONTRACT.md` lines 48–57 fix the vocabulary as `FIT`, `DNP`, `OPTION`,
`TUNE_TBD`, `VALIDATION_ONLY`. None of these exists as a structured field. The state is
carried in the free-text `Name` field, mixed with the electrical value
(`DNP / 100pF USB D+ TUNE`) or replacing it entirely (`DNP`). Nothing machine-checks that a
part whose `Name` says `DNP` has `Add into BOM` = `no` — which is exactly how the seven
resistors in §1.2 passed. The vocabulary is documented but not enforced.

**Bounded repair (systemic).** Add a check that reads both properties and fails when a part
whose `Name` declares `DNP` lacks `Add into BOM` = `no`. That check is the only thing that
would have caught §1.2, and it must be proven able to go red before it is trusted.

---

# 3. MAJOR — supplier identity is not recorded in the supplier field (160 parts)

`supplierId` holds a valid LCSC `Cxxxxxxx` code on **57 of 229** instances. On the other
**172** it holds an EasyEDA device key of the form `<MPN>.<n>` — e.g.
`GRM155R71C104KA88D.1`, `RC0402FR-0710KL.1`, `TP-黄色测试点.1`. That is not a supplier code
and cannot be ordered against.

`Supplier Part` is the mirror image: `MPN.n` on 180, empty on 47, and an LCSC code on
exactly **2** — `R1-PWR1` and `R8-PWR2`, the two parts in §1.1, where the *correct* code
ended up in the *unused* field.

The two fields are not consistently assigned. Within a single device the encoding varies:
device `a9cf2f91` (31× 100 nF) carries `GRM155R71C104KA88D.1` on 30 instances and `C71629`
on one. Same part, same device, two different `supplierId` encodings.

`LCSC Part Name`, `Supplier Footprint` and `JLCPCB Part Class` are **empty on all 229**.

**Bounded repair.** Populate `supplierId` with the LCSC code for the bound device on all 172
instances. This is mechanical once the device→LCSC table is settled; only 8 of the 61 bind-map
entries currently carry an `lcsc` field, so the table has to be completed first.

## 3.1 EasyEDA's own DRC already reports this, at scale

DRC lines 407–413: *"Component attributes does not match the Supplier Part, It is
recommended to use Device Standardization"* — naming **209 distinct designators**.

This is an independent, external confirmation that instance attributes have drifted from
their bound devices across **209 of 228** designators (92%). It is not a novel finding of
this audit; it is a warning the tool has been emitting and that has not been actioned.

The 19 designators EasyEDA does *not* flag are the clean ones:
`C10-PWR2, C35-RTDBG, C36-RTDBG, C42-ESP, C43-ESP, C44-ESP, C51-AUD, C52-AUD, C68-PWR2,
C92-NFC…C97-NFC, L1-PWR2, L4-RTC, R75-PWR2, R76-NFC`.

## 3.2 This is a solved step, not a new problem

The same pipeline has already done this repair once. In the IM69D130 fab package the raw
export and the normalised export differ in exactly one respect — `Supplier Part`:

| | Raw export | Normalised for JLC |
|---|---|---|
| R1 | `0402WGF2201TCE.1` | `C25879` |
| R7,R8,R14,R23 | `0402WGF0000TCE.1` | `C17168` |
| R24,R25 | `0402WGF100JTCE.1` | `C25077` |

The `MPN.n` device key is replaced with the real LCSC code, and nothing else changes. That
is precisely the repair the 160 MAJOR instances need, and it is why they are MAJOR rather
than BLOCKER: the correct part is bound, its code simply has to be resolved before JLC can
auto-match it. Check C3 in `EasyEDA-MCP/tools/verify_fab_package.py` exists to catch exactly
this (*"'Supplier Part' = MPN + '.1' is EasyEDA's internal device revision, not an LCSC
code; JLC cannot auto-match it"*).

Only **8 of the 61** bind-map entries currently carry an `lcsc` field, so the lookup table
has to be completed first — that is the real work in this item.

---

# 4. MINOR — MPN coverage collapse, quantified

| Field | Present | Of 229 |
|---|---|---|
| `supplier` | 229 | 100% |
| `supplierId` (any content) | 229 | 100% |
| `supplierId` (valid LCSC code) | 57 | 25% |
| `Supplier Part` | 182 | 79% |
| `Manufacturer` | **37** | **16%** |
| `Manufacturer Part` | **24** | **10%** |
| `Value` | **0** | **0%** |
| `LCSC Part Name` | 0 | 0% |
| `Supplier Footprint` | 0 | 0% |
| `JLCPCB Part Class` | 0 | 0% |

**205 of 229 instances have no MPN at all.**

## By domain suffix

| Domain | Instances | With `Manufacturer Part` | With `Manufacturer` |
|---|---|---|---|
| RTC | 47 | 0 | 37 |
| AUD | 32 | 8 | 0 |
| PWR2 | 28 | 2 | 0 |
| ESP | 28 | 3 | 0 |
| NFC | 22 | 2 | 0 |
| PWR1 | 20 | 2 | 0 |
| RTDBG | 16 | 0 | 0 |
| VAL | 14 | 4 | 0 |
| LED | 12 | 0 | 0 |
| MOT | 10 | 3 | 0 |

`Manufacturer` is populated on exactly one domain — 37 RTC parts, all reading `Murata`. Every
other domain is empty.

## The populated MPNs are worse than the empty ones

Of the 24 instances that do carry an MPN:

| MPN | Count | Status |
|---|---|---|
| `5001` | 8 | Keystone test point, but bound to EasyEDA's generic `TP-黄色测试点` pad |
| `RC0402FR-07DNP` | 7 | **Fabricated — does not exist** (§1.2) |
| `PREC006SAAN-RC` | 2 | Documented stand-in, bound to `HEADER_MALE-XH_1X6P_2.54MM` |
| `TPS259474L` | 2 | Truncated; orderable part is `TPS259474LRPWR` |
| `RC0402FR-071K33L` | 1 | Correct MPN, **wrong device bound** (§1.1) |
| `RC0402FR-073K48L` | 1 | Correct MPN, **wrong device bound** (§1.1) |
| `RC0402FR-072R2L` | 1 | Documented stand-in — 5% JR substituted for 1% FR |
| `U.FL-R-SMT-1` | 1 | Correct |
| `FH12-10S-0.5SH` | 1 | Correct |

**Exactly 2 of 24 populated MPNs are both correct and correctly bound.** The MPN field is not
merely sparse — where it is populated it is predominantly misleading. Treating "has an MPN"
as a completeness signal would produce a false pass on this board.

---

# 5. BLOCKER — undeclared stand-in binds (the other 3 of the 14)

Three instances are bound to a part other than the one drawn, deliberately, per the bind
map's `note` fields. They are **not** errors of execution — someone chose each one. They are
BLOCKER anyway, by the same test as §1: **the part that gets fitted is not the part the
schematic displays**, and nothing on the sheet says so. A note in a side file is not a
declaration; a fabricator never sees it.

| Designator | Drawn | Actually bound | Note | Risk |
|---|---|---|---|---|
| `R42-NFC` | `RC0402FR-072R2L` (2.2 Ω, 1% FR) | `RC0402JR-072R2L` (5% JR) | "JR 5% stand-in for missing FR 2.2R" | Tolerance downgrade 1% → 5% on an NFC matching network |
| `J6-ESP` | `PREC006SAAN-RC` | `HEADER_MALE-XH_1X6P_2.54MM` | "6-pin 2.54 header stand-in" | **Different footprint family** — plain 0.1" header vs shrouded JST-XH |
| `J11-VAL` | `PREC006SAAN-RC` | `HEADER_MALE-XH_1X6P_2.54MM` | "6-pin 2.54 header stand-in" | Same |

**Bounded repair.** Each needs an explicit waiver naming the substituted part, visible on the
sheet — not a note in a side file. `R42-NFC` additionally needs a decision: a 5% resistor in
an NFC matching network is an electrical choice, not a sourcing convenience. The two headers
need the footprint checked before layout, not after.

---

# 6. MAJOR, MINOR and INFO

## 6.1 Test points claim a purchased part they are not bound to (8)

`TP1-ESP, TP2-ESP, TP3-AUD, TP4-AUD, TP5-AUD, TP6-VAL, TP7-AUD, TP8-AUD` all carry
`Manufacturer Part = 5001` (Keystone 5001 test point, a real purchased through-hole part)
while bound to EasyEDA's generic `TP-黄色测试点` device — a bare pad.

**Bounded repair.** Decide which is intended. If these are bare pads, clear the MPN and set
`Add into BOM` = `no`. If real Keystone parts are wanted, bind the real device. Either way
the two must agree, or eight phantom line items ship in the BOM.

## 6.2 MPN is a decorated library name (4)

`J10-NFC` (`U.FL-R-SMT-1` vs `U.FL-R-SMT-1(80)_C9900020048`), `J9-AUD` (`FH12-10S-0.5SH` vs
`FH12-10S-0.5SH(55)`), `U1-PWR1` and `U4-PWR2` (`TPS259474L` vs `TPS259474LRPWR` / `C2864845`).
Same physical part in each case. Low severity — but `TPS259474L` is not orderable as written;
the package suffix is load-bearing.

## 6.3 `Value` is empty on all 229 — measured as conventional, downgraded to INFO

An earlier draft of this audit scored this as a defect on all 229 instances, which made
every record fail and destroyed the severity signal. It was challenged, so it was measured
rather than argued.

**Method.** Read the column layout and contents of real EasyEDA BOM exports on disk, plus
the JLCPCB-format BOM the same pipeline produced.

**What the exported EasyEDA BOM actually contains** (UTF-16, TAB-separated):

```
No. · Quantity · Comment · Designator · Footprint · Value · Manufacturer Part ·
Manufacturer · Supplier Part · Supplier · LCSC Stock · Pins · Category ·
Add into BOM · Convert to PCB · Datasheet
```

There are **two** identity columns, `Comment` and `Value`. In the sample, `Value` was blank
on 19 of 20 rows while `Comment` was populated on all 20 — for example
`Comment='0402WGF0000TCE', Value=''`. **A blank `Value` does not produce a blank BOM line;
`Comment` carries the identity.**

And the JLCPCB-format BOM the pipeline emits has only four columns:

```
Comment · Designator · Footprint · LCSC Part #
```

**There is no `Value` column in a JLC BOM at all.** For the artefact a fab actually ingests,
`Value` is irrelevant by construction.

**Verdict: `EMPTY_VALUE_FIELD` is INFO, not a defect.** The convention of carrying the value
in `Name` is sound. Its only visible cost is the ~200 `Component has empty value of property
"Value"` infos in the DRC log, which are noise.

**One question this did not settle, flagged rather than assumed.** Whether K1's literal
`Name` values (`1.33k`, `10k`, `DNP`) will populate `Comment`, or whether `Comment` falls
back to the device name. Two readings fit the sample equally well — `Comment` ← `Name`, or
`Comment` ← `Value` with a device-name fallback — and the one board with both a schematic
source and an export on disk is a **different revision** whose parts used
`Name = "={Value}"`, a template expression, not literal names like K1's. That board cannot
discriminate the two readings.

If `Comment` turns out to be fed by `Value`, every K1 BOM line would read `RC0402FR-0710KL`
instead of `10k`, and this becomes a real finding rather than a cosmetic one. **Export K1's
BOM and read the `Comment` column.** That single check settles it; until then this section
claims only what was measured.

## 6.4 27 instances have no `Symbol` attribute

`J2-LED, J3-LED, R2-PWR1, R5-PWR2, R51-LED, R52-LED, R59-VAL, R60-VAL, R64-PWR1, R66-PWR1,
R7-PWR2, R70-RTC, R71-ESP, R72-ESP, R9-PWR2, SW1-RTC, SW2-ESP, SW3-ESP, SW4-VAL,
TP1-ESP…TP8-AUD`. All 27 do carry a `Device`, so the symbol most likely resolves from the
device at render time. Informational — flagged so the writer can confirm rather than assume.

---

# 7. The two structural questions from the brief

## 7.1 `U6-RTC` appears twice — legitimate

Both instances share symbol `6b50fcab…`, device `69a263214ca544edaed5248f1d7e5e69`, and a
`Multi-Part Group` attribute. This is the MIMXRT1062DVJ6B MCU drawn as a genuine multi-part
symbol. The whitelist in `check_single_schematic.py` is correct.

Two caveats. DRC line 406 reports: *"Component MIMXRT1062DVJ6B is a multi-part component, the
properties of each part should be the same. `$1I3295`、`$1I3673` have different property
Supplier Part, Add into BOM, supplierId."* Part 1 is `MIMXRT1062DVJ6B.1` with no
`Add into BOM`; part 2 is `MIMXRT1062DVJ6B.2` with `Add into BOM` = `no`.

The `Add into BOM` = `no` on part 2 is almost certainly *intentional* — it stops the MCU being
counted twice. But EasyEDA considers divergent properties across a multi-part symbol an error
in its own right, and if its BOM engine already de-duplicates multi-part symbols, the manual
override is redundant and the warning is the only effect. **Bounded repair:** export the BOM
and confirm the MCU appears exactly once; if it does with the override removed, remove it and
clear the warning.

## 7.2 The undesignated component is the sheet frame — not a part

The single component with no `Designator` is `e1`. Its attributes are `@Project Name`,
`@Page Count`, `@Schematic Name`, `Border`, `Page Size`, `Width`, `Height`,
`Title Block Position`, `Company: SPECTRASYNQ`, `Version: V1.0`. It is the drawing frame and
title block, not a component.

**No defect.** But the census that reports "230 components" is counting it. The correct
denominator for any BOM completeness claim on this board is **229 placed instances / 228
distinct designators**, and that denominator should be stated wherever a completeness
percentage is quoted.

---

# 8. Out of scope, observed and passed on

These are connectivity findings from the DRC log, recorded here only so they are not lost.
They belong to the netlist lane, not this audit.

- **Six single-pin NFC power nets** — `NFC_AGDC`, `NFC_VDD_A`, `NFC_VDD_AM`, `NFC_VDD_D`,
  `NFC_VDD_DR`, `NFC_VDD_RF` each connect to exactly one pin. Plus `BUCK_SS`.
- **`C10-PWR2` has both pins floating** — a completely unconnected capacitor.
- **~150 floating pins**, concentrated on `U6-RTC` (111), `U9-ESP` (19), `J1-PWR1` (15),
  `U12-NFC` (11), `J9-AUD` (6), `U13-MOT` (6).
- DRC summary: Fatal 0, Error 0, **Warning 22**, Info 398. Zero errors is not a clean board —
  none of the defects in §1 raises an ERC error, which is the whole reason this audit exists.

---

# 9. Repair order

**The 14 BLOCKERs first — these are the parts that ship wrong.**

1. **`R1-PWR1`, `R8-PWR2`** — rebind to the 1.33 kΩ and 3.48 kΩ devices. Wrong resistors on
   a power rail; the correct LCSC codes are already in the file.
2. **`R40/R41-AUD`, `R45/R47/R49-MOT`, `R56/R57-VAL`** — set `Add into BOM` = `no` **and**
   `Convert to PCB` = `no`, and clear the fabricated MPN. Both flags, not one: BOM exclusion
   alone leaves a CPL row with no BOM line (§2).
3. **`J1-PWR1`, `J7-ESP`** — resolve the USB-C shell pads before layout.
4. **`J6-ESP`, `J11-VAL`, `R42-NFC`** — the three stand-ins. The two headers are a different
   footprint family and need checking before layout; `R42-NFC` needs a decision on 5% vs 1%
   in an NFC matching network. Record each as an explicit waiver on the sheet.

**Then the batch work.**

5. **Export K1's BOM and CPL.** Two things depend on it and nothing above is confirmed for
   *this board* until it exists: that `Add into BOM` behaves here as it does on IM69D130
   (§2), and whether `Comment` carries the literal `Name` (§6.3). One export answers both.
6. `supplierId` / `Supplier Part` on the 160 MAJOR instances — complete the device→LCSC
   table, then run the normalisation already proven in §3.2.
7. **Add the `Name`-declares-DNP vs `Add into BOM`/`Convert to PCB` check**, and prove it
   goes red before trusting it.
8. Test-point MPN decision (8 phantom BOM lines); MPN and Manufacturer backfill for
   traceability.

---

**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:bom-audit | Created — full semantic audit of 229 placed instances at frozen hash 489736:464c27d4 |
| 2026-08-28 | agent:bom-audit | Re-tiered to BLOCKER/MAJOR/MINOR/INFO after a 100% defect rate was challenged as unprioritisable. Measured BOM export semantics against real EasyEDA exports on disk: `EMPTY_VALUE_FIELD` demoted to INFO (JLC BOM has no Value column); `Add into BOM` behaviour confirmed by BOM/CPL designator reconciliation; added §2 flag provenance, §3.2 normalisation precedent, and the `Convert to PCB` CPL half of the DNP repair. |
