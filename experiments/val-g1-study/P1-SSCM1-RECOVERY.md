# Package 1 — SSCM-1 Recovery Pass

**Status:** NOT FOUND — Recovery Pass Complete (Bounded Search)  
**Authority for Downstream Work:** `contracts/sscm1-v2/` (`REQUIREMENTS.md`, `pin-budget.csv`, `STATUS.md`)

---

## 1. Search Scope and Locations Inspected

A bounded recovery search was conducted across all local repository directories, file trees, and recorded internal reference registers to locate the SSCM-1 v1.0 pin map declared frozen on 2026-08-14.

Locations inspected:
1. **Local Repository Trees:**
   - `authority/` (`00-AUTHORITY-PRECEDENCE.md`, `01-DECISION-REGISTER.md`, `02-Q0-B-vs-C.md`, `04-TERMINOLOGY.md`, `05-SUPERSESSIONS.md`)
   - `contracts/` (`audio-interface.md`, `debug-fabric.md`, `k1br-bridge.md`, `led-interface.md`, `microphone-interface.md`, `motion-interface.md`, `nfc-interface.md`, `usb-interface.md`, `sscm1-v2/*`)
   - `architecture/` (`CLOCK-ARCHITECTURE.md`, `DOMAINS-OF-CONCERN.md`, `MISSION.md`, `POWER-ARCHITECTURE.md`, `VALIDATION-ARCHITECTURE.md`)
   - `pcb/` (`LAYER-USE-POLICY.md`, `STACKUP-STATUS.md`, `floorplan/FLOORPLAN-STUDY.md`)
   - `schematic/` (`SINGLE-SHEET-CONTRACT.md`, `single-sheet-qualification/TEST-PLAN.md`)
   - `evidence/` (`VAL-G0-2026-08-27/*`)
   - `archive/` (`README.md` — archive uningested, legacy snapshots excluded)
   - `sources/SOURCE-REGISTER.md`
2. **Internal Repository Register State (per `sources/SOURCE-REGISTER.md` and `contracts/sscm1-v2/STATUS.md`):**
   - `K1.hardware`: Searched, no interface specification found (footprint-library references only).
   - `SpectraSynq-Instrument-Spine`: Searched, no interface specification found (footprint-library references only).
   - `SpectraSynq-K1-DualMCU-Firmware`: Ingested at commit `4e985c6`; contains zero references to SSCM-1, M.2 pin mapping, or carrier interface contracts.

---

## 2. Findings and Conclusion

- **Outcome:** The declared frozen v1.0 pin map (2026-08-14) **could not be located**.
- **Specification Status:** A contract that cannot be retrieved cannot function as a frozen engineering constraint. In accordance with Decision `D-005` and `authority/05-SUPERSESSIONS.md`, SSCM-1 v1.0 is treated as **unfrozen and retired**.
- **Rule Adherence:** No attempt is made to reconstruct or reverse-engineer a v1.0 pin map from fragmentary notes or infer pin assignments from raw pin budgets.
- **Proceeding Authority:** All downstream analysis for Option B in Package 2 proceeds strictly using the requirements-driven boundary specification defined in `contracts/sscm1-v2/` (`REQUIREMENTS.md`, `pin-budget.csv`, and `STATUS.md`).
