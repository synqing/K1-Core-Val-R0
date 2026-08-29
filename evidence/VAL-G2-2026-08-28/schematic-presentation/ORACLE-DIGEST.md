# G2.1 electrical digest — published, not frozen

Date: 2026-08-28

This is **not** an official freeze. Official freeze is a Captain
decision-register stamp and requires item-level GUI ERC from review project
`dcd7e3cab2a24b9aa6e531d2b62e1b6f`.

## What happened

The saved EasyEDA-normalised review source
(`review-source-after-reopen.json`, host hash `2352834:a75b5884`) was extracted
into a hashed electrical digest. Geometry, wire segmentation, labels and domain
graphics were excluded.

## What is true now

```text
official_freeze          = False
serialization            = V3_TYPED_RECORD
source_document_uuid     = 1435cb46f39e48c8a8aadbb84ca81603
electrical_digest_sha256 = 0651019a5a3453895870c9de2c74e8ab30e3cd6a085935c8a66950454f28962f
designators              = 252
named_nets               = 159
nc                       = 95
bound_pins               = 105 (PARTIAL_LIVE_BINDINGS)
u4_census                = OK (U4-era absent; U1-PWR1 and U17-PWR2 present)
```

`--official-freeze` was attempted and **refused**: unclassified ERC fatals remain.

Machine record: `g2.1-electrical-digest.json`.
