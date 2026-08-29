# EasyEDA PREFLIGHT — DEC-USB-HUB

What happened. This session read the execution canon, checked the mutation
gate, and found the create/import path for a disposable hub project. Nobody
placed a part. Nobody wrote a schematic net. Nobody touched the live product
project.

What is true now. H is already GREEN. A disposable project named
`K1-Core-Val-R0-G2.1-HUB-CANDIDATE` already exists. Its own mutation lane is
READY. A bare `validate` now refuses, because two live lanes exist. Typed
EasyEDA MCP tools cannot create or import a project. The proven import path
is host `importProjectByProjectFile` as a New Project, already used once.

What is left. Mutation writers start T00 on the hub lane only, with explicit
`--state` / `--ledger`. Do not create a second disposable project. Do not
reconcile the live product lane as part of this programme.

```text
DATE                 = 2026-08-29
AGENT                = EasyEDA PREFLIGHT only
EASYEDA_WRITE        = no
PARTS_PLACED         = no
LIVE_UNTOUCHED       = yes
DCD7E3CA_BEAUTIFIED  = no
H                    = GREEN (GO-NO-GO.md; not re-scored here)
D049                 = RATIFIED
D050                 = BOUND GT-USB-7005A / C5250872
HUB_PROJECT_EXISTS   = yes
HUB_PROJECT_UUID     = 41c8e6523576456582ea35958b3684ed
MCP_TYPED_CREATE     = absent
HOST_IMPORT_PATH     = proven (already used)
CREATE_EMPTY_NOW     = no
```

---

## 1. Mutation gate — recorded this session

### 1.1 Bare `validate` (AGENTS.md wording)

Command: `python3 harness/easyeda_mutation_gate.py validate`

**First observation this session** (hub-lane directory not yet visible to
discovery): resolved to the live product lane.

```text
EASYEDA_MUTATION_LANE_RESOLVED=evidence/VAL-G2-2026-08-28/canonical-core-val-r0
EASYEDA_MUTATION_LANE_PROJECT=64325d0e55e0435abd018defb0089a9b
EASYEDA_MUTATION_LEDGER_RECORDS=256
EASYEDA_MUTATION_TERMINAL_EVENT=STATE_QUARANTINED
state = BLOCKED_RECONCILIATION
project_uuid = 64325d0e55e0435abd018defb0089a9b
document_uuid = 59bef7e87cff4cd580561703b62d8c19
blocking_reason = Intermediate outline-only shell state requires transform seating repair
current_source_hash = null
EASYEDA_MUTATION_GATE_STATE=BLOCKED_RECONCILIATION
```

That PCB UUID is inherited from the G2.1 archive. It also appears on the
review oracle and on the hub candidate. **It is not a project identity.**
The live product project is the one named `64325d0e…`. Do not begin on it.
Do not “reconcile through” it for hub work. `FROZEN_INCIDENT` was not used.

**Second observation this session** (after `hub-lane/` existed):

```text
EASYEDA_MUTATION_GATE=BLOCKED
REASON=2 live mutation lanes found and no --state/--ledger given:
  evidence/VAL-G2-2026-08-28/canonical-core-val-r0
    (project 64325d0e55e0435abd018defb0089a9b, state BLOCKED_RECONCILIATION)
  evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane
    (project 41c8e6523576456582ea35958b3684ed, state READY)
Refusing to guess which lane you meant.
```

Exit 2. This is the intended fail-closed behaviour. A bare invocation must
never silently pick the live product.

### 1.2 Hub-lane `validate` (the campaign lane)

Command (flags **before** the subcommand):

```bash
python3 harness/easyeda_mutation_gate.py \
  --state evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-STATE.json \
  --ledger evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-LEDGER.jsonl \
  validate
```

Stdout this session:

```text
EASYEDA_MUTATION_LEDGER_RECORDS=2
EASYEDA_MUTATION_TERMINAL_EVENT=STATE_RECONCILED
{
  "active_transaction": null,
  "blocked_transaction_id": null,
  "blocking_reason": null,
  "current_source_hash": "2352202:c5bf1157",
  "document_uuid": "1435cb46f39e48c8a8aadbb84ca81603",
  "last_closed_transaction_id": "hub-lane-import-reconcile-2026-08-29",
  "project_uuid": "41c8e6523576456582ea35958b3684ed",
  "schema_version": 1,
  "state": "READY",
  "updated_at": "2026-08-28T23:27:34.923839+00:00"
}
EASYEDA_MUTATION_GATE_STATE=READY
```

Exit 0. This is the only lane that may receive T00–T24.

### 1.3 Lane census (`lanes`)

```text
EASYEDA_MUTATION_LANES=3
  [RETIRED] evidence/VAL-G2-2026-08-28
            project=09e9c541fd3d404082d4b92e55ae5336 state=READY
  [LIVE   ] evidence/VAL-G2-2026-08-28/canonical-core-val-r0
            project=64325d0e55e0435abd018defb0089a9b state=BLOCKED_RECONCILIATION
  [LIVE   ] evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane
            project=41c8e6523576456582ea35958b3684ed state=READY
EASYEDA_MUTATION_LIVE_LANES=2
```

Do **not** put `LANE-RETIRED` on the canonical live product lane to make
bare `validate` guess the hub. Always name the hub files.

---

## 2. Identity — hard list

| Role | UUID / name | This programme |
| --- | --- | --- |
| Live product | `64325d0e55e0435abd018defb0089a9b` `K1-Core-Val-R0` | **never open-for-write, never mutate** |
| G2.1 oracle | `dcd7e3cab2a24b9aa6e531d2b62e1b6f` `K1-Core-Val-R0-G2.1-BULK-CANDIDATE` | **do not beautify** |
| Hub disposable | `41c8e6523576456582ea35958b3684ed` `K1-Core-Val-R0-G2.1-HUB-CANDIDATE` | **only write target** |
| Inherited page | `1435cb46f39e48c8a8aadbb84ca81603` | same number on live, oracle, and hub — **parent UUID is the discriminator** |
| Inherited PCB | `59bef7e87cff4cd580561703b62d8c19` | must stay electrically empty (0 components, 0 vias) |
| Archive file hash | `3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7` | **not** a project UUID |
| Team | `27700277ef7a49e48a0293bece6b2993` | owner team for New Project import |
| Dead qualification | `09e9c541fd3d404082d4b92e55ae5336` | retired lane; do not revive |

CDP window this session (read-only `/json/list` on port 9223): title
`K1-Core-Val-R0-G2.1-HUB-CANDIDATE | JLCEDA Pro - V3.2.149.88089769`, URL
fragment `id=41c8e6523576456582ea35958b3684ed` with tabs
`1435cb46…@41c8e652…` and `59bef7e8…@41c8e652…`. The operator window is
already the hub candidate, not the live product.

`get_current_context` was **not** called from this preflight. Identity is
from CDP chrome plus `DISPOSABLE-IDENTITY.md`. Re-assert parent UUID before
every later write.

One electrical schematic sheet only. The G2.1 canvas shows ten **domain
boxes** on that one page. That is not hierarchical sheets. Do not call
`create_schematic` or `create_schematic_page`.

---

## 3. Create / import recipe

Canon does **not** require `create-empty` for preflight. Empty create would
provision `Board1` / `Schematic1` / `PCB1` (K1E-005) and would not carry the
G2.1 graph. **Do not create another project now.**

### 3.1 Typed EasyEDA MCP — cannot create a project

Live `mcp_http_call.mjs` tool list this session (HTTP `:19733/mcp`):
`create_project` **ABSENT**, `open_project` **ABSENT**,
`get_project_info` **ABSENT**, `import_project` **ABSENT**.

Present and dangerous if misused: `create_schematic`,
`create_schematic_page`, `create_pcb`, `import_schematic_to_pcb`,
`copy_board`. None of those is the hub import. Using them on the hub
project would add a second sheet or fill the empty PCB.

Cursor’s attached MCP namespaces this session have **no EasyEDA tools**.
EasyEDA actuation is `EasyEDA-MCP` HTTP (`mcp_http_call.mjs` /
`mcp_batch.mjs`), not a Cursor MCP namespace.

This is a **wrapper gap**, not an EasyEDA capability gap (K1E-003 / F-05).
Host APIs exist: `dmt_Project.createProject`, `getProjectInfo`,
`openProject`, `sys_FileManager.importProjectByProjectFile`.

### 3.2 Proven path — import archive as New Project

This is how `dcd7e3ca…` was born, and how `41c8e652…` was born. Do not
repeat it unless the existing hub UUID is abandoned (wrong name →
`ABANDONED_DO_NOT_USE`, create another; never rename).

Archive (hash confirmed this session):

```text
evidence/VAL-G2-2026-08-28/offline-bulk-repair/K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro
SHA256 = 3db861a351239a8628b151c4610a845da761ed9bcb562755f9ea9374aa262ba7
```

Exact command (not executed this session):

```bash
cd /Users/spectrasynq/SpectraSynq-EDA/EasyEDA-MCP

# Requires EasyEDA CDP on 127.0.0.1:9223 and a connected editor page.
# Pass team UUID explicitly. Leave source-project UUID empty so this does
# not even read dcd7e3ca or live 64325d0e.
# argv: <epro> <friendly-name> [source-uuid] [team-uuid] [folder-uuid]

node tools/easyeda_import_project_file.mjs \
  /Users/spectrasynq/Workspace_Management/Software/K1-CORE-VAL-R0/evidence/VAL-G2-2026-08-28/offline-bulk-repair/K1-Core-Val-R0-G2.1-BULK-CANDIDATE-3db861a3.epro \
  'K1-Core-Val-R0-G2.1-HUB-CANDIDATE' \
  '' \
  '27700277ef7a49e48a0293bece6b2993'
```

Host call inside that script:

```text
eda.sys_FileManager.importProjectByProjectFile(
  projectFile,
  'JLCEDA Pro',
  undefined,
  {
    operation: 'New Project',
    newProjectOwnerTeamUuid: <team>,
    newProjectName: 'K1-Core-Val-R0-G2.1-HUB-CANDIDATE',
    newProjectFriendlyName: 'K1-Core-Val-R0-G2.1-HUB-CANDIDATE',
    ...
  },
  { ownerTeamUuid, createDeviceForSingleSymbol: false }
)
```

Reject host `undefined` / `false` / missing `imported.uuid`. Require exact
friendly-name match and a UUID that is not live and not `dcd7e3ca…`.

### 3.3 After import (already done for `41c8e652…`)

1. Inventory: exactly one schematic, exactly one page, PCB electrically empty.
2. `openProject` only the new UUID. Prove `getCurrentProjectInfo().uuid`
   equals the new UUID.
3. Snapshot source + hash into `anchors/pre-hub-amend.*`.
4. Initialise a **new** mutation lane (already:
   `dec-usb-hub/hub-lane/`). Never begin on the canonical live lane.
5. `expectedDocumentUuid` on every later mutating MCP call = page
   `1435cb46…`. **Also** prove parent project `41c8e652…` first.

### 3.4 Forbidden substitutes

- Create empty then `set_document_source` the archive into it.
- `copy_board` / `copy_schematic` inside live `64325d0e…`.
- Beautify `dcd7e3ca…` in place.
- Import into the live product.
- Click project-management menus to compensate for missing MCP wrappers.
- Rename a wrong UUID.

---

## 4. Lock path — how later writers serialise

The gate is not atomic JSON replace. Every transition, including
`validate`, takes an OS exclusive flock:

```text
lock_path = <state_path>.lock
fcntl.flock(fd, LOCK_EX)
```

| Lane | State file | Lock file | Ledger |
| --- | --- | --- | --- |
| Hub campaign | `evidence/VAL-G2-2026-08-28/dec-usb-hub/hub-lane/MUTATION-STATE.json` | **`…/MUTATION-STATE.json.lock`** | `…/MUTATION-LEDGER.jsonl` |
| Live product (do not use) | `…/canonical-core-val-r0/MUTATION-STATE.json` | `…/MUTATION-STATE.json.lock` | `…/MUTATION-LEDGER.jsonl` |
| Retired fixture | `evidence/VAL-G2-2026-08-28/EASYEDA-MUTATION-STATE.json` | `…/EASYEDA-MUTATION-STATE.json.lock` | paired jsonl |

Hub writers **must** pass `--state` and `--ledger` pointing at
`hub-lane/` on **every** gate verb (`validate`, `begin`, `record`,
`close`, `abort-unchanged`). Flags go **before** the subcommand.

**The flock serialises one lane, not the EasyEDA host.** Two lanes have two
locks. K1E-065 still requires one explicit EasyEDA operator. Practical
protection this session: canonical lane is `BLOCKED_RECONCILIATION` and
cannot `begin`; the focused window is the hub candidate. Do not reconcile
the live product lane while hub mutations run.

---

## 5. Can MCP create a disposable project?

| Surface | Create / import a new EasyEDA project? |
| --- | --- |
| Typed EasyEDA MCP tools | **No** (`create_project` / `open_project` / `import_project` absent) |
| Cursor MCP namespaces this session | **No** EasyEDA tools attached |
| Host API + CDP import script | **Yes** — `importProjectByProjectFile` as New Project (proven; already used) |
| Host `dmt_Project.createProject` | **Yes** as a blank project — **wrong** for this programme (would not import G2.1) |

**Answer for the parent:** typed MCP cannot create the disposable project.
The host import path can, and has already created `41c8e652…`. Preflight
did not create another.

---

## 6. Blockers (for the mutation campaign, not for this preflight file)

1. **Bare `validate` is BLOCKED** while two live lanes exist. Writers must
   name `hub-lane` files. Do not retire the live product lane.
2. **Live product gate is `BLOCKED_RECONCILIATION`.** Hub work must not
   “fix” that. It is a PCB-experiment block on `64325d0e…`.
3. **Inherited page/PCB UUIDs collide** with live and with `dcd7e3ca…`.
   Every write proves parent `41c8e652…` first.
4. **Typed MCP cannot create/open/import projects.** Further clones use the
   CDP import recipe, not MCP `create_project`.
5. **Empty PCB must stay empty.** No PCB place, no `import_schematic_to_pcb`,
   no DeepPCB.
6. **PIN-CONTRACT G6 still says `Rxx-USB` / `Ryy-USB`.** The runbook fills
   those from the reserved block (`R85-USB` FIT, `R86-USB` DNP). Do not
   invent a second XOR pair.
7. **U18-USB / U19-USB stay spare.** Hub IC is `U20-USB`, switch is
   `U21-USB` (census + PIN-CONTRACT). Sequential next-free is U18; it is
   reserved unused, not the USB2422.
8. **T23a is skipped** (CC-PROTECTION letter is IEC ESD only).
9. **One EasyEDA operator.** Gate flock ≠ host mutex.

None of these forbids starting T00 on the hub lane once the writer re-runs
the named `validate` and T01 identity re-assert.

---

## 7. Ship path (same answer while EasyEDA is on hold)

1. Already true: D-049 RATIFIED, D-050 BOUND, H GREEN, disposable project
   imported, hub-lane READY — **done by prior agents**.
2. Mutation campaign T00–T24 on `41c8e652…` only, gate-named, place /
   designate / wire separate — **agent**.
3. Item-level ERC, then hub-graph official freeze — **agent**, Captain on
   freeze stamp if required.
4. Reconstruct G2.2 once against the hub digest — **agent**.
5. Captain stamps `JLC-SCH-READY` — **Captain**.
6. Later IOMUX / footprint / one-Type-C mechanics programme, then Captain
   stamps `JLC-LAYOUT-READY`.

The stamp that means architecture shipped electrically remains **D-049
RATIFIED + D-050 usable bind + hub-graph official freeze**.
