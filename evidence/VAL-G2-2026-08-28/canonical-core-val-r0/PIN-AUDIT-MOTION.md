---
abstract: "VAL-G2 pin audit of the K1-CORE-VAL-R0 motion block (U13-MOT LIS2DH12, C62/C63-MOT, R44-R50-MOT) against the ST LIS2DH12 datasheet and contracts/motion-interface.md. Verdict: five sensor pins are still unconnected at the 14:58 DRC - CS and SA0 (both mode/address straps), RES, and two GNDs; INT2 is now closed as INTENTIONAL_NC. The RT-or-S3 ownership matrix is FAKE on SDA and SCL (both the 0R and the DNP resistor bridge the same net pair) and drawn-but-unterminated on INT, and it sits on the wrong side of the bus - it isolates the sensor, not the master. The RT1062, the contracted default owner, has no I2C connection anywhere on the board. Section 5 gives the correct topology: one bus, four slaves, one selectable master leg. Proposals only; a single writer must reconfirm against live."
---

# PIN-AUDIT-MOTION — VAL-G2

**Lane:** A6-MOTION-LED · **Date:** 2026-08-28 · **Status:** PROPOSAL, not a write

Denominator: `frozen-denominator-489736`, source hash `489736:464c27d4` — 228 designators,
143 named nets, 675 wires. Machine-readable form of everything below:
`pin-audit-motion-led.json`.

---

## 1. What was measured, and how it could have gone wrong

The claim "this pin is connected" is only worth anything if the check can go red. Two
independent oracles were run against the same frozen source, plus one archived third party.

| Oracle | What it measures | Result |
| --- | --- | --- |
| Union-find geometry oracle (this lane) | Do the wire segments and pin coordinates actually coincide, and what net label does the resulting island carry | 62 in-scope pins classified, 0 unclassified |
| `harness/check_schematic_connectivity.py` | Label-to-pin binding, independently implemented | 229/229 parts, 0 abstentions, `wrong_pin_bindings=0`, agrees pin-for-pin |
| `anchors/schDrcLog_2026-08-28.txt` (12:17) | EasyEDA's own netlister view | Lists `U13-MOT.2, .3, .5, .7, .8, .11` floating — exactly this audit's six |
| `anchors/schDrcLog_2026-08-28T1458.txt` (14:58) | Same, on a state **newer** than the frozen hash | Lists `U13-MOT.2, .3, .5, .7, .8` — five of the six still floating after the intervening work (§6) |

**Fault battery.** The geometry oracle was proven fault-evident before it was believed:
three positive controls stayed green while five injected faults went red — a pin displaced
perpendicular off its wire, a synthetic 3V3-to-GND bridge, and the dangling-net detector.

**The battery earned its keep, and it caught a wrong answer in this very audit.** The first
pass used `jobs/all-pins-nc-audit.results.json` as the pin denominator. That file covers 228
component *parts*; the RT1062 is a two-part symbol, and the file silently omits part `e3295`
and its 98 balls. On that denominator the LED data path reads as absent and the RT1062 reads
as owning nothing. Widening the denominator to `jobs/full-pin-harvest.results.json`
(230 of 230 source parts, 880 pins) turned the self-test red, and the corrected answer is the
opposite one. **Any motion or LED audit run against `all-pins-nc-audit.results.json` is wrong
by construction.**

**Structural fact worth stating plainly.** All 675 wires resolve to 675 electrically isolated
islands — no wire on this sheet touches any other wire. Connectivity here is established
entirely by net labels on single stubs. Both oracles measured it independently and agree. That
is a legal construction under `schematic/SINGLE-SHEET-CONTRACT.md`, but it means a net label
typed onto a stub that reaches nothing looks identical to a real connection until something
counts endpoints.

**Coverage.** 10 in-scope components, 30 in-scope pins, 30 classified, 0 silent unknowns.

---

## 2. U13-MOT (LIS2DH12TR, LGA-12) — 6 of 12 pins unconnected at the frozen hash, 5 still unconnected at 14:58

Authority: ST LIS2DH12 datasheet, Table 2 pin description and section 6 interface selection.
The datasheet outranks every internal note here.

| Pin | Name | Net | Status | Finding |
| --- | --- | --- | --- | --- |
| 1 | SCL/SPC | `MOTION_SCL` | CONNECTED | — |
| **2** | **CS** | — | **FLOATING** | Datasheet: *"To select/exploit the I²C interface, the CS line must be tied high (i.e. connected to Vdd_IO)."* CS defaults to **input high impedance — there is no internal pull-up.** A floating CS can put the part into SPI mode and disable I²C. **Highest-severity defect in this block.** |
| **3** | **SDO/SA0** | — | **FLOATING** | I²C address LSB. Default is *input with internal pull-up*, so the part will most likely answer at the SA0=1 address — but the strap is undeclared, noise-exposed, and the firmware contract has no address to bind to. |
| 4 | SDA/SDI/SDO | `MOTION_SDA` | CONNECTED | — |
| **5** | **RES** | — | **FLOATING** | The datasheet function column is literally *"Connect to GND"*. It is not. |
| 6 | GND | `GND` | GND | — |
| **7** | **GND** | — | **FLOATING** | 0 V supply. Datasheet: *"All the voltage and ground supplies must be present at the same time to have proper behavior of the IC."* <!-- british-english-guard: ignore — verbatim ST datasheet quote, US spelling preserved for fidelity --> |
| **8** | **GND** | — | **FLOATING** | Same as pin 7. |
| 9 | VDD | `3V3` | POWER | Decoupled by C62-MOT 100 nF. The datasheet application hints ask for **100 nF ceramic *and* 10 µF** at this pin; only the 100 nF is local. |
| 10 | VDD_IO | `3V3` | POWER | Decoupled by C63-MOT 100 nF, as the datasheet requires. |
| 11 | INT2 | — | **INTENTIONAL_NC** *(resolved after the frozen hash)* | A push-pull *output* (default forced to GND), so leaving it open is electrically safe. It carried no No-Connect flag at the frozen hash; the 14:58 DRC no longer lists it, and the mutation ledger attributes that to Captain's unused-pin NC sweep. Disposition closed — see §6. |
| 12 | INT1 | `MOTION_INT1` | CONNECTED | Feeds the R48/R49 owner-selection pair. |

### Bounded repair — motion sensor pins

1. `U13-MOT.2 (CS)` → tie to `3V3` (the VDD_IO rail). Non-negotiable for I²C mode.
2. `U13-MOT.5 (RES)` → tie to `GND`. Datasheet-mandated.
3. `U13-MOT.7`, `U13-MOT.8` → tie to `GND`.
4. `U13-MOT.3 (SA0)` → strap deliberately to `GND` or `3V3`, and record the resulting 7-bit
   address in the hardware-to-firmware contract (D18). Do not leave it to the internal pull-up.
5. `U13-MOT.11 (INT2)` → **already done.** Captain's 14:58 NC sweep placed the flag; the pin is
   closed as `INTENTIONAL_NC`. Route it to the owner alongside INT1 only if a second interrupt
   source is wanted later.
6. Add a 10 µF bulk capacitor local to `U13-MOT.9 (VDD)` unless the 3V3 lane can show existing
   bulk within the datasheet's "as near as possible" intent. Hand to A2-RAILS if contested.

---

## 3. The ownership matrix — it is not a matrix

`contracts/motion-interface.md` requires RT1062 as default owner, with a 0R/DNP matrix that
selects RT **or** S3 and never enables both as uncontrolled masters. The required shape is one
owner path per signal:

```
                     /-- 0R  FIT --> RT_I2C_SDA
MOTION_SDA ---------<
                     \-- 0R  DNP --> S3_I2C_SDA
```

What is actually drawn, measured at pin level:

| Signal | FIT leg | DNP leg | Measured | Verdict |
| --- | --- | --- | --- | --- |
| SDA | R44-MOT 0R: `MOTION_SDA` ↔ `I2C_SDA` | R45-MOT: `MOTION_SDA` ↔ `I2C_SDA` | **identical net pair** | **FAKE** |
| SCL | R46-MOT 0R: `MOTION_SCL` ↔ `I2C_SCL` | R47-MOT: `MOTION_SCL` ↔ `I2C_SCL` | **identical net pair** | **FAKE** |
| INT | R48-MOT 0R: `MOTION_INT1` → `MOTION_INT_RT` → U6-RTC ball L11 (GPIO_AD_B1_02) | R49-MOT: `MOTION_INT1` → `MOTION_INT_S3` | genuine per-owner nets; the S3 leg binds one pin | **REAL SHAPE, UNTERMINATED** |

On SDA and SCL the two resistors are wired **in parallel across the same two nets**. Fitting
R44 or R45 makes no electrical difference whatsoever. There is no `RT_I2C_SDA`, no
`S3_I2C_SDA`, and no per-owner net of any kind on either bus line. This is not a half-built
XOR; on those two signals it is a resistor pattern that selects nothing.

### The finding underneath the finding

The shared bus that both resistors land on is:

- `I2C_SDA` [8 pins] — R4-PWR1.1, R28-AUD.2, R44-MOT.2, R45-MOT.2, U2-PWR1.4 (SDA),
  U11-AUD.12 (SDA), U12-NFC.32 (MISO/SDA), **U9-ESP.37 (TXD0)**
- `I2C_SCL` [7 pins] — R29-AUD.2, R46-MOT.2, R47-MOT.2, U2-PWR1.5 (SCL), U11-AUD.13 (SCL),
  U12-NFC.30 (SCLK/SCL), **U9-ESP.36 (RXD0)**

**The RT1062 is not on this bus. It is not on any I²C bus.** U6-RTC binds 41 distinct nets
across both symbol parts, and not one of them is an I²C net. The only master-capable endpoint
on the shared bus is the ESP32-S3.

So the contract's default owner has no data path to the sensor at all, and the only owner that
does have one is the owner the contract makes optional. The RT1062 sees the interrupt and
nothing else. **The ownership matrix cannot be repaired by fixing resistors — the RT leg does
not exist to select.**

Two caveats stated so they are not mistaken for confidence:

- `MOTION_INT_S3` binds exactly one pin (R49-MOT.2). A second labelled stub for that net
  (wire `e8944`, segment `[4170,4365,4040,4365]`) is drawn in the ESP block but lands on no
  pin; the nearest U9-ESP pin is 90 units away. The S3 interrupt leg is drawn and unterminated,
  not absent by intent.
- U9-ESP is recorded by the connectivity harness as **displaced from its own wiring**
  (`offset [5,-20]`, 41 pins), with only 5 of its 41 pins bound to anything and no supply net.
  Its `I2C_SDA`/`I2C_SCL` bindings are exact zero-tolerance coincidences, but on a displaced
  component that is worth reconfirming — handed to **A4-S3-AUDIO**.

### Bounded repair — ownership matrix

Per signal, and only after the RT1062 I²C pad assignment exists:

1. **A3-RT-DEBUG must first assign two RT1062 balls to `RT_I2C_SDA` / `RT_I2C_SCL`.** Until
   that exists, nothing in this block can be repaired into a real XOR. This is the blocking
   dependency, and it is outside this lane.
2. Split each shared line into per-owner nets: `MOTION_SDA` → R44-MOT (FIT) → `RT_I2C_SDA`;
   `MOTION_SDA` → R45-MOT (DNP) → `S3_I2C_SDA`. Same for SCL through R46/R47.
3. Terminate `MOTION_INT_S3` on a real ESP32-S3 pin, or delete the leg and say so.
4. Draw the XOR rule beside the circuit on the sheet, as the contract requires. It is not there.

### Pull-ups

R50-MOT is a 4.7k pull-up on `MOTION_SDA`. **There is no pull-up on `MOTION_SCL`.** With the
0R links fitted the shared bus pull-ups (R4-PWR1, R28-AUD, R29-AUD, all 4.7k) serve both lines,
so the bus works today — but the asymmetry means that the moment the buses are genuinely split
per owner, SCL has no pull-up on the sensor side. Fix it in the same edit as the split, not
after.

---

## 4. R45 / R47 / R49-MOT are not DNP — and what that actually costs

Re-derived independently from the frozen source, not taken from the BOM lane.

| Fact | Measured |
| --- | --- |
| `Name` | `DNP` |
| `Manufacturer Part` | `RC0402FR-07DNP` — not a catalogue part |
| Orderable `Supplier Part` | `RC0402FR-0710KL.1` — a genuine 10 kΩ |
| `Add into BOM` = `no` | **Absent.** The attribute exists on this sheet and demonstrably works: `C43-ESP`, `C44-ESP` and `C52-AUD` all carry it with `Name` values like `DNP / 100pF USB D+ TUNE`. None of the three MOT resistors carry it. |
| Bound device | `e1b1f220e40a…`, a shared 24-member resistor device whose `Name` values across instances are `1.33k`, `3.48k`, `10k`, `DNP` |

**As the BOM stands they will be manufactured and fitted, as 10 kΩ resistors.**

Scanning drawn `Name` against orderable `Supplier Part` across all 65 RC0402 resistors finds
this fake-DNP pattern on exactly seven parts board-wide: **R40-AUD, R41-AUD, R45-MOT, R47-MOT,
R49-MOT, R56-VAL, R57-VAL.** No other resistor mismatches once notation differences
(`5.1k`/`5K1`, `32.4k`/`32K4`, `1.05M`/`1M05`) are discounted.

### 4.1 Which side of the matrix each resistor sits on

| Ref | Drawn | Orderable | Intended role, RT1062-default | Net pair |
| --- | --- | --- | --- | --- |
| R44-MOT | 0R | genuine 0 Ω | **FIT** — SDA owner link | `MOTION_SDA` ↔ `I2C_SDA` |
| R45-MOT | DNP | **10 kΩ** | intended DNP — SDA alternate | `MOTION_SDA` ↔ `I2C_SDA` (same pair) |
| R46-MOT | 0R | genuine 0 Ω | **FIT** — SCL owner link | `MOTION_SCL` ↔ `I2C_SCL` |
| R47-MOT | DNP | **10 kΩ** | intended DNP — SCL alternate | `MOTION_SCL` ↔ `I2C_SCL` (same pair) |
| R48-MOT | 0R | genuine 0 Ω | **FIT** — INT to RT1062 | `MOTION_INT1` → `MOTION_INT_RT` → U6-RTC L11 |
| R49-MOT | DNP | **10 kΩ** | intended DNP — INT to S3 | `MOTION_INT1` → `MOTION_INT_S3` (unterminated) |
| R50-MOT | 4.7k | genuine 4.7 kΩ | FIT — pull-up, not part of the matrix | `3V3` ↔ `MOTION_SDA` |

### 4.2 Does fitting them create a dual-master condition?

**Not today — and the reason is the deeper defect.**

On SDA and SCL, R44 and R45 bridge the **identical net pair**, as do R46 and R47. Fitting both
puts 0 Ω in parallel with 10 kΩ between the same two nets: electrically no change. No
dual-master arises, because **only one master is wired to the shared bus at all** — `U9-ESP` —
and the RT1062 is on no I²C bus anywhere on the board (§3). The safety property the contract
exists to enforce is **vacuously satisfied**: satisfied by the absence of the very configuration
the contract requires. That is worse than a violation, because it looks clean.

**The hazard is latent and it arms on repair.** The moment the correct per-owner split is
built — `MOTION_SDA` → R44 (0R) → `RT_I2C_SDA` and `MOTION_SDA` → R45 → `S3_I2C_SDA` — a
populated R45 ties the sensor to **both** masters simultaneously. That is exactly the
uncontrolled dual-master connection `contracts/motion-interface.md` exists to prevent. So the
BOM fix is not optional cleanup that can follow the topology fix: **it must land before or with
the split, never after.**

**`MOTION_INT` is not a dual-master risk and should not be treated as one.** `MOTION_INT1` is a
single push-pull *output* from U13-MOT feeding MCU *inputs*. Driving it into two receivers is
one driver into two loads — no contention. The XOR on INT is about which MCU services the
interrupt in firmware, not about electrical conflict.

### 4.3 Is the FIT side genuinely 0R?

**Yes. The concern does not carry over to the fitted side.** R44/R46/R48-MOT bind device
`0f3d5fb5eae5…` — a separate 11-member family whose *only* `Name` value is `0R`, with
`Supplier Part = RC0402FR-070RL.1`, a genuine 0 Ω. They are real 0 Ω links. Only the DNP side is
mis-specified.

But the value question does cut the other way, and it matters: **a 10 kΩ in series on an I²C
line does not select an owner, it breaks the bus.** Against the 4.7 kΩ bus pull-ups it forms a
divider and neither side would meet V_OL. So R45/R47 are wrong twice over — wrong exclusion
status, *and* wrong value class for the position they occupy. If they are ever wanted as a
genuine fitted alternative they must be 0 Ω, matching their R44/R46 counterparts.

**Handed to B-BOM** for the exclusion fix; the value-class and topology fixes belong to the
repair in §3.

### 4.4 Correction to an earlier handoff from this lane

An earlier revision of the companion LED audit reported the LED-branch eFuse current limit as
UNDETERMINED, on the grounds that `R8-PWR2` reads `3.48k` while its supplier field showed a
10 kΩ. **That was wrong and is withdrawn.** `R8-PWR2` orders as `Supplier Part = C185418`,
`Manufacturer Part = RC0402FR-073K48L` — a genuine 3.48 kΩ, giving a determined 0.96 A limit.
The misread was of `supplierId`, which is a stale library-inherited string on several parts;
the orderable identity lives in `Supplier Part`. That distinction is also the clean test for the
fake DNPs: real-valued parts carry an LCSC `Cxxxxxxx` code in `Supplier Part`, while the seven
fake DNPs carry the inherited 10 kΩ string in **both** fields.

---

## 5. The correct per-signal topology, and whether isolation is possible at all

### 5.1 The matrix is in the wrong place

This is the load-bearing correction, and it is not the one the brief anticipated.

A link between `MOTION_SDA` and the shared bus isolates **the sensor**, not **the master**. Owner
selection is a property of which *master* is attached, so the 0R/DNP pair has to sit on each
master's leg, not on the sensor's leg. That is why no arrangement of R44–R49 in their present
positions can ever produce a real XOR: they are on the wrong side of the bus.

The bus census settles the shape. Every other device on `I2C_SDA` / `I2C_SCL` is a **slave**:

| Device | Part | Role |
| --- | --- | --- |
| U2-PWR1 | INA226 | slave (power monitor) |
| U11-AUD | TLV320ADC6120 | slave (audio ADC) |
| U12-NFC | ST25R3916B | slave (NFC reader IC) |
| U13-MOT | LIS2DH12 | slave (this lane) |
| **U9-ESP** | **ESP32-S3-WROOM-1** | **the only master-capable device on the bus** |

One bus, four slaves, one master socket. So the correct topology is not "split the bus per owner"
— it is **keep one bus and select which master drives it**:

```
   U2-PWR1   U11-AUD   U12-NFC   U13-MOT      <- slaves, permanently attached
      |         |         |         |
      +---------+---------+---------+------ I2C_SDA / I2C_SCL  (bus pull-ups live here)
                                    |
                        /-- 0R  FIT --> RT_I2C_SDA / RT_I2C_SCL   (RT1062, default owner)
                       <
                        \-- 0R  DNP --> S3_I2C_SDA / S3_I2C_SCL   (ESP32-S3)
```

**Two resistor pairs total — four parts, on the master legs.** Not three pairs on the sensor leg.

Consequences, stated so the repair is bounded:

1. `R44`/`R45` and `R46`/`R47` move from the sensor leg to the master legs, or are deleted and
   replaced there. In their present positions they are not owner-selection hardware.
2. `MOTION_SDA` / `MOTION_SCL` collapse into `I2C_SDA` / `I2C_SCL`. The sensor is a slave; it has
   no reason to sit behind a link.
3. `MOTION_INT1` keeps its `_RT` / `_S3` split through `R48`/`R49`. **The interrupt is the one
   signal whose XOR is correctly placed already** — because an interrupt line genuinely is
   point-to-point between the sensor and one owner, unlike the shared bus. Follow it as the model
   for the master legs, not for the bus legs.
4. **Recompute the pull-up budget in the same edit.** `R50-MOT` (4.7 k) currently pulls up
   `MOTION_SDA`. Once that merges into `I2C_SDA` it lands in parallel with `R4-PWR1` (4.7 k) and
   `R28-AUD` (4.7 k) → about 1.57 kΩ on SDA against 2.35 kΩ on SCL (`R29-AUD` + none from motion).
   That is both asymmetric and stronger than intended. Consolidate to **one** pull-up pair on the
   shared bus and remove the rest.

### 5.2 Can RT and S3 be genuinely isolated? Yes — but not by splitting the bus

**Answer: yes, and it is easier than the brief assumed, because there is only one master socket
to arbitrate.** The NFC, audio and power-monitor devices are not an obstacle to isolation — they
are slaves, and slaves do not care which master is talking. Nothing about their presence forces
a dual-master condition.

What would *not* work, and should be ruled out explicitly:

- **Duplicating the bus per owner** (an RT bus and an S3 bus, each with its own copy of the
  slaves) — impossible, the slaves are single instances.
- **Leaving both masters permanently attached and arbitrating in firmware** — I²C multi-master
  arbitration is legal but requires both masters powered and both stacks implementing it. On a
  validation platform where the whole point is to test one owner at a time, this is exactly the
  "uncontrolled dual-master connection" `contracts/motion-interface.md` forbids.
- **Selecting on the sensor leg** — what is drawn today. Isolates the wrong device.

The blocking dependency is unchanged and belongs to another lane: **A3-RT-DEBUG must assign two
RT1062 balls to `RT_I2C_SDA` / `RT_I2C_SCL`.** Until then there is no RT master leg to link to,
and the matrix cannot be built in any position.

### 5.3 Is the FIT value genuinely 0 Ω? Yes — re-confirming, because the premise recurs

`R44`/`R46`/`R48-MOT` bind device `0f3d5fb5eae5…`, an 11-member family whose only `Name` value is
`0R`, with `Supplier Part = RC0402FR-070RL.1` — a genuine 0 Ω. **The FIT side is not bound to a
10 kΩ device.** Only `R45`/`R47`/`R49` are, and that is the defect. When the matrix moves to the
master legs, all four parts must be 0 Ω, with the DNP half excluded via `Add into BOM = no`
rather than by a `Name` field.

---

## 6. The 14:58 DRC run — five of six confirmed, and one inference to be careful with

Captain's fresh GUI DRC (`anchors/schDrcLog_2026-08-28T1458.txt`, Fatal 0 / Error 0 / Warn 15 /
Info 414) post-dates this audit's frozen hash. Diffing it against the 12:17 run:

| | 12:17 | 14:58 |
| --- | --- | --- |
| Floating pins, board-wide | 195 | 101 |
| `U13-MOT` floating | 2, 3, 5, 7, 8, **11** | 2, 3, 5, 7, 8 |
| `U9-ESP` floating | 19 | 0 |
| `U6-RTC` floating | 111 | 80 |

**Five of this audit's six `U13-MOT` findings are confirmed by netlist-grade evidence on a state
newer than the frozen source.** `CS`, `SDO/SA0`, `RES` and both spare `GND` pins are still
floating. None of them is a registration artefact, and none was touched by the intervening work.

`U13-MOT.11 (INT2)` is resolved — which is exactly repair item 5 in §2. Its disposition changes
from `FLOATING_DEFECT` to `INTENTIONAL_NC`.

### The inference to be careful with

95 pins were resolved in one sweep across 17 designators spanning every functional block —
`U6-RTC` 31, `U9-ESP` 19, `U12-NFC` 10, plus connectors and switches. Nobody wires 95 pins across
17 unrelated blocks between two DRC runs. The mutation ledger names the mechanism outright:

> `STATE_QUARANTINED … "Captain applied unused-pin NC crosses after the open NFC NC transaction"`

**These pins were declared, not connected.** A No-Connect cross is an assertion that a pin is
deliberately unused; it is the opposite of a connection. So `U9-ESP` reaching zero floating pins
is **not** evidence that any S3-side net became terminated, and no finding that depended on
`MOTION_INT_S3` being unterminated is weakened by it. The last direct measurement — the frozen
source plus the connectivity harness — puts `MOTION_INT_S3` at one bound pin, and an NC sweep
cannot add one.

There is a sharper risk in the other direction, and it is worth checking before the next write:
**if an NC cross was applied to the S3 pin that was meant to receive `MOTION_INT_S3`, the S3
owner leg is now documented as permanently unused.** That is worse than unterminated, because it
reads as intentional. Handed to **A4-S3-AUDIO** to confirm against live.

Two further notes from the same diff. The DRC "single network" warning is **not** a reliable
dangling-net detector: `MOTION_INT_S3` was a one-pin net in the frozen source and appeared in
neither run's list, while `BUCK_PG` did. Its silence is not evidence. And one pin went the wrong
way — **`U3-PWR2.5` became floating between the two runs**, a regression outside this lane,
handed to **A2-RAILS**.

---

## 7. VAL-G3 — recorded, not acted on

**VAL-G3-MOT-01.** Mount U13-MOT on a rigid structural section near the assembled structural
centre — not on a board edge, connector tongue, or unsupported cantilever. Source:
`contracts/motion-interface.md`. No placement, footprint or geometry action was taken in this
lane and none is proposed.

---

## 8. Verdict

| Requirement | Verdict |
| --- | --- |
| Every LIS2DH12 pin audited against the datasheet | Done — 12/12, no silent unknowns |
| No required pin floating | **FAIL** — CS, RES, GND×2 floating and SA0 unstrapped, all five re-confirmed by the 14:58 DRC. INT2 closed as INTENTIONAL_NC. |
| Ownership matrix is a real XOR | **FAIL on SDA, FAIL on SCL, INCOMPLETE on INT** — and the matrix is on the wrong side of the bus entirely (§5.1) |
| Can RT and S3 be genuinely isolated | **Yes** — one bus, four slaves, one master socket; select the master leg, not the sensor leg (§5.2) |
| RT1062 is the default owner | **FAIL** — RT1062 has no I²C connection on the board |
| R45/R47/R49 DNP status confirmed | Confirmed as populated 10 kΩ; handed to B-BOM |

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:A6-MOTION-LED | Created. VAL-G2 motion pin audit against frozen denominator 489736:464c27d4 and the ST LIS2DH12 datasheet. |
| 2026-08-28 | agent:A6-MOTION-LED | Added §5 (correct per-signal topology — the matrix is on the wrong side of the bus; isolation verdict) and §6 (14:58 DRC diff — five of six U13-MOT findings re-confirmed, INT2 closed as INTENTIONAL_NC, and the 95-pin resolution identified as an NC-cross sweep rather than wiring). |
| 2026-08-28 | agent:A6-MOTION-LED | Section 4 expanded to answer the ownership-matrix questions raised by the BOM lane: per-resistor FIT/DNP roles, the dual-master verdict (latent, not present), confirmation that the FIT side is genuine 0R, and the seven-resistor fake-DNP census. Added 4.4 withdrawing this lane's earlier UNDETERMINED claim about the LED eFuse current limit. |
