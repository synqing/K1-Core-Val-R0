# K1-specific engineering review — Voice PE candidates

Date: 2026-08-28. Voice PE surfaces questions. K1 contract + vendor source answers them.

## 1. Test access (adopted)

A validation mule needs **observability**, not a dedicated TP symbol on every net.

Legitimate mechanisms: dedicated probe/pogo pad; fitted debug-connector pin; service-header pin;
0R / series-termination pad; option-jumper pad; accessible IC test node.

**Dedicated TP preferred:** rails; POR/reset; boot straps; power-good / fault / INA alert;
slow ownership/select; useful low-speed control.

**Access required, no automatic stub TP:** K1BR clock/data; PDM; audio clocks; SWD; UART.
The 10-pin Cortex header **is** the SWD interface if fitted (`debug_connector` in the retired
plan; RTDBG on the live sheet).

**No casual TP stub:** USB D+/D−; NFC RF/matching; other impedance-sensitive lines.

K1 basis: `contracts/debug-fabric.md` (independent physical doors), power architecture
(named rails), audio/mic contracts (clock isolation and PDM XOR already imply pads).

## 2. USB shield (candidate, not frozen)

`contracts/usb-interface.md` freezes S3 ownership, 90 Ω, ESD/SI/return path. It does **not**
freeze a shell-bond topology.

```text
USB_SHIELD separate net = CANDIDATE / VALIDATION_DESIRABLE
bond menu = hard bond | R||C hybrid | float
1 MΩ / 1 nF = Voice PE precedent, not K1 values
GNDA island = REJECTED (layer policy: no AGND/DGND split)
```

Espressif HW design guidelines cover 90 Ω USB and antenna keepout, not this exact hybrid.
Do not write 1 MΩ / 1 nF into the USB contract. Evaluate later from K1 connector, ESD,
chassis and EMC.

## 3. LED branch-protection bypass (capability OPEN)

Power architecture already branches LED power after monitored `5V_SYS` through an LED eFuse.
Diagnostic idea: bypass **that** branch protector only, so bring-up can separate eFuse / load /
connector / firmware-enable faults.

Carried current envelope: 0.95 A LED branch (design input, to be re-derived). A random 0402 0R
is **not** an amp-class bypass.

```text
VAL-only branch-protection bypass = CANDIDATE capability
implementation = OPEN until branch current and the selected protector are known
marking = DNP and clearly defeating branch protection
forbidden = input reverse/OV, whole-board source protection, USB eFuse
```

No fixture symbol. No EasyEDA part.

## 4. Selective scission

Already required by K1 (not Voice PE):

- PDM XOR: `contracts/microphone-interface.md` — retired plan R38–R41
- Motion ownership: `contracts/motion-interface.md` — R44–R49
- Audio clock isolation: `contracts/audio-interface.md` — R34–R36

Do not freeze:

- K1BR series ohms (`contracts/k1br-bridge.md` freezes payload class, not damping)
- Debug Fabric mux versus jumper/0R (`contracts/debug-fabric.md` still OPEN)

Forbid 0R on USB pairs and NFC RF unless a later K1 SI note demands a named exception.

## 5. Other

- Alternate footprints: principle only; no stacked flash/regulator without a real K1 alternate.
- Service silk and fab impedance table: G4/G5/G7.
- Acoustic geometry principle when the K1 flex is frozen; do not import 71 mm.
- Hardware mute: out of G2.0A.
- RF plane-void: reject (WROOM).
- USB mux to both processors: do not add by default.
- Strap-pin reuse as doctrine: reject.
- Teardrops: G6 reviewed finishing pass.
- L2/L5: no routed signal/power tracks.
- L3: power-only by baseline; documented G3/G5 exception possible for BGA escape.

## Estimate invariant

Option-C estimate changes only from source-derived K1 baseline parts, ratified K1 validation
options, and named stress parts. Voice PE component/footprint counts never drive it.

This review adds **no** new baseline symbols.
