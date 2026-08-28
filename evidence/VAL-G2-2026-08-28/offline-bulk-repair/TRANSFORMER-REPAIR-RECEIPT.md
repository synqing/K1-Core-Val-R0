# TRANSFORMER-REPAIR-RECEIPT

State: **ARCHIVE_REPAIRED_NOT_IMPORTED**

Date: 2026-08-28

## Provenance

- Input export: `ProPrj_K1-Core-Val-R0_2026-08-28-input-78245760.epro`
  - SHA256: `78245760ba3f824f0d585e5ca7d0488e86dc1761d39a08a0503484b0184d4893`
  - Source path: `/Users/spectrasynq/Downloads/ProPrj_K1-Core-Val-R0_2026-08-28.epro`
  - Bytes: 273846; mtime: 2026-08-28 16:54:54
  - Repo anchor `06c5ac38…` was not used
- Known-bad candidate (not imported): `1dd7d8156071e5b06163a9a3d28b22f24eab7e5ff62b2fa26ac59623c283cc54`
- Unpatched transformer: `86ecc12828da17a2c53ca1cea9fb91a813e6c118a4d4d9ab6fe18cf551f08475`
- Original auditor (bytes untouched): `90f109c3a4e7895cb67599902bebcc2605f63e39cbb78aa8c8deabe9ad743116`
- CLI auditor (hashed; `/mnt/data` script was not the evidence command): `f9825d035296cb62884313c35e408b2781015ebf9f9b06066176b8ba59419bd1`
- Patched transformer: `b5e460f745e0cef70b9108679df934426fc1fb454b2692b6aa68d1c7a8e0d782`

The CLI auditor was revised once before the official new-candidate run so retired (zero-endpoint) nets and named G3 holds are not false orphans. `1dd7…` still fails after that freeze.

## Regeneration

- Two patched runs, byte-identical
- New candidate SHA256: `3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7`
- Parked as `K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro`
- Not `1dd7d815…`

## Remnant disposition

- `C11-PWR2`: re-homed to `5V_SYS` (U17 input / LED supply bulk). Still present.
- `C68-PWR2`: removed (U4 dV/dt; TPS2561 has no DVDT).
- `R8-PWR2`: removed (U4 ILIM; U17 uses `RILIM-LED`). RQ-047 = `SUPERSEDED_BY_U4_REMOVAL`.
- `R67-PWR1`: follows U1.3 onto `PWR_ENTRY_PG_RT_IOMUX_TBD`.
- `U4-PWR2`: removed. Shared LED eFuse. Not USB.
- `U1-PWR1`: remains. Inlet/trunk eFuse.
- `U17-PWR2`: present. Per-branch LED protection.

## Strengthened audit

- `1dd7…` FAIL: leftover `5V_LED_COMMON` / `LED_EFUSE_DVDT` / `LED_EFUSE_ILIM` / `USB_EFUSE_PG`, and U1.3 not sharing a net with R67.
- `3db861a3…` PASS: `independent-audit-3db861a3.json`, errors empty.
- PCB member `PCB/59bef7e87cff4cd580561703b62d8c19.epcb` unchanged.
- RQ-048 seven refs exact. `DVBUS-PWR1` and `U17-PWR2` Convert to PCB = no.
- U16.5 on `3V3`. U1.3 and R67.2 both on `PWR_ENTRY_PG_RT_IOMUX_TBD`.

## Restamped census (new archive)

- Archive members: 155 → 157
- Schematic records: 7317
- Component primitives: 255
- Designator attributes: 253
- Unique designators: 252
- Wires: 773
- NC yes: 106
- Added symbols: `SYMBOL/414ba6da3ac51b406da3fbb13e589c49.esym` (TPS2561), `SYMBOL/99ae5a8d90c97ad043c45f352e4c1422.esym` (SMF5.0A)

Live canonical remains `64325d0e55e0435abd018defb0089a9b`. Qualification `09e9c541…` stays dead. This receipt does not import and does not promote.
