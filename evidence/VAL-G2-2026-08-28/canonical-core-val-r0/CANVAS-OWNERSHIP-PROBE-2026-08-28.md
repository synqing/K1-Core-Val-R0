# Canvas ownership probe — 2026-08-28

Read-only. No EasyEDA call was made. Nothing was frozen.

## Verdict

**The canonical canvas is owned by another live operator. This operator did not take it.**

Canon `K1E-065` forbids two operators sharing one live canvas. Canon `F-20A` records that
freezing a legitimately authorised operator is itself a logged failure. Both applied, so the
correct action was to stand off and run every lane that needs no EasyEDA authority.

## Evidence

Gate state moved twice while this session was planning, with no action by this operator:

```text
05:12:11Z  state=READY               hash 489805:542305a0   164 ledger events
05:18:56Z  state=AWAITING_EVIDENCE   hash 490331:ca12d078   169 ledger events
           active tx = canonical-nfc-unused-nc-2026-08-28 (stage repair, scope NFC)
           blocking_reason = "Mutation exists; settled screenshot and visual inspection are required"
05:52:30Z  state=READY               hash 497055:82c17c12   170 ledger events
           last_closed = captain-nc-reconcile-2026-08-28
           preceded by STATE_QUARANTINED then STATE_RECONCILED at the same second
```

Source grew 489736 → 497055 characters (+7319) across that window.

Live operator process, uptime 14 h 45 m at probe time:

```text
PID 70163  node /opt/homebrew/bin/codex
PID 70166  .../codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex
```

Transports listening: MCP `127.0.0.1:19733`, EasyEDA CDP `127.0.0.1:9223`,
extension bridge `127.0.0.1:49620`. EasyEDA Pro 2.2.40.8 running, PID 2656.

The `TAKEOVER-RECEIPT.md` in this directory records Captain handing the canvas from Codex to
an operator earlier the same day. The evidence above is consistent with that Codex lane still
being active, not with an abandoned session.

## Consequence for the VAL-G2.1 programme

The write lane is stood down until Captain confirms the handover. Every other lane proceeds,
because none of them needs the canvas:

- pin-level vendor audits, BOM/CPL semantic audit — read the frozen denominator below
- authority, contract and source-register catch-up — no EDA surface at all
- connectivity oracle, DRC-log parser, false-green fixes — operate on files

## Frozen denominator

Parallel auditors read one shared, faithful extraction rather than each re-parsing 490 KB of
raw source. Produced by `harness/extract_frozen_denominator.py` from the newest on-disk
pre-write snapshot:

```text
snapshot     = snapshots/canonical-nfc-unused-nc-2026-08-28-before.json
source_hash  = 489736:464c27d4
out          = frozen-denominator-489736/{index.json, source.txt, bom_flat.csv}

records 6631 · components 230 · designators 228 · undesignated 1
duplicate designators {U6-RTC: 2} · wires 675 · named nets 143
unnamed wires 0 · NO_CONNECT marks 12
```

Live has since moved to `497055:82c17c12`. **Every audit finding is a proposal.** The single
writer reconfirms against live before changing anything.

## Offline cross-check anchors, now inside the repo

```text
anchors/ProPrj_K1-Core-Val-R0_2026-08-28.epro  267604 B
  sha256 06c5ac3800a5397aa07343fb99a1c0c895960050a6878695a5653cef50404828
  re-verified against Captain's handover value — identical. 222 components, 8 behind the dump.

anchors/schDrcLog_2026-08-28.txt                69267 B
  sha256 51080f43bd981015... (see anchors/SHA256SUMS.txt)
  Captain's EasyEDA DRC run, 422 lines. Until now the only real connectivity detector in the
  programme, and consumed by hand-transcription into Python dict literals in four scripts.
```

## Independent measurements taken by the orchestrator

Not delegated — these gate later decisions, so they were re-derived directly.

**Net-to-geometry binding.** Union-find over wire-segment endpoints, all 143 named nets:

```text
nets whose name spans more than one disjoint island : 142
nets that are a single joined island                :   1
GND 186 islands / 186 wires · 3V3 90/90 · 1V15_CORE 18/18 · I2C_SDA 8/8 · POR_B 5/5
```

Islands equal wire count for essentially every net. This is the sheet's construction method,
not 142 defects: each pin gets a 20-unit stub carrying a `NET` attribute, so pins share a net
by sharing a *name* and never by touching. `SINGLE-SHEET-CONTRACT.md` permits labelled trunks
for global rails and major shared buses, so `GND` and `3V3` are legitimate — but with 142 of
143 nets built this way, almost nothing on the sheet is drawn as a real wire, which is the
condition that contract's own sentence warns against.

The consequence for tooling: a fragmentation counter would report 142 failures and be as
useless as a checker that always passes. The property worth measuring is the **label-to-pin
binding** — how many distinct component *pins* a net actually reaches — which is what
`K1E-016` means and what the EasyEDA DRC already reports as *"single network connected to only
one component pin."*

**Confirmed defects.**

```text
RT_RESET_REQ_N   carried by exactly one wire — a genuine single-endpoint net
NFC_RFO1         exists; NFC_RFO2, NFC_RFI1, NFC_RFI2 do not exist at all
                 → only half the differential RF front end is represented (P0-G)
USB_DP/USB_DM    exist with _ESD and _S3 variants; no RT-side variant exists
                 → consistent with Captain's finding that no USB data pair reaches RT1062
OPT_USB_AUD      2 endpoints, via R56-VAL to OPT_USB_AUD_RT — an option strap, not D+/D−
```

**BOM identity, sampled directly from the source.**

```text
R1-PWR1  Name=1.33k  Manufacturer Part=RC0402FR-071K33L  Supplier Part=C276261
         supplierId=C60490  ← the LCSC code for the 10 k RC0402FR-0710KL
R8-PWR2  Name=3.48k  Manufacturer Part=RC0402FR-073K48L  Supplier Part=C185418
         supplierId='RC0402FR-0710KL.1'  ← an MPN sitting in the supplierId field
R56-VAL  Name=DNP    Manufacturer Part='RC0402FR-07DNP'  ← a fabricated MPN
         bound to the real 10 k device identity
coverage Manufacturer present on 37 of 230 · Manufacturer Part on 24 of 230
         → roughly 206 parts carry no MPN at all
```

Component `Value` is empty across the sampled parts; the displayed value lives in `Name`.

> **Correction, same day.** This section first stated that no `Add into BOM` attribute appears
> anywhere in the schematic source. That was wrong, and the BOM audit lane corrected it with
> evidence. The attribute **does** exist, on four ATTR records — it ranks 44th of 213 distinct
> attribute keys, below the cut-off of the truncated census list this claim was read from. The
> error was reading a top-N print as if it were the whole set.
>
> ```text
> C43-ESP   Add into BOM='no'   Name='DNP / 100pF USB D+ TUNE'   <- genuine non-population
> C44-ESP   Add into BOM='no'   Name='DNP / 100pF USB D- TUNE'   <- genuine non-population
> C52-AUD   Add into BOM='no'   Name='DNP / 100pF MCLK TUNE'     <- genuine non-population
> ```
>
> A fourth record carries the same attribute for an entirely different and **opposite** reason,
> and listing it beside the three above was a reporting error that made it look like a DNP:
>
> ```text
> e3673     Add into BOM='no'   Name='FITTED'   MIMXRT1062DVJ6B.2
> ```
>
> That is the second symbol part of the **single** RT1062. Here the flag prevents the BOM from
> ordering the same chip twice — it means "already counted", not "do not fit". See the dedicated
> section below.
>
> Two consequences, both stronger than the original claim. First, the DNP exclusion mechanism is
> schematic-level and **works** — so the seven DNP-named resistors that lack the flag are a real
> defect measured against a working example three times over on the same sheet, not an inference.
> Second, the `e3673` entry independently confirms `U6-RTC` appearing twice is a legitimate
> multi-part symbol with its second part correctly excluded from the BOM, not a duplicate.

## Next allowed action

Captain confirms whether the Codex lane has finished. On confirmation, one operator closes any
open transaction with a settled pin-readable screenshot, reconciles the stamp, and begins the
repair queue. Until then the write lock stays with its current owner and is not contested.


---

## The RT1062 is ONE device, not two — measured, not assumed

Earlier passes of this document and its status reports described `U6-RTC` as "appearing twice"
and as a "duplicate designator", and asserted it was a legitimate multi-part symbol on the
strength of 98 + 98 = 196 matching the ball count. That was a plausible inference stated as a
checked fact. Here is the check.

**The two entries hold disjoint halves of the same package.**

```text
                       e3295                      e3673
anchor            (2315,4440) rot 0          (2250,3930) rot 90
balls             A1 .. G14   (rows A-G)     H1 .. P14   (rows H-P)
pin count         98                         98
ball overlap      0                          union = 196 = DVJ6B ball count
Device UUID       69a263214ca544edaed5248f1d7e5e69   -- identical
Symbol UUID       6b50fcab76dc45c3bb51cfd14e3e6973   -- identical
Unique ID         gge220                     gge220   -- identical
Supplier Part     MIMXRT1062DVJ6B.1          MIMXRT1062DVJ6B.2
Name              FITTED                     FITTED
Add into BOM      (absent)                   no
```

Zero shared ball designations, one shared `Unique ID`, and `.1`/`.2` part indices. This is one
`MIMXRT1062DVJ6B` drawn as two symbols because 196 balls are not legible on one. **Neither part is
DNC; both read `FITTED`.** `Add into BOM = no` on part 2 is required — without it the BOM would
order two RT1062s.

### The asymmetry that makes part 2 look like the "real" one

```text
e3295  (rows A-G)  25 of 98 balls wired   -- mostly GPIO banks, largely unused on this design
e3673  (rows H-P)  60 of 98 balls wired   -- XTALI/XTALO, FlexSPI, DCDC, VDD_HIGH, NVCC_PLL
```

Part 2 carries the crystal, boot flash, core power and PLL supplies, so it is far more densely
wired. That is expected for this package split and is not evidence of duplication.

### The finding this had been masking

```text
196 balls total - 85 wired (25 + 60) = 111 unconnected
EasyEDA DRC independently reports 111 floating pins on U6-RTC
```

Two independent methods agreeing to the ball. Many of the 111 will be legitimately unused GPIO,
but this is the **largest block of unaccounted pins on the sheet** and every one requires an
explicit disposition before VAL-G2 can close.

### Consequence for tooling

`harness/check_single_schematic.py` whitelists `duplicates == {"U6-RTC": 2}`, which reads as a
tolerated duplicate rather than a declared multi-part symbol. The connectivity oracle also keyed
pin data by Designator, silently dropping one of the two parts and manufacturing six false
"net reaches fewer than two pins" findings. Both should key by `componentPrimitiveId` and treat a
shared `Unique ID` with disjoint pin sets as one device, so this never reads as duplication again.
