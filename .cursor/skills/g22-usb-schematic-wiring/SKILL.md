---
name: g22-usb-schematic-wiring
description: >-
  USB2422 / J1 / GT-USB-7005A / Type-C keepouts for K1-CORE-VAL-R0
  GREENFIELD. Prevents stacked Type-C, pin-column 3V3 shorts, crystal/GND
  merges, and MCP symbol moves. D-052: HOLD and canonical are ARCHIVE — do
  not wire them. Use before any greenfield USB EasyEDA write.
---

# USB schematic wiring (greenfield knowledge)

Read `docs/agent/SESSION-CANON-2026-08-30-G22-USB-WIRING.md` before the first
USB wire on **GREENFIELD**. EasyEDA execution canon still applies.

**D-052 terminated HOLD / G2.2 / canonical schematic repair.** These UUIDs
are ARCHIVE / DO NOT MUTATE:

- product `64325d0e55e0435abd018defb0089a9b`
- HOLD `55ed9ee948734a0e903f37744b51f3b8`
- G2.1 `dcd7e3cab2a24b9aa6e531d2b62e1b6f`

The only implementation canvas is `K1-Core-VAL-R0-GREENFIELD` (UUID not
allocated until the blank project exists). Component #1 waits on
`architecture/GREENFIELD-BUILD-SPEC.md` OPEN items. This skill is keepout
knowledge for the USB **block**, not a T1–T6 repair queue.

## Hard stops

Stop before another `add_schematic_wire` if any is true:

1. The focused EasyEDA project is an archived UUID (HOLD, canonical, G2.1, hub).
2. Two Type-C origins are within **80** units.
3. Any USB2422 west-column signal (pins 2–8, 10–12) is on **`3V3`**.
4. USB2422 pin 21 is **`GND`**, or RBIAS shares a net with XTALIN.
5. The mutation gate is not `READY` on the **greenfield** lane.
6. You planned to `modify_schematic_component` x/y (wires stay behind).
7. You are about to delete a wire id returned by `add_schematic_wire` that
   belongs to `3V3` or `GND` without a pre/post segment census.

`J1-USB4105-RETIRED` is **deleted, not reinstated**. Do not place a second
Type-C on the greenfield sheet.

## `add_schematic_wire` is a net-join, not a pen

The API returns the **whole merged net**, not the polyline you drew. EasyEDA
auto-extends onto a pin column. A vertical within **40** units of the hub
west pins will short DN pairs onto 3V3.

Never:

- run a vertical parallel to a pin column inside the keepout
- share an east-side x between RBIAS and XTALIN
- route along a crystal pin row
- polyline through a Type-C or QFN body

Y-sign: dump the live greenfield source. Do not assume HOLD negative-Y
geometry. MCP pin list is host +Y; negate if the source is negative Y.

## One visual transaction

Dump source → inspect **that symbol’s pin nets** → one short wire set →
screenshot the hub or J1, not the whole sheet → USB + drawing checkers →
**diff this transaction’s errors vs pre**. Overall USB red is not a licence
to ignore **new** shorts. A USB fault is a USB repair, not a whole-board
snapshot restore.

## Checkers (mandatory after every USB visual transaction)

```text
python3 harness/check_g22_usb_hub.py <dump.json>
python3 harness/check_g22_schematic_drawing.py <dump.json>
python3 harness/check_g22_pwr1_ilm.py <dump.json>
```

Do not stamp `JLC-SCH-READY`. Do not `set_document_source` on archived
projects. Do not snapshot-restore HOLD.

## J1 pin map (GT-USB-7005A)

Historical live MCP 2026-08-30 on HOLD at origin 150,−4120. **Re-measure on
greenfield** before the first wire. Do not reconstruct from memory.

- A-column `sx=−40`, A1 `sy=0`, pitch `−32` (HOLD origin 150,−4120)
- B-column `sx=240`
- Shields `sy=−420`, S1 `sx=20`, step 50
- SuperSpeed and SBU stay NC
- `connect_schematic_pins_to_nets` is **not** vertex evidence

Table: `J1_PINS` in `harness/g22_usb_hub.py`.

## Do not move

Never MCP-move a connected Type-C, eFuse, or USB2422. Native drag only.
ILM ohmic identity 1.24 kΩ / `RNCF0402BTC1K24` is knowledge, not a copied
wire. Pin 9 must not land on USB D+.

## Dark canvas is not DNP

Selection hatch and QFN fill are not a deprecated sub-sheet. DNP is
`Add into BOM=no`. Long OCS/EN rectangles are live nets, not a ghost sheet.

## Identity

EasyEDA restamps DOCHEAD every save. Semantic census is identity
(components, bindings, pin-nets). A hash may fingerprint that state. The
hash is not the design. `3165690:5aad2e78` is a recovery payload, not live
identity.
