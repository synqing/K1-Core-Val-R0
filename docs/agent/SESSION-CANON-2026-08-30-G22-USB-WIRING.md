# SESSION CANON — 2026-08-30 G2.2 USB wiring

```text
STATUS     = KNOWLEDGE_ONLY — D-052 TERMINATED HOLD/G2.2 WRITES
LANE       = HOLD 55ed9ee948734a0e903f37744b51f3b8  (ARCHIVE / DO NOT MUTATE)
PAGE       = 1435cb46f39e48c8a8aadbb84ca81603
CANONICAL  = 64325d0e55e0435abd018defb0089a9b  (ARCHIVE / DO NOT MUTATE)
GREENFIELD = K1-Core-VAL-R0-GREENFIELD  (UUID not allocated; only future canvas)
JLC-SCH-READY = NOT STAMPED — attaches to GREENFIELD, not this sheet
```

This is the durable record of what this session discovered by wrecking the
HOLD sheet. Prose here is the map. **It is not a licence to mutate HOLD.**
Apply the keepouts when the greenfield USB block is drawn.

The executable controls are:

- `harness/g22_usb_hub.py` (electrical)
- `harness/g22_schematic_drawing.py` (drawing)
- `.cursor/skills/g22-usb-schematic-wiring/SKILL.md`
- `docs/agent/EASYEDA-EXECUTION-CANON.md` K1E-069…K1E-077 and F-23…F-32

A future agent that wires USB on GREENFIELD without loading the skill and running
both checkers is repeating this session. Wiring USB on HOLD is forbidden (D-052).

---

## What happened, in plain English

T1 wired the live Type-C (GT-USB-7005A / `J1-PWR1`) onto the correct nets.
That electrical step was real. The drawing was already two USB-C symbols
occupying the same pin field, so the new wires landed in a blob.

T2 then tried to wire USB2422 support (3V3, CRFILT, PLLFILT, RBIAS, crystal).
EasyEDA merged the new polylines into existing nets. Downstream USB pairs
became 3V3. Crystal-out became GND. RBIAS became XTALIN. The ILM repair on U1
did not regress. Captain stopped T3–T6. Nothing was snapshot-restored.

The “blacked out” region on the canvas was selection hatch plus EasyEDA’s
dark IC fill, not a deprecated sub-sheet. The rectangular wiring under the
hub is live `USB_OCS1_N` / `USB_OCS2_N` drawn as a 1 200-unit picture frame.

---

## Map versus territory (this session’s maps that lied)

| Map trusted | Territory | Control |
| --- | --- | --- |
| MCP `add_schematic_wire` `ok:true` | Net merge; returned `line` is the **whole net**, not the new dogleg | Semantic pin nets + screenshot before next write |
| `delete_schematic_wire` `deleted:true` | Inventory still had the id (F34); source later dropped some stubs anyway | Re-query source ids; do not trust the boolean |
| `list_schematic_component_pins` | No `net` field. `noConnected` is NC intent, not net membership | Vertex nets from V3 source |
| USB checker `j1_wired=18` after T1 | Drawing still two stacked Type-Cs | Drawing checker: origin distance |
| Domain boxes / “readable G2.2” | G2.1 graph dumped into boxes; long OCS loops; retired USB4105 kept | One Type-C; local stubs; no picture frames |
| EasyEDA dark hatch = DNP | Selection overlay, or QFN body fill | Click empty canvas; DNP is `Add into BOM=no` |
| `3165690:5aad2e78` as live identity | Recovery payload only; live restamps DOCHEAD constantly | Body SHA for electrical identity; restamp before `begin` |
| Pin-list reconstruction ±20 | Missed GT-USB-7005A live pin ends | MCP pin ends, host Y negated, tol 0 |
| `connect_schematic_pins_to_nets` | Reported 0 committed; geometric wires still landed | Ignore connect as vertex evidence |
| MCP `modify_schematic_component` x/y | Symbol moves, wires stay, nets break | Native drag only; never MCP-move |

---

## Systems: the loop that ate the evening

```text
slow MCP + pressure to finish T1–T6
  → one fat wire batch (T2)
  → EasyEDA auto-connects to pin column / shares a corridor
  → silent net merge
  → USB checker still “red as expected until T6”
  → agent continues
  → larger hidden short
```

Break the loop at **Observe after one visually atomic wire set**, not after
the convenient batch. T2’s six failures in one batch were the delay-of-
observation archetype (EASYEDA-EXECUTION-CANON). Captain STOP was the only
balancing loop that fired in time.

**Fixes that fail:** west dogleg at x=200 “to avoid the pin column” still
auto-extended horizontals onto pins 2–5 (30 units away). Distance 30 ≠ keepout.

**Shifting the burden:** USB checker staying red “until T6” was used to
excuse not inspecting T2’s new errors. New errors versus the pre-transaction
error set are the gate, not the overall red.

**Success to the successful:** T1 geometric wires “worked” (j1_wired=18), so
the same `add_schematic_wire` style was applied to U20, a pin-pitch-10
device. J1 pitch is 32. U20 is not J1.

---

## OODA failure

| Phase | What we did | What we should have done |
| --- | --- | --- |
| Observe | Batch result 6 ok / 6 fail; pin-list without nets | Dump source + USB checker + hub screenshot **before** another add |
| Orient | “T2 support wires; USB is allowed to stay red” | Diff **this transaction’s** USB errors vs pre-T2 |
| Decide | Retry / continue T3–T6 (Captain had authorised continuous T2–T6) | STOP on new DN=3V3 / XTALOUT=GND |
| Act | Further planning while IN_FLIGHT | Close T2 REJECTED or repair in-scope; no T3 |

Captain’s “do not stop merely because USB stays red” was correct for
**pre-existing** T3–T6 gaps. It is not a licence to ignore **new** shorts.

---

## Steel-man (why the T2 batch was not irrational)

U20 support is one circuit block. One wire-stage transaction is canon.
CRFILT/PLLFILT/RBIAS required lifting GND stubs first. Batching delete-then-
add in one `mcp_batch` is the fast path (F106). Pin 9 was already 3V3, so a
west dogleg to pin 9 looked like the least-bad 3V3 path. Crystal caps were
already electrically correct. Straps were not to be moved.

That strongest case still fails: EasyEDA **joins any vertex within snap
range to the pin column**, `add_schematic_wire` **renames consumed nets**,
and a 12-segment return value is the **merged 3V3 rail**, not a new wire
you can delete safely. The map (orthogonal dogleg) was not the territory
(auto-filled pin shorts).

---

## Red team: how the next agent will repeat this

1. Trust `ok:true` and skip the hub screenshot because “semantic read-back
   will catch it” — pin-list has no nets; USB overall-red hides new errors.
2. MCP-move the retired Type-C to tidy — wires stay, ILM/5V_USB geometry
   tears.
3. Delete the new 3V3 primitive id `1682def94aa38c4a` to “undo T2” — that
   id **is** the merged 3V3 net (12 segs including pin 9). Deleting it
   depowers the hub.
4. Treat EasyEDA hatch as DNP and delete U1/U20 with the Type-C stack.
5. Snapshot-restore T2 against Captain “do not revert” — or the inverse:
   refuse to park USB4105 because “keep retired inert” was heard as
   “keep it on top of J1-PWR1”.
6. Run T3 on a sheet whose DN pairs are 3V3.
7. Stamp progress as JLC-SCH-READY because T1 closed.

---

## Failure inventory (trial and error)

| ID | Failure | Resolved? | Lasting rule |
| --- | --- | --- | --- |
| S-USB-01 | J1 pin table used sx=−35 / A1 sy=+100 | Live MCP: sx=−40, A1 sy=0, pitch −32 | `J1_PINS` in `g22_usb_hub.py`; never reconstruct Type-C from memory |
| S-USB-02 | `connect_schematic_pins_to_nets` 0 committed | Geometric wires sufficient | Not vertex evidence |
| S-USB-03 | First CC1 polyline through symbol / retired CC1 | North tap (245,−3995) worked | No polyline through a symbol body |
| S-USB-04 | Two Type-C origins 35,25 apart | T1 closed electrically; drawing still stacked | Drawing checker radius 80; delete `e339`; do not reinstate |
| S-USB-05 | C1/C2 on J1 pin field | Not yet moved | Caps on 5V island, x≥430 |
| S-USB-06 | T2 west 3V3 dogleg at x=200 | Pins 2–5 → 3V3 | Keepout **≥40** from pin column; no vertical parallel to it |
| S-USB-07 | T2 RBIAS and XTALIN shared x=590 | Pin 24 = USB_XTALIN | Distinct east corridors; RBIAS only x≥600 at y=−850 |
| S-USB-08 | Y3 OSC2 run along y=−745 through pin 4 | USB_XTALOUT swallowed into GND | Never route along a crystal pin row |
| S-USB-09 | PLLFILT polyline merged to x=1570 | Named USB_PLLFILT ate foreign copper | After add, longest new net segs; if >> requested, STOP |
| S-USB-10 | `delete_schematic_wire` F34 | Some stubs gone in source anyway | Source id absence is the proof |
| S-USB-11 | EasyEDA restamps DOCHEAD every save | `3378125:03e680f8` → `de69d05b` same body | Quarantine + reconcile; never require recovery hash as live id |
| S-USB-12 | `get_document_source` hangs after save | CDP `dump-hold-source.mjs` | HOLD dump script, not MCP |
| S-USB-13 | `zoomToFit` is not a function | `hold_parent_shot.mjs` `xy` | Never whole-sheet 5% view as evidence |
| S-USB-14 | OCS1/OCS2 1195-unit frame at y=−1500 | Misread as deprecated sheet | Picture-frame checker; local stub + label |
| S-USB-15 | Dark hatch = “deprecated” | Selection / symbol fill | DNP = BOM attr; retired = `J1-USB4105-RETIRED` only |
| S-USB-16 | Continuous T2–T6 GO used as “ignore new fails” | Captain STOP | Diff error set per transaction |
| S-USB-17 | `modify_schematic_component` coordinates | Wires do not follow (2026-07-17) | Native drag or delete+replace |
| S-USB-18 | Returned wire id looks “new” | May be renamed whole-net | Never delete a power-net id from an add result without segment census vs pre |

---

## Insights that survive this sheet

1. **G2.2 “readable” is not a licence to wire into G2.1 debris.** One Type-C.
   USB4105 does not come back.
2. **U20 pin pitch is 10.** A dogleg that would be safe on J1 (pitch 32) is
   a short on U20.
3. **y=−850 is both pin 1 and pin 24.** Horizontal runs on that Y through
   the body are forbidden.
4. **ILM and USB are different Y-bands.** T2 may not move U1/R1. Tidy of
   J1 may not move U1/R1.
5. **`add_schematic_wire` is a net-join, not a pen.** If the polyline shares
   a vertex with a foreign net, that net **becomes** the named net you passed.
6. **Overall USB FAIL is not a transaction FAIL.** Pre-T2 errors vs post
   errors is the progression gate.
7. Recovery hash `3165690:5aad2e78` is a payload. Live identity is whatever
   EasyEDA last saved. Body SHA detects restamp vs electrical change.

---

## Do not delete when “cleaning the group”

KEEP: U1-PWR1 `e504`, R1-PWR1 `e426`, U2-PWR1, RSH1, U20-USB `e154001`,
box-2 bucks. DELETE: `J1-USB4105-RETIRED` `e339`. Replace, do not MCP-move,
J1-PWR1 / D1 / RUSB if the island is rebuilt.

---

## Checkers a future agent must run after every USB visual transaction

```text
python3 harness/check_g22_usb_hub.py <dump.json>
python3 harness/check_g22_schematic_drawing.py <dump.json>
python3 harness/check_g22_pwr1_ilm.py <dump.json>
```

New T2-class errors (DN on 3V3, XTALOUT on GND, RBIAS=XTALIN, Type-C stack,
OCS picture-frame) are a STOP, even if the USB checker was already red.

---

## Related

- T1 close / T2 partial: `evidence/VAL-G2-2026-08-28/g22-hold-lane/`
- Reinstatement drawing: `G2.2-USB-REINSTATE.html`
- PWR1 tidy: `G2.2-PWR1-TIDY-PLAN.html`
- Pre-audit: `evidence/VAL-G2-2026-08-28/G2.2-USB-HUB-J1-PRE-AUDIT.md`
- MCP move scar: EasyEDA-MCP `docs/SESSION-CANON-2026-07-17-map-not-territory.md`
