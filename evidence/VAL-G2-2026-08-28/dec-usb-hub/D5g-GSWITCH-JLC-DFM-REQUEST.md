# D5g — GT-USB-7005A / C5250872 thickness and DFM request

Status: **REQUEST OUTSTANDING**. Not a fake letter. Not a bind.

Date: 2026-08-29.

The manufacturer drawing is on disk
(`datasheets/D5g-GSwitch-GT-USB-7005A-manufacturer-drawing.pdf`).
It is **SILENT** on recommended PCB thickness versus D-012 **1.60 mm**.
See `GSWITCH-7005A-MEASURED-EXTRACT.md`.

## Questions for G-Switch / 品赞 (drawing owner)

Send against **GT-USB-7005A** exactly (not the 7005X family page):

1. Recommended **PCB-thickness window** (min / max, mm). State whether
   **1.60 mm** is inside that window. Do not accept “Sinker 1.9”,
   “CH=0.4”, or “laminated board / 沉板” as that answer.
2. How the recommended **board cutout** relates to that thickness
   (does the body sit through a 1.60 mm stack, and by how much do the
   front and rear tabs / legs protrude on the bottom side?).
3. Count, size, and plating of every **shell / shield tab**, and the
   intended net (signal GND vs chassis).
4. Whether the recommended PCB layout on Rev A0 (2023-02-01) is the
   current land pattern, including slot vs plated-through requirements.
5. USB-IF TID for this MPN, or a written “none claimed”.

Keep the written reply in this folder. Until it exists this remains a
**process hold**, not a thickness reject. The mechanical bind is
geometric section (`H0-CLOSE.md`); this request does not reopen it.

## Questions for JLCPCB (process, not thickness authority)

JLC 2026-08-29 catalogue reading: Extended, SMT Assembly, **Assembly
Difficulty High**. That is a process hold, not a thickness waiver.

1. Will JLC assemble **C5250872** on a **1.60 mm / six-layer**
   `JLC06161H-3313`-class stack with the manufacturer cutout and hybrid
   front-TH / rear-SMT lands?
2. Slot / edge-cutout / keep-out rules for that cutout on this stack.
3. Whether “Assembly Difficulty High” forbids Standard assembly or only
   names a fixture / yield risk.

A JLC “we can assemble it” note still does **not** replace G-Switch’s
thickness window.

## What this file is not

It is not a manufacturer letter. It is not a JLC DFM approval. It does
not bind the MPN. It does not change D-012.
