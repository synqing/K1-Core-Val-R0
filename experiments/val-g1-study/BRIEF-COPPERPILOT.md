# CopperPilot brief — VAL-G1 analysis

**Two packages, in order. Analysis only. You produce studies; the Captain rules.**

This brief deliberately does not restate the specification. Every fact you need is in the
repository, and duplicated authority drifts. Read it there.

---

## Your role here

Read `AGENTS.md` section "CopperPilot role" before anything else. It is binding. In short:

- Your coordinates, measurements and PASS claims are **proposals** until independently
  reproduced through the project evidence path.
- You do not author a schematic, mutate a PCB, place parts, route copper, alter rule
  expectations, run and certify your own gate, or act as both builder and verifier.
- There is no live board. There is no EasyEDA project. Do not create one, open one, or claim a
  measurement from one.

If a report of yours contains only successes, it will not be trusted. Name what you did not
finish and why.

---

## Read these first

| File | What it gives you |
| --- | --- |
| `authority/02-Q0-B-vs-C.md` | the open gate, and the conditional interaction table |
| `authority/03-OWNERSHIP-MATRIX.csv` | who owns what — settled, not yours to reopen |
| `contracts/sscm1-v2/STATUS.md` | why v1.0 is treated as unfrozen |
| `contracts/sscm1-v2/REQUIREMENTS.md` | the crossing set and what each demands |
| `contracts/sscm1-v2/pin-budget.csv` | the crossing table, with status per row |
| `contracts/debug-fabric.md` | D13.1, including its five SSCM-1 crossings |
| `pcb/floorplan/FLOORPLAN-STUDY.md` | the escape-pressure method and the cost-table rule |
| `pcb/LAYER-USE-POLICY.md` | six layers, L2/L5 solid ground, no AGND/DGND split |
| `architecture/DOMAINS-OF-CONCERN.md` | the domain list, and why the matrix waits for VAL-G1 |

---

## Package 1 — SSCM-1 recovery pass

**One bounded attempt. Do not open-endedly search.**

The v1.0 pin map declared frozen on 2026-08-14 could not be located in `K1.hardware` or
`SpectraSynq-Instrument-Spine`; every hit there was footprint-library noise. The DualMCU
firmware repository contains no SSCM-1, M.2 or carrier reference at all.

Report one of two outcomes:

- **Found** — cite exactly where, and state what it specifies beyond the pin budget already
  recorded in `STATUS.md`: which processors the module carries, interface semantics per contact,
  and the ownership boundary. This changes Package 2's input, so stop and report before
  continuing.
- **Not found** — say so plainly, list where you looked, and proceed to Package 2 using
  `contracts/sscm1-v2/` as the authority.

Do not reconstruct a specification from fragments. Do not infer one from the pin budget.

---

## Package 2 — B versus C escape-pressure study

Apply the method in `FLOORPLAN-STUDY.md`. Both options, same rigour.

### Option B — the connector is the question

Not "do the signals fit the pin count". The question is whether the functional groups can cross
M.2 B-key **with appropriate grounds, adjacency, signal integrity and real contingency, without
making the connector the most constrained object in the product.**

Work from `pin-budget.csv`. Several rows carry status `OPEN` — the audio clock direction rows in
particular. **Analyse around them. Do not resolve them.** An open row is an input to your study,
not a decision you get to make. State explicitly how each open row changes the answer under each
plausible resolution.

Report: total crossings by class, ground adjacency demand, which groups must not neighbour,
where contingency lands, and whether the budget survives. If it does not, say Option B fails at
the requirements stage and why. That is a legitimate and useful result.

### Option C — the package edges are the question

Which RT1062 package edges carry the most escape pressure from west-side LED outputs, the audio
interface, the bridge, USB experiments, service and debug access. Compute raw density and
weighted pressure separately, per the method.

Report which edge is worst, whether the worst edge is also the most constrained, and what that
forces for orientation. This is the analysis that settles RT1062 rotation before a part is placed.

### Both options

Every proposal carries its cost. The benefit-and-cost table in `FLOORPLAN-STUDY.md` is mandatory,
not illustrative. **If nothing got worse, the analysis is not finished.**

---

## Boundaries

- No EasyEDA project, schematic, PCB, Gerber, BOM, CPL or DSN is created by this work.
- No GPIO assignment. Physical placement precedes pin assignment, always.
- No component part numbers frozen. TMUX1574 and any reset supervisor are candidates only.
- No ownership change. The matrix is settled.
- Do not import, open or measure any pre-existing board or project from anywhere.
- Historical CopperPilot lanes, including `SpectraSynq-K1-CORE-Final`, are evidence only. Its
  stepped-T geometry and numbers are prior art and do not transfer. The method does.

## Output

Two documents in this directory: `P1-SSCM1-RECOVERY.md` and `P2-B-VS-C-STUDY.md`.

Show your arithmetic on the page. Label projections as projected — a number computed from a
proposal is not a measurement, and calling it one is the specific failure this project's gates
exist to catch. Include a "Not done" section.

Stop after Package 2. Do not proceed to any gate beyond VAL-G1.
