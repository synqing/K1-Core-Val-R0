---
contract: led
status: RATIFIED
output_owner: RT1062
channels: 2
level_shift: required
---

# LED interface contract

RT1062 owns portable pixels, FastLED adaptation and strip output. J2 and J3 therefore belong
electrically to RT1062, not to ESP32_S3.

Placement consequence under Option C: RT1062 is floorplanned with a clean route to the west-edge
LED output circuitry. Under Option B both channels cross the module connector as fast-edge
outputs, which is a signal-integrity cost the SSCM-1 pin budget must carry rather than a plain
pin count.

A level shifter is required between 3.3 V logic and the 5 V strip. High-current LED copper is
implemented as deliberate regions, never router-default traces.
