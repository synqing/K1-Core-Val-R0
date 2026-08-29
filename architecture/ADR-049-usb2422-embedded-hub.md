# ADR-049: one USB-C plus embedded USB2422

**Status:** RATIFIED
**Date:** 2026-08-29
**Deciders:** Captain implement-the-plan 2026-08-29; H GREEN 2026-08-29
**Register:** D-049 = `RATIFIED`

This ADR is architecture authority. Official electrical freeze still requires
the hub-graph official freeze after EasyEDA ERC (Phase K).

## Context

D-044 put two USB-C receptacles on the board: `J1-PWR1` as 5 V inlet and direct
RT1062 USB2, `J7-ESP` as ESP32-S3 service USB. That ruling closed a real error —
the idea that RT1062 could only see external USB across K1BR — and it stays in
the register as history (`AMENDED_BY_D-049`).

The validation mule now wants **one cable** to reach both processors as USB
devices, without a second Type-C, a second connector ESD island, or a second
CC/VBUS eFuse. Attach and detach must not be faked by always-on `5V_SYS`.
S3 recovery must not depend on the hub.

USB2422 is a two-port USB 2.0 hub with strap configuration, integrated
terminations, and no required EEPROM. Both downstream ports can be declared
non-removable (`NON_REM[1:0] = 10`). That is the intended architecture.

J1 MPN is D-050. Bound: G-Switch `GT-USB-7005A` / `C5250872`.

## Decision

One USB-C receptacle `J1-PWR1`. No second. No third.

J1 remains the 5 V inlet and the Type-C sink (Rd, CC advertisement sense, eFuse /
INA / throttle). USB2 D+/D− on J1 go through connector ESD to USB2422 **upstream**.

- USB2422 DN1 = RT1062 USB OTG1 (HS device, non-removable).
- USB2422 DN2 = ESP32-S3 native USB GPIO20/19 (FS device, non-removable).
- Both processors stay on `5V_SYS` / 3V3. Conventional downstream USB power
  islands are forbidden.
- Hub `VBUS_DET` tracks inlet `5V_USB`, never always-on `5V_SYS` or `3V3`.
- RT `USB_OTG1_VBUS` and S3 VBUS sense track host/hub attach. VAL-R0 default is
  F6-B (TPS2052B) as a validity switch, not as MCU power. An independent
  `5V_USB`-presence kill is mandatory (KILL-B). `VBUS_DET` falling does not
  guarantee `PRTPWR` falling. `F6_VALIDITY_SOURCE` is `5V0_USB_VALID`
  (TPS7A2550DRVR / C2876265).
- `J6-ESP` UART0 + EN + GPIO0 is the brick-proof S3 path. RT SWD/boot stays
  independent of the hub.
- Optional 0 Ω XOR USB recovery pads, DNP by default, mutually exclusive with DN2.
- USB audio remains `EXPERIMENT_ONLY`, terminated DN1 → RT OTG1, not across K1BR.
- This does **not** revive the tombstoned “single USB owned by S3” idea.

D-049 does not bind J1 (that is D-050). Both are now RATIFIED / BOUND. Official
hub-graph freeze waits on Phase K ERC.

## Options considered

### Option A: keep D-044 dual USB-C

| Dimension | Assessment |
|-----------|------------|
| Complexity | Already paid for on the G2.1 graph |
| Cost | Second receptacle, ESD, CC, and operator two-cable reasoning |
| Recovery | Independent S3 cable if the hub dies |
| Errata | No USB2422 Single-TT exposure |

**Pros:** Independent S3 cable; no transaction-translator errata; D-044 already
exists.
**Cons:** The mule still wants one-cable dual-device access; J7’s connector cost
is no longer earned once S3 can sit on the hub; two power/protection islands
remain in front of the two USB PHYs.

**Answer to the steel-man:** J6 UART is the brick path. XOR pads are extra.
One-cable dual-device access is the validation mission. Dual USB remains the
**RED** fallback if H is NO-GO or Captain rejects D-049 at Phase C.

### Option B: one USB-C owned only by ESP32-S3 (tombstoned)

Forbidden. That framing hid RT1062’s own USB OTG1 and left USB audio as an
unnamed exception. D-044 tombstoned it. D-049 does not bring it back.

### Option C: one USB-C + USB2422, both processors non-removable (selected)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — hub island, VBUS validity, three 90 Ω pairs |
| Cost | One receptacle; hub 3V3 70/89 mA; F6-B switch |
| Recovery | J6 UART mandatory; hub is not the brick path |
| Errata | Anomaly 3 is a named hold on USB audio |

**Pros:** One cable reaches both devices; no second Type-C island; source-policy
stays on J1.
**Cons:** Hub is a new single point of USB enumeration; Single-TT errata;
connector physics bound under D-050.

## Named holds

- USB2422 errata Anomaly 3 (HS split / 288 bytes/µframe / Single-TT). USB audio
  is not proven behind this hub.
- JLC Extended class for USB2422T-I/MJ (`C622610`) until procurement proves
  otherwise.
- Bench injection of 5 V onto J1 VBUS without a host remains a named hazard.
- NXP `USB_OTG1_VBUS` absolute maximum 5.50 V versus eFuse OVLO near 6 V.
  Closed by `5V0_USB_VALID` (TPS7A2550DRVR). Do not write “`5V_PROTECTED` is safe”.
- D-050 bound on GT-USB-7005A / C5250872. Drawing still SILENT on thickness;
  bind is geometric section. JLC Assembly Difficulty High remains a process hold.
- USB-IF UFP-powered-hub white paper Rev 0.9 is not a certification basis.

## Consequences

- Living USB contract front matter is `RATIFIED` with `receptacle_count: 1`.
- D-044 remains readable history with status `AMENDED_BY_D-049`.
- `J7-ESP` is removed from living contracts. Historical evidence keeps it.
- EasyEDA mutation is authorised on a **disposable** hub project only.
  Live `64325d0e` stays untouched. Official freeze and `JLC-SCH-READY` wait
  on Phase K / L.
- Phase Z (restore D-044) is **not** this path. H GREEN adopted the hub.

## Action items

1. [x] Captain Phase C: stamp D-049 `APPROVED_FOR_PHYSICS / PROVISIONAL` from implement-the-plan 2026-08-29.
2. [x] Do not write `RATIFIED` at Phase C.
3. [x] Physics pack (D, D050, E–G) completed.
4. [x] H GREEN 2026-08-29 wrote `RATIFIED`.
