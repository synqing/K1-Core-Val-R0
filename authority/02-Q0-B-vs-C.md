# VAL-G1 — CLOSED. Option C selected; Option B deferred.

**Ruled 2026-08-27.** Q0-A was already closed: RT1062 owns audio, processing and render;
ESP32_S3 is the radio bridge; monolithic ESP32-S3 is the legacy parity oracle only.

---

## Ruling

| | |
| --- | --- |
| **Option C** — RT1062 and ESP32_S3 on the Core | **SELECTED for K1-CORE-VAL-R0** |
| **Option B** — carrier plus SSCM-1 compute module | **DEFERRED. Not rejected, not disproven.** |

### Basis — a programme decision, not a technical defeat

Option C is the shortest path to proving the thing that actually needs proving. It puts the
RT1062, ESP32_S3, K1BR, audio, LEDs, NFC, motion, the Debug Fabric and power on one board where
all of it is directly observable.

Option B would require proving a second architecture wrapped around the first: a custom compute
module, a module connector contract, module power delivery, carrier-to-module boot sequencing,
cross-connector audio clocks, LED fast-edge crossings, module mechanics, module thermal
behaviour and connector reliability — **before** the dual-MCU hardware baseline itself has been
validated. For a first validation mule that reduces experimental clarity rather than increasing
it.

Once C works, an SSCM-1 migration becomes a clean experiment: modularising a known-good system
instead of debugging the compute architecture and the modular architecture simultaneously.

---

## Option B — actual status at closure

Option B is **not** recorded as failed. Its measured position:

| Aspect | State |
| --- | --- |
| Interface budget | **PASS at current estimate.** Sub-option B2 robust = 59 of 67 contacts, 8 spare, 11.94 % contingency |
| Mechanical | **NOT PROVEN** — neither viable nor unviable |
| Thermal | **OPEN RISK** — no quantified model exists |
| Modularity value | **VALID** — the upgrade path remains genuinely attractive |
| Reason not selected | Introduces a second custom board and interface architecture before the dual-MCU baseline is proven |

### Two arguments withdrawn

- **The M.2 antenna clash is withdrawn as a general objection to Option B.** It applies only to
  sub-option B2, where both processors sit on the module. Under B1 the ESP32_S3 and its radio
  remain on the carrier and an RT-only module has no 2.4 GHz antenna at its retention end.
  Generic M.2 2280 mechanics do not establish otherwise.
- **The thermal argument is downgraded from rejection to open risk.** A 22 x 80 mm card is not
  inherently incapable of carrying an RT1062. The answer depends on real dissipation under the
  K1 workload, regulator losses, copper area, layer stack, thermal vias, plane count, enclosure
  coupling and airflow. None of those results exist.

### Note for whoever revisits this

The D13.1 crossing set in `contracts/sscm1-v2/` was written assuming **B1** — ESP32_S3 on the
carrier, RT1062 on the module. B2 is the stronger pin-budget case because K1BR stays local. If
Option B is revived, the crossing set must be re-derived for whichever sub-option is chosen.
The study's own signal count also carries an unresolved contradiction: prose states 26–28
signals while the lead calculation uses 29. Resolve that before reusing the figures.

---

## Option C — what closing this gate does NOT establish

**Do not write, anywhere in authority, that Option C routes cleanly on six layers.** It has not
been shown.

| Item | State |
| --- | --- |
| `OPTION_C_BGA_ESCAPE` | **OPEN** |
| `OPTION_C_6_LAYER_ROUTABILITY` | **OPEN** |
| `HDI / VIPPO requirement` | **OPEN** |
| `RT1062 package` | **MUST CLOSE BEFORE VAL-G2** |
| `8-layer escalation` | **CONDITIONAL ONLY**, per `pcb/STACKUP-STATUS.md` |

The ring-capacity argument advanced in the VAL-G1 study is rejected as a proof. Comparing 40
required signals against 96 outer-ring slots assumes signals can be assigned to balls. They
cannot — NXP fixes the ball map. A required function sitting on ring 5 must escape from ring 5
regardless of how many outer slots are free. The same argument also invoked VIPPO while
concluding no HDI was required, which is internally inconsistent.

---

## RT1062 package — close before VAL-G2

Verified against NXP `IMXRT1060CEC` and `IMXRT1060IEC`:

| Suffix | Package | Balls | Body | Pitch |
| --- | --- | --- | --- | --- |
| `DVL6A` / `DVL6B` / `CVL` | MAPBGA | 196 | 10 x 10 mm | 0.65 mm |
| `DVJ6A` / `DVJ6B` / `CVJ` | MAPBGA | 196 | 12 x 12 mm | 0.80 mm |

Both carry 127 GPIO (124 tightly coupled) and identical feature sets. **There is no reduced-ball
RT1062.** The `AG` 144-pin LQFP code exists in the i.MX RT family nomenclature but is not an
RT1061/RT1062 ordering option in either datasheet. Ball count is therefore not a design lever;
pitch is.

**Recommended, not yet frozen: `MIMXRT1062DVJ6B`** — 196-ball, 12 x 12 mm, 0.8 mm pitch. The
wider pitch gives materially more escape room, and Teensy 4.1 uses that package, making it a
routed precedent worth studying. Teensy 4.0 uses the 10 x 10 mm `DVL6B`.

K1-CORE-VAL does not minimise board area, so the extra 2 mm per axis is not a cost worth
weighing against escape headroom. Study the Teensy fanout as reference. Do not copy its layout.

---

## VAL-G3 gains a real BGA escape gate

Ring arithmetic does not satisfy it. The gate takes the **actual NXP ball map for the selected
package** and the **actual K1 net assignment**, and produces: required ball-to-signal table;
ball-ring classification; escape direction per ball; power and ground ball map; via locations;
channel widths; conflicts; routing layers used; count of signals requiring inner-ring escape;
whether through-vias suffice; whether dog-bone escape suffices; any blind, buried or via-in-pad
requirement; and actual six-layer feasibility.

Only that evidence may set `6_LAYER_BGA_ESCAPE = PASS`.

If it fails, remedy order is: placement and orientation, then 0.8 mm package escape
optimisation, then six-layer routing strategy, then 8-layer escalation.
