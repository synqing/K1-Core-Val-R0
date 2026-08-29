# Power architecture

The single schematic sheet must show the whole tree as visible wiring. Power symbols are not a
way to hide power flow, and six disconnected `5V_SYS` labels are not a power tree.

    USB / power entry
           |
        protection / eFuse
           |
        5V_PROTECTED
           |
          RSH1  ---- INA226 (Kelvin)
           |
        5V_SYS
           |
           +--> LED eFuse --> +5V_LED_L
           |               \-> +5V_LED_R
           +--> TPS62913 -----> 3V3
           +--> MIC filter/LDO -> 3V3_MIC
           +--> NFC filter -----> NFC_5V
           +--> validation and accessory feeds

Voltage and current budgets are annotated on the schematic beside the relevant branch.

Carried forward from prior K1 power-class work as design input, to be re-derived for this board:
2.35 A trunk, 0.95 A LED branch, 0.60 A 3V3 envelope.

High-current copper is implemented as deliberate regions with via arrays, never as
router-default traces.

J1 is the only USB-C and the 5 V inlet (D-049 `RATIFIED`). USB2 data on J1 is hub
upstream, not a termination on RT1062. `J7-ESP` is deleted. Hub 3V3 comes from the
existing 3V3 rail. No 1.2 V domain. See `contracts/usb-interface.md`. J1 MPN is
D-050 **bound** GT-USB-7005A / C5250872. F6 validity rail is `5V0_USB_VALID`
(TPS7A2550DRVR), not `5V_PROTECTED`.

## TPS62913 required support components (D-045)

These are vendor requirements from TI SLUSEA4, ratified as design facts. They are not optional
hygiene and not script constants.

| Pin | Requirement | Implementation |
| --- | --- | --- |
| PG | Open-drain. Requires an external pull-up when used. K1-CORE-VAL **uses** PG; it must not be tied off as no-connect | `R75-PWR2` 10k from `BUCK_PG` to `3V3`, `U3-PWR2` pin 5 on `BUCK_PG` |
| NR/SS | Requires its soft-start capacitor to GND | `C10-PWR2` 100 nF from `BUCK_SS` to GND, `U3-PWR2` pin 8 on `BUCK_SS` |

An open-drain PG left floating reports nothing. Because this board exists to be measured, PG is a
validation signal, so the pull-up is a requirement of the board's purpose as well as of the part.
