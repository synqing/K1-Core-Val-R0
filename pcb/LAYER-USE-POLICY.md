# Layer use policy

| Layer | Role |
| --- | --- |
| L1 / F.Cu | Components, critical local routes, USB and fast digital where appropriate, NFC matching |
| L2 | Solid uninterrupted GND reference |
| L3 | Primary power regions |
| L4 | Slow, control and secondary routing |
| L5 | Solid uninterrupted GND reference |
| L6 / B.Cu | Secondary components and signals referenced to L5 |

## Rules

- No AGND / DGND split. Separation is achieved by placement and routing over continuous ground.
- No fast signal crosses a power-region boundary without its actual reference remaining continuous.
- Fast routes stay adjacent to a solid ground reference.
- NFC matching stays over uninterrupted ground.
- RF antenna keep-outs apply across all six copper layers.
- High-current LED and power copper is implemented as deliberate regions, not router-default traces.
- Every layer change of a sensitive or fast net includes return-current consideration.
- Top and bottom ground pours require deliberate stitching to L2 and L5.
- No via strategy is accepted merely because DRC permits it.
