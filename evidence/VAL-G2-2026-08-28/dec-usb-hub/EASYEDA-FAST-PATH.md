# EasyEDA fast path — DEC-USB-HUB discovery

What happened. This pass discovered how EasyEDA is actually reachable from this agent, checked the write lock, and searched three library families read-only. Nobody placed a part. Nobody wrote the live product board. Nobody imported a new project.

What is true now. EasyEDA is **not** attached to this Cursor session as an MCP namespace. The live HTTP bridge on this machine is healthy and already knows `search_library_devices`. The G2.1 archive `3db861a3` is on disk and hashes correctly. The live mutation gate is **blocked** on the product project, so that board cannot be written even by accident through the canonical lane. H is already **GREEN**; the remaining EasyEDA work is a **new disposable** hub project, not this discovery file.

What is left. A later I–L agent may import `3db861a3` as `K1-Core-Val-R0-G2.1-HUB-CANDIDATE`, then place and wire under the mutation gate on **that** UUID. This file does not authorise that write.

```text
DATE = 2026-08-29
AGENT = DEC-USB-HUB EasyEDA fast-path discovery
LIVE_PROJECT_UUID = 64325d0e55e0435abd018defb0089a9b
LIVE_FRIENDLY_NAME = K1-Core-Val-R0
G21_ORACLE_UUID = dcd7e3cab2a24b9aa6e531d2b62e1b6f
G21_ARCHIVE = evidence/VAL-G2-2026-08-28/offline-bulk-repair/K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro
G21_ARCHIVE_SHA256 = 3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7
INTENDED_DISPOSABLE_NAME = K1-Core-Val-R0-G2.1-HUB-CANDIDATE
INTENDED_TARGET_UUID = NONE_THIS_SESSION
EASYEDA_WRITE = no
LIVE_UNTOUCHED = yes
CURSOR_MCP_EASYEDA = not_attached
HTTP_MCP = http://127.0.0.1:19733/mcp  (live; 97 tools)
H = GREEN
EASYEDA_MUTATION_GATE_STATE = BLOCKED_RECONCILIATION
```

Skills and canon followed: `easyeda-mcp-fast-path`, `docs/agent/EASYEDA-EXECUTION-CANON.md`.
No cua-driver. No focus steal. No `get_current_context` / `open_document` / `get_document_source` on the live product.

---

## 1. How EasyEDA MCP is reached from this session

### Cursor `GetDynamicTools`

EasyEDA is **absent** from this Cursor MCP catalog. The attached namespaces were Cursor native, browser, Konnect (KiCad), Desktop Commander, CUA, and other product servers. There is no `easyeda` / `user-easyeda` namespace to call with `CallDynamicTool`.

Konnect is KiCad. It is not a substitute.

### Live transport (use this)

The SpectraSynq EasyEDA MCP HTTP server is running:

| Item | Value |
| --- | --- |
| Streamable HTTP | `http://127.0.0.1:19733/mcp` |
| Bare `curl` | `406` + `Client must accept text/event-stream` (server alive; not a browser API) |
| Extension WS | `ws://127.0.0.1:19732/easyeda-mcp` |
| Extension | `1.5.9` (matches package) |
| Preflight | `ok: true`, 90/90 bridge methods |
| Fast path N = 1 | `node tools/mcp_http_call.mjs` in `SpectraSynq-EDA/EasyEDA-MCP` |
| Fast path N ≥ 2 | `node tools/mcp_batch.mjs jobs.json results.json` — **never** loop `mcp_http_call` |

This discovery used one `mcp_http_call` to list tools, then **one** `mcp_batch` of eight read-only jobs (8 ok / 0 fail / 16.1 s).

### Not in MCP (do not invent a wrapper)

There is **no** MCP `create_project`, `import_project`, or “open this `.epro`” tool. Library **create** is also not an MCP method. Map is not territory (K1E-003 / F126): EasyEDA still imports archives through `eda.sys_FileManager.importProjectByProjectFile`. That path is the CDP helper below, not a GUI click-fest and not cua-driver.

---

## 2. Available MCP tools (live `tools/list`, 97 names)

Read-only / status (safe for discovery; still do **not** point them at the live product unless the task says so):

`bridge_status`, `get_usage_guide`, `ping_bridge`, `echo_bridge`, `search_library_devices`, `get_capabilities`, `get_current_context`, `list_project_objects`, `list_schematic_component_pins`, `get_schematic_netlist`, `run_schematic_drc`, `list_schematic_primitive_ids`, `get_schematic_primitive`, `get_schematic_primitives_bbox`, `list_pcb_component_pads`, `list_pcb_primitive_ids`, `get_pcb_primitive`, `get_pcb_primitives_bbox`, `list_pcb_nets`, `run_pcb_drc`, `get_pcb_net`, `get_layout_fitness_score`, `get_pcb_net_primitives`, `get_document_source`, `compute_source_revision`, `pcb_gate_status`, `hygiene_status`

This session called only `bridge_status`, `ping_bridge`, and `search_library_devices`.

Document / project lifecycle (would hit **whatever EasyEDA currently has focused** — that is the live product today — so they are forbidden against `64325d0e…`):

`open_document`, `save_active_document`, `create_board`, `create_pcb`, `import_schematic_to_pcb`, `create_panel`, `create_schematic`, `create_schematic_page`, `copy_*`, `rename_*`, `delete_board`, `delete_pcb`, `delete_schematic`, `delete_schematic_page`, `delete_panel`, `set_document_source`

Schematic mutation (place / designate / wire / delete):

`add_schematic_component`, `modify_schematic_component`, `delete_schematic_component`, `add_schematic_net_flag`, `add_schematic_net_port`, `add_schematic_short_circuit_flag`, `set_schematic_pin_no_connect`, `connect_schematic_pin_to_net`, `connect_schematic_pins_to_nets`, `connect_schematic_pins_with_prefix`, `add_schematic_text`, `add_schematic_net_label`, `add_schematic_wire`, `add_schematic_rectangle`, `modify_schematic_text`, `delete_schematic_text`, `modify_schematic_net_label`, `modify_schematic_wire`, `delete_schematic_wire`

PCB mutation (VAL-G2 schematic programme does not use these on the product board):

`add_pcb_component`, `modify_pcb_component`, `align_to_board_edge`, `delete_pcb_component`, `modify_pcb_component_pad_net`, `route_pcb_line_between_component_pads`, `route_pcb_lines_between_component_pads`, `add_pcb_via`, `add_pcb_copper_fill`, `delete_pcb_fill`, `add_pcb_pad`, `add_pcb_hole`, `import_pcb_autoroute_ses`, `export_pcb_gerber`, `export_pcb_bom`, `export_pcb_pick_and_place`, `modify_pcb_pad`, `delete_pcb_pad`, `add_pcb_line`, `add_pcb_text`, `set_pcb_net_color`, `modify_pcb_via`, `delete_pcb_via`, `modify_pcb_line`, `delete_pcb_line`, `modify_pcb_text`, `delete_pcb_text`

Iron law for later writes: N ≥ 2 mutating calls → `mcp_batch.mjs`, `saveAfter: false` until the last job of **one** visual stage (`place` **or** `designate` **or** `wire`). Screenshot after settle. Do not hide stages in one batch.

---

## 3. How to create the disposable project from archive `3db861a3`

**Not done this session.** Recipe only.

### Identity

| Item | Value |
| --- | --- |
| Archive | `evidence/VAL-G2-2026-08-28/offline-bulk-repair/K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro` |
| File SHA-256 (reconfirmed this pass) | `3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7` |
| `3db861a3` | **file hash prefix**, not a project UUID |
| Exact new friendly name | `K1-Core-Val-R0-G2.1-HUB-CANDIDATE` (K1E-004) |
| Must not be | live `64325d0e55e0435abd018defb0089a9b` |
| Must not be | beautify / mutate oracle `dcd7e3cab2a24b9aa6e531d2b62e1b6f` |
| Prior successful import of the same archive | `dcd7e3ca…` as `K1-Core-Val-R0-G2.1-BULK-CANDIDATE` (D-048 oracle). Leave it hung/idle. No Force Quit. |
| Team UUID from that import | `27700277ef7a49e48a0293bece6b2993` |
| Do not import | `1dd7d815…` (known-bad) |

### Command (CDP, new project, not MCP)

From `SpectraSynq-EDA/EasyEDA-MCP`, after EasyEDA’s CDP port `9223` is up:

```bash
node tools/easyeda_import_project_file.mjs \
  /Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/offline-bulk-repair/K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro \
  K1-Core-Val-R0-G2.1-HUB-CANDIDATE \
  '' \
  27700277ef7a49e48a0293bece6b2993
```

The helper calls `eda.sys_FileManager.importProjectByProjectFile` with `saveTo.operation = 'New Project'`. `sourceProjectUuid` is only used to copy team/folder metadata. **Do not pass the live product UUID as source.** Pass the team UUID explicitly, as above.

### After import (still future work)

1. Read back the **new** project UUID and document UUIDs. Page UUID `1435cb46…` is inherited from the archive and is **not** a project discriminator (K1E-007).
2. If the friendly name is wrong, **abandon** the UUID. Do not rename through unsupported behaviour (K1E-004 / K1E-006).
3. Inventory automatically created schematic/PCB before creating another (K1E-005). The previous `3db861a3` import produced one type-1 sheet and an empty PCB.
4. Open a **new** mutation-gate lane for the hub UUID. Do not `begin` on `canonical-core-val-r0/MUTATION-STATE.json` (that file owns `64325d0e…` and is currently blocked).
5. Snapshot, then one visual stage at a time. Circuit topology first; no decorative frames (K1E-022).

Importing will change what EasyEDA shows. Do that only when the operator window is allowed to leave the live product, without stealing OS focus (`open -g` / CDP; never cua-driver unless MCP **and** CDP are dead).

---

## 4. Mutation gate (this pass)

Command: `python3 harness/easyeda_mutation_gate.py validate`

Exit: 0

Stdout, copied:

```text
EASYEDA_MUTATION_LANE_RESOLVED=evidence/VAL-G2-2026-08-28/canonical-core-val-r0
EASYEDA_MUTATION_LANE_PROJECT=64325d0e55e0435abd018defb0089a9b
EASYEDA_MUTATION_LEDGER_RECORDS=256
EASYEDA_MUTATION_TERMINAL_EVENT=STATE_QUARANTINED
{
  "active_transaction": null,
  "blocked_transaction_id": null,
  "blocking_reason": "Intermediate outline-only shell state requires transform seating repair",
  "current_source_hash": null,
  "document_uuid": "59bef7e87cff4cd580561703b62d8c19",
  "last_closed_transaction_id": "external-button-state-reconcile-native-retry-2026-08-29",
  "project_uuid": "64325d0e55e0435abd018defb0089a9b",
  "schema_version": 1,
  "state": "BLOCKED_RECONCILIATION",
  "updated_at": "2026-08-28T23:22:16.906679+00:00"
}
EASYEDA_MUTATION_GATE_STATE=BLOCKED_RECONCILIATION
```

Meaning:

- The default gate is the **live product** lane. State is **not** `READY`.
- `BLOCKED_RECONCILIATION` plus `STATE_QUARANTINED` forbids a normal write on `64325d0e…`.
- Recorded document `59bef7e87cff4cd580561703b62d8c19` is the live **PCB** document. Observed only.
- No `FROZEN_INCIDENT`. This session did not reconcile, did not `begin`, and did not write.
- Hub EasyEDA work, when authorised, needs its **own** lane on the disposable UUID. It must not wait for this PCB-outline quarantine to clear, and it must not use this state file to green-light a live write.

---

## 5. What is blocked until H GREEN

H is **already GREEN** (2026-08-29). `GO-NO-GO.md` `VERDICT = GREEN`. D-049 is `RATIFIED`. D-050 is `BOUND` on `GT-USB-7005A` / `C5250872`. The list below is the **H gate**, not a current stop.

While H was not GREEN, these stayed blocked:

| ID | Blocked action |
| --- | --- |
| H1 | Ratify D-049 (one USB-C + USB2422) |
| H0 | Bind D-050 MPN + mechanics + footprint + CC letter |
| PIN-CONTRACT | Any EasyEDA mutation of hub / TPS2052B / J1 replacement pins (`EXECUTABLE = after H GREEN`) |
| Phase I | Create/import `K1-Core-Val-R0-G2.1-HUB-CANDIDATE` |
| I–L | Place, designate, wire hub island; retarget J1 D+/D−; delete J7; ERC; freeze hub graph |
| H15–H17 | Adopt DEC-USB-HUB and start I–L |

H GREEN does **not** lift:

| Still blocked | Why |
| --- | --- |
| Any write to live `64325d0e55e0435abd018defb0089a9b` | Programme hard rule; gate also `BLOCKED_RECONCILIATION` |
| Beautify / mutate `dcd7e3ca…` | D-048 oracle only |
| Place / wire **this** session | Discovery only |
| `create_schematic*` / `add_schematic_component` while EasyEDA is focused on the live product | Would mutate the wrong UUID |
| `G2_1_OFFICIAL_FREEZE` | Waits on hub ERC (Phase K), not on H |
| `JLC-SCH-READY` | Attaches to G2.2, after hub graph + readable reconstruction |
| `JLC-LAYOUT-READY` | Blocked by `JLC-SCH-READY` |
| Canonical PCB place / fan-out / route | VAL-G2 schematic still open |
| SuperSpeed / SBU routing; second receptacle; conventional downstream VBUS islands | D-049 / D-050 |

Phase I is therefore **authorised by H** and **not executed here**.

---

## 6. Library search (read-only) — UUIDs are reference, not authority

Live `search_library_devices` via `mcp_batch`. One LCSC id per job (F126: `lcscIds` arrays come back out of order). Jobs/results:

- `evidence/VAL-G2-2026-08-28/dec-usb-hub/library-search-jobs.json`
- `evidence/VAL-G2-2026-08-28/dec-usb-hub/library-search-results.json`

System library UUID for every hit below: `0819f05c4eef4c71ace90d822a990e87` (LCSC catalog). **Not** a bind.

### Bound / intended LCSC lookups

| Query | MPN (library) | LCSC | device `uuid` | symbol UUID | footprint UUID | 3D UUID |
| --- | --- | --- | --- | --- | --- | --- |
| `lcscIds: C5250872` | GT-USB-7005A | C5250872 | `5dc457597e3143e4a20f9524f559bd07` | `f53e9740f767419fb71147aacf36c525` | `1cad738ee1594315b752ff008a616130` | (none in payload) |
| `lcscIds: C622610` | USB2422T-I/MJ | C622610 | `491ab0a775b4494da1b45bf7008bcf36` | `da0ff7540acd40c89e7def6284f73d48` | `40feb8733a43466aa042834b3ee39bef` | `32bdb58b15ed4019bf73efab52005598` |
| `lcscIds: C130049` | TPS2052BDR | C130049 | `cfd37297ae6546f5a59bbaa3c1ffaaa1` | `69e4f5e224ee403799919c2dcecd2c4d` | `1645372dca8547f19e87c6a19f78de2a` | `2ec1ac1bf9bf4d09a988fcee15e6a02d` |
| `lcscIds: C2680445` | TPS2052BDRBT | C2680445 | `517b9b4459f042f495f4726d1820c7cd` | `32f538f39bfd4ca1b11e8062f5a80ffe` | `2b8e7a26c6f34ba18fc1363904019abd` | `6218c10c783647f3a4f20938433cd455` |

D-050 bind is the **MPN / C5250872**, not this EasyEDA device UUID. Independently rebuilt J1 footprint in `J1-GT-USB-7005A-FOOTPRINT-REBUILD.md` remains the geometric lock; cache/library artwork is not authority.

TPS2052B package is **not bound**. `PROCUREMENT.md` lists both C130049 (SOIC-8) and C2680445 (WSON-8-EP). Do not place from this table.

Keyword `USB2422` returned **four** devices; **C622610 was last**. Commercial/non-T variants first:

| ordinal | MPN | LCSC | device UUID |
| --- | --- | --- | --- |
| 0 | USB2422T/MJ | C622611 | `51446c0da5e549699bff0871254563bb` |
| 1 | USB2422-I/MJ | C220747 | `f63d6fe4b2c14cf5a914926129158d20` |
| 2 | USB2422/MJ | C633330 | `b4f3e56b90b148b6a7e8dbd1d48f153d` |
| 3 | USB2422T-I/MJ | C622610 | `491ab0a775b4494da1b45bf7008bcf36` |

Intended hub LCSC remains **C622610** (industrial, In Production). Substitutes are not authorised.

Keyword `TPS2052B` returned ten catalog variants (C1556842, C2653771, C2865139, C2149906, C3230114, C1556751, C129369, C130049, C131918, C2680445). Full dump in the results JSON. Not a package pick.

LCSC metadata on C5250872 says `USB 3.1` / 24P. Electrical contract is USB 2.0; SuperSpeed and SBU stay NC. Catalog text is not routing authority.

---

## 7. This session did not do

- Place, designate, or wire anything
- Import `3db861a3`
- `get_current_context` on the live window
- cua-driver / GUI focus steal
- Reconcile or `begin` the blocked live gate
- Force Quit EasyEDA

```text
READY_FOR_EASYEDA_DISPOSABLE = yes   (H GREEN; I–L in scope)
THIS_SESSION_EASYEDA_WRITE = no
LIVE_UNTOUCHED = yes
```
