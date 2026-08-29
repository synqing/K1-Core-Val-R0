# EasyEDA mutation runbook — DEC-USB-HUB T00–T24

Execute only after H GREEN (already true) on disposable
`K1-Core-Val-R0-G2.1-HUB-CANDIDATE` / `41c8e6523576456582ea35958b3684ed`.
Never mutate live `64325d0e55e0435abd018defb0089a9b`. Never beautify
`dcd7e3ca…`. Empty PCB stays empty. One electrical sheet only.

Authority for nets and pins: `PIN-CONTRACT.md`. Census KEEP/DELETE:
`CENSUS.md`. Gate: see `EASYEDA-PREFLIGHT.md`.

```text
TARGET_PROJECT = 41c8e6523576456582ea35958b3684ed
TARGET_PAGE    = 1435cb46f39e48c8a8aadbb84ca81603
PARENT_IS_DISCRIMINATOR = yes
PCB            = 59bef7e87cff4cd580561703b62d8c19  (empty; do not place)
PRE_HASH       = 2352202:c5bf1157
GATE_STATE     = READY on hub-lane only
```

---

## Gate command (every transaction)

Flags **before** the verb:

```bash
GATE=(python3 harness/easyeda_mutation_gate.py
  --state evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-STATE.json
  --ledger evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-LEDGER.jsonl)

"${GATE[@]}" validate     # must print READY and project 41c8e652
"${GATE[@]}" begin …      # IN_FLIGHT
# one visual stage only
"${GATE[@]}" record --semantic jobs/Txx-…-semantic.json
"${GATE[@]}" close  --visual   jobs/Txx-…-visual.json
```

Lock file (OS flock, every transition including `validate`):

```text
evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-STATE.json.lock
```

N≥2 MCP calls in one stage: `mcp_batch.mjs`, `saveAfter:false` until last
job. One batch must not hide place+designate, or designate+wire.

Every mutating MCP call: `expectedDocumentUuid = 1435cb46f39e48c8a8aadbb84ca81603`
**after** proving `currentProject.uuid == 41c8e6523576456582ea35958b3684ed`.

If `validate` is not READY, stop. If visual FAIL, stop; only a named repair
of that Txx may follow.

---

## Screenshot duty (non-substitutable)

After **each** transaction:

1. Wait for canvas settle (render + autosave).
2. Capture a **block-scale** PNG that makes the changed objects and
   designators readable.
3. Capture a **whole-sheet** PNG when bounds or composition can change
   (place, delete, T00, T18–T22, T24).
4. Inspect: intended delta, unexpected changes, pin labels, collisions,
   out-of-bounds, unrelated movement.
5. Write `jobs/Txx-<name>-visual.json` (schema_version 1, ≥4 checks,
   `captured_after_settle: true`, verdict ACCEPTED or REJECTED).
6. Pair with `jobs/Txx-<name>-semantic.json` (pre/post hashes, census,
   affected designators, net membership).

A missing, empty, distant, cropped or unreadable screenshot **closes the
lock**. Semantic read-back cannot replace it. Tool `ok:true` is not
evidence.

Preserve PNGs under `evidence/VAL-G2-2026-08-28/dec-usb-hub/screenshots/`.

---

## Reserved designators

Census sequential next-free is U18; **U18 and U19 stay spare**. Hub silicon
starts at U20. Do not put USB2422 on U18.

| Ref | Part | Status |
| --- | --- | --- |
| **U18-USB** | spare | **do not place** |
| **U19-USB** | spare | **do not place** |
| U20-USB | USB2422T-I/MJ C622610 | place T02 |
| U21-USB | TPS2052B C130049 | place T07a |
| U22-USB | TPS7A2550DRVR C2876265 | F6 validity LDO |
| U23-USB | TLV7031DBVR | KILL-B comparator |
| U24-USB | SN74LVC1G08DBVR | EN1 AND |
| U25-USB | SN74LVC1G08DBVR | EN2 AND |
| **Y3-USB** | 24 MHz crystal | place T03 |
| **J12-USB** | 4-pad XOR header, not USB-C | place T08 |
| J6-ESP | UART recovery | **do not touch** |
| J1-PWR1 | receptacle | T00 replace symbol; do not delete |

### R77–R96 (reserved block)

PIN-CONTRACT already named R77 and R80–R84. This runbook **fills** G6
placeholders `Rxx`/`Ryy` and the unnamed straps / T14 pair from the same
block so two writers cannot pick different numbers.

| Ref | Role | Stage |
| --- | --- | --- |
| R77-USB | 12 kΩ ±1% RBIAS | T03/T04/T06 |
| R78-USB | VBUS_DET upper 100 kΩ `5V_USB` → tap | T03/T07 |
| R79-USB | VBUS_DET lower 100 kΩ tap → GND | T03/T07 |
| R80-USB | F8 bleeder **4.7 kΩ** `5V_USB`–GND (H0f; not 10 kΩ) | T03/T07 |
| R81-USB | KILL-B **169 kΩ** `5V_USB` → TAP_VBUS | with U23 |
| R82-USB | KILL-B 100 kΩ TAP_VBUS → GND | with U23 |
| R83-USB | KILL-B 100 kΩ `3V3` → TAP_REF | with U23 |
| R84-USB | KILL-B 100 kΩ TAP_REF → GND | with U23 |
| **R85-USB** | 470 Ω `USB_5V_VALID` → U9.8 GPIO15 | T16 (H0f Clock 1; **not** XOR) |
| **R86-USB** | 4.7 kΩ `RT_USB_VBUS`–GND | with T12 |
| **R87-USB** | 10 kΩ `S3_USB_VBUS_VALID`–GND | with T07f (OUT2 bleeder, not GPIO15) |
| R88-USB | CFG_SEL strap **low** (47–100 kΩ) | T03/T06 |
| R89-USB | NON_REM1 strap high (for `10`) | T03/T06 |
| R90-USB | NON_REM0 strap low (for `10`) | T03/T06 |
| R91-USB | RESET_N pull-up | T03/T06 |
| R92-USB | RESET_N timing if the RC needs a second R | T03 if required |
| R93-USB | spare in-block | do not invent a second XOR |
| **R94-USB** | XOR 0 Ω **FIT** hub DN2 path-select | T08/T09/T13 |
| **R95-USB** | XOR 0 Ω **DNP** to J12-USB | T08/T09; never FIT with R94 |
| R96-USB | spare | |

S3 PHY TUNE uses **named** refs, not R73/R74:

| Ref | Role | Stage |
| --- | --- | --- |
| RUSB_S3_DP_TUNE | 22 Ω or 33 Ω at GPIO20 | T13a place / T13b designate / T13c wire |
| RUSB_S3_DM_TUNE | 22 Ω or 33 Ω at GPIO19 | same |
| CUSB_S3_DP_TUNE | optional DNP shunt GPIO20–GND | T13a if placed |
| CUSB_S3_DM_TUNE | optional DNP shunt GPIO19–GND | T13a if placed |

BC_EN1 shares USB2422 pin 7 with PRTPWR1. F6-B uses pin 7 as PRTPWR1
output into KILL-B. Strap-off is the internal pull-down. **Do not add a
pull-up that fights PRTPWR1.**

### C100–C114 (reserved island) plus PIN-CONTRACT extras

| Ref | Role |
| --- | --- |
| C100-USB | CRFILT 1 µF |
| C101-USB | PLLFILT 0.1 µF |
| C102-USB / C103-USB | Y3 load caps (D11) |
| C104-USB | VDD33 pin 1, 100 nF |
| C105-USB | VDD33 pin 9, 1 µF |
| C106-USB | VDD33 pin 18, 100 nF |
| C107-USB | RESET RC cap if required |
| C108–C110-USB | TPS2052B IN/OUT local caps (TI) |
| C111–C112-USB | U22 LDO locals **or** leave to C121/C122 |
| C113–C114-USB | optional S3 TUNE DNP shunts if not using CUSB_* names |

PIN-CONTRACT also names **C120-USB** (22 µF on `5V_PROTECTED`), **C121** /
**C122** (LDO CIN/COUT). Those sit outside C100–C114 and must still be
placed in the F6/inlet transactions. Do not put 22 µF back on `5V_USB`.
C1-PWR1 **value retarget** 22 µF → 1.0 µF (G3b), still on `5V_USB`.

Do not reuse retired numbers: U4, R8, C68, J7.

---

## XOR FIT / DNP (true XOR)

Default (G6, H10):

```text
R94-USB  0 Ω  FIT   hub DN2 → TUNE → GPIO20/19
R95-USB  0 Ω  DNP   J12-USB pads → USB_REC_DP / USB_REC_DM
J12-USB        present as pads/header, not a USB-C
Assembly: never fit both R94 and R95
R85-USB is GPIO15 series, not XOR.
```

T13 wires hub DN2 **only** to the hub-side 0 Ω. T13c lands on the PHY
through the TUNE pair. Header-side stays open.

---

## J7 delete list (after the new path exists)

Do not delete until T17 has lifted these off shared nets. `FB4-ESP` is
absent — not a delete.

| Designator | Transaction |
| --- | --- |
| J7-ESP | T18 |
| U10-ESP | T19 |
| C43-ESP, C44-ESP | T19 |
| R73-ESP, R74-ESP, R71-ESP, R72-ESP | T20 |
| R21-ESP, R22-ESP (J7 Rd only) | T21 |
| leftover J7-only nets / ferrites | T22 |
| DVBUS-PWR1 (leftover rail TVS) | with T22 or a named T22a; census DELETE |

After T21, `USB_CC1` / `USB_CC2` membership must be **J1-only**
(J1 + RCC1/RCC2 + sense). T24: drop stale J7 SBU waiver on a **copy** of
the hub-candidate waiver file, not by rewriting historical
`canonical-core-val-r0/DRC-WAIVERS.json` in place.

---

## T14 skipped / T16 from `USB_5V_VALID` (H0f Clock 1)

H0f closed Espressif 3 ms on the comparator, not on TPS2052B OUT2
(`toff` max 10 ms cannot own 3 ms). T14/T15 (OUT2 resistor divider onto
GPIO15) are **skipped**. Do not place R91/R92 as a S3 VBUS divider.

- **T16:** place was T07g+ for U23; this wire step is R85 470 Ω
  `USB_5V_VALID` → U9.8 GPIO15. Prove GPIO15 is off the old `S3_VBUS`
  divider. OUT2 stays bleeder-only (R87).

S3 TUNE pair is T13a–c, not T14.

---

## Ordered transactions

Place, designate, and wire stay **separate visual transactions**. One
circuit block, one stage, per invocation. No `all` mode.

| ID | Stage | Intended delta | Stop if |
| --- | --- | --- | --- |
| **T00** | place | GT-USB-7005A-IND (`ea47c20de228fa3a`) beside existing USB4105. No wiring. Never cache footprint on PCB. CLOSED 2026-08-29. | Cache footprint used |
| **T00d1** | designate | Old USB4105 `J1-PWR1` → `J1-USB4105-RETIRED`. Do not delete. Do not wire. | Old part deleted; two J1-PWR1 |
| **T00d2** | designate | New `ea47c20de228fa3a` → `J1-PWR1` / MPN GT-USB-7005A. No wire. No move. | Cache artwork swap |
| **T01** | read-only + gate | Re-assert project `41c8e652`, page `1435cb46`, component sentinel, PCB 0/0. Snapshot. | Parent UUID ≠ hub; live focused |
| **T02** | place | U20-USB only, clear empty region, pins readable | Dropped into a prison box; auto-wired |
| **T03** | place | Y3, C100–C107 as needed, R77–R80, R87–R90, VBUS_DET pair, RESET RC. No designate if auto-names are wrong — T04 fixes. No wiring | Wired in this step |
| **T04** | designate | Every T02–T03 part gets the `-USB` refs above | Unreadable designators |
| **T05** | wire | Hub 3V3 / GND / ePad only | USB pairs touched |
| **T06** | wire | RBIAS, CRFILT, PLLFILT, XTAL, RESET_N, CFG_SEL low, NON_REM `10`, BC_EN off (no fighting pull-up) | USB pairs touched |
| **T07** | wire | `USB_VBUS_DET` from `5V_USB` via R78/R79 + R80 bleeder. Prove **not** on `5V_SYS` | Tap on 3V3 or 5V_SYS |
| **T07a** | place | U21-USB only | F6-A (not this programme) |
| **T07b** | place | TPS2052B support caps | Combined with wire |
| **T07c** | designate | T07a–T07b | |
| **T07d** | wire | Switch IN / GND only (`5V0_USB_VALID`). U22 island may need its own place/designate/wire triplet **before** this if not already present | IN = `5V_PROTECTED` by habit |
| **T07e** | wire | PRTPWR1/2 and OCS1_N/OCS2_N into KILL-B (U23–U25). AND/comparator themselves need prior place/designate/wire | EN wired to PRTPWR alone (KILL-C) |
| **T07f** | wire | OUT1 `RT_USB_VBUS`, OUT2 `S3_USB_VBUS_VALID`. **No MCU core pins** on these nets yet | OUT feeding 3V3 / MCU VDD |
| **T08** | place | R94 FIT, R95 DNP, J12-USB pads | Second USB-C |
| **T09** | designate | T08 | |
| **T10** | wire | J1 D+/D− after ESD → `USB_DP_UP` / `USB_DM_UP`. Disconnect RT if still on J1. Keep D1-PWR1 | J1 ESD deleted |
| **T11** | wire | Hub DN1 → U6 L8/M8 `USB_DP_DN1` / `USB_DM_DN1`. `OPT_USB_AUD` stays off those balls | M6/M7 treated as USB |
| **T12** | wire | N6 → `RT_USB_VBUS` + retarget `CUSBVBUS-RTC`. If the 1 µF is missing: **stop** — T12a place / T12b designate / T12c wire | Sneaking a place into a wire |
| **T13** | wire | Hub DN2 to **R94 only**. Do not land GPIO19/20 | Dual-drive with header |
| **T13a** | place | RUSB_S3_DP_TUNE / RUSB_S3_DM_TUNE at PHY; optional DNP shunts | Reusing R73/R74 |
| **T13b** | designate | T13a | |
| **T13c** | wire | R94 → TUNE → GPIO20/19. Optional shunts to GND if DNP footprints exist | |
| **T14** | — | **Skip** — H0f does not put an OUT2 divider on GPIO15 | |
| **T15** | — | **Skip** | |
| **T16** | wire | R85 `USB_5V_VALID` → U9.8. Prove old `S3_VBUS` divider gone | OUT2 still on GPIO15 |
| **T17** | wire | Lift J7 island off `USB_CC1`/`USB_CC2`/`USB_DP*`/`S3_VBUS` | CC nets still include J7 |
| **T18** | delete | J7-ESP. Screenshot: J7 gone, J1 present | J1 deleted |
| **T19** | delete | U10, C43, C44 | |
| **T20** | delete | R73, R74, R71, R72 | |
| **T21** | delete | R21, R22. Re-read CC nets = J1-only | J1 Rd gone |
| **T22** | delete | J7-only nets; DVBUS-PWR1. `S3_VBUS` zero members | |
| **T23** | text/NC | Hub unused; J1 SBU + all SuperSpeed; RT CHD_B / OTG2. No frames. No SS net names | SuperSpeed routed |
| **T23a** | — | **Skip** — CC-PROTECTION letter is IEC ESD only | |
| **T24** | save/hygiene | `save_active_document` `saved:true`; hash changed; hub waiver copy without J7 SBU; still one sheet; PCB still 0/0; whole-sheet + zooms of J1, hub, RT USB, S3 USB, J6 unchanged | PCB gained parts |

U22/U23/U24/U25/D3: insert as extra place → designate → wire triplets
**before** T07d/T07e if they are not already on the sheet. Do not fold
them into T07d. Same gate, new T-numbers (T07g…) if needed.

C1-PWR1 22 µF → 1.0 µF is a **designate/value** transaction of its own
(do not hide it inside T07). C120 add is place then designate then wire
on `5V_PROTECTED`.

---

## Semantic proof points (spot checks)

| After | Must be true |
| --- | --- |
| T07 | `USB_VBUS_DET` members include hub pin 16 + R78 + R79; not `5V_SYS` |
| T07f | Neither TPS2052B OUT on an MCU core rail |
| T10 | RT L8/M8 **not** still on J1 ESD far side |
| T13+T13c | GPIO20/19 on DN2 path through R94 + TUNE; R95 open |
| T16 | U9.8 on `USB_5V_VALID` via R85, not `S3_VBUS`, not OUT2 |
| T21 | `USB_CC1`/`USB_CC2` = J1 + J1 Rd + J1 sense only |
| T22 | `S3_VBUS`, `USB_DP`, `USB_DM`, `USB_DP_ESD`, `USB_DM_ESD` gone or empty |
| T24 | live `64325d0e…` hash unchanged; hub PCB still empty |
| any | J6 six pins untouched |

Library identity: LCSC search by code, never `devices[0]` on a name query.

---

## Evidence paths

```text
evidence/VAL-G2-2026-08-28/dec-usb-hub/
  EASYEDA-PREFLIGHT.md
  EASYEDA-MUTATION-RUNBOOK.md
  PIN-CONTRACT.md
  CENSUS.md
  DISPOSABLE-IDENTITY.md
  hub-lane/MUTATION-STATE.json
  hub-lane/MUTATION-STATE.json.lock
  hub-lane/MUTATION-LEDGER.jsonl
  jobs/Txx-*
  screenshots/Txx-*
  anchors/
```
