---
contract: motion
status: DEFAULT
owner: RT1062
bus: I2C
ownership_matrix: 0R_DNP_REQUIRED
---

# Motion interface contract

Default owner is RT1062, because structural vibration, impact suppression and motion-reactive
render are real-time inputs to the visual engine.

Fit an explicit 0R / DNP ownership matrix so the I2C and IRQ lines can be assigned to either
RT1062 or ESP32_S3 during validation, but are never electrically enabled to both as uncontrolled
masters simultaneously. The matrix and its XOR rule are drawn beside the circuit on the single
schematic sheet.

Mechanical requirement: mount on a rigid section near the assembled structural centre, not on a
board edge, connector tongue or unsupported cantilever.
