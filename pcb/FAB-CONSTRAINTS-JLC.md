# K1-CORE-VAL-R0 — JLCPCB Fabrication-Constraints Register

```text
STATUS   = STUDY_INPUT (fab-capability register for the S1N-R1 placement study)
BINDING  = NO — records manufacturer capability, changes no authority
SOURCES  = 8 JLCPCB help articles, fetched 2026-08-29 (URLs per row)
SCOPE    = 155.0 × 38.0 × 1.60 mm, six-layer JLC06161H-3313 candidate, LFBGA-196 0.8 mm
RULE     = capability figures are JLC-published (CAPABILITY); their application to K1 is
           CALCULATED/CONDITIONAL until the pad geometry and stack order are frozen
```

## 1. BGA escape — the 0.8 mm dogbone assumption now has fab backing
Source: help/article/bga-design-guidelines---pcb-layout-recommendations-for-bga-packages

- JLC ≥4-layer capability: trace–trace 0.09 mm, trace–BGA-pad 0.10 mm, via-copper–pad
  0.10 mm, drill-to-pad spacing down to 0 mm; escape trace standard 0.09 mm (0.076 mm at
  cost). CAPABILITY.
- With a ~0.4 mm land on 0.8 mm pitch (land size itself still D-034-open): one 0.09 mm
  trace between lands needs ≈0.29 mm of the ≈0.40 mm gap → **one-trace-between-balls is
  feasible at standard capability** → outer TWO rings escape on L1. This upgrades D-029's
  caution with numbers, and it is the assumption the S1N-R1 escape study drew (J1/K1 on L1;
  J3/J4 dogboned). CALCULATED — conditional on the frozen land diameter.
- **Via-in-pad is only *forced* at 0.5 mm pitch** per JLC — the 0.8 mm RT1062 escapes with
  conventional dogbones. Filled via-in-pad spec if elected: drill ≥0.15 mm, pad ≥0.35 mm,
  epoxy or copper paste. **POFV (plated-over-filled-via) is free on 6–20 layer boards** —
  directly available to this 6-layer build. CAPABILITY; supports D-034 ("VIPPO ≠ HDI").

## 2. Via covering — binds the B-side owner-shadow
Source: help/article/pcb-via-covering

- Epoxy-filled & capped (and copper-paste) vias: holes ≤0.5 mm; required for
  double-sided via-in-pad; **resin filling free on ≥6-layer boards**. CAPABILITY.
- Ink plugging cannot serve vias <0.35 mm from pads — the B-side decap ring and the DN1
  GND-return vias near pads must use tenting (holes ≤0.4 mm recommended) or epoxy
  fill+cap, not ink plugs. BINDING on the §5 B-side scheme; the drawn decap-in-via-field
  strategy is compatible via POFV at zero cost.
- Untented vias need 0.2 mm copper clearance under HASL; ENIG relaxes it. Note for probe/TP
  vias in the service corridor.

## 3. Copper weight — worksheet numbers verified, one in K1's favour
Sources: help/article/jlcpcb-copper-weight · multi-layer-pcb-standard-laminated-structures

- Inner 0.5 oz finished ≈0.6 mil ≈ **15.2 µm — exactly the value the LED worksheet used**
  for the L3 trunk resistance. VERIFIED.
- Outer finished ≈1.6 mil ≈ **40 µm plated**, vs the worksheet's 35 µm — the trunk/branch
  drops are therefore slightly conservative (in K1's favour). Worksheet stands; note added.
- Min trace at 0.5–1 oz on ≥4 layers: 0.09 mm (3 mil at extra cost) — consistent with §1.

## 4. Inner-layer copper coverage — NEW constraint interaction (the real find)
Source: help/article/inner-layer-copper-coverage-pcb

- JLC: below **25 % coverage**, pour copper in empty areas; sparse inner copper causes
  prepreg thinning, thickness deviation and **warpage**.
- K1 tension: the NFC reserve (x 126–155, full height, ~19 % of board area) plus the 2.4 GHz
  aperture demand **copper-free zones on all six layers**, on a long, skinny 155 × 38 board
  whose warpage risk is highest along exactly that axis. Whole-board coverage ≥25 % is easy;
  the problem is **local** thinning/asymmetry at the copper-free east end.
- Disposition: pour L2–L5 GND everywhere outside the two RF keepouts (already the plan);
  the copper-free east end becomes a named **JLC DFM consultation item** — ask whether a
  ~27 mm all-layer copper-free end zone on a 155 mm 6-layer board holds thickness/warpage
  tolerance, and whether panel rails mitigate. The antenna field is NOT compromised to
  please the fab without that answer. UNPROVEN → added to the study's UNPROVEN list.

## 5. Back-drilling — available, deliberately not used
Source: help/article/back-drill-process

- JLC offers controlled-depth back-drilling (0.15 mm clearance to the adjacent kept layer;
  two file conventions). CAPABILITY.
- K1 decision with reason: **not required** — USB2 HS (480 Mbps) tolerance and the chosen
  structures (DN1 routed on L6 via full-length through-via = no stub; K1BR L1→L4 vias carry
  a ~0.75 mm stub at SPI speeds, harmless). Recorded so nobody resurrects it as cargo cult.

## 6. Solder-mask-defined pads — ordering path recorded for the D-034 decision
Source: help/article/how-to-order-boards-with-solder-mask-defined-pads

- SMD pads: mask intentionally overlaps copper by **≥3 mil (0.076 mm) on all sides**;
  ordered via PCB Remark ("U6 uses solder-mask-defined pads — do not adjust") plus
  "Confirm Production File = Yes". CAPABILITY.
- The NSMD-vs-SMD choice for the LFBGA-196 land pattern remains a **D-034 open item**
  (NXP land pattern + JLC process reconciled at G4); this register records *how* to order
  whichever wins, and that the mask-registration overlap must be budgeted into the land
  geometry if SMD is chosen.

## 7. Drill-file hygiene — G7 export gate item
Source: help/article/manually-adding-tool-list-for-a-drill-file

- Drill files must be self-contained: M48/% header, `T<n>C<dia>` tool list, units matching
  the coordinate file. Missing tool lists → CAM re-entry → misdrill/delay risk.
- Action: append to the G7 fabrication-output proof checklist next to the
  easyeda-verification-contract Gerber rules (explicit layer list): verify the exported
  drill file carries its own tool table before any order.

## 8. Stack confirmation
Source: help/article/multi-layer-pcb-standard-laminated-structures

- Exact JLC06161H-3313 numbers live on the order page (the repo's STACKUP-STATUS already
  carries the listed construction; the article confirms >200 structures + free ±20 %
  impedance testing, precision testing chargeable). The USB 90 Ω width/gap remains
  **UNPROVEN until the live calculator run against the selected structure** — unchanged
  from S1N-R1 §R1-g, now with the verification path named.

## Effect on S1N-R1 (summary)
Validated: escape-study dogbone assumptions (§1) · B-side via strategy at zero cost (§2) ·
LED worksheet copper numbers (§3, outer conservative). Newly UNPROVEN: east-end
coverage/warpage DFM question (§4). Decisions recorded with reasons: no back-drill (§5) ·
SMD-pad ordering path (§6) · drill self-containment gate (§7). No placement moved.
