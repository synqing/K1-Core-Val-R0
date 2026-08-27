# VAL-G1 — Option B versus Option C

Q0-A is closed. Dual-MCU ownership is reaffirmed: RT1062 owns audio, processing and render;
ESP32_S3 is the radio bridge. Monolithic ESP32-S3 remains the legacy parity oracle and is not a
new-hardware candidate unless fresh current-silicon measurement disproves the compute-wall premise.

The open question is **where the RT1062 lives**.

| | Option B | Option C |
| --- | --- | --- |
| Compute | SSCM-1 swappable module | Soldered to Core |
| Upgrade path | Module swap | Respin only |
| Blocking issue | SSCM-1 interface must be reconstructed | None; best defined today |

## Conditional interaction table

The domain-interaction matrix is **not yet a single Core-placement authority**, because the
meaning of each relationship differs between B and C. These conditional entries live here until
VAL-G1 closes. Only then is `architecture/DOMAIN-INTERACTION-MATRIX.csv` instantiated as the
real floorplanning authority.

| Relationship | Option B | Option C |
| --- | --- | --- |
| RT1062 to LED output | Connector crossing, two fast-edge outputs | Core placement and routing constraint |
| RT1062 to ADC and TDM | Connector crossing unless the ADC is module-side | Core placement and routing constraint |
| RT1062 to audio clocks | Connector crossing, with direction and isolation defined | Core routing constraint |
| RT1062 to accelerometer | Connector crossing, or a module-side sensor | Core placement constraint |
| ESP32_S3 to 2.4 GHz antenna | Module mechanical and RF constraint | Core mechanical and RF constraint |
| ESP32_S3 to NFC front end | Bus crossing only; RF stays carrier-side | Core placement constraint |
| Buck to audio | Noise aggressor, must be far | Noise aggressor, must be far |
| Shunt to INA226 | Must be close | Must be close |

## Closing criteria

VAL-G1 closes when the SSCM-1 v2 requirements sheet exists and B can be scored against C on the
real crossing set — signal count, grounds, power contacts, clock adjacency, direction, isolation,
boot and debug ownership, and genuine spare contingency. If M.2 B-key cannot carry that crossing
with real contingency, Option B fails honestly at the requirements stage, before any copper.
