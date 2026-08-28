---
contract: nfc
status: RATIFIED
frontend_location: K1_CARRIER
host_owner: ESP32_S3
part: ST25R3916B
crystal_mhz: 27.12
matching_values: TUNE_TBD
host_interface: I2C
i2c_en_strap: PULLED_HIGH_TO_3V3
i2c_en_no_connect: FORBIDDEN
internal_regulator_rails_are_outputs: true
internal_regulator_decoupling_uf: 2.2
---

# NFC interface contract

Frozen independent of VAL-G1.

ST25R3916B, its 27.12 MHz crystal, local supply filtering, RFO EMI network, matching network,
RFI network and antenna terminals all stay physically on the K1 carrier.

If ESP32_S3 is module-mounted under Option B, only low-frequency host signals cross SSCM-1:

    I2C_SDA
    I2C_SCL
    NFC_IRQ

The 13.56 MHz RF path never crosses the module connector. This is open risk R3 resolved by
freezing the front end carrier-side: an RF antenna lead across a connector budgeted for digital
signals is a cost neither option should pay.

Layout requirements: continuous ground beneath the matching network, short RFO and RFI geometry,
symmetric routing, no cuts in the return plane, no through-vias in the matching path.

Matching values remain `TUNE_TBD` until the real antenna, lead and installation are characterised.

## Host interface strap (D-046)

ST25R3916B selects its host interface from the I2C_EN pin. **I2C_EN high selects I2C. Floating is
not a valid strap** — an unstrapped I2C_EN is an undefined interface selection, not a default.

K1-CORE-VAL uses `I2C_SDA` and `I2C_SCL`, so I2C_EN is held high: `R76-NFC` 10k from net
`NFC_I2C_EN` to `3V3`, with U12 pin 20 on `NFC_I2C_EN`. Marking that pin no-connect is forbidden.

## Internal-regulator rails are outputs (D-047)

`VDD_A`, `VDD_D`, `VDD_RF`, `VDD_AM`, `VDD_DR` and `AGDC` are **outputs of the ST25R3916B
internal regulators**. They must never be driven from `NFC_5V`, from `3V3`, or from any other
supply. Wiring any of them to a rail back-drives a regulator output.

Each rail carries its own 2.2 µF decoupling capacitor to GND, matching the STEVAL-ST25R3916B
reference design: `C92-NFC` through `C97-NFC`, GRM155R60J225ME15D.

The correct DRC reading of these nets is therefore "regulator output plus its decoupling
capacitor", never "unsupplied net that needs a source".
