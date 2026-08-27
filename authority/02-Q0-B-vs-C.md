# VAL-G1 — CLOSED. Option C selected; Option B deferred.

**Ruled 2026-08-27.** Q0-A was already closed: RT1062 owns audio, processing and render;
ESP32_S3 is the radio bridge; monolithic ESP32-S3 is the legacy parity oracle only.

---

## Ruling

| | |
| --- | --- |
| **Option C** — RT1062 and ESP32_S3 on the Core | **SELECTED for K1-CORE-VAL-R0** |
| **Option B** — carrier plus SSCM-1 compute module | **DEFERRED. Not rejected, not disproven.** |

```text
OPTION_C = SELECTED
OPTION_B = DEFERRED
OPTION_B_INTERFACE_FEASIBILITY = UNPROVEN
MIMXRT1062DVJ6B = FROZEN
OPTION_C_BGA_ESCAPE = OPEN
OPTION_C_6_LAYER_ROUTABILITY = OPEN
8_LAYER = CONDITIONAL
```

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

Option B is **not** recorded as failed. Its current authority position:

| Aspect | State |
| --- | --- |
| Interface feasibility | **UNPROVEN — prior 59/67 PASS withdrawn** |
| Mechanical | **NOT PROVEN** — neither viable nor unviable |
| Thermal | **OPEN RISK** — no quantified model exists |
| Modularity value | **VALID** — the upgrade path remains genuinely attractive |
| Reason not selected | Introduces a second custom board and interface architecture before the dual-MCU baseline is proven |

### Why the interface PASS was withdrawn

The VAL-G1 projected study cannot establish either B1 failure or B2 success. It states 26–28 B2
signal crossings but uses 29 in its lead calculation; crosses service USB and NFC IRQ in B1 even
though their ESP32_S3 owner remains carrier-side; and allocates return/shield grounds without a
physical pin assignment or return-path proof.

It also incorrectly treats the complete 2.35 A K1 carrier-source envelope as SSCM-1 connector
current. Carrier-side LED-power demand does not automatically belong on a compute-module
connector. If Option B is revived, connector power is re-derived from actual module-local rails
and loads, including margin, derating and current-sharing requirements. No replacement connector
current is asserted here, and the carried-forward 0.95 A LED-branch input remains subject to
board-level re-derivation.

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
carrier, RT1062 on the module. If Option B is revived, the complete crossing set, rail partition,
return allocation and contingency must be re-derived for the then-current sub-option. None of the
P2 contact totals is an input to that future work.

---

## Option C — what closing this gate does NOT establish

**Do not write, anywhere in authority, that Option C routes cleanly on six layers.** It has not
been shown.

| Item | State |
| --- | --- |
| `OPTION_C_BGA_ESCAPE` | **OPEN** |
| `OPTION_C_6_LAYER_ROUTABILITY` | **OPEN** |
| `HDI / VIPPO requirement` | **OPEN** |
| `RT1062 package` | **FROZEN — MIMXRT1062DVJ6B** |
| `8-layer escalation` | **CONDITIONAL ONLY**, per `pcb/STACKUP-STATUS.md` |

The ring-capacity argument advanced in the VAL-G1 study is rejected as a proof. Comparing 40
required signals against 96 outer-ring slots assumes functions can be placed on convenient balls.

The accurate statement is narrower than "signals cannot be assigned to balls":

> **NXP fixes the physical ball positions and the set of alternate functions each pad may
> provide. Many K1 peripheral functions are IOMUX-selectable across several pads, so there is
> real choice. Others are genuinely fixed — the BootROM UART recovery path on `GPIO_AD_B0_12`
> and `GPIO_AD_B0_13` among them. K1 may therefore choose among legal IOMUX alternatives, but
> may not map a function to whichever ball is convenient.**

Consequently pinmux, package orientation and BGA escape must be **co-optimised** at VAL-G3, not
resolved in sequence. That preserves the standing doctrine: placement and physics first, pin
assignment afterward.

The rejected argument invoked unspecified dog-bone/VIPPO fanout without defining via geometry,
annular structure, layer connectivity or compatibility with the selected six-layer process.
Therefore no HDI or non-HDI conclusion follows from it.

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

### FROZEN: `MIMXRT1062DVJ6B`

| | |
| --- | --- |
| Part | `MIMXRT1062DVJ6B` |
| Balls | 196 MAPBGA |
| Body | 12 x 12 mm |
| Pitch | 0.80 mm |
| Core | 600 MHz Cortex-M7 |
| NXP status | **ACTIVE** |

The **B revision is mandatory for a new design.** NXP marks `MIMXRT1062DVJ6A` and
`MIMXRT1062DVL6A` **Not Recommended for New Designs**; the `6B` parts are active. Any earlier
suggestion of `DVJ6A` is withdrawn.

Chosen over `DVL6B` because 0.8 mm pitch gives materially more geometric escape headroom than
0.65 mm, and K1-CORE-VAL does not minimise board area, so 2 mm per axis is not a cost worth
weighing against it. Teensy 4.1 uses the DVJ package and Teensy 4.0 the DVL, giving real routed
references for both. Study the fanout. Do not copy the layout.

### 0.8 mm is an advantage, not a routability proof

**No traces-between-balls capacity is accepted** until the PCB land diameter, clearance rules,
via geometry, mask expansion and fabrication limits are sourced from the NXP land-pattern
recommendation and the fabricator's rules, and until the actual pinmux is known.

An earlier channel calculation in this project derived a 450 um channel from an assumed 350 um
PCB land. That land was not sourced — the package drawing specifies **solder-ball** geometry,
which is not a PCB land. And even on that assumption, two 90 um traces with 90 um pad and
intertrace clearances consume exactly 450 um: zero surplus before tolerance, registration or
mask rules. A 330 um land leaves 20 um total. Neither supports "comfortable", "roughly doubles
capacity", or any PASS.

### JLC capability is not the DVJ6B design rule

JLCPCB's current general capability table lists 0.20 mm minimum BGA pads, 0.09 mm local
pad-to-trace clearance on multilayer boards, and filled/plated-over via-in-pad with compatible
holes down to 0.15 mm. Its dedicated BGA guidance uses 0.25 mm BGA pads and recommends an outer
via-in-pad land of at least 0.35 mm around a filled plated through-hole of at least 0.15 mm.

Those are different capability and guidance contexts. **Headline minimum fabrication
capabilities are not K1 DVJ6B design rules.** No DVJ6B pad, via or traces-between-balls geometry is
frozen until the NXP land recommendation, assembly requirement, selected JLC BGA process and the
actual VAL-G3 pinmux/fanout are reconciled.

---

## VAL-G3 gains a real BGA escape gate

Ring arithmetic does not satisfy it. The gate takes the **actual NXP ball map for
`MIMXRT1062DVJ6B`** and the **completed single-sheet schematic**, then **derives** the best legal
pinmux jointly with orientation and floorplan — it does not consume a net-to-ball assignment
handed to it as immutable. It produces: complete physical ball map; fixed power and ground map;
fixed and recovery pin reservations; every K1 functional signal; all legal IOMUX alternatives per
flexible function; orientation candidates; peripheral-zone positions; candidate pinmux scored by
escape pressure; ball-ring classification after the pinmux choice; required ball-to-signal table;
ball-ring classification; escape direction per ball; power and ground ball map; via locations;
channel widths; conflicts; routing layers used; count of signals requiring inner-ring escape;
whether through-vias suffice; whether dog-bone escape suffices; any blind, buried or via-in-pad
requirement; and actual six-layer feasibility.

Only that evidence may set `6_LAYER_BGA_ESCAPE = PASS`.

If it fails, remedy order is: placement and orientation, then 0.8 mm package escape
optimisation, then six-layer routing strategy, then 8-layer escalation.
