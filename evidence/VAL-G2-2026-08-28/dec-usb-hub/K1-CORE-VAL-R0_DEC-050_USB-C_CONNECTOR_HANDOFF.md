# K1-CORE-VAL-R0 — USB-C receptacle decision / Type-C power-domain execution handoff

**Programme priority:** BLOCKING / load-bearing.  
**Date:** 2026-08-29  
**Applies to:** DEC-USB-HUB / D-049 / Type-C inlet / USB2422 / F6-B validity rails / G2.1 hub graph.  
**Do not freeze or reconstruct G2.2 until this handoff is dispositioned.**

---

## 0. Executive ruling

The connector decision cannot be treated as an isolated BOM choice because the preferred Hirose `CX70M-24P1` is a **mid-mount connector whose manufacturer specifies 0.8 mm maximum PCB thickness**, while K1-CORE-VAL-R0 currently has a **1.60 mm / six-layer** baseline.

### Current decision matrix

| Candidate | Electrical evidence | Mechanical compatibility with current 1.60 mm K1 | Lifecycle / compliance evidence | Current ruling |
|---|---|---|---|---|
| **Hirose CX70M-24P1 / C778726** | **Strong:** Hirose 5 A total rating; 1.25 A max per power contact; 40 mΩ max contact R; 10,000 cycles | **RED as direct mount on current board:** Hirose says recommended PCB thickness **0.8 mm max** | USB-IF TID **5,200,000,077**; Hirose currently marks part **Not Recommended For New Design** | **Preferred by Captain, but CONDITIONAL. Do not bind to 1.60 mm board. Requires explicit 0.8 mm board-thickness/stack decision or rejection.** |
| **HOAUC HYCW78-USBC24-140B / C3034184** | **Medium:** JLC/LCSC catalog claims 5 A and 10,000 cycles; manufacturer-controlled per-contact/current-test evidence not yet in hand | **AMBER:** recessed/sink-mount geometry is attractive, but exact 1.60 mm PCB-thickness compatibility must be proven from the exact manufacturer drawing/sample; “sink 1.4” is a recess dimension, not proof of PCB thickness | USB-IF TID not publicly established in this review; JLC says assembly fixture required | **Best current recessed candidate for a 1.60 mm VAL board only after exact drawing + sample + DFM validation. Production remains held pending stronger evidence.** |
| **Hirose CX90B2-24P** | Strong: Hirose 5 A, 10,000 cycles, 40 mΩ max | **GREEN:** manufacturer says 1.6 mm max | Current Hirose family; authoritative drawings/guides available | **Control/fallback if Hirose quality is required but recessed/mid-mount CX70M geometry cannot be retained. Not the Captain’s preferred shape.** |

**Do not silently solve the CX70M mismatch by changing the whole board to 0.8 mm.** That would supersede the current 1.60 mm / six-layer baseline and invalidates the current stack, impedance geometry, stiffness assumptions, connector-load mechanics, enclosure datums and aspects of the power/layout study.

---

# 1. CX70M-24P1 — resolved current rating

The CX70M current question is closed from Hirose authority:

- Part: `CX70M-24P1`
- Positions: 24
- Type: USB Type-C receptacle
- Mount: right-angle **mid-mount**, hybrid SMT + THR
- Rated current: **5.0 A**
- Current distribution: **1.25 A max per power contact**, with the 5 A path obtained by using the parallel VBUS and GND contacts as intended
- Other signal contacts: 0.25 A class
- Contact resistance: **40 mΩ max initial**
- Mating durability: **10,000 cycles**
- Temperature: current Hirose page **-40 °C to +105 °C**
- USB data capability: 5 Gbit/s (vastly above K1’s USB2 need)
- USB-IF TID: **5,200,000,077**
- Recommended PCB thickness: **0.8 mm max**
- Current Hirose lifecycle flag: **Not Recommended For New Design (NRND)**

For K1’s present **non-PD 5 V Type-C** architecture, the connector’s 5 A rating is *headroom*, not permission to draw 5 A. Source current still comes from CC advertisement:
- USB2 Default: 500 mA
- Type-C 1.5 A
- Type-C 3.0 A

K1 must remain at or below the source advertisement and must throttle if the advertisement changes. A future >3 A path requires USB-PD/cable rules and is a separate architecture decision.

At 3 A, ideal equal sharing is ~0.75 A per VBUS contact and ~0.75 A per GND contact, comfortably below the Hirose per-contact 1.25 A figure. Layout must nevertheless use all four VBUS and all four ground contacts; do not rely on ideal current sharing.

---

# 2. CX70M-24P1 — hard blockers / steelman

## 2.1 0.8 mm PCB requirement

Hirose explicitly states **Recommended PCB Thickness: 0.8 mm Max**.

Current K1 authority is 1.60 mm / six layers (`JLC06161H-3313` preferred candidate). Therefore:

**CX70M direct-mounted to the existing 1.60 mm board is NOT AUTHORISED.**

There are only three honest paths:

### CX-PATH-A — whole K1 board becomes 0.8 mm
Allowed only after a dedicated board-thickness/stack study proves:
- JLC will fabricate the required six-layer 0.8 mm stack with the selected copper weights;
- actual JLC controlled-impedance stack is defined and USB geometry is recalculated;
- RT1062 BGA escape remains viable;
- high-current copper/via capacity remains acceptable;
- insertion/extraction load does not flex the board unacceptably;
- mounting / enclosure support is revised for the thinner board;
- board flatness / assembly / reflow risks are acceptable;
- acoustic/mechanical assumptions remain acceptable.

Hirose specifies insertion forces up to ~20 N and extraction up to ~20 N. On a thinner validation board, connector-area mechanical support must be treated deliberately. This is an engineering inference from connector force + board thickness, not a Hirose failure claim.

### CX-PATH-B — local stepped/thinned PCB tongue
**NOT AUTHORISED by assumption.**

A “blind slot” or local mechanical recess is not automatically a valid way to turn a six-layer 1.6 mm board into a 0.8 mm connector tongue. Local thinning can cut into internal copper/dielectrics and change the stack. Use this only if JLC provides an explicit manufacturable stepped-thickness process/DFM ruling for the actual six-layer stack.

### CX-PATH-C — separate 0.8 mm USB daughterboard
Technically possible, but poor default for VAL-R0 because it adds:
- a high-current 5 V interconnect,
- USB2 interconnect,
- additional mechanical connector,
- more failure modes,
- more board area and assembly.

Do not choose this merely to preserve CX70M unless the product mechanical architecture independently wants a USB daughterboard.

## 2.2 NRND lifecycle

Hirose currently marks `CX70M-24P1` **Not Recommended For New Design**.

This is not “obsolete” and current distributor/JLC stock exists, but it is a real production-life warning.

If Captain deliberately chooses CX70M for **VAL-R0 only**, record:
`VAL_ACCEPTED_NRND / PRODUCTION_SUCCESSOR_REQUIRED`.

Do not silently turn it into a production freeze.

---

# 3. HYCW78-USBC24-140B — current evidence and holds

Known current catalog evidence:
- MPN `HYCW78-USBC24-140B`
- LCSC/JLC `C3034184`
- 24-position Type-C receptacle
- recessed/sink mount
- JLC/LCSC catalog claim: **5 A**
- JLC catalog claim: **10,000 cycles**
- operating range in JLC catalog: **-40 °C to +80 °C**
- JLC body/dimension metadata includes **9.65 mm**
- JLC marks it Extended
- JLC explicitly says **a PCB assembly fixture is needed to protect/support this part during assembly**

### Important evidence limitations

`沉板1.4` / “sink board 1.4” means approximately a **1.4 mm recessed/sink geometry**. It is **not proof that the PCB must or may be 1.4 mm thick**.

The exact HYC drawing must be used to prove:
- PCB thickness window;
- cutout geometry;
- shell THR/DIP geometry;
- SMT pad geometry;
- connector Z datum;
- board-edge datum;
- insertion axis;
- keepouts.

The JLC/LCSC **5 A** field is useful evidence for a VAL candidate, but production freeze requires a manufacturer-controlled spec/test report defining at minimum:
- total VBUS current;
- per-contact current if specified;
- temperature-rise conditions;
- contact resistance;
- mating-cycle test conditions.

Public USB-IF TID evidence comparable to Hirose was **not established in this review**. Do not write “no TID exists”; write:
`USB_IF_TID = UNPROVEN / REQUEST_MANUFACTURER_EVIDENCE`.

If future USB-IF compliance is a product requirement, this is a material risk.

### HYCW78 approval gate for VAL-R0

Do not bind `J1-PWR1` to HYCW78 until all are YES:
- exact manufacturer drawing obtained and archived;
- drawing proves compatibility with the selected K1 board thickness;
- exact footprint independently redrawn/verified against drawing;
- one physical sample measured against drawing;
- JLC DFM confirms assembly/cutout/fixture;
- current claim evidence accepted as VAL-grade;
- USB-IF TID either proven or explicitly held as production-only;
- connector STEP checked against enclosure/rear-cover insertion axis.

---

# 4. Common electrical pin contract — applies regardless of CX70M vs HYCW78

K1 uses the 24-pin receptacle only as **USB2 + Type-C 5 V sink**. SuperSpeed and alternate-mode pins are unused.

The executing agent shall create/verify the symbol from an authoritative connector drawing and must not trust an EasyEDA cached symbol blindly.

| Receptacle contact family | K1 action |
|---|---|
| A4, A9, B4, B9 — VBUS | all tied into `5V_USB`; no missing power contact |
| A1, A12, B1, B12 — GND | all tied to GND with low-inductance plane entry |
| A6 + B6 — D+ | tied together on connector side, then low-C upstream USB2 ESD, then `USB_DP_UP` to USB2422 |
| A7 + B7 — D− | tied together on connector side, then low-C upstream USB2 ESD, then `USB_DM_UP` to USB2422 |
| A5 — CC1 | independent `USB_CC1`: 5.1 kΩ Rd + source-current sense/protection |
| B5 — CC2 | independent `USB_CC2`: 5.1 kΩ Rd + source-current sense/protection |
| SBU1/SBU2 | NC for this design |
| all SSTX/SSRX contacts | NC for this design; do not route “for future” |
| shell / mechanical shield tabs | use current K1 shield strategy; low-inductance chassis/GND-style bond + stitching, not signal-return neck-down |

Flip-ability is mandatory: both A/B USB2 contacts and both CC pins must be represented correctly.

---

# 5. Protection architecture that must be evaluated before D-049/D-050 freeze

The old “D+/D− TVS only” mindset is insufficient for a 24-pin Type-C inlet.

The connector exposes VBUS, D+/D−, CC1/CC2, unused SBU/SuperSpeed contacts and shell.

### D+/D−
Retain a connector-side **low-capacitance IEC ESD array** directly between J1 and USB2422 upstream. The USB2422 on-chip ESD does not replace system-level connector protection.

### CC1/CC2
Create a named **CC-PROTECTION decision**. Both CC pins are externally exposed and feed Rd plus analogue capability sensing.

At minimum, assess:
- IEC ESD on CC1/CC2;
- accidental short-to-VBUS / noncompliant-source overvoltage risk;
- the voltage tolerance of every resistor/ADC/protection component behind CC;
- whether a USB-C-specific CC protector (for example a short-to-VBUS/ESD device class such as TI TPD2S300/TPD4S201) is warranted.

Do **not** add a CC protector blindly: confirm its series resistance/leakage does not corrupt Rp-current-advertisement sensing.

Unused SBU and SuperSpeed pins may remain NC because K1 does not route them; do not populate unnecessary high-speed protection on unconnected interfaces.

### VBUS
Re-derive the complete inlet as one system:
`J1 VBUS → VBUS TVS/protection → eFuse → shunt/INA → 5V_SYS`

Also in parallel from true `5V_USB`:
`VBUS_DET divider + deliberate discharge`

The hub / F6-B programme must not proceed until:
- upstream VBUS capacitance is within USB2422 / USB-C limits;
- unplug discharge timing is proven;
- the eFuse OVLO is re-derived relative to the 5.5 V limits of RT USB VBUS / TPS2052B;
- no “5V_PROTECTED is safe” claim survives if its OVLO remains ~6.01 V.

---

# 6. Current draw / Type-C power contract

The receptacle rating and K1 load entitlement are separate.

Even with a 5 A connector:
- source Rp Default → K1 uses only Default USB power;
- source Rp 1.5 A → K1 ≤1.5 A;
- source Rp 3.0 A → K1 ≤3.0 A;
- >3 A is not available merely because the connector says 5 A.

CC1/CC2 source-capability sensing + throttle remains mandatory.

The USB2422 adds roughly 70 mA typical / 89 mA max to the 3.3 V budget and must be included in the full inlet-power envelope.

Before electrical freeze, compare:
- 5 V Type-C-only solution (Default / 1.5 / 3 A + throttle)
- USB-PD sink alternative

Do not add PD merely for elegance. The comparison exists to prove that 5 V / 3 A is sufficient or to expose that it is not.

Also compute the **pre-firmware source-classification startup current**. LED branches, mic, NFC TX, etc. must have safe reset defaults so a Default-current source is not collapsed before firmware can throttle.

---

# 7. Mechanical / PCB-layout constraints to hand to JLC later

For either connector:
- all four VBUS contacts must fan into a low-resistance copper entry, not a thin daisy-chain;
- all four signal GND contacts land immediately into ground/reference with local vias;
- shell tabs take insertion/extraction load into the PCB/enclosure;
- place mounting/support geometry so connector insertion force is not carried by a long flexible PCB cantilever;
- D+/D− ESD sits immediately behind J1; route `J1 → ESD → USB2422 UP` as one compact USB2 path;
- CC protection / Rd / sensing sits immediately behind CC pins;
- VBUS TVS/eFuse entry is physically short and broad;
- connector cutout, shell, solder tabs, keepout and rear-cover aperture come from the manufacturer drawing/STEP, never from a generic EasyEDA model.

For HYCW78 specifically, include JLC’s required assembly fixture in manufacturing notes.

---

# 8. Required change to the existing DEC-USB-HUB plan

The current hub plan explicitly treats the connector as a separate later decision and forbids changing J1’s MPN inside D-049. Captain has now moved that decision into the blocking programme.

Do **not** collapse architecture and part lifecycle into one overloaded decision row. Add:

`D-050 — K1-CORE-VAL-R0 Type-C receptacle`

and make D-049 depend on D-050 reaching a usable state.

D-049 should say:
`J1-PWR1 exact receptacle is governed by D-050. Hub architecture may not reach official electrical freeze until D-050 has resolved PCB-thickness/mechanical compatibility and J1 pin/footprint authority.`

### Proposed D-050 state today

```text
D-050 = OPEN / CONNECTOR-PHYSICS BLOCK

PREFERENCE:
    1. CX70M-24P1 — Captain preference
    2. HYCW78-USBC24-140B — recessed fallback

FACT:
    CX70M-24P1 = 5 A, 10k cycles, TID 5,200,000,077, 0.8 mm PCB max, NRND.
    Current K1 baseline = 1.60 mm / 6 layers.

RULING:
    CX70M cannot be bound to the current 1.60 mm board.
    Captain must either:
      CX-A) authorise a full 0.8 mm six-layer stack/mechanics study; or
      CX-B) keep 1.60 mm and move to HYCW78 subject to HYC gates; or
      CX-C) keep 1.60 mm and permit a current 1.6-mm Hirose form factor such as CX90B2 if enclosure geometry can change.

HYCW78:
    provisional VAL candidate only until exact PCB-thickness / drawing / sample / JLC DFM is green.
```

---

# 9. Executing-agent sequence — do not skip

1. Patch DEC-USB-HUB so D-049 final ratification happens only after physics GREEN and add D-050 connector dependency.
2. Archive official Hirose CX70M page, 2D drawing, spec sheet, design guide, STEP and CX catalog/TID.
3. Archive exact HYCW78 datasheet/drawing available from JLC/LCSC and request manufacturer/JLC clarification for PCB thickness, 5 A test basis and USB-IF TID.
4. Run `CONNECTOR-COMPATIBILITY.md`: CX70M 0.8-vs-current-1.6 study; HYC exact-thickness study; CX90B2 control.
5. If CX70M remains preferred, run a **whole-board 0.8 mm / six-layer** feasibility gate before changing any schematic MPN. No local-thinning workaround without JLC written DFM.
6. If HYCW78 is selected for 1.6 mm, obtain sample + JLC DFM + independently verified footprint before binding J1.
7. Add common J1 pin contract from §4; delete any legacy connector symbol that omits duplicated VBUS/GND/D+/D− contacts.
8. Add a CC-protection evaluation and close ESD/short-to-VBUS risk before electrical freeze.
9. Re-derive raw `5V_USB` capacitance/discharge, TVS, eFuse OVLO/ILIM, shunt/INA and F6-B validity source as one power-domain contract.
10. Re-run Type-C Default/1.5A/3A delivered-power budget + startup budget + USB-PD steelman.
11. Only after connector + power + hub GO/NO-GO is GREEN: ratify D-049/D-050, mutate disposable EasyEDA graph, run item-level ERC, freeze hub graph, then reconstruct G2.2 once.

---

# 10. Source authority used for this handoff

Hirose:
- Product page: https://www.hirose.com/en/product/p/CL0480-0304-0-00
- CX family/catalog: https://www.hirose.com/en/product/pr/CX/
- CX70M official catalog/spec/drawing/design guide linked from product page
- CX90B2 control: https://www.hirose.com/en/product/p/CL0480-0889-0-00

JLC/LCSC:
- CX70M / C778726: https://jlcpcb.com/partdetail/HRS_Hirose-CX70M24P1/C778726
- HYCW78 / C3034184: https://jlcpcb.com/partdetail/HOAUC-HYCW78_USBC24140B/C3034184
- https://www.lcsc.com/product-detail/C3034184.html

USB / protection:
- USB Type-C current advertisement: USB Type-C Cable and Connector Specification
- TI ESD and Surge Protection for USB Interfaces, SLVAF82
- TI Type-C CC/SBU short-to-VBUS protection literature

K1:
- Current board baseline remains 1.60 mm / six layers / JLC06161H-3313 preferred candidate until a Captain decision supersedes it.
