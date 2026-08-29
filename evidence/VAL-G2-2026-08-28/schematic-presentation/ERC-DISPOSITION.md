# ERC disposition — G2.1 review source

Date: 2026-08-28

Review EasyEDA **project UUID**: `dcd7e3cab2a24b9aa6e531d2b62e1b6f`.
Live canonical EasyEDA **project UUID**: `64325d0e55e0435abd018defb0089a9b` — not opened, not switched.

## What happened

The host still reports **9 fatals and 19 warnings** with no per-item text
(`erc/bridge-erc.json`). The EasyEDA window attached to this workstation is the
live product project. It was left alone. A GUI panel from the disposable review
project was therefore not captured.

An independent source census was run against the EasyEDA-normalised V3 dump
`review-source-after-reopen.json` and the G2.1 digest. That census names every
finding the source can support.

## What is true now

- Source-visible **real defects: 0**.
- `U4-PWR2` / `C68-PWR2` / `R8-PWR2` are absent.
- `U1-PWR1` and `U17-PWR2` are present.
- 95 intentional NC flags are present, including DEC-04 `RFO2`/`RFI2`, motion
  `INT2`, and U1 `ITIMER`.
- Named holds remain: `IOMUX_TBD`, `TUNE_TBD`, `VALIDATION_ONLY`, Convert-to-PCB=no
  on the empty-PCB parts, custom-footprint holds.
- The **9 host fatals stay unclassified** because the GUI panel is missing.
  Official freeze is refused.

Machine record: `erc-disposition.json`.

```text
unclassified_fatals = 9
real_defects_open = 0
gui_panel = NOT_CAPTURED_LIVE_WINDOW_IS_CANONICAL
```

## What is left

1. Captain or a later agent: open a *new* EasyEDA window on review project
   `dcd7e3ca…` without abandoning live `64325d0e…`.
2. Export the GUI ERC panel. Classify each of the 9 fatals and 19 warnings.
3. If any item is a real electrical defect, repair it once in the G2.1 graph and
   regenerate. Do not weaken ERC rules.
4. Only then may an official electrical-oracle freeze be stamped.
