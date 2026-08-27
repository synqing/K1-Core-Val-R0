# Floorplan study

Status: **NOT STARTED — blocked on VAL-G1**

One contraction study. Not three parallel envelope documents: three lanes produce one answer
three times, and the method below already contains the comparison.

## Method

1. Begin with an intentionally generous east-west outline.
2. Place every domain according to physics, mechanics and the interaction requirements.
3. Establish clean routing corridors and return paths.
4. Contract the east-west outline incrementally.
5. Stop at the first material compromise.
6. Record: selected length; last passing length; first rejected length; the exact reason it failed.

Multiple EasyEDA snapshots or screenshots during the contraction are evidence from one method,
not three separately maintained designs.

## Placement priority

1. Enclosure and mechanical constraints
2. Compute and RF architecture
3. Fixed external connectors
4. Power entry
5. Buck and high di/dt block
6. Shunt and INA226 measurement
7. LED power and data
8. NFC RF island
9. Audio interfaces
10. Microphone flex exit
11. Accelerometer
12. Service and test
13. Remaining passives

Compute placement is physics-first: position from RF and mechanical requirements, peripherals
second, GPIO assignment last.

## Prerequisite

`architecture/DOMAIN-INTERACTION-MATRIX.csv` must exist first, and it cannot be instantiated
until VAL-G1 selects Option B or Option C — the meaning of each relationship differs between
them. Conditional entries live in `authority/02-Q0-B-vs-C.md` until then.
