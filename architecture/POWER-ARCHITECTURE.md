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
