# Live schematic validation — 2026-08-30

Read-only. No EasyEDA write. Project `K1-Core-Val-R0` `64325d0e55e0435abd018defb0089a9b`, page `1435cb46f39e48c8a8aadbb84ca81603`.

**Verdict: not 100% solid. Not freeze. Not `JLC-SCH-READY`.**

Source hash `2261786:87a5e33b`. Host DRC after `sch_Drc.check(true,false,true)`: Fatal 0, Error 0, Warn 26, Info 406. Warn *item* text was not exported from the panel this run; counts come from the DRC summary line at 04:08:31.

Instrument positive controls that did fire: `U3-PWR2`, `J1-PWR1`, `J7-ESP`, `USB_DP`/`USB_DM`, `U11-AUD`, `LED_FAULT_L_N` stub, `R75-PWR2` 10k, `C10-PWR2` 100nF.

## What is electrically sound on this sheet

- One schematic page. 229 components, 687 wires, 225 named designators, 150 named nets. Zero wires carrying two different net names (no FAULT1-on-GND class short).
- `U17-PWR2` `FAULT1#` is a dedicated `LED_FAULT_L_N` stub (`2639a4b072b190b5`). The exposed-pad island is GND-only.
- D-045 as now drawn: `U3-PWR2` sits at (1615, −4605). `BUCK_PG` is a short stub on the PG pin row (1555, −4585) to (1510, −4585). `R75-PWR2` 10k is vertical at (1510, −4565). `3V3` meets the other end of R75 (`e146320`). The long PG run from earlier this session is gone; the pull-up moved next to the pin. PG is not NC.
- D-046 `R76-NFC` and D-047 `C92-NFC`…`C97-NFC` are present. `NFC_I2C_EN` and `BUCK_SS` (`C10-PWR2` 100nF) exist.
- `U11-AUD` TLV320ADC6120 and `J9-AUD` FFC-10 (PDM flex) are present.

## Contract gaps (the sheet does not match ratified living truth)

1. **D-049 USB hub is not on this sheet.** Living contract is one USB-C plus USB2422. Live still has `J1-PWR1` *and* `J7-ESP`, nets `USB_DP`/`USB_DM`, and no `USB_DP_UP`/`USB_DM_UP`, no `U20-USB`/`U22-USB`. That is the old two-receptacle graph. GUI DRC will not flag it; it is not a floating-pin error.
2. **D-051 AUX is not on this sheet.** Contract is dual-input (switched 3.5 mm AUX + PDM). Nets `AUX_L`/`AUX_R` are absent. `J9-AUD` is the PDM FFC, not a TRS jack. STATUS.md already records this; freeze of a PDM-only graph is forbidden.

## Remaining schematic dirt (not architecture)

- Orphan named stubs still present: `5V_LED_COMMON`, `LED_EFUSE_DVDT`, `LED_EFUSE_ILIM`.
- Duplicate same-name labels are widespread (`GND` 208, `3V3` 89, `5V_SYS` 16, plus others). Cosmetic DRC Warn class.
- `U6-RTC` appears twice (multi-unit symbol, expected).
- Three empty-designator drawing symbols (`e153999`, `6da43ee181cf13a9`, `42df88e4a3e64915`).
- DRC Warn 26 is uncleared item text. Historically unused RT balls, J1 SuperSpeed/SBU, NFC/motion NC candidates. Not re-listed without panel export.

## Process debt (not a new electrical defect)

Schematic-lane gate is still `AWAITING_EVIDENCE` on `live-u3-pg-buck-pg-2026-08-30` at hash `2259451:ad461e85`. Live is `2261786:87a5e33b` after later canvas edits (R75 relocated, U3 nudged, PG run replaced by a local stub). Do not begin another schematic write until that lane is closed or quarantined against the current hash.

Snapshot: `evidence/VAL-G2-2026-08-28/canonical-core-val-r0/schematic-lane/anchors/validate-2026-08-30-source.json`.
