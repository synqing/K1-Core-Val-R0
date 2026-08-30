# U1-PWR1 G2.2 pin differential

Scope: TPS259474L ten-pin audit of the G2.2 hub candidate.
Canonical project `64325d0e55e0435abd018defb0089a9b` is **CLEAN** for this defect and was not mutated.

Reconstruction: symbol offsets for `TPS259474LRPWR.1` plus the instance transform, 
validated against a known-good majority of U1 pins at tolerance 0. 
A graph with `bound_pin_count=0` cannot pass this gate.

| Pin | Datasheet/symbol role | Canonical net | G2.2 pre-fix net | G2.2 post-fix net | Classification | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | EN/UVLO | USB_EFUSE_EN | USB_EFUSE_EN | USB_EFUSE_EN | SAME | abs (775, -4110) |
| 2 | OVLO | USB_EFUSE_OVLO | USB_EFUSE_OVLO | USB_EFUSE_OVLO | SAME | abs (775, -4130) |
| 3 | PG | PWR_ENTRY_PG_RT_IOMUX_TBD | PWR_ENTRY_PG_RT_IOMUX_TBD | PWR_ENTRY_PG_RT_IOMUX_TBD | SAME | abs (600, -4130) |
| 4 | PGTH | USB_EFUSE_PGTH | USB_EFUSE_PGTH | USB_EFUSE_PGTH | SAME | abs (600, -4110) |
| 5 | IN | 5V_USB_FILTERED | 5V_USB | 5V_USB | INTENDED_RENAME | abs (775, -4090); hub-era 5V_USB_FILTERED → 5V_USB after F1 left the trunk |
| 6 | OUT | 5V_PROTECTED | 5V_PROTECTED | 5V_PROTECTED | SAME | abs (600, -4090) |
| 7 | DVDT | USB_EFUSE_DVDT | USB_EFUSE_DVDT | USB_EFUSE_DVDT | SAME | abs (705, -4165) |
| 8 | GND | GND | GND | GND | SAME | abs (665, -4165) |
| 9 | ILM | USB_EFUSE_ILIM | USB_DP_UP | USB_EFUSE_ILIM | DEFECT_FIXED | abs (625, -4165); ILM restored onto USB_EFUSE_ILIM; USB_DP_UP no longer owns pin 9 |
| 10 | ITIMER | OPEN | OPEN | OPEN | SAME | abs (740, -4165) |

## R1-PWR1

- electrical/device identity: 1240 Ω / RNCF0402BTC1K24 / C2491273 / device `263cdab6e3341f4ea8fd57ccc688e923`
- display Name: `1.24k`
- legacy partId: `RC0402FR-0710KL.1`
- metadata mismatch: True

Authoritative fields: Manufacturer Part, Name, Device, Supplier Part. Do not infer the ohmic value from `partId`.

## Checker counts

```
{
  "files_inspected": 1,
  "easyeda_records_parsed": 9893,
  "components_inspected": 287,
  "symbol_pins_resolved": 10,
  "nets_inspected": 174,
  "assertions_executed": 11
}
```

