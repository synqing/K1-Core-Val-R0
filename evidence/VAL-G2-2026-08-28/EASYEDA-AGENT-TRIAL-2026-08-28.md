---
abstract: "Trial verdict on integrating zhoushoujianwork/easyeda-agent v1.2.10: CLI + daemon + 37-block circuit library build and work on this Mac, but its connector extension NEVER executes inside EasyEDA Pro 2.2.40.8. ROOT CAUSE CORRECTED 2026-08-28 (see banner): the original loader-rejection explanation is DISPROVEN; leading cause is now an F96-class unguarded eda.sys_* call in activate(). Live block-apply is blocked pending an EasyEDA host upgrade decision. Approved route: harvest block-library JSON (parts/nets/ports + verification provenance) and execute through our own EasyEDA-MCP bridge. Includes full evidence chain and rollback state."
---

> **⚠ ROOT CAUSE SUPERSEDED — 2026-08-28 (same day, later session).**
> The conclusion below that "the 2.2.40.8 extension loader silently declines the connector bundle
> (3.2-era eext format/entry)" **did not survive verification and must not be repeated.**
> Disproving evidence: the *working* Run API Gateway declares the **same** `engines.eda ~3.2.0` and the
> **same** `@jlceda/pro-api-types ^0.2.21` as the dead connector on this same host, our own bridge
> declares `^3.0.0` with the identical types pin, and the packaged `.eext` contains a well-formed
> `dist/index.js`. Manifest generation is therefore **not** the discriminator.
> **Surviving hypothesis (untested):** the connector's `activate()` calls `eda.sys_Storage` /
> `sys_I18n` / `sys_Log` before dialling; an unguarded call to a mount this build lacks throws
> silently — menus registered from the manifest, module dead. That is failure class **F96**, and if
> it holds a guard patch fixes the connector on 2.2.40.8 **with no upgrade at all**.
> Decide it with the capability probe (Phase 1), not with this document's §Evidence chain item 6.
> Full assessment + migration plan: `easyeda-v3-migration-plan.html`
> (published: https://claude.ai/code/artifact/535731d5-0a37-4ab5-bc22-ed44fc30b0c3)

# easyeda-agent integration trial — 2026-08-28

## Verdict

**Partial adoption.** The tool's CLI, daemon, and embedded circuit-block library work
standalone on this machine. Its EasyEDA connector extension is **dead on arrival on our
host**: its module never executes inside our installed EasyEDA Pro **2.2.40.8** — no dial,
no log, no exception, inert menus — across import-time activation, a renderer reload, and
two full app restarts, including with a patched manifest. It targets the 3.2 API generation;
**why it does not run here is not yet established** (see banner). Live `block-apply` cannot
run on this host today.

**The value survives anyway**: the 37-block library is embedded in the CLI and readable
offline. Each block carries parts (library part refs), internal net topology, boundary
ports, and honest per-block verification provenance (netlist counts per net, bridge-check
results, known defects — e.g. `block.ch340c_usb_serial` flags its own SM712 ESD part as
wrong for USB). That JSON is directly consumable by our own EasyEDA-MCP bridge's typed
tools (`add_schematic_component`, `connect_schematic_pins_to_nets`, net flags/ports),
which is the execution path this repo already trusts and gates.

## Evidence chain (connector root-cause)

1. Daemon v1.2.10 healthy on 127.0.0.1:60832; raw WebSocket from inside the EasyEDA
   renderer to `ws://127.0.0.1:60832/eda` **opens and receives the daemon handshake**
   (daemon log: `handshake sent to 127.0.0.1:53834`) — network path fully clear.
2. Connector installed, enabled, External Interactions Yes (Extensions Manager row
   `EDA Agent Connector ✔️Yes ✔️Yes 1.66MiB 4dae2740…`).
3. Zero connection attempts from the connector at any point: daemon log shows only our
   probe sockets; 12 s TCP sampling on :60832 during its 3 s watchdog cadence shows no dials.
4. Its manifest declares `activationEvents: { onStartupFinished: true }` — an event this
   host never fires. Both extensions that DO work here (our MCP bridge, run-api-gateway)
   declare `activationEvents: {}`. Patched the manifest to `{}`, rebuilt
   (`extension/build/dist/easyeda-agent-connector_v1.2.10.eext`), deleted old, imported
   patched build — still no execution after a full restart.
5. Full-boot CDP capture (attached pre-boot, `PRO_LOG_LEVEL=debug` injected via
   `Page.addScriptToEvaluateOnNewDocument`): 52 events, **zero** from the connector, zero
   exceptions. The bundle never runs. Their own code comments reference EasyEDA 3.2.175
   behaviour; `engines: ~3.2.0`.
6. ~~Conclusion: the 2.2.40.8 extension loader silently declines the connector bundle~~
   **SUPERSEDED — see banner.** Items 1–5 stand as measurements; item 6's inference does not.
   What is established: the connector's module does not execute. What is NOT established: why.
   The manifest/packaging explanation is disproven; the F96 unguarded-mount explanation is
   untested and cheap to test.

## Side findings

- EasyEDA 2.2.40.8 does **not** re-activate extensions on `Page.reload` — a reload leaves
  every extension's menus rendered but dead (our bridge included). Only a full app restart
  re-activates. This contradicts the F55 assumption that a renderer reload re-runs
  `activate()`; on this build it does not.
- `tools/easyeda_reconnect.mjs --force-restart` heals our bridge after such a restart;
  project bootstrap can still land on Start Page (`suspectedBootstrapFailure`) needing a
  tree double-click to reopen the document.
- `.eext` import via CDP works by clicking Import Extensions and setting the transient
  `input[type=file]` with `DOM.setFileInputFiles` (the input exists only ~seconds after
  the click; `Page.fileChooserOpened` does not fire).

## What is installed / running now

- `Workspace_Management/Software/easyeda-agent` — cloned repo, built CLI `bin/easyeda`
  v1.2.10 (Go). Offline commands (`blocks ls/search/show`, `api`, `actions`) work with no
  daemon and no EasyEDA.
- EasyEDA extension list carries `EDA Agent Connector` (patched build, inert on this
  host). Harmless; delete via Extensions Manager if unwanted.
- easyeda-agent daemon: **stopped** (start with `bin/easyeda daemon start` when needed).
- Our stack: MCP bridge Connected, 90/90 methods, both gates enabled; project
  `K1-Core-Val-R0` reopened with `P1.Schematic1` active and saved. No design document was
  modified by this trial.

## Decision required (Captain)

1. **Host upgrade** — now scoped properly in `easyeda-v3-migration-plan.html`. Verified facts:
   current release is **3.2.149** (macOS arm64 available); our client is **2.2.40.8, built
   2025-07-15**; **2.2.40.8 is not obtainable from the vendor** (archive holds 2.2.47.7 / 2.1.64)
   and has now been archived to `SpectraSynq-EDA/_archive/easyeda-clients/`. V3 uses a new
   format (`.epro2`) and **auto-upgrades a legacy project on open+save, after which V2.2 can
   never reopen it** (vendor's own notice). Default if no decision: do not upgrade — but the
   P0 backup work is mandatory regardless, because the web editor is already V3 and reaches
   the same cloud projects.
2. **Harvest route (recommended, no decision blocker)** — consume easyeda-agent block
   JSON through our own bridge: a small translator (block parts → `search_library_devices`
   + `add_schematic_component`; block nets → `connect_schematic_pins_to_nets` + net
   flags/ports) gives us block-level composition on the trusted stack. Also port their
   layout-score "not-measured ≠ full-marks" scoring conventions into our fitness tooling.
3. **Reject** — remove the connector row and the repo clone.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:claude (Fable 5) | Created — trial execution record, connector root-cause evidence, verdict and decision options |
| 2026-08-28 | agent:claude (Opus 5) | Root cause SUPERSEDED — loader-rejection inference disproven (working gateway shares identical engines/types pin); F96 unguarded-mount now the leading hypothesis. Upgrade decision rescoped against verified version landscape (3.2.149 current, 2.2.40.8 unobtainable, .epro2 one-way). Client bundle archived. Added pointer to easyeda-v3-migration-plan.html |
