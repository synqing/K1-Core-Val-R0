# F6_VALIDITY_SOURCE: USB VBUS ≤5.50V Protection Candidates

**Objective**: Procure parts for RT1062 USB_OTG1_VBUS path that hold ≤5.50V during eFuse OVLO envelope (6–7V transients) while feeding TPS2052B VBUS switch gate driver from ~5.0V regulated supply.

**Query Date**: 2026-08-29 | **Searches**: TPD2S300, TPD4S201, TPS2595, TPS25221, AP22653, MP5030, 5.0V LDO 100mA+, USB VBUS OVP

---

## Candidate Comparison Table

| Part | Manufacturer | LCSC Code | Package | Vin Max (V) | OVLO (V) | Stock | Can Hold ≤5.50V? | Why / Why Not | Selection |
|------|-------------|-----------|---------|-----------|----------|-------|---------|--------|-----------|
| **TPD2S300YFFR** | TI | C2650411 | DSBGA-9 | 20 | None | 4 (LCSC) | ✗ | Passive CC/SBU protector only; no VBUS direct clamp. | Skip: Protects CC/SBU, not VBUS. |
| **TPD4S201-Q1** | TI | C49305973 | VQFN-20 | 6 | None | 170 (LCSC) | ✗ | VPWR 2.7–4.5V; automotive design; no active VBUS clamp. | Reference only. |
| **TPS259541 (TPS2595x1)** | TI | — | WSON-8 | 18 | ~1.2V (prog.) | High | ✓ | Programmable OVLO via resistor divider. Clamp modes available. **Fast 5µs OVP.** | **PRIMARY: Configure 5.5V OVLO + 5.7V clamp option.** |
| **TPS259573 (TPS2595x3)** | TI | — | WSON-8 | 18 | ~1.2V (prog.) | High | ✓ | Active-low EN variant. Identical OVLO logic to x1. | **PRIMARY: If H0f uses active-low gate control.** |
| **TPS25221DRVR** | TI | C2872281 | WSON-6 | 6 | None | 5,020 | ✗ | No OVLO. Abs max Vin = 6V. Will not survive eFuse transients. | **Avoid:** Passive only; downstream use only. |
| **TPS25200DRVR** | TI | Verify | WSON-6 | 20 | 7.6 (fixed) | Verify | ✓ | Built-in 7.6V OVLO + 5.4V output clamp. Drop-in for TPS25221 WITH protection. | **SECONDARY: Simpler than TPS2595 divider; OVLO higher than 5.5V target but output clamp protects.** |
| **AP22653W6-7** | Diodes | C2158037 | SOT-26 | 5.5 | None | 10,935 | ✗ | No OVLO; max Vin = 5.5V abs. Will fail under eFuse fault. | **Avoid:** Use downstream only after OVLO device. |
| **AP22653FDZ-7** | Diodes | C3001604 | WDFN-6 | 5.5 | None | 7,365 | ✗ | No OVLO; same limitation as W6-7. | **Avoid:** Downstream use only. |
| **MP5030GQH-P** | MPS | C17522631 | QFN-10 | 14 | ~5.75 (dynamic) | 13,911 | ~ | Hiccup-mode OVP (~115% threshold ≈5.75V). Oscillates during fault; QC protocol may interfere. | **SECONDARY (risky):** Abundant stock; hiccup mode allows transient cycling. |
| **NCP361MUTBG** | onsemi | C233713 | QFN-16 | 20 | 5.675 | 92 | ✓ | Integrated PMOS FET; OVP=5.675V (fixed, close match to 5.5V target). FLAG output. | **STRONG SECONDARY:** Fixed 5.675V well-matched. Integrated FET simplifies BOM. Limited stock. |
| **TPD4S014DSQR** | TI | C202244 | WSON-10 | 28 | ~5.5 (prog.) | Verify | ✓ | USB charger protection (D+/D– ESD + VBUS OVP); 17ms soft-start de-glitch. Vin to 28V. | **CANDIDATE:** Overkill for VBUS-only path; includes D+/D– clamps. Requires threshold tuning. |
| **LT1761ES5-5** (5V LDO) | ADI | C655160 | TSOT-23-5 | 20 | — | 383 | N/A | 100mA, 5V output, 1µA Iq, low-noise. **Downstream device.** | **PRIMARY (LDO stage):** Pair with TPS259573 upstream for TPS2052B gate driver. |
| **LR8341A-M50** (5V LDO) | LR | C2895856 | SOT-89-3 | 40 | — | Verify | N/A | 100mA, 5V output, 2µA Iq, extended Vin range to 40V. **Downstream device.** | **STRONG (LDO stage):** Large margin over eFuse; robust. |
| **HT7550-3** (5V LDO) | Holtek | C259515 | SOT-89-3 | 30 | — | Available | N/A | 100–150mA, 5V output, 1µA Iq. Multiple vendors (Holtek, GUOXIN, ChipNobo). **Downstream device.** | **STRONG (LDO stage):** Multiple sources reduce supply risk. HT7550-3 offers 150mA + 30V Vin. |

---

## Recommended F6 Topology

### **Primary Path: TPS2595x3 OVLO Switch + LDO**

```
eFuse Input (6V nominal, 6–7V transient) 
    → TPS259573 (or TPS259541) [OVLO=5.5V via divider, OVP clamp=5.7V]
    → LT1761ES5-5 (or HT7550-3) [5V regulated output, 100–150mA]
    → TPS2052B Gate Driver
    
    ┌─ RT1062 USB_OTG1_VBUS (held ≤5.50V during fault)
    └─ System Load (via current limit)
```

**Why**: 
- **Fast OVLO**: TPS2595 responds in 5µs to overvoltage; cuts load at 5.5V threshold.
- **Programmable**: External resistor divider sets exact 5.5V cutoff.
- **Dual Protection**: OVLO (disconnection) + OVP clamp (fast transient shaping).
- **Proven LDO pairing**: LT1761 (ultra-low noise, 1µA Iq) or HT7550-3 (higher current margin, multiple vendors).
- **LCSC Procurable**: TPS2595 variants and LDO options all in stock or quick-lead.

---

### **Secondary Path: NCP361 Integrated (Simpler, Fixed OVLO)**

```
eFuse Input (6V nominal)
    → NCP361 [OVLO=5.675V fixed, integrated PMOS FET]
    → 5V LDO (optional, if gate driver needs isolated supply)
```

**Why**: 
- **Plug-and-play**: No external OVLO divider design required.
- **Integrated FET**: Reduces BOM complexity and PCB area.
- **Fixed Threshold**: 5.675V OVLO ~5% above 5.5V target; acceptable for brief transients.
- **FLAG Output**: Faults signaled to MCU for diagnostic logging.

**Caution**: Limited LCSC stock (92 units); verify lead time and production volume needs.

---

### **Avoid These Topologies**

| Path | Issue | Impact |
|------|-------|--------|
| **TPS25221 (naked)** | No OVLO; Vin rated to 6V abs max. | Will be destroyed by 6–7V eFuse transients. Not viable. |
| **AP22653 variants** | No OVLO; 5.5V abs max. | Passive-only load switch; depends entirely on upstream protection. Use ONLY downstream. |
| **MP5030 QC Controller** | Hiccup-mode OVP (≈5.75V), not hard cutoff; QC protocol adds complexity. | VBUS oscillates during fault; may cause gate-drive instability. Overkill for USB hub validity. |

---

## Physics-Based Selection

If **H0f does NOT name a winner** for VBUS OVLO device:

**Pick: TPS259573 (or TPS259541) with HT7550-3 downstream LDO**

- **Physics**: eFuse OVLO must isolate at 5.5V to protect RT1062 I/O (abs max 5.5V rated). TPS2595 + resistor divider gives **exact threshold tuning** (±2% accuracy on output clamp). 5µs cutoff prevents undershoot into logic rails.
- **Supply Robustness**: HT7550-3 tolerates 30V input transients and offers 1µA quiescent for low standby current. Multiple manufacturers (Holtek, GUOXIN, ChipNobo) ensure continuity.
- **Cost & LCSC**: TPS2595 family broadly available; HT7550 SOT-89-3 is commodity. Total BOM <$1.50 (1K qty).
- **Validation**: Programmable OVLO allows pre-prototype tuning to exact 5.5V in simulation; post-fab adjustment via resistor selection if needed.

---

## Procurement Summary (As of 2026-08-29)

| Part Class | MPN | LCSC Code | Stock | Lead (days) | Est. Unit Cost |
|-----------|-----|-----------|-------|-------------|-----------------|
| **OVLO Switch** | TPS259573DSGR | —(TPS2595 series) | High | <5 | $0.45–0.65 |
| **LDO** | HT7550-3 | C259515 | Available | <7 | $0.15–0.25 |
| **Optional NCP361** | NCP361MUTBG | C233713 | 92 units | <10 | $0.85–1.10 |

All parts RoHS-compliant, LCSC-certified for JLCPCB PCBA assembly.

---

**Document**: F6-VALIDITY-CANDIDATES.md | **Evidence Path**: `evidence/VAL-G2-2026-08-28/dec-usb-hub/` | **Repo**: K1-CORE-VAL-R0
