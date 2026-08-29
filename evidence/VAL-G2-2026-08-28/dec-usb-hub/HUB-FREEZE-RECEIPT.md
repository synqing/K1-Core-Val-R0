# HUB-FREEZE-RECEIPT — CLOSED 2026-08-29

```text
H_FREEZE              = CLOSED
PROJECT               = 41c8e6523576456582ea35958b3684ed
PAGE                  = 1435cb46f39e48c8a8aadbb84ca81603
LAST_CLOSED           = T25-tap-split-wire-2026-08-29
TAP_SHORT_GONE        = yes
TAP_VBUS_PARENT       = 54b8d6c7efc61c4c
TAP_REF_PARENT        = 766b3b0368bbe7cc
BAR_1460_1580_Y1010   = absent
SOURCE_HASH           = 2981994:272660f1
DIGEST_SHA256         = 7f31e8164cd9cab1a1637569811bb66915036ec8888fb656b9c18a0b90137258
FROZEN_FILE           = anchors/hub-electrical-digest.frozen.json
PREMATURE_FILE        = not used
ERC_UNCLASSIFIED      = 0
ERC_REAL_DEFECTS      = 0
HUB_CENSUS            = ok
LIVE_64325d0e         = not mutated
HOST_DRC_FATALS       = 14 (not classified; count-only sch_Drc.check)
```

What happened. T25 deleted the merged TAP wire and gave `TAP_VBUS` and
`TAP_REF` their own primitives. Independent ERC then reported zero real
defects and zero unclassified fatals. The hub digest was frozen from
`hub-source-post-T25.json`.

What is true now. `TAP_REF` is a named net of its own. The 1460–1580 bar
at y=1010 is gone. The premature digest stays parked.

G2.2 live sheet. The UUID that actually has a schematic page is
`54d2a25bce4b44c3af878e8b91af3554` page `1435cb46f39e48c8a8aadbb84ca81603`
(see `G2.2-IMPORT-RECEIPT.md`). Husk `f0f6cd233d69411ea478de1037da28fc` still
holds the reserved friendly name and has no usable sheet. Offline freeze vs
reconstructed graph remains PASS. `JLC-SCH-READY` remains Captain-only.
