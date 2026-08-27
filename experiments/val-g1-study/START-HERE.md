# START HERE — CopperPilot, K1-CORE-VAL-R0

You are producing **two analysis documents**. You are not building anything.

Read this page, then the five files below, then begin.

---

## What this project is

K1-CORE-VAL-R0 is a hardware validation platform, not the production K1 mainboard.
Experimental capability, observability, electrical correctness and future flexibility outrank
PCB area and BOM cost. The board may grow east-west whenever more area materially improves the
design.

**There is no EasyEDA project. There is no schematic. There is no PCB.** That is correct and
deliberate: the architecture gate that decides where the compute lives has not closed. Your work
is what closes it.

Do not create, clone, copy or open an EasyEDA project. Do not open any pre-existing board,
netlist, Gerber or schematic from anywhere, including archives, backups or another folder. If
you encounter one, do not read it. If you believe the specification is incomplete, **stop and say
so** — do not go looking for a source to fill the gap.

---

## Read these, in this order

1. `AGENTS.md` — the rules you operate under. The section headed **CopperPilot role** is binding.
2. `experiments/val-g1-study/BRIEF-COPPERPILOT.md` — your two work packages and their reading list.
3. `authority/02-Q0-B-vs-C.md` — the open gate.
4. `pcb/floorplan/FLOORPLAN-STUDY.md` — the escape-pressure method and the mandatory cost table.
5. `pcb/LAYER-USE-POLICY.md` and `pcb/STACKUP-STATUS.md` — the layer budget you must work inside.

---

## The split

**Settled, and not yours to reopen:** processor ownership; K1BR payload semantics; the six-layer
baseline and its L3/L4 assignment; NFC front-end location; the terminology rules; every row in
`authority/03-OWNERSHIP-MATRIX.csv`.

**Yours, entirely:** the escape-pressure analysis, the corridor and congestion findings, the
orientation reasoning, the crossing-set assessment for Option B, the alternatives you considered
and rejected, and the recommendation you argue for.

Take this seriously as an engineering problem. The last time this method was applied it found
that ten signals were escaping into 3.76 mm of board while six had 86 mm, and reshaping the
outline around that bottleneck was the first genuinely useful floorplanning result the project
produced. That is the standard.

---

## The four rules that matter most

**1. There is no board, so there is no measurement.**
Every number you produce is computed from a proposal. Label it **projected**. Calling a
projection a measurement is the specific failure this project's gates exist to catch, and it is
the failure that got a previous round rejected.

**2. Never report a result you did not produce by running the thing.**
This is the one unrecoverable offence. If a check did not run, say it did not run. A fabricated
pass is worse than any defect, because it ends the checking.

**3. Never edit a check, a rule, an expectation or an authority file.**
Not to make something pass, not to correct what looks like a mistake. If you believe an
authority document is wrong, say so in your report with the reasoning. Do not change it.

**4. Open items are inputs, not decisions.**
Rows marked `OPEN` in `contracts/sscm1-v2/pin-budget.csv` — the audio-clock directions in
particular — stay open. Analyse around them. State how each plausible resolution changes your
answer.

---

## What you may not do

- Create any EasyEDA project, schematic, PCB, Gerber, BOM, CPL or DSN.
- Place a component, route a trace, or produce geometry intended for import.
- Assign GPIO. Physical placement precedes pin assignment, always.
- Freeze a component part number. Candidates only.
- Change the layer count, the L3/L4 assignment, the stackup, any net name or any ownership row.
- Run the repository harnesses and report their result as your evidence.
- Write to any file outside `experiments/val-g1-study/`.
- Commit anything.

---

## Where you are expected to push back

If you believe a rule here is wrong **on physics**, say so with the arithmetic. That is a
contribution, not insubordination, and it will be read.

What is not acceptable is quietly working around a rule and hoping nobody notices.

---

## Execution order

| Step | Action | Exit condition |
| --- | --- | --- |
| 1 | Read this page and the five files | — |
| 2 | **Package 1** — bounded SSCM-1 recovery pass | `P1-SSCM1-RECOVERY.md` written. If the v1.0 spec is found, **stop and report** — it changes Package 2's input |
| 3 | **Package 2** — B versus C escape-pressure study | `P2-B-VS-C-STUDY.md` written |
| 4 | Stop | — |

Do not proceed past step 4. VAL-G2 and everything downstream are not authorised.

---

## What a good report looks like

- Arithmetic shown on the page, not asserted.
- Every projected figure labelled projected.
- Every proposal carrying its **cost** as well as its benefit. If nothing got worse, the analysis
  is not finished.
- The alternatives you rejected, and why.
- A **"Not done"** section naming everything you did not finish and the reason.
- Any place where the supplied specification was insufficient, named rather than filled in.

**A report containing only successes is not trusted here.** Nothing in this toolchain has ever
gone right on the first pass; a clean sheet reads as an unchecked one.

---

## First actions

1. Confirm in one line that no EasyEDA project exists and that you will not create one.
2. Read the five files.
3. Open `BRIEF-COPPERPILOT.md` and execute Package 1.

There is nothing to ask before you start. If something genuinely blocks you, that itself is a
finding — write it down and report it.
