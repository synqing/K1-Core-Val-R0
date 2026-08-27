# Package 1 — SSCM-1 Recovery Pass

**Status:** NOT FOUND — Recovery Pass Complete (Bounded Search)  
**Authority if Option B is Revived:** `contracts/sscm1-v2/` (`REQUIREMENTS.md`, `pin-budget.csv`, `STATUS.md`)

```text
SSCM1_V1 = UNRECOVERED / UNFROZEN / RETIRED AS AUTHORITY
```

---

## 1. Search Scope and Locations Inspected

A bounded recovery assessment was conducted across this repository, the accessible current
checkouts and the recorded internal source register to locate the SSCM-1 v1.0 pin map declared
frozen on 2026-08-14. The current review could not reproduce every historical search location;
that limitation is recorded below.

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
   - `K1.hardware`: Historical K1-M2B/module architecture fragments and a placeholder 40-pin
     mapping exist. They are not the frozen SSCM-1 v1 interface specification and must not be
     promoted into it.
   - `SpectraSynq-Instrument-Spine`: The prior search could not be reproduced during the current
     verification because this checkout was not locally available.
   - `SpectraSynq-K1-DualMCU-Firmware`: The recorded ingest at commit `4e985c6` and the accessible
     current firmware checkout contain no recovered SSCM-1 interface authority.

---

## 2. Findings and Conclusion

- **Outcome:** The declared frozen v1.0 pin map (2026-08-14) **could not be located**.
- **Specification Status:** A contract that cannot be retrieved cannot function as a frozen engineering constraint. In accordance with Decision `D-005` and `authority/05-SUPERSESSIONS.md`, SSCM-1 v1.0 is treated as **unfrozen and retired**.
- **Fragment Treatment:** Historical K1-M2B/module notes and the placeholder mapping remain
  historical evidence only. They do not reverse the recovery result.
- **Rule Adherence:** No attempt is made to reconstruct or reverse-engineer a v1.0 pin map from fragmentary notes or infer pin assignments from raw pin budgets.
- **Proceeding Authority:** Option B is deferred and no re-analysis is authorised now. If it is
  revived, new work begins from the current requirements-driven boundary in `contracts/sscm1-v2/`;
  Package 2 is historical projected analysis, not proof.
