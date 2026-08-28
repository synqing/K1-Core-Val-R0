---
abstract: "Pin-by-pin audit of the audio capture block on K1-CORE-VAL-R0 (U11-AUD TLV320ADC6120, J8/J9-AUD, C46-C53, C90/C91, R28-R41, FB5, TP3/4/5/7/8) plus the MIC_PWR_EN switch chain, against frozen denominator 489736:464c27d4. Answers: MIC_PWR_EN is ACTIVE LOW through a DMG2305UX P-channel high-side switch with a 100k pull-DOWN, so the mic rail defaults ON at power-up and through RT1062 reset, and the sheet nowhere states this (defect AUD-01); the PDM route XOR is annotation-only, the DNP alternates R40/R41 carry a 10k MPN that would not work if populated, and both drivers meet on one node (AUD-02/AUD-03); clock isolation exists on MCLK/BCLK/FSYNC but the documented procedure disconnects the RT1062 from BCLK/FSYNC so it can no longer clock in AUDIO_DOUT (AUD-04). ADC6120 decoupling and GPIO1/GPI1/GPI2 repurposing verified correct against the TI datasheet."
---

# PIN-AUDIT-AUDIO — audio capture, clock and mic flex

**Status: PROPOSAL.** Findings are proposals against a frozen snapshot. A single writer must reconfirm
against live, which has moved past this hash.

| | |
|---|---|
| Frozen denominator | `frozen-denominator-489736/` · hash `489736:464c27d4` |
| External denominator | `anchors/schDrcLog_2026-08-28.txt` (195 floating-pin entries, not derived from this audit) |
| Machine-readable | `pin-audit-s3-audio.json` |
| Scope B components audited | 36 of 36 · **102 pins, 100% classified, 0 unresolved** |

Method, registration and the oracle fault battery are documented in `PIN-AUDIT-S3.md` §1 and apply
identically here. Every Scope B component registers at offset `(0,0)`, an exact fit to EasyEDA's own
DRC verdict. Stub counts re-derived here reproduce every audio net count quoted in the brief exactly.

---

## 1. Headline answers

### 1.1 `MIC_PWR_EN` polarity — **ACTIVE LOW, defaults the rail ON** · derived from the selected part

Measured topology, end to end:

```
5V_SYS ─ U5-PWR2 TLV75533 (IN, EN tied to 5V_SYS = always enabled) ─ OUT
   └─ 3V3_MIC_REG ─ Q1-PWR2 pin 2 (SOURCE)
                    Q1-PWR2 pin 1 (GATE) ─ MIC_PWR_EN ─┬─ R9-PWR2 100k ─ GND   ← PULL-DOWN
                                                       └─ U6-RTC.J11 (RT1062 GPIO)
                    Q1-PWR2 pin 3 (DRAIN) ─ 3V3_MIC ─ C15-PWR2 10 µF
                       └─ FB5-AUD 220 Ω @100 MHz ─ 3V3_MIC_FLEX ─ C53-AUD 100nF ─ J9-AUD.1
```

**Q1-PWR2 is a DMG2305UX, a P-channel MOSFET** (Diodes Incorporated, SOT-23: pin 1 gate, pin 2 source,
pin 3 drain; Vgs(th) typ 0.9 V, Vgs max ±8 V). It is wired as a high-side switch with source on the
LDO output and drain on the load.

| Question | Answer | Derivation |
|---|---|---|
| Active level | **ACTIVE LOW** | P-channel: gate below source by more than \|Vgs(th)\| turns it ON. Gate at 0 V ⇒ Vgs = −3.3 V ⇒ fully on. Gate at 3.3 V ⇒ Vgs = 0 ⇒ off. |
| Power-on default | **RAIL ON** | R9-PWR2 100k pulls the gate to **GND**. With the RT1062 pin high-Z the gate sits at 0 V, so the FET is fully enhanced and `3V3_MIC` comes up unconditionally. |
| While the RT pin is high-Z during and after reset | **RAIL ON** | Same path. The rail is live before firmware runs, throughout RT1062 reset, during ISP/recovery, and permanently if firmware never boots. |
| Can the RT1062 hold it OFF? | Yes | RT VOH ≈ 3.1 V against a 3.3 V source gives \|Vgs\| = 0.2 V, below the 0.4 V minimum threshold ⇒ off, with 0.2 V of margin. |

This is a **defined** state, not an indeterminate one — but it is not a *deliberately chosen* one, and
that is the problem. See **AUD-01**.

The supply value is safe: the Infineon IM69D130 recommended VDD range is **1.62 V to 3.6 V**, so the
3.3 V delivered on `3V3_MIC_FLEX` is in range. (The LCSC parametric field lists "1.8 V" for this part;
the Infineon datasheet is the authority and it does not agree.)

### 1.2 PDM route XOR — **FAIL as an interlock, PASS as an annotation**

```
                        ┌─ R38-AUD  0R      ─ PDM_CLK_ADC ─ U11-AUD.11 (GPIO1)   route A
J9-AUD.3 ─ PDM_CLK ─────┼─ R40-AUD  DNP     ─ PDM_CLK_RT  ─ U6-RTC.J13           route B
                        └─ TP4-AUD

                        ┌─ R39-AUD  0R      ─ PDM_DAT_ADC ─ U11-AUD.3 (IN2P_GPI1) route A
J9-AUD.5 ─ PDM_DAT ─────┼─ R41-AUD  DNP     ─ PDM_DAT_RT  ─ U6-RTC.L13            route B
                        └─ TP5-AUD
```

The brief asks whether the XOR is enforced using **distinct nets per owner**, and whether two
resistors landing on one shared net counts. Answering both halves honestly:

* **The per-owner nets *are* distinct.** `PDM_CLK_ADC` and `PDM_CLK_RT` are separate nets, as are
  `PDM_DAT_ADC` and `PDM_DAT_RT`. They converge only on `PDM_CLK` / `PDM_DAT`, which *are the
  microphone's own clock and data pins*. The microphone has one clock pin. Any two candidate drivers
  must meet there. This is the minimum achievable merge point, and no 0R/DNP matrix can do better.
* **Therefore the XOR is not, and cannot be, enforced by topology.** The only thing preventing both
  routes being populated is the DNP marking in the BOM — an annotation, not a mechanism.
* **The consequence is asymmetric and is worst on the clock.** If R38 *and* R40 are both populated,
  the ADC6120's GPIO1 PDM clock **output** is hard-shorted to the RT1062 SAI clock **output** through
  0 Ω: two active push-pull drivers into each other. On the data line the ADC's GPI1 and the RT's SAI
  input are both **receivers**, so R39 + R41 both populated is electrically benign.

**Verdict: the exclusivity requirement is met in net naming and documented on the sheet, but there is
no physical interlock and the clock-contention case is unguarded.** See **AUD-02** and **AUD-03**.

The route choice *is* recorded beside the circuit, as `contracts/microphone-interface.md` requires —
sheet text `e129958`: *"PDM DEFAULT R38/R39 | DIRECT RT R40/R41 = DNP EXPERIMENT"*. It states which
route is default and which is the experiment. **It does not state "never both."**

### 1.3 Clock master default and external override — **isolation exists, but the documented procedure breaks capture**

```
U6-RTC.J14 ─ AUDIO_MCLK_RT  ─ R31 22Ω ─ AUDIO_MCLK_ISO  ─ R34 0R ─┐
       ???  ─ AUDIO_BCLK_RT  ─ R32 22Ω ─ AUDIO_BCLK_ISO  ─ R35 0R ─┤  shared clock nets, each also
U6-RTC.H11 ─ AUDIO_FSYNC_RT ─ R33 22Ω ─ AUDIO_FSYNC_ISO ─ R36 0R ─┘  reaching U11-AUD, J8-AUD, a TP
```

`AUDIO_MCLK` → U11-AUD.19 (`MICBIAS_GPI2`), J8-AUD.1, TP3-AUD, C52 (DNP tune), R57-VAL (DNP).
`AUDIO_BCLK` → U11-AUD.7, J8-AUD.2, TP7-AUD. `AUDIO_FSYNC` → U11-AUD.8, J8-AUD.3, TP8-AUD.

RT1062 is the default master ✓. J8-AUD is a 4-pin external clock header (MCLK / BCLK / FSYNC / GND) ✓.
Removing R31–R33 does genuinely cut the RT1062 away from all three clock nets ✓, and the sheet
documents the procedure — text `e129956`: *"RT CLOCK MASTER | REMOVE R31-R33 BEFORE EXTERNAL J8
DRIVE"*. The named resistors are the correct ones (they are the cut nearest the RT, which leaves no
long unterminated stub on the driven net).

**But that procedure also removes the RT1062's ability to receive.** `AUDIO_DOUT` runs
U11-AUD.6 → R37 22 Ω → U6-RTC.H12. The RT1062's SAI needs BCLK and FSYNC to sample it. With R31–R33
removed the RT has neither, so in external-clock mode it cannot clock in the ADC's TDM output at all.
`contracts/audio-interface.md` requires that the capture path used to evaluate converter dynamic range
preserve full sample width — which means the RT1062 must be *in* the loop during that evaluation.
See **AUD-04**.

### 1.4 ADC6120 pin-by-pin — **all 21 pins classified; decoupling and pin repurposing correct**

Verified against the TI TLV320ADC6120 datasheet, Table 6-1 and §8.3.2/8.3.3:

| Pin | Name | Net | Verdict | Datasheet check |
|---|---|---|---|---|
| 1 | IN1P | — | INTENTIONAL_NC | analogue channel unused — see AUD-05 |
| 2 | IN1M | — | INTENTIONAL_NC | see AUD-05 |
| 3 | IN2P_GPI1 | `PDM_DAT_ADC` | CONNECTED | ✓ GPI1 configurable as **PDM data input** (PDMDIN1/2) |
| 4 | IN2M_GPO1 | — | INTENTIONAL_NC | see AUD-05 |
| 5 | VSS | `GND` | GND | ✓ |
| 6 | SDOUT | `AUDIO_DOUT_ADC` | CONNECTED | ✓ TDM/I2S data out → R37 → RT1062.H12 |
| 7 | BCLK | `AUDIO_BCLK` | CONNECTED | ✓ slave-mode bit clock in |
| 8 | FSYNC | `AUDIO_FSYNC` | CONNECTED | ✓ slave-mode frame sync in |
| 9 | IOVDD | `3V3` | POWER | ✓ IOVDD range 3.0–3.6 V |
| 10 | VSS | `GND` | GND | ✓ |
| 11 | GPIO1 | `PDM_CLK_ADC` | CONNECTED | ✓ GPIO1 configurable as **PDM clock output** |
| 12 | SDA | `I2C_SDA` | CONNECTED | R28 4.7k pull-up ✓ |
| 13 | SCL | `I2C_SCL` | CONNECTED | R29 4.7k pull-up ✓ |
| 14 | DREG | `ADC_DREG` | POWER | ✓ **10 µF (C91) + 0.1 µF (C49) in parallel to VSS — exactly as specified** |
| 15 | VSS | `GND` | GND | ✓ |
| 16 | AVDD | `3V3` | POWER | ✓ AVDD 3.0–3.6 V with on-chip AREG regulator |
| 17 | AREG | `ADC_AREG` | POWER | ✓ **10 µF (C90) + 0.1 µF (C48) in parallel to AVSS — exactly as specified** |
| 18 | VREF | `ADC_VREF` | POWER | ✓ **1 µF (C51) to AVSS — exactly as specified** |
| 19 | MICBIAS_GPI2 | `AUDIO_MCLK` | CONNECTED | ✓ GPI2 configurable as **MCLK input**. MICBIAS is correctly sacrificed — the IM69D130 is a digital PDM mic and needs no bias |
| 20 | VSS | `GND` | GND | ✓ |
| 21 | EP | `GND` | GND | ✓ exposed pad grounded |

The GPIO1 / GPI1 / GPI2 allocation is coherent and each assignment is a documented capability of the
part, not an assumption. MCLK is not strictly required in slave mode when the internal PLL is enabled,
but TI recommends the PLL for high-performance work and the board supplies MCLK anyway — correct for
a dynamic-range evaluation.

**No 16-bit application path is imposed by this hardware.** `SDOUT` is a plain TDM/I2S output into the
RT1062 SAI; sample width is a firmware and SAI-configuration matter, and nothing on this sheet
truncates it. The `contracts/audio-interface.md` measurement constraint is not violated by the
schematic.

### 1.5 Mic flex, J9-AUD

`J9-AUD` (FH12-10S-0.5SH, 10 positions + 2 hold-downs): pin 1 `3V3_MIC_FLEX`, 2 `GND`,
3 `PDM_CLK`, 4 `GND`, 5 `PDM_DAT`, 6 `GND`, 7–10 floating, 11/12 floating. This matches the sheet's
own annotation `e129957` exactly — *"J9: 1 PWR | 2 GND | 3 CLK | 4 GND | 5 DATA | 6 GND | 7-10 NC"* —
and the GND-interleaved signal ordering is the right choice for a 3.072 MHz clock on flex.

`PDM_CLK` target: the IM69D130's specified clock range is **0.4 MHz to 3.3 MHz**, with the
high-performance mode band at 2.9–3.072 MHz. **3.072 MHz is supported and sits at the top of that
band** — matching `contracts/microphone-interface.md` and `architecture/CLOCK-ARCHITECTURE.md`. Note
there is only ~7 % headroom to the absolute maximum, so under route B the RT1062's SAI divider must
land on 3.072 MHz accurately rather than overshoot.

---

## 2. Defects

### AUD-01 — `MIC_PWR_EN` is active LOW, defaults the rail ON, and the sheet says neither · **HIGH**

Three separate problems in one net:

1. **The name inverts the behaviour.** A signal called `MIC_PWR_EN` that is asserted by driving it
   *low* is a firmware trap: writing 1 to "MIC power enable" turns the microphone off.
2. **The default is ON, and it was probably not chosen.** R9-PWR2 is a 100k pull-**down**, so the
   switched `3V3_MIC` rail comes up with the board and stays up through RT1062 reset. If the intended
   safe default is "microphone unpowered until firmware asks for it", R9 must instead pull **up to
   `3V3_MIC_REG`** — Q1's source, not the main `3V3` rail, so that Vgs can never be reversed during
   rail sequencing.
3. **`contracts/audio-interface.md` and `microphone-interface.md` require the active level to be
   annotated on the sheet beside the circuit. It is not.** All 22 `TEXT` primitives on the sheet were
   read; none mentions `MIC_PWR_EN`, its polarity, or the rail's power-on state.

**Fix:** decide the safe default explicitly, set R9's destination to match, and add a sheet
annotation of the form `MIC_PWR_EN: ACTIVE LOW (P-FET gate) | default <ON|OFF> via R9 pull-<down|up>`.
If the default stays ON, rename the net `MIC_PWR_EN_N` so firmware cannot get the sense wrong.

### AUD-02 — PDM route exclusivity has no physical interlock, and clock contention is unguarded · **HIGH**

R38 (0R, fitted) and R40 (DNP) both land on `PDM_CLK`. Populating both hard-shorts the ADC6120's
GPIO1 clock output to the RT1062's SAI clock output through 0 Ω — two push-pull drivers in
contention. Nothing but a BOM annotation prevents it, and the sheet note names the default route
without prohibiting the both-populated case.

**Fix, in order of strength:** (a) amend the sheet note to read *"POPULATE R38+R39 **XOR** R40+R41 —
NEVER BOTH; both fitted shorts two clock drivers"*; (b) make R38 and R40 **22 Ω rather than 0 Ω**, so
a double-populate is current-limited instead of a dead short — 22 Ω is harmless at 3.072 MHz into a
MEMS mic clock input and is already the house value elsewhere on this board; (c) if a real interlock
is wanted, the two routes need a mux or a physically shared single footprint, which is a bigger
change than this validation board warrants.

### AUD-03 — the DNP route-B alternates carry a 10 kΩ part number · **HIGH**

R40-AUD and R41-AUD are marked `DNP` but their supplier part is **`RC0402FR-0710KL` — a 10 kΩ
resistor**. R38/R39, the fitted route-A pair, are `RC0402FR-070RL` (0 Ω).

If anyone populates R40/R41 to enable the direct-RT experiment as documented, they will place 10 kΩ in
series with a 3.072 MHz PDM clock and its return data. With the mic's input capacitance and the flex,
the RC time constant destroys the clock edge — route B will simply not work, and the failure will look
like a firmware or decimation problem rather than a BOM problem. This is precisely the experiment
`contracts/audio-interface.md` says *"must be proven"*.

**Fix:** change the R40/R41 part to 0 Ω or 22 Ω (matching whatever AUD-02 settles on), keeping the DNP
fitting instruction.

### AUD-04 — the documented clock-isolation procedure disconnects the RT1062 from BCLK/FSYNC · **HIGH**

Sheet text `e129956` instructs *"REMOVE R31-R33 BEFORE EXTERNAL J8 DRIVE"*. That is electrically safe
and it does isolate the RT1062's outputs, which is what the contract asks for. But it also leaves the
RT1062 with no bit clock and no frame sync, so it can no longer sample `AUDIO_DOUT`. The
external-clock evaluation mode, as documented, cannot capture through the RT1062 — only through a
scope or analyser at J8/TP3/TP7/TP8.

`contracts/audio-interface.md` requires the capture path used to evaluate converter dynamic range to
preserve full sample width, which puts the RT1062 SAI inside the measurement loop. The two
requirements as currently realised are in conflict.

**Fix [INFERENCE — needs confirmation by whoever owns the RT1062 SAI configuration]:** the i.MX RT
SAI supports slave operation with BCLK/FSYNC as inputs and MCLK direction selectable. If so, the
correct external-override procedure is *"leave R31–R33 fitted; configure the RT1062 SAI as clock
slave so its clock pins become inputs; drive J8"*, with the 22 Ω acting as damping. Resistor removal
then becomes the fallback for the case where the SAI cannot be put into slave mode, and the sheet
note should say which mode it is describing.

### AUD-05 — three ADC6120 analogue pins float on a dynamic-range evaluation board · **MEDIUM**

`IN1P` (pin 1), `IN1M` (pin 2) and `IN2M_GPO1` (pin 4) are unconnected. The TI datasheet does not
sanction leaving them open: §8.3.3 says unused analogue input channels *can be repurposed* as GPIx/GPOx
via the `CHx_INSRC[1:0]` register bits, and every typical-application figure shows these pins
connected to external components. On a board whose stated purpose is resolving a 113 dB against
123 dB question, three floating high-impedance analogue nodes on the measurement die are an avoidable
noise-injection path.

**Fix:** terminate them (to AVSS or the common-mode reference per the datasheet) or register them
explicitly as GPIx/GPOx and record that decision on the sheet.

### AUD-06 — J9-AUD shell tabs are not grounded · **MEDIUM**

`J9-AUD` pins 11 and 12 float. On an FH12-10S-0.5SH these are the hold-down / shell tabs [INFERENCE:
a 10-position part presented with 12 symbol pins, and the sheet's own annotation accounts for signal
pins 1–10 only]. An ungrounded connector shell on a flex carrying a 3.072 MHz clock is an EMI
liability in both directions and gives the flex shield no return.

**Fix:** tie pins 11 and 12 to `GND`.

### AUD-07 — ADC AVDD shares the noisy main 3V3 rail · **MEDIUM**

The microphone gets a dedicated LDO (U5-PWR2 TLV75533 → `3V3_MIC_REG`), a switch, a 10 µF bulk cap and
a ferrite. **The converter does not.** U11-AUD's `AVDD` (pin 16) and `IOVDD` (pin 9) both sit on the
board-wide `3V3` net, shared with the ESP32-S3 radio, the RT1062, the NFC front end and the
accelerometer. The on-chip AREG regulator and the C90/C48 network give some rejection, but for the
113/123 dB measurement this is the wrong rail to share. Worth quantifying before the evaluation rather
than after an ambiguous result.

### AUD-08 — R30-AUD does not exist · **LOW**

The `-AUD` designator sequence runs R28, R29, **R31**, R32 … R41. R30 is absent from the frozen source
(evidence file `container-6-r30-removed.png` suggests a deliberate removal). Harmless in itself, but a
numbering hole invites a future part to reuse the reference and silently collide with history.

### AUD-09 — C52-AUD DNP alternate is 100 pF on MCLK · **LOW**

C52-AUD is `DNP / 100pF MCLK TUNE`. If ever populated, 100 pF on an MCLK line up to 24.576 MHz is a
large load. Same observation applies to C43/C44-ESP on USB. All three are correctly DNP today; the
note is that the *alternate value* should be re-picked (10 pF is the usual starting point) before
anyone fits them.

---

## 3. Coverage and what this audit could not see

| | |
|---|---|
| Components in frozen source | 230 (228 designated, 1 undesignated `e1`) |
| Designators with pin readback | 228 |
| Pins parsed across the whole board | 782 |
| Nets in frozen source | 143 |
| **Scope A + B components audited** | **64** |
| **Scope A + B pins audited and classified** | **222 · 0 unresolved** |
| Verdict tally (A + B) | CONNECTED 104 · GND 44 · POWER 39 · INTENTIONAL_NC 29 · RESERVED_WITH_DOCUMENTED_REASON 6 |

**Honest gaps:**

* **U6-RTC (MIMXRT1062DVJ6B) is covered at 98 balls.** EasyEDA's DRC names 111 floating U6-RTC pins,
  of which 73 lie outside that readback. Wherever an in-scope net crosses into the RT1062 I can name
  the ball only if it falls inside those 98.
* **`AUDIO_BCLK_RT` is the one in-scope case where that bites.** Its far stub terminates at sheet
  `(2415, 4660)` — inside the U6-RTC symbol extent but outside the 98-ball readback, so I cannot name
  the ball. I initially read this as a stub to nowhere and that was wrong: EasyEDA's DRC lists seven
  single-pin nets (`BUCK_SS`, `NFC_AGDC`, `NFC_VDD_A/AM/D/DR/RF`) and `AUDIO_BCLK_RT` is **not** among
  them, so the connection exists. **UNVERIFIED as to which ball — not a defect.** 25 further stubs in
  the same coordinate band (`1V15_CORE`, `3V3`, `GND`, `BOOT_MODE0/1`, `SWD_SWCLK/SWDIO`,
  `LED_D0_3V3`, `LED_D1_3V3`) sit in exactly the same position; A3-RT-DEBUG should take a full
  196-ball readback.
* **No PCB geometry, placement, routing or RF work is in this audit** — that is VAL-G3.
* **Nothing here was written to the schematic.** No EasyEDA tool was called at any point.

---

## 4. Sources

Primary vendor documentation, which outranks CopperPilot, Voice PE, Teensy, old K1 and agent memory:

* [TI TLV320ADC6120 datasheet](https://www.ti.com/lit/ds/symlink/tlv320adc6120.pdf) — Table 6-1 pin
  functions and required AREG / DREG / VREF capacitors; Table 8-51 GPIO1 / GPI1 / GPI2 function
  assignment; §8.3.2 clocking and PLL; §8.3.3 analogue-input repurposing; Table 7-3 recommended
  operating conditions; §11.1 layout guidelines
* [Infineon IM69D130 datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-im69d130-datasheet-en.pdf)
  — VDD 1.62–3.6 V; PDM clock range 0.4–3.3 MHz with the 2.9–3.072 MHz high-performance band
  ([DigiKey HTML mirror](https://www.digikey.com/en/htmldatasheets/production/2844684/0/0/1/im69d130))
* Diodes Incorporated DMG2305UX — P-channel, SOT-23 G/S/D, Vgs(th) 0.9 V typ, Vgs ±8 V
  ([LCSC C144153 parametric record](https://www.lcsc.com/product-detail/C144153.html))

---
**Document Changelog**

| Date | Author | Change |
|------|--------|--------|
| 2026-08-28 | agent:A4-S3-AUDIO | Created — Scope B pin audit against frozen denominator 489736:464c27d4 |
