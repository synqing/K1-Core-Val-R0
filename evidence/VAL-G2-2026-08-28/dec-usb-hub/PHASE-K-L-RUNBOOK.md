# Phase K–L — hub freeze then G2.2 (after T24)

Run only on disposable `41c8e6523576456582ea35958b3684ed`. Never live `64325d0e`.
Never beautify `dcd7e3ca`. Hub-lane gate flags before every verb.

## K — ERC then official freeze

```bash
# Item-level GUI log (MCP run_schematic_drc verbose / schDrcResult text)
# → evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/schDrcLog-hub.txt

python3 harness/epro_electrical_oracle.py <hub-source.json> \
  -o evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/hub-electrical-graph.json \
  --role G2.1_HUB_DIGEST \
  --hub-identity

python3 harness/independent_schematic_erc.py <hub-source.json> \
  --graph evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/hub-electrical-graph.json \
  --gui-log evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/schDrcLog-hub.txt \
  --overlay evidence/VAL-G2-2026-08-28/dec-usb-hub/ERC-OVERLAY.json \
  --review-project-uuid 41c8e6523576456582ea35958b3684ed \
  -o evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/erc-disposition-hub.json
```

Repair `real_defect` with T25+ (place / designate / wire still separate). Re-ERC.
Freeze only when `unclassified_fatals=0` and `real_defects_open=0` and hub census OK:

```bash
python3 harness/epro_electrical_oracle.py <hub-source.json> \
  -o evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/hub-electrical-digest.frozen.json \
  --role G2.1_HUB_DIGEST \
  --hub-identity \
  --official-freeze \
  --erc-disposition evidence/VAL-G2-2026-08-28/dec-usb-hub/anchors/erc-disposition-hub.json
```

Write `HUB-FREEZE-RECEIPT.md` with digest SHA-256, source hash, ERC counts.

## L — reconstruct, import third UUID, prove

Renderer: `harness/epro_schematic_renderer.py` against the **hub** freeze (no
`--allow-unfrozen`). Equivalence: `harness/check_electrical_equivalence.py`
frozen digest vs reconstructed graph.

ILM / R1 semantic gate (mandatory before asking for `JLC-SCH-READY`):

```bash
python3 harness/check_g22_pwr1_ilm.py <g22-source> \
  -o evidence/VAL-G2-2026-08-28/dec-usb-hub/g22/g22-pwr1-ilm.json

python3 harness/epro_electrical_oracle.py <g22-source.json> \
  -o evidence/VAL-G2-2026-08-28/dec-usb-hub/g22/g22-electrical-graph.json \
  --role G2.2_READABLE
```

`U1-PWR1.9` on `USB_DP_UP`, an orphaned `USB_EFUSE_ILIM`, unresolved pin roles,
unresolvable R1 ohms, or a broken D+ path all refuse the oracle. Canonical
`64325d0e` is not the subject of this check.

Pack `K1-Core-Val-R0-G2.2-READABLE-CANDIDATE` by replacing only the schematic
member in a copy of the hub export. Import as a **new** disposable project.
Save / close / reopen. ERC + BOM. Domain screenshots. Live `64325d0e` hash
unchanged.

`JLC-SCH-READY` is Captain-only after that proof.
