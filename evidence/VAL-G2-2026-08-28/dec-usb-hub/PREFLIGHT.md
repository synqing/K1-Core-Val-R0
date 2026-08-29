# Phase A preflight — DEC-USB-HUB

What happened. This session read the operating files, checked the EasyEDA write lock, confirmed the operator’s EasyEDA window, and copied the connector handoff into this folder. Nobody wrote EasyEDA. Nobody opened the live product project through the editor API.

What is true now. The live product project is still the one on screen, and it was left alone. The G2.1 review project is still only an electrical reference. The write lock is idle. The connector handoff is on disk with the expected hash.

What is left. Phase B drafts D-049 and D-050 on paper. Captain has not stamped Phase C. No EasyEDA work is authorised.

```text
DATE = 2026-08-29
AGENT = DEC-USB-HUB Phase A/B (Agents Orchestrator)
LIVE_PROJECT_UUID = 64325d0e55e0435abd018defb0089a9b
LIVE_FRIENDLY_NAME = K1-Core-Val-R0
G21_ORACLE_UUID = dcd7e3cab2a24b9aa6e531d2b62e1b6f
INTENDED_TARGET_UUID = NONE_THIS_SESSION
INTENDED_TARGET_MUST_NOT_BE_LIVE = yes
EASYEDA_WRITE = no
LIVE_UNTOUCHED = yes
D049_RATIFIED = no
D050_BOUND = no
PHASE_C_STAMP = not_requested
```

## A1 — files read

- `AGENTS.md`
- `docs/agent/EASYEDA-EXECUTION-CANON.md`
- `STATUS.md`

Read only. No EasyEDA write followed.

## A2 — identity

| Item | Value |
| --- | --- |
| Date | 2026-08-29 |
| Agent | DEC-USB-HUB Phase A/B (Agents Orchestrator) |
| Live product UUID | `64325d0e55e0435abd018defb0089a9b` |
| Live friendly name | `K1-Core-Val-R0` |
| G2.1 oracle UUID | `dcd7e3cab2a24b9aa6e531d2b62e1b6f` |
| Intended EasyEDA target | none — this session is files only |
| Mutation-gate state | `READY` (stdout below) |
| EasyEDA window | one window titled `K1-Core-Val-R0 \| JLCEDA Pro - V3.2.149.88089769` |

The intended later EasyEDA target for this programme is a **new disposable** project. It is not the live product and it is not a beautified `dcd7e3ca…`. That project does not exist yet. Phase I is not this session.

## A3 — mutation gate

Command: `python3 harness/easyeda_mutation_gate.py validate`

Exit: 0

Stdout, copied in full:

```text
EASYEDA_MUTATION_LANE_RESOLVED=evidence/VAL-G2-2026-08-28/canonical-core-val-r0
EASYEDA_MUTATION_LANE_PROJECT=64325d0e55e0435abd018defb0089a9b
EASYEDA_MUTATION_LEDGER_RECORDS=243
EASYEDA_MUTATION_TERMINAL_EVENT=MUTATION_ABORTED_NO_CHANGE
{
  "active_transaction": null,
  "blocked_transaction_id": null,
  "blocking_reason": null,
  "current_source_hash": "658056:4134f164",
  "document_uuid": "59bef7e87cff4cd580561703b62d8c19",
  "last_closed_transaction_id": "usb1-3d-hash-reconcile-8-2026-08-29",
  "project_uuid": "64325d0e55e0435abd018defb0089a9b",
  "schema_version": 1,
  "state": "READY",
  "updated_at": "2026-08-28T19:54:48.298038+00:00"
}
EASYEDA_MUTATION_GATE_STATE=READY
```

State is `READY`. No `FROZEN_INCIDENT`. No reconcile was attempted. The gate names the live product lane. This session did not begin a transaction and did not write.

The recorded document UUID `59bef7e87cff4cd580561703b62d8c19` is the live project’s PCB document in the mutation-state file. It is observed only. It is not a write target.

## A4 — session ownership

The gate shows no active transaction and no blocked transaction. Last closed transaction: `usb1-3d-hash-reconcile-8-2026-08-29`. That is a closed PCB-experiment line on the live lane, not a live write now.

`get_current_context` was **not** called. We have no EasyEDA write target this session. The only visible EasyEDA window is the live product. Opening that project through the editor API is forbidden for this programme. Two ticket/updateTime reads on a window we refuse to write would still be an open of the live product. They were not done.

Ownership conclusion for this files-only session: no competing gate transaction; live window left alone.

## A5 — operator window

The operator’s EasyEDA window **is** the live product (`K1-Core-Val-R0`). It was left alone. No focus steal, no project switch, no Force Quit, no beautify of `dcd7e3ca…`.

```text
OPERATOR_WINDOW_IS_LIVE_PRODUCT = yes
ACTION = leave_alone
```

## A6 — evidence directory and handoff

Created `evidence/VAL-G2-2026-08-28/dec-usb-hub/`.

Copied `K1-CORE-VAL-R0_DEC-050_USB-C_CONNECTOR_HANDOFF.md` from the Captain handoff file. Recorded SHA-256:

```text
c3b6a533e9eecaaaeaf465c0368dc070b176b7cc3724a1445dee393f18c32703  K1-CORE-VAL-R0_DEC-050_USB-C_CONNECTOR_HANDOFF.md
```

That hash matches the working-plan expectation. The handoff is **not** a ratified MPN and **not** a D-050 bind. It still discusses the earlier CX70M preference. Captain later selected G-Switch `GT-USB-7005A` / `C5250872`; that selection is written in Phase B as selected, not bound.

`SHA256SUMS.txt` exists and now holds that line. No EasyEDA files were added.

## Exit A

```text
PREFLIGHT.md exists
LIVE_UNTOUCHED=yes
EASYEDA_MUTATION_GATE_STATE=READY
HANDOFF_SHA256=c3b6a533e9eecaaaeaf465c0368dc070b176b7cc3724a1445dee393f18c32703
```
