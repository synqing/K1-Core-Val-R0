# DEC-USB-HUB Phase E census

What happened. This census reads the G2.1 electrical archive and the review dumps. Nobody opened EasyEDA. Nobody wrote a schematic.

What is true now. J1 is a working Type-C sink on `5V_USB` with its own 5.1 kΩ Rd, and J1 D+/D− already reach RT1062 OTG1. J7 still exists and still shares `USB_CC1` / `USB_CC2` with J1. That shared-Rd collision is proven. The next free hub-island block is reserved on paper only.

What is left. Do not place the hub until this reserved block is used. After the new path exists, delete the J7 island and prune J7 from the CC nets. Schedule T24 for the J7 SBU DRC waivers.

```text
DATE = 2026-08-29
PHASE = E
EASYEDA = no
LIVE_PROJECT = 64325d0e55e0435abd018defb0089a9b  (not read; not authority)
G21_ORACLE_UUID = dcd7e3cab2a24b9aa6e531d2b62e1b6f
G21_ARCHIVE_SHA256 = 3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7
SEED_SHA256 = 892bbaee80f22d7086d42faa43557be4600b34d99b765914f7caf4c2c2a7e568
REVIEW_SOURCE_HASH = 2352834:a75b5884
DOCUMENT_UUID = 1435cb46f39e48c8a8aadbb84ca81603
OFFICIAL_FREEZE = false
PIN_METHOD = 3db861a3 epro geometric pin-to-wire join (independent_epro_audit_cli.build)
HELPER = evidence/VAL-G2-2026-08-28/dec-usb-hub/_phase_e_census.py
HELPER_JSON = evidence/VAL-G2-2026-08-28/dec-usb-hub/_phase_e_census.json
```

## How this was proven

Pin-to-net membership for J1, J7, U10, U9 and U6 is **not** in `review-pin-bindings.json`. That file is `PARTIAL_LIVE_BINDINGS` (14 designators). The graph seed says the same. The host dump `review-source-after-reopen.json` has COMPONENT / WIRE / ATTR records and no PIN primitives (`pin_net_count` empty in `review-source-census-after-reopen.json`).

So connector and MCU USB pins were taken from archive
`evidence/VAL-G2-2026-08-28/offline-bulk-repair/K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro`
by the same geometric join the independent auditor already used. Identity (MPN / LCSC / value) was taken from `g2.1-electrical-graph-seed.json` and from epro ATTR. Where those two disagree, both are written.

U1-PWR1, U2-PWR1 and R67-PWR1 also have live bindings. Those three agree with the epro join pin-for-pin.

If a net is not on that join and not in the seed net list, it is **UNKNOWN**. SuperSpeed contacts that are missing from today's USB4105 symbol are **ABSENT-FROM-SYMBOL**, not guessed.

## Historical audits — cross-check only

These files are **not** authority. They measure live product `64325d0e` at frozen hash `489736:464c27d4`, before G2.1 repair. They are not rewritten here.

| File | Why it is historical |
| --- | --- |
| `canonical-core-val-r0/USB-TOPOLOGY-AUDIT.md` | J1 recorded as almost unwired, no Rd, no D+/D−. G2.1 contradicts that. |
| `canonical-core-val-r0/PIN-AUDIT-PWR1.md` | Records D1 as a misapplied rail TVS and F1 still present. G2.1 has D1 as data ESD and F1 absent. |
| `canonical-core-val-r0/PIN-AUDIT-S3.md` | J7-era S3 USB path. Useful only as a reminder that no USB-UART bridge was found then either. |
| `canonical-core-val-r0/PIN-AUDIT-RT.md` | OTG1 gap on the old live sheet. G2.1 already binds L8/M8/N6. |

`DRC-WAIVERS.json` is the live-lane waiver register, not G2.1. Its J7 SBU entries become stale after J7 delete (E2.2 / T24).

---

## E1. J1 island — KEEP unless a part is the leftover rail TVS

Today's receptacle MPN on G2.1 is **USB4105-GF-A / C3020560** (graph seed `part_id` `USB4105-GF-A.1`, LCSC `C3020560`). D-050 may replace the symbol later. Do not treat this census as a D-050 bind.

### E1.0 J1-PWR1 — KEEP (D-050 may replace the symbol later)

| Pin | Symbol name | Net | NC flag | 24-pin role | Disposition |
| --- | --- | --- | --- | --- | --- |
| A4 | VBUS | `5V_USB` | no | VBUS | KEEP |
| A9 | VBUS | `5V_USB` | no | VBUS | KEEP |
| B4 | VBUS | `5V_USB` | no | VBUS | KEEP |
| B9 | VBUS | `5V_USB` | no | VBUS | KEEP |
| A1 | GND | `GND` | no | GND | KEEP |
| A12 | GND | `GND` | no | GND | KEEP |
| B1 | GND | `GND` | no | GND | KEEP |
| B12 | GND | `GND` | no | GND | KEEP |
| A5 | CC1 | `USB_CC1` | no | CC | KEEP |
| B5 | CC2 | `USB_CC2` | no | CC | KEEP |
| A6 | DP1 | `USB_DP_J1` | no | D+ | RETARGET (today → RT; hub US later) |
| B6 | DP2 | `USB_DP_J1` | no | D+ | RETARGET |
| A7 | DN1 | `USB_DN_J1` | no | D− | RETARGET |
| B7 | DN2 | `USB_DN_J1` | no | D− | RETARGET |
| A8 | SBU1 | none | yes | SBU | KEEP, NC-intended |
| B8 | SBU2 | none | yes | SBU | KEEP, NC-intended |
| 1 | EH | `GND` | no | shell / housing | KEEP |
| 2 | SHIELD | `GND` | no | shell | KEEP |
| 3 | SHIELD | `GND` | no | shell | KEEP |
| 4 | SHIELD | `GND` | no | shell | KEEP |
| A2 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| A3 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| A10 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| A11 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| B2 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| B3 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| B10 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |
| B11 | — | ABSENT-FROM-SYMBOL | — | SuperSpeed | NC-intended if D-050 adds a 24-pin symbol |

**J1 VBUS.** All four VBUS contacts on the symbol (A4, A9, B4, B9) sit on **`5V_USB`**. Confirmed. `5V_USB` members in the archive: those four J1 pins, `C1-PWR1.1`, `U1-PWR1.5`, `R63-PWR1.1`, `DVBUS-PWR1.1`.

**J1 CC.** A5 = `USB_CC1`, B5 = `USB_CC2`. J1's own Rd is `RCC1-PWR1` / `RCC2-PWR1` (5.1 kΩ, `RC0402FR-075K1L` / C105872). J7 also sits on the same two nets (E2.1). That is a defect, not J1 using J7's Rd.

**J1 D+/D− destination.** Proven path, J1 → RT, as G2.1 repair intended:

```text
J1 A6+B6  USB_DP_J1  → D1.1 → D1.6 USB_DP_PROT → RUSB_DP-PWR1 → USB_DP_RT → U6 L8 USB_OTG1_DP
J1 A7+B7  USB_DN_J1  → D1.3 → D1.4 USB_DN_PROT → RUSB_DN-PWR1 → USB_DN_RT → U6 M8 USB_OTG1_DN
```

`USB_DP_RT` members: `RUSB_DP-PWR1.2`, `U6-RTC L8` only. Independent audit postcondition `RT_USB_DP` = `USB_DP_RT`.

`USB_DN_RT` members: `RUSB_DN-PWR1.2`, `U6-RTC M8`, plus geometry extras `U6 M6` and `U6 M7` (see E3). Primary destination is still RT OTG1 DN.

### E1.1 D1-PWR1 — KEEP (data ESD, not the leftover rail TVS)

| | |
| --- | --- |
| Designator | D1-PWR1 |
| Part | USBLC6-2SC6 / C323793 (`USBLC6-2SC6_C323793.1`) |
| Disposition | KEEP |

| Pin | Name | Net | NC |
| --- | --- | --- | --- |
| 1 | 1 | `USB_DP_J1` | no |
| 2 | 2 | `GND` | no |
| 3 | 3 | `USB_DN_J1` | no |
| 4 | 4 | `USB_DN_PROT` | no |
| 5 | 5 | `5V_PROTECTED` | no |
| 6 | 6 | `USB_DP_PROT` | no |

This is the J1 data-line array. It is not the leftover rail TVS.

### E1.2 U1-PWR1 — KEEP

| | |
| --- | --- |
| Designator | U1-PWR1 |
| MPN / LCSC | TPS259474L / C2864845 |
| Part | TPS259474LRPWR.1 |
| Disposition | KEEP |

| Pin | Name | Net | NC | Live binding agrees |
| --- | --- | --- | --- | --- |
| 1 | EN/UVLO | `USB_EFUSE_EN` | no | yes |
| 2 | OVLO/OVCSEL | `USB_EFUSE_OVLO` | no | yes |
| 3 | PG/AUXOFF | `PWR_ENTRY_PG_RT_IOMUX_TBD` | no | yes |
| 4 | PGTH/FLT# | `USB_EFUSE_PGTH` | no | yes |
| 5 | IN | `5V_USB` | no | yes |
| 6 | OUT | `5V_PROTECTED` | no | yes |
| 7 | DVDT | `USB_EFUSE_DVDT` | no | yes |
| 8 | GND | `GND` | no | yes |
| 9 | ILM | `USB_EFUSE_ILIM` | no | yes |
| 10 | ITIMER | none | yes | yes |

### E1.3 U2-PWR1 — KEEP

| | |
| --- | --- |
| Designator | U2-PWR1 |
| MPN / LCSC | (seed MPN empty) INA226AIDGSR.1 / C49851 |
| epro Name | INA226 |
| Disposition | KEEP |

| Pin | Name | Net | NC | Live binding agrees |
| --- | --- | --- | --- | --- |
| 1 | A1 | `GND` | no | yes |
| 2 | A0 | `GND` | no | yes |
| 3 | Alert | `INA_ALERT` | no | yes |
| 4 | SDA | `I2C_SDA` | no | yes |
| 5 | SCL | `I2C_SCL` | no | yes |
| 6 | VS+ | `3V3` | no | yes |
| 7 | GND | `GND` | no | yes |
| 8 | VBUS | `INA_KELVIN_N` | no | yes |
| 9 | VIN− | `INA_KELVIN_N` | no | yes |
| 10 | VIN+ | `INA_KELVIN_P` | no | yes |

### E1.4 RSH1-PWR1 — KEEP

The archive symbol exposes **two** pins only. A four-terminal kelvin map was not proven.

| | |
| --- | --- |
| Designator | RSH1-PWR1 |
| Part / LCSC | WSHP2818R0100FEA.1 / C4274345 |
| epro Name | 10mohm |
| Disposition | KEEP |

| Pin | Net |
| --- | --- |
| 1 | `5V_PROTECTED` |
| 2 | `5V_SYS` |

Kelvin taps are separate parts `RINA_P-PWR1` / `RINA_N-PWR1` (10 Ω), not extra RSH1 pins.

### E1.5 J1 CC Rd pair — KEEP

| Designator | MPN / LCSC | Value | Pin 1 | Pin 2 | Disposition |
| --- | --- | --- | --- | --- | --- |
| RCC1-PWR1 | RC0402FR-075K1L / C105872 | 5.1 kΩ | `USB_CC1` | `GND` | KEEP |
| RCC2-PWR1 | RC0402FR-075K1L / C105872 | 5.1 kΩ | `USB_CC2` | `GND` | KEEP |

These are J1's Rd. They are not J7's.

### E1.6 J1 CC sense / ADC taps — KEEP

Values are `TUNE_TBD`, BOM no, Convert to PCB yes. MPN/LCSC empty on the epro; `part_id` is `RC0402FR-0710KL.1`.

| Designator | Pin 1 | Pin 2 | Disposition |
| --- | --- | --- | --- |
| RCC1S-PWR1 | `USB_CC1` | `USB_CC1_ADC_TAP` | KEEP |
| RCC1B-PWR1 | `USB_CC1_ADC_TAP` | `GND` | KEEP |
| RCC2S-PWR1 | `USB_CC2` | `USB_CC2_ADC_TAP` | KEEP |
| RCC2B-PWR1 | `USB_CC2_ADC_TAP` | `GND` | KEEP |

`USB_CC1_ADC_TAP` members: RCC1S.2, RCC1B.1 only. `USB_CC2_ADC_TAP` members: RCC2S.2, RCC2B.1 only. No RT/S3 ADC ball is on those nets in this archive. Destination of the tap is **UNKNOWN** beyond the divider.

### E1.7 J1 series USB resistors — RETARGET

| Designator | MPN / LCSC | Value | Pin 1 | Pin 2 | Disposition |
| --- | --- | --- | --- | --- | --- |
| RUSB_DP-PWR1 | RC0402FR-070RL / C106231 | 0 Ω | `USB_DP_PROT` | `USB_DP_RT` | RETARGET |
| RUSB_DN-PWR1 | RC0402FR-070RL / C106231 | 0 Ω | `USB_DN_PROT` | `USB_DN_RT` | RETARGET |

They stay as physical parts until the hub US pair is placed. Their far-side nets today are RT, not a stub.

### E1.8 J1 VBUS capacitors

| Designator | Part / LCSC | epro Name | Pin 1 | Pin 2 | Role | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| C1-PWR1 | GRM21BR61E226ME44L.1 / C86816 | 22uF | `5V_USB` | `GND` | J1 VBUS bulk | KEEP |
| C2-PWR1 | GRM21BR61E226ME44L.1 / C86816 | 22uF | `5V_PROTECTED` | `GND` | eFuse OUT, not J1 VBUS | KEEP |

No other capacitor sits on `5V_USB` in this archive.

### E1.9 eFuse programming parts — KEEP

| Designator | MPN or Name / LCSC | Pin 1 | Pin 2 | Net role |
| --- | --- | --- | --- | --- |
| R1-PWR1 | RNCF0402BTC1K24 / C2491273; Name 1.24k | `USB_EFUSE_ILIM` | `GND` | ILIM |
| R2-PWR1 | Name 100k / C60491 | `USB_EFUSE_EN` | `USB_EFUSE_OVLO` | EN–OVLO link |
| R63-PWR1 | Name 1.05M / C477184 | `5V_USB` | `USB_EFUSE_EN` | EN from VBUS |
| R64-PWR1 | Name 287k / C327358 | `USB_EFUSE_OVLO` | `GND` | OVLO |
| R65-PWR1 | Name 274k / C185435 | `5V_PROTECTED` | `USB_EFUSE_PGTH` | PGTH |
| R66-PWR1 | Name 100k / C60491 | `USB_EFUSE_PGTH` | `GND` | PGTH |
| R67-PWR1 | Name 10k / C60490 | `3V3` | `PWR_ENTRY_PG_RT_IOMUX_TBD` | PG pull-up |
| C67-PWR1 | Name 2.2nF / C77022 | `USB_EFUSE_DVDT` | `GND` | dV/dt |

INA support on the same island (KEEP, not eFuse programming):

| Designator | Value / LCSC | Pin 1 | Pin 2 |
| --- | --- | --- | --- |
| R3-PWR1 | Name 10k / C60490 | `3V3` | `INA_ALERT` |
| R4-PWR1 | Name 4.7k / C105871 | `I2C_SDA` | `3V3` |
| C3-PWR1 | Name 100nF / C71629 | `3V3` | `GND` |
| C4-PWR1 | Name 100nF / C71629 | `3V3` | `GND` |
| CINA_DIFF-PWR1 | 100nF GRM155R71C104KA88D / C71629 | `INA_KELVIN_P` | `INA_KELVIN_N` |
| RINA_P-PWR1 | 10 Ω RC0402FR-0710RL / C138066 | `5V_PROTECTED` | `INA_KELVIN_P` |
| RINA_N-PWR1 | 10 Ω RC0402FR-0710RL / C138066 | `5V_SYS` | `INA_KELVIN_N` |

No second 4.7 kΩ on `I2C_SCL` was found in this PWR1 set. That is a note, not a guess that one exists elsewhere.

### E1.10 Leftover rail TVS — DELETE from physics

| | |
| --- | --- |
| Designator | DVBUS-PWR1 |
| MPN / LCSC | SMF5.0A / C2758488 |
| Part | K1_SMF5V_TVS.1 |
| BOM | yes |
| Convert to PCB | **no** |
| Pin 1 K | `5V_USB` |
| Pin 2 A | `GND` |
| Disposition | **DELETE** from the placed island. This is the leftover rail TVS. Independent audit already holds `Convert to PCB = no`. |

D1 is not this leftover.

---

## E2. J7 island — DELETE after the new path exists

Every listed J7-island part still exists except `FB4-ESP`.

| Designator | Still exists | MPN / LCSC / part | Pins and nets | Disposition |
| --- | --- | --- | --- | --- |
| J7-ESP | yes | USB4105-GF-A / C3020560 | full table below | DELETE |
| U10-ESP | yes | USBLC6-2SC6 / C323793 | full table below | DELETE |
| C43-ESP | yes | epro Name `TUNE_TBD / DNP`; supplier field records `GRM1555C1H101JA01D.1` (not a C-code); `part_id` `GRM155R71C104KA88D.1`; BOM no | 1=`USB_DP_S3`, 2=`GND` | DELETE |
| C44-ESP | yes | same as C43 | 1=`USB_DM_S3`, 2=`GND` | DELETE |
| R71-ESP | yes | Name 100k; epro supplierId C60491; seed LCSC empty; `RC0402FR-07100KL.1` | 1=`S3_VBUS`, 2=`ESP_USB_VBUS_SENSE` | DELETE |
| R72-ESP | yes | Name 150k; supplierId C93947; `RC0402FR-0710KL.1` | 1=`ESP_USB_VBUS_SENSE`, 2=`GND` | DELETE |
| R73-ESP | yes | Name 22R / C114765; `RC0402FR-0722RL.1` | 1=`USB_DP_ESD`, 2=`USB_DP_S3` | DELETE |
| R74-ESP | yes | Name 22R / C114765; `RC0402FR-0722RL.1` | 1=`USB_DM_ESD`, 2=`USB_DM_S3` | DELETE |
| R21-ESP | yes | Name 5.1k / C105872; `RC0402FR-075K1L.1` | 1=`USB_CC1`, 2=`GND` | DELETE |
| R22-ESP | yes | Name 5.1k / C105872; `RC0402FR-075K1L.1` | 1=`USB_CC2`, 2=`GND` | DELETE |
| FB4-ESP | **no** | searched epro designators, seed identity, census list | ABSENT | not a delete |

`FB6-ESP` exists (BLM21PG221SN1D / C85840) but it is **not** J7 USB. Pin 1=`3V3`, pin 2=`3V3_S3_FILTERED`. KEEP with the S3 module.

### E2.0 J7-PWR — J7-ESP every pin — DELETE

| Pin | Symbol name | Net | NC | Disposition |
| --- | --- | --- | --- | --- |
| A4 | VBUS | `S3_VBUS` | no | DELETE |
| A9 | VBUS | `S3_VBUS` | no | DELETE |
| B4 | VBUS | `S3_VBUS` | no | DELETE |
| B9 | VBUS | `S3_VBUS` | no | DELETE |
| A1 | GND | `GND` | no | DELETE with part |
| A12 | GND | `GND` | no | DELETE with part |
| B1 | GND | `GND` | no | DELETE with part |
| B12 | GND | `GND` | no | DELETE with part |
| A5 | CC1 | `USB_CC1` | no | DELETE (collision member) |
| B5 | CC2 | `USB_CC2` | no | DELETE (collision member) |
| A6 | DP1 | `USB_DP` | no | DELETE |
| B6 | DP2 | `USB_DP` | no | DELETE |
| A7 | DN1 | `USB_DM` | no | DELETE |
| B7 | DN2 | `USB_DM` | no | DELETE |
| A8 | SBU1 | none | yes | DELETE; waiver T24 |
| B8 | SBU2 | none | yes | DELETE; waiver T24 |
| 1 | EH | `GND` | no | DELETE with part |
| 2 | SHIELD | `GND` | no | DELETE with part |
| 3 | SHIELD | `GND` | no | DELETE with part |
| 4 | SHIELD | `GND` | no | DELETE with part |
| A2 A3 A10 A11 B2 B3 B10 B11 | — | ABSENT-FROM-SYMBOL | — | not present |

J7 SuperSpeed contacts are the same ABSENT-FROM-SYMBOL set as J1.

### E2.0b U10-ESP every pin — DELETE

| Pin | Name | Net | NC | Disposition |
| --- | --- | --- | --- | --- |
| 1 | 1 | `USB_DP` | no | DELETE |
| 2 | 2 | `GND` | no | DELETE |
| 3 | 3 | `USB_DM` | no | DELETE |
| 4 | 4 | `USB_DM_ESD` | no | DELETE |
| 5 | 5 | `S3_VBUS` | no | DELETE |
| 6 | 6 | `USB_DP_ESD` | no | DELETE |

### E2.0c Nets unique to J7 (still present)

| Net | Members | After J7 delete |
| --- | --- | --- |
| `S3_VBUS` | J7 A4/A9/B4/B9, U10.5, R71.1 | must go. U9.8 sense must RETARGET off this divider. |
| `USB_DP` | J7 A6/B6, U10.1 | must go |
| `USB_DM` | J7 A7/B7, U10.3 | must go |
| `USB_DP_ESD` | U10.6, R73.1 | must go |
| `USB_DM_ESD` | U10.4, R74.1 | must go |

`USB_DP_S3` / `USB_DM_S3` are **not** J7-only. They already include U9.14 / U9.13. Those nets RETARGET to hub DN2; they are not deleted with J7.

### E2.1 CC collision — PROVEN

`USB_CC1` members:

| Member | Island |
| --- | --- |
| J1-PWR1 A5 | J1 KEEP |
| RCC1-PWR1.1 | J1 KEEP |
| RCC1S-PWR1.1 | J1 KEEP |
| J7-ESP A5 | J7 DELETE |
| R21-ESP.1 | J7 Rd DELETE |

`USB_CC2` members:

| Member | Island |
| --- | --- |
| J1-PWR1 B5 | J1 KEEP |
| RCC2-PWR1.1 | J1 KEEP |
| RCC2S-PWR1.1 | J1 KEEP |
| J7-ESP B5 | J7 DELETE |
| R22-ESP.1 | J7 Rd DELETE |

Two 5.1 kΩ Rd pairs share one CC pair. That is a Type-C sink defect. Disposition: J1 keeps `USB_CC1` / `USB_CC2`. J7 Rd and J7 CC pins are deleted. After delete, membership must be J1-only (J1 + RCC1/RCC2 + sense series).

### E2.2 T24 — J7 SBU waivers become stale

Live-lane `canonical-core-val-r0/DRC-WAIVERS.json` has one waiver:

```text
kind: floating_pins
match: J7-ESP\.(A8|B8)
date: 2026-08-28
```

After J7 delete that match hits nothing and the waiver is stale. **Schedule T24** to remove or rewrite it. Do not edit that file in this Phase E write.

---

## E3. RT USB balls

U6-RTC is two units, one device (`MIMXRT1062DVJ6B` / C3216699). USB balls below are on part `MIMXRT1062DVJ6B.2`. Independent audit postconditions agree on L8, M8, N6.

| Ball | Symbol name | Net | NC | Disposition |
| --- | --- | --- | --- | --- |
| L8 | USB_OTG1_DP | `USB_DP_RT` | no | RETARGET to hub DN1; ball KEEP |
| M8 | USB_OTG1_DN | `USB_DN_RT` | no | RETARGET to hub DN1; ball KEEP |
| N6 | USB_OTG1_VBUS | `5V_PROTECTED` | no | RETARGET later to attach-valid; today it is always-on protected 5 V |
| N12 | USB_OTG1_CHD_B | none | yes | KEEP, NC |
| N7 | USB_OTG2_DN | none | yes | KEEP, NC |
| P6 | USB_OTG2_VBUS | none | yes | KEEP, NC |
| P7 | USB_OTG2_DP | none | yes | KEEP, NC |
| K8 | VDD_USB_CAP | `VDD_USB_CAP` | no | KEEP (PHY cap net, not OTG1 data) |

**CUSBVBUS-RTC** — KEEP. MPN GRM155R61A105KE15D / C76999, value **1 µF**, BOM yes, PCB yes. Pin 1=`5V_PROTECTED`, pin 2=`GND`. This is the 1 µF on OTG1 VBUS.

### Geometry extras — not treated as USB intent

The same on-segment join also put `USB_DN_RT` on `U6 M6` (ONOFF, NC flag set) and `U6 M7` (POR_B, also on `POR_B`). It put `5V_PROTECTED` on `U6 N4` (GPIO_SD_B1_09, also `FLEXSPI_D1`) and `U6 N5` (VSS, also `GND`). Those look like wire-cross hits next to N6/M8. They are recorded, not used as USB membership. A second method (official `.epro` export with library pins, or a live pin read of G2.1) is required before anyone treats M6/M7/N4/N5 as USB.

### Leftover OPT USB audio

| Item | Proven | Disposition |
| --- | --- | --- |
| Net `OPT_USB_AUD` | yes. Members: `J11-VAL.2`, `R56-VAL.1` | leftover KEEP (DNP experiment) |
| Net `OPT_USB_AUD_RT` | **absent** from seed net list and from epro membership | do not invent |
| R56-VAL | DNP, BOM no, PCB no. Pin 1=`OPT_USB_AUD`, pin 2=`RT_USB_AUD_STRAP_IOMUX_TBD` (single-endpoint named hold) | KEEP as leftover DNP |
| J11-VAL | PREC006SAAN-RC / C9900007627. Pin 2=`OPT_USB_AUD`. Other pins: 1=`OPT_BOOT_REC`, 3=`OPT_MCLK`, 4=`OPT_S3_LOG`, 5=`3V3`, 6=`GND` | KEEP (validation header, not J7) |

R57-VAL is MCLK DNP, not USB.

---

## E4. S3 USB and recovery — KEEP module and J6

U9-ESP: ESP32-S3-WROOM-1-N16R8 / C2913202 (`ESP32-S3-WROOM-1(N16R8).1`). Module KEEP.

### U9 USB pins

| Pin | Symbol name | Net | Disposition |
| --- | --- | --- | --- |
| 14 | IO20 | `USB_DP_S3` | RETARGET to hub DN2; pin KEEP |
| 13 | IO19 | `USB_DM_S3` | RETARGET to hub DN2; pin KEEP |
| 8 | IO15 | `ESP_USB_VBUS_SENSE` | RETARGET off `S3_VBUS` after J7 delete; pin KEEP |

`USB_DP_S3` members today: U9.14, R73.2, C43.1. `USB_DM_S3`: U9.13, R74.2, C44.1. `ESP_USB_VBUS_SENSE`: U9.8, R71.2, R72.1.

GPIO15 / GPIO19 / GPIO20 match the requested map. The symbol names are IO15 / IO19 / IO20.

### J6-ESP — KEEP, do not touch

| Pin | Net |
| --- | --- |
| 1 | `GND` |
| 2 | `3V3` |
| 3 | `ESP_UART0_TX` |
| 4 | `ESP_UART0_RX` |
| 5 | `ESP_EN` |
| 6 | `ESP_GPIO0` |

MPN PREC006SAAN-RC / C9900007627. epro Name `RECOVERY 1x6`.

`ESP_UART0_TX` also reaches `R58-VAL.2` (0 Ω option) and U9.37. That is not a USB-UART bridge IC. Do not touch J6.

### No USB-UART bridge IC

Searched every seed identity blob for CP210, CH340, CH344, FT232, FT2232, USB-UART, CP211. Hits: **none**. No such designator on the 252-name G2.1 list.

---

## E5. Designator allocator

G2.1 sheet unique designators: **252** (epro, seed and census-after-reopen agree).

### Every existing U*

U1-PWR1, U2-PWR1, U3-PWR2, U5-PWR2, U6-RTC, U7-RTC, U8-RTDBG, U9-ESP, U10-ESP, U11-AUD, U12-NFC, U13-MOT, U14-LED, U15-LED, U16-VAL, U17-PWR2.

U4 is **absent** (retired). Do not reuse U4.

### Every existing R*

R1-PWR1, R2-PWR1, R3-PWR1, R4-PWR1, R5-PWR2, R6-PWR2, R7-PWR2, R9-PWR2, R10-RTC, R11-RTC, R12-RTC, R13-RTDBG, R14-RTDBG, R15-RTDBG, R16-RTDBG, R17-RTDBG, R18-RTDBG, R19-ESP, R20-ESP, R21-ESP, R22-ESP, R23-ESP, R24-ESP, R25-ESP, R26-ESP, R27-ESP, R28-AUD, R29-AUD, R31-AUD, R32-AUD, R33-AUD, R34-AUD, R35-AUD, R36-AUD, R37-AUD, R38-AUD, R39-AUD, R40-AUD, R41-AUD, R42-NFC, R44-MOT, R45-MOT, R46-MOT, R47-MOT, R48-MOT, R49-MOT, R51-LED, R52-LED, R53-LED, R54-LED, R55-VAL, R56-VAL, R57-VAL, R58-VAL, R59-VAL, R60-VAL, R61-VAL, R62-VAL, R63-PWR1, R64-PWR1, R65-PWR1, R66-PWR1, R67-PWR1, R68-RTDBG, R69-RTDBG, R70-RTC, R71-ESP, R72-ESP, R73-ESP, R74-ESP, R75-PWR2, R76-NFC, RCC1-PWR1, RCC1B-PWR1, RCC1S-PWR1, RCC2-PWR1, RCC2B-PWR1, RCC2S-PWR1, RILIM-LED, RINA_N-PWR1, RINA_P-PWR1, RLED_ENL_PD-LED, RLED_ENR_PD-LED, RLED_PD0-LED, RLED_PD1-LED, RNTC_L-LED, RNTC_R-LED, RSH1-PWR1, RT1-LED, RT2-LED, RUSB_DN-PWR1, RUSB_DP-PWR1.

Numeric holes: R8, R30, R43, R50. Do not reuse them for the hub. R8 is a known retired leftover-support number.

### Every existing C*

C1-PWR1, C2-PWR1, C3-PWR1, C4-PWR1, C5-PWR2 … C17-PWR2, C18-RTC … C34-RTC, C35-RTDBG … C38-RTDBG, C39-ESP … C45-ESP, C46-AUD … C53-AUD, C54-NFC … C61-NFC, C62-MOT, C63-MOT, C64-LED, C65-LED, C66-VAL, C67-PWR1, C69-RTC … C89-RTC, C90-AUD, C91-AUD, C92-NFC … C99-NFC, C910-NFC, C911-NFC, C912-NFC, CINA_DIFF-PWR1, CMICREG-PWR2, CMOT-BULK, CUSBVBUS-RTC, CVDR1-NFC, CVDR2-NFC.

C68 is absent (retired). Do not reuse it.

### Every existing Y*

Y1-RTDBG, Y2-NFC.

### Every existing J*

J1-PWR1, J2-LED, J3-LED, J4-RTDBG, J5-RTDBG, J6-ESP, J7-ESP, J8-AUD, J9-AUD, J10-NFC, J11-VAL.

### Suffix and next-free block

| Family | Used numbers | Next free sequential | Notes |
| --- | --- | --- | --- |
| U | 1–3, 5–17 | **U18** | U4 retired. Proposed hub start **U20** so U18/U19 stay spare. |
| R | 1–7, 9–29, 31–42, 44–49, 51–76 plus named RCC/RUSB/… | **R77** | Do not fill R8/R30/R43/R50. |
| C | 1–67, 69–99, 910–912 plus named | **C100** | Do not fill C68. C910+ are NFC, not a cue to use C913. |
| Y | 1, 2 | **Y3** | |
| J | 1–11 | **J12** | Hub island does not need a new receptacle. Do not reuse J7 after delete. |

Suffix `-USB`: **no collision**. Suffix `-HUB`: **no collision**. `RUSB_*` and `CUSBVBUS-RTC` are not `-USB` suffixes. Use **-USB**.

### Reserved list — not placed

| Reserved | Intended part | Status |
| --- | --- | --- |
| U20-USB | USB2422 | reserved, not placed |
| U21-USB | TPS2052B | reserved, not placed |
| U22-USB | TPS7A2550DRVR / C2876265 (F6 validity LDO) | reserved, named — `H0f-CLOSE.md` |
| U23-USB | TLV7031DBVR / C2869832 (KILL-B comparator) | reserved, named |
| U24-USB | SN74LVC1G08DBVR / C7666 (EN1 AND) | reserved, named |
| U25-USB | SN74LVC1G08DBVR / C7666 (EN2 AND) | reserved, named |
| Y3-USB | 24 MHz hub crystal | reserved, not placed |
| R77-USB … R96-USB | hub straps, 90 Ω pairs, VBUS_DET, POR, XOR pads | reserved block |
| R78/R79 | VBUS_DET 100 k / 100 k | reserved, named in `H0f-CLOSE.md` |
| R80-USB | 4.7 kΩ F8 bleeder | reserved, named |
| R81–R87 | KILL-B + GPIO15 + OUT1/OUT2 bleeders | reserved, named |
| C100-USB … C119-USB | hub decouple, crystal load, port caps | reserved block |
| C120-USB | 22 µF on `5V_PROTECTED` | reserved, named |
| C121-USB | 100 nF at U22 IN (not 1 µF) | reserved, named |
| C122-USB | 2.2 µF on `5V0_USB_VALID` | reserved, named |
| C123–C125 | 100 nF at U23/U24/U25 | reserved, named |
| D2-USB | hub-side ESD only if D1 is not reused for US | reserved empty |

Do not place any of these in this phase. New parts get new numbers. Do not recycle J7, U10, R21, R22, R71–R74.

---

## Exit — pin census with KEEP / DELETE / RETARGET

### J1-PWR1

Every symbol pin named in E1.0. KEEP on power, GND, CC, SBU-NC, shell. RETARGET on A6/B6/A7/B7. SuperSpeed ABSENT-FROM-SYMBOL.

### J7-ESP

Every symbol pin named in E2.0. DELETE after the new path exists.

### U10-ESP

Pins 1–6 named in E2.0b. DELETE.

### U9 USB

Pins 8, 13, 14 named in E4. RETARGET. Module KEEP.

### U6 OTG1

L8, M8, N6 RETARGET. N12 KEEP NC. OTG2 N7/P6/P7 KEEP NC.

### CC nets

| Net | Today | After J7 Rd delete |
| --- | --- | --- |
| `USB_CC1` | J1 A5 + RCC1 + RCC1S + **J7 A5 + R21** | J1-only |
| `USB_CC2` | J1 B5 + RCC2 + RCC2S + **J7 B5 + R22** | J1-only |

Collision **proven**. J1 keeps the net names.

### Counts

**Designators:** KEEP = the part stays. DELETE = the part goes after the new path exists. RETARGET = the part stays and its far-side net changes.

| Disposition | Count | Designators |
| --- | --- | --- |
| KEEP | **35** | J1-PWR1, D1-PWR1, U1-PWR1, U2-PWR1, RSH1-PWR1, RCC1-PWR1, RCC2-PWR1, RCC1S-PWR1, RCC1B-PWR1, RCC2S-PWR1, RCC2B-PWR1, C1-PWR1, C2-PWR1, R1-PWR1, R2-PWR1, R63-PWR1, R64-PWR1, R65-PWR1, R66-PWR1, R67-PWR1, C67-PWR1, R3-PWR1, R4-PWR1, C3-PWR1, C4-PWR1, CINA_DIFF-PWR1, RINA_P-PWR1, RINA_N-PWR1, U6-RTC, CUSBVBUS-RTC, R56-VAL, J11-VAL, U9-ESP, J6-ESP, FB6-ESP |
| DELETE | **11** | J7-ESP, U10-ESP, C43-ESP, C44-ESP, R71-ESP, R72-ESP, R73-ESP, R74-ESP, R21-ESP, R22-ESP, DVBUS-PWR1 |
| RETARGET | **2** | RUSB_DP-PWR1, RUSB_DN-PWR1 |
| ABSENT | **2** | FB4-ESP; net `OPT_USB_AUD_RT` |

J1, U6 and U9 stay. Some of their USB pins still RETARGET (below). Those chips are not deleted.

**Named pins in the exit tables:**

| Disposition | Count | What |
| --- | --- | --- |
| KEEP | J1 16 + J6 6 + U6 N12/K8 + OTG2 3 | power, GND, CC, SBU-NC, shell, recovery, NC OTG2 |
| DELETE | J7 20 + U10 6 | whole J7 island connector and ESD |
| RETARGET | **12** | J1 A6, B6, A7, B7; RUSB_DP; RUSB_DN; U6 L8, M8, N6; U9.14, U9.13, U9.8 |
| ABSENT-FROM-SYMBOL | **8** | J1 SuperSpeed A2/A3/A10/A11/B2/B3/B10/B11 (same eight missing on J7) |

### Verdicts the parent asked for

| Question | Answer |
| --- | --- |
| Path of this file | `evidence/VAL-G2-2026-08-28/dec-usb-hub/CENSUS.md` |
| KEEP / DELETE / RETARGET (designators) | **35 / 11 / 2** |
| RETARGET (named pins) | **12** |
| CC collision proven | **yes** — `USB_CC1` and `USB_CC2` each include J1 Rd and J7 Rd |
| Next-free designator block | U20-USB / U21-USB / U22-USB / U23-USB / U24-USB / U25-USB / Y3-USB / R77-USB…R96-USB / C100-USB…C122-USB / D3-USB / D4-USB / J12-USB (U18/U19 stay spare) |
