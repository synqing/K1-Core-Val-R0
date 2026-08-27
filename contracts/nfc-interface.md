---
contract: nfc
status: RATIFIED
frontend_location: K1_CARRIER
host_owner: ESP32_S3
part: ST25R3916B
crystal_mhz: 27.12
matching_values: TUNE_TBD
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
